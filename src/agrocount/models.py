"""Entidades de domínio, invariantes e exceções de negócio do AgroCount IA (u1-agrocount-platform)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    """Retorna o timestamp UTC atual em formato ISO-8601."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class AgroCountError(Exception):
    """Exceção canônica de regras de negócio e validação com mapeamento HTTP."""

    def __init__(
        self,
        code: str,
        message: str,
        http_status: int = 422,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details or {}

    def to_envelope(self, correlation_id: str) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "correlation_id": correlation_id,
            }
        }


@dataclass
class Farm:
    """Entidade Fazenda (Unidade Produtiva Rural) — BR1.1, BR1.2."""

    id: str
    name: str
    code: str
    created_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> None:
        clean_name = (self.name or "").strip()
        if len(clean_name) < 3 or len(clean_name) > 120:
            raise AgroCountError(
                code="INVALID_FARM_NAME",
                message="O nome da fazenda deve possuir entre 3 e 120 caracteres.",
                http_status=400,
                details={"name": self.name},
            )
        self.name = clean_name
        clean_code = (self.code or "").strip().upper()
        if not clean_code or len(clean_code) > 40:
            raise AgroCountError(
                code="INVALID_FARM_CODE",
                message="O código da fazenda é obrigatório e deve ter até 40 caracteres.",
                http_status=400,
                details={"code": self.code},
            )
        self.code = clean_code

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Paddock:
    """Entidade Pasto / Piquete — BR1.2, BR1.3."""

    id: str
    farm_id: str
    name: str
    code: str
    area_hectares: Optional[float] = None
    created_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> None:
        if not self.farm_id:
            raise AgroCountError(
                code="MISSING_FARM_ID",
                message="Todo pasto/piquete deve estar associado a uma fazenda válida.",
                http_status=400,
            )
        clean_name = (self.name or "").strip()
        if len(clean_name) < 2 or len(clean_name) > 120:
            raise AgroCountError(
                code="INVALID_PADDOCK_NAME",
                message="O nome do pasto/piquete deve possuir entre 2 e 120 caracteres.",
                http_status=400,
                details={"name": self.name},
            )
        self.name = clean_name
        clean_code = (self.code or "").strip().upper()
        if not clean_code or len(clean_code) > 40:
            raise AgroCountError(
                code="INVALID_PADDOCK_CODE",
                message="O código do pasto/piquete é obrigatório.",
                http_status=400,
                details={"code": self.code},
            )
        self.code = clean_code
        if self.area_hectares is not None and self.area_hectares <= 0:
            raise AgroCountError(
                code="INVALID_PADDOCK_AREA",
                message="A área em hectares do pasto deve ser estritamente positiva (> 0).",
                http_status=400,
                details={"area_hectares": self.area_hectares},
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


VALID_MEDIA_TYPES = ("IMAGE_4K", "VIDEO_DRONE")
VALID_INSPECTION_STATUSES = (
    "UPLOADED",
    "VALIDATING",
    "INFERRING",
    "READY_FOR_REVIEW",
    "AUDITED",
    "FAILED_VALIDATION",
)


@dataclass
class Inspection:
    """Entidade Inspeção de Voo de Drone — BR2.1, BR2.2, BR4.2, BR4.3."""

    id: str
    farm_id: str
    paddock_id: str
    idempotency_key: str
    media_type: str
    source_uri: str
    file_size_bytes: int
    flight_altitude_m: Optional[int] = None
    overlap_pct: Optional[int] = None
    status: str = "UPLOADED"
    active_model_version: str = "yolo11m-agro-v1.0"
    raw_ai_count: int = 0
    final_audited_count: Optional[int] = None
    error_code: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)
    completed_at: Optional[str] = None

    def validate_metadata(self) -> None:
        if not self.idempotency_key or not self.idempotency_key.strip():
            raise AgroCountError(
                code="MISSING_IDEMPOTENCY_KEY",
                message="A chave de idempotência (idempotency_key) é obrigatória.",
                http_status=400,
            )
        if self.status not in VALID_INSPECTION_STATUSES:
            raise AgroCountError(
                code="INVALID_INSPECTION_STATUS",
                message=f"Status de inspeção inválido: {self.status}",
                http_status=400,
            )
        if self.flight_altitude_m is not None and not (10 <= self.flight_altitude_m <= 500):
            raise AgroCountError(
                code="INVALID_FLIGHT_ALTITUDE",
                message="A altitude de voo deve estar entre 10m e 500m.",
                http_status=400,
                details={"flight_altitude_m": self.flight_altitude_m},
            )
        if self.overlap_pct is not None and not (0 <= self.overlap_pct <= 95):
            raise AgroCountError(
                code="INVALID_OVERLAP_PCT",
                message="O percentual de sobreposição (overlap_pct) deve estar entre 0 e 95.",
                http_status=400,
                details={"overlap_pct": self.overlap_pct},
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionRun:
    """Entidade Execução de Inferência IA — BR3.1, BR3.2, BR3.3."""

    id: str
    inspection_id: str
    model_version: str
    inference_mode: str  # SAHI_SLICED | BYTETRACK_VIDEO
    total_slices_or_frames: int
    high_confidence_count: int
    uncertain_count: int
    execution_ms: int
    created_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> None:
        if self.inference_mode not in ("SAHI_SLICED", "BYTETRACK_VIDEO"):
            raise AgroCountError(
                code="INVALID_INFERENCE_MODE",
                message=f"Modo de inferência inválido: {self.inference_mode}",
                http_status=400,
            )
        if self.total_slices_or_frames < 1:
            raise AgroCountError(
                code="INVALID_SLICE_COUNT",
                message="O total de fatias/frames processados deve ser >= 1.",
                http_status=400,
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


VALID_CONFIDENCE_TIERS = ("high_confidence", "uncertain")
VALID_REVIEW_STATUSES = (
    "AI_AUTO",
    "AI_UNCERTAIN",
    "HUMAN_CONFIRMED",
    "HUMAN_REMOVED_FP",
    "HUMAN_ADDED",
)


@dataclass
class BoundingBoxDetection:
    """Entidade Caixa Delimitadora de Animal — BR3.3, BR4.1."""

    id: str
    detection_run_id: str
    inspection_id: str
    frame_or_slice_index: int
    x_center: float
    y_center: float
    width: float
    height: float
    confidence: float
    confidence_tier: str
    review_status: str
    track_id: Optional[int] = None
    reviewed_by: Optional[str] = None
    updated_at: str = field(default_factory=utc_now_iso)

    def validate_geometry(self) -> None:
        if not (0.0 <= self.x_center <= 1.0 and 0.0 <= self.y_center <= 1.0):
            raise AgroCountError(
                code="INVALID_BOUNDING_BOX_CENTER",
                message="As coordenadas x_center e y_center devem estar normalizadas em [0.0, 1.0].",
                http_status=422,
                details={"x_center": self.x_center, "y_center": self.y_center},
            )
        if not (0.0 < self.width <= 1.0 and 0.0 < self.height <= 1.0):
            raise AgroCountError(
                code="INVALID_BOUNDING_BOX_DIMENSIONS",
                message="As dimensões width e height devem ser estritamente positivas em (0.0, 1.0].",
                http_status=422,
                details={"width": self.width, "height": self.height},
            )
        if self.confidence_tier not in VALID_CONFIDENCE_TIERS:
            raise AgroCountError(
                code="INVALID_CONFIDENCE_TIER",
                message=f"Faixa de confiança inválida: {self.confidence_tier}",
                http_status=422,
            )
        if self.review_status not in VALID_REVIEW_STATUSES:
            raise AgroCountError(
                code="INVALID_REVIEW_STATUS",
                message=f"Status de revisão inválido: {self.review_status}",
                http_status=422,
            )

    def to_yolo_line(self) -> str:
        """Retorna a linha formatada no padrão YOLO (<class_id> <x_center> <y_center> <width> <height>)."""
        return f"0 {self.x_center:.6f} {self.y_center:.6f} {self.width:.6f} {self.height:.6f}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HitlCorrectionBatch:
    """Entidade Lote de Correções Human-in-the-Loop — BR4.1, BR4.2, BR4.3."""

    id: str
    inspection_id: str
    auditor_id: str
    confirmed_count: int
    false_positive_removed_count: int
    false_negative_added_count: int
    net_delta: int
    golden_sample_id: str
    submitted_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> None:
        expected_delta = self.false_negative_added_count - self.false_positive_removed_count
        if self.net_delta != expected_delta:
            raise AgroCountError(
                code="INVALID_HITL_NET_DELTA",
                message="Invariante violada: net_delta deve ser igual a false_negative_added_count - false_positive_removed_count.",
                http_status=422,
                details={"net_delta": self.net_delta, "expected": expected_delta},
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GoldenDatasetSample:
    """Entidade Amostra Curada do Golden Dataset — BR5.1."""

    id: str
    inspection_id: str
    hitl_batch_id: str
    media_gcs_uri: str
    yolo_labels_gcs_uri: str
    metadata_gcs_uri: str
    total_boxes: int
    manual_corrections_count: int
    base_model_version: str
    used_in_model_version: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


VALID_MODEL_STATUSES = ("TRAINING", "ACTIVE", "REJECTED_REGRESSION", "ARCHIVED")


@dataclass
class ModelVersion:
    """Entidade Versão do Modelo de Visão Computacional — BR5.2, BR5.3."""

    version_tag: str
    parent_version_tag: Optional[str]
    weights_gcs_uri: str
    golden_samples_used: int
    validation_map50: float
    validation_counting_accuracy: float
    status: str
    promoted_at: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> None:
        if self.status not in VALID_MODEL_STATUSES:
            raise AgroCountError(
                code="INVALID_MODEL_STATUS",
                message=f"Status de versão de modelo inválido: {self.status}",
                http_status=422,
            )
        if not (0.0 <= self.validation_map50 <= 1.0 and 0.0 <= self.validation_counting_accuracy <= 1.0):
            raise AgroCountError(
                code="INVALID_MODEL_METRICS",
                message="As métricas de validação devem estar no intervalo [0.0, 1.0].",
                http_status=422,
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuditReport:
    """Entidade Laudo de Auditoria Exportado (PDF/CSV) — BR6.1."""

    id: str
    inspection_id: str
    format: str  # PDF | CSV
    report_gcs_uri: str
    sha256_checksum: str
    generated_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> None:
        if self.format not in ("PDF", "CSV"):
            raise AgroCountError(
                code="INVALID_REPORT_FORMAT",
                message="O formato do laudo deve ser PDF ou CSV.",
                http_status=400,
                details={"format": self.format},
            )
        if not self.sha256_checksum.startswith("sha256:") or len(self.sha256_checksum) != 71:
            raise AgroCountError(
                code="INVALID_REPORT_CHECKSUM",
                message="O checksum SHA-256 do laudo deve possuir o formato 'sha256:<64_hex>'.",
                http_status=422,
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewSessionState:
    """Estado de Sessão de Revisão no Estúdio Web HITL (`WebReviewStudioComponent`)."""

    inspection_id: str
    selected_box_id: Optional[str] = None
    active_filter: str = "UNCERTAIN_ONLY"  # ALL | UNCERTAIN_ONLY | MANUAL_EDITS
    zoom_level: float = 1.0
    pan_x: float = 0.0
    pan_y: float = 0.0
    dirty_changes_count: int = 0
    keyboard_shortcuts_enabled: bool = True

    def set_zoom(self, zoom: float) -> None:
        if not (0.5 <= zoom <= 8.0):
            raise AgroCountError(
                code="INVALID_ZOOM_LEVEL",
                message="O nível de zoom deve estar entre 0.5x e 8.0x.",
                http_status=400,
                details={"zoom_level": zoom},
            )
        self.zoom_level = round(zoom, 2)

    def set_filter(self, filter_mode: str) -> None:
        if filter_mode not in ("ALL", "UNCERTAIN_ONLY", "MANUAL_EDITS"):
            raise AgroCountError(
                code="INVALID_REVIEW_FILTER",
                message="Filtro de revisão inválido.",
                http_status=400,
                details={"active_filter": filter_mode},
            )
        self.active_filter = filter_mode

    def apply_keyboard_shortcut(
        self,
        key: str,
        uncertain_box_ids: List[str],
    ) -> Dict[str, Any]:
        """Processa atalhos de teclado do Estúdio HITL (Setas, Espaço, Delete, N)."""
        if not self.keyboard_shortcuts_enabled:
            return {"action": "IGNORED", "selected_box_id": self.selected_box_id}

        if key in ("ArrowRight", "ArrowDown"):
            if not uncertain_box_ids:
                self.selected_box_id = None
            elif self.selected_box_id not in uncertain_box_ids:
                self.selected_box_id = uncertain_box_ids[0]
            else:
                idx = uncertain_box_ids.index(self.selected_box_id)
                self.selected_box_id = uncertain_box_ids[(idx + 1) % len(uncertain_box_ids)]
            return {"action": "NAVIGATE_NEXT", "selected_box_id": self.selected_box_id}

        if key in ("ArrowLeft", "ArrowUp"):
            if not uncertain_box_ids:
                self.selected_box_id = None
            elif self.selected_box_id not in uncertain_box_ids:
                self.selected_box_id = uncertain_box_ids[-1]
            else:
                idx = uncertain_box_ids.index(self.selected_box_id)
                self.selected_box_id = uncertain_box_ids[(idx - 1) % len(uncertain_box_ids)]
            return {"action": "NAVIGATE_PREV", "selected_box_id": self.selected_box_id}

        if key == "Space" and self.selected_box_id:
            self.dirty_changes_count += 1
            return {"action": "CONFIRM", "box_id": self.selected_box_id}

        if key in ("Delete", "Backspace") and self.selected_box_id:
            self.dirty_changes_count += 1
            return {"action": "REMOVE_FALSE_POSITIVE", "box_id": self.selected_box_id}

        if key in ("KeyN", "n", "N"):
            return {"action": "DRAW_MODE_NEW_BOX", "selected_box_id": self.selected_box_id}

        return {"action": "NOOP", "selected_box_id": self.selected_box_id}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
