"""Camada de persistência transacional SQLite e armazenamento atômico de artefatos (Golden Dataset e Laudos)."""

from __future__ import annotations

import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    AgroCountError,
    AuditReport,
    BoundingBoxDetection,
    DetectionRun,
    Farm,
    GoldenDatasetSample,
    HitlCorrectionBatch,
    Inspection,
    ModelVersion,
    Paddock,
    utc_now_iso,
)


class AgroCountRepository:
    """Repositório transacional SQLite e espelho local do bucket gs://agrocount-storage."""

    def __init__(self, db_path: str = ":memory:", storage_dir: Optional[str] = None) -> None:
        self.db_path = db_path
        self.storage_root = Path(storage_dir or os.path.join(os.getcwd(), "data", "storage"))
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._init_schema()
        self._seed_default_model()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS farms (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS paddocks (
                    id TEXT PRIMARY KEY,
                    farm_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    area_hectares REAL,
                    created_at TEXT NOT NULL,
                    UNIQUE(farm_id, code),
                    FOREIGN KEY(farm_id) REFERENCES farms(id)
                );

                CREATE TABLE IF NOT EXISTS inspections (
                    id TEXT PRIMARY KEY,
                    farm_id TEXT NOT NULL,
                    paddock_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    media_type TEXT NOT NULL,
                    source_uri TEXT NOT NULL,
                    file_size_bytes INTEGER NOT NULL,
                    flight_altitude_m INTEGER,
                    overlap_pct INTEGER,
                    status TEXT NOT NULL,
                    active_model_version TEXT NOT NULL,
                    raw_ai_count INTEGER NOT NULL DEFAULT 0,
                    final_audited_count INTEGER,
                    error_code TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY(farm_id) REFERENCES farms(id),
                    FOREIGN KEY(paddock_id) REFERENCES paddocks(id)
                );

                CREATE TABLE IF NOT EXISTS detection_runs (
                    id TEXT PRIMARY KEY,
                    inspection_id TEXT NOT NULL UNIQUE,
                    model_version TEXT NOT NULL,
                    inference_mode TEXT NOT NULL,
                    total_slices_or_frames INTEGER NOT NULL,
                    high_confidence_count INTEGER NOT NULL,
                    uncertain_count INTEGER NOT NULL,
                    execution_ms INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(inspection_id) REFERENCES inspections(id)
                );

                CREATE TABLE IF NOT EXISTS bounding_box_detections (
                    id TEXT PRIMARY KEY,
                    detection_run_id TEXT NOT NULL,
                    inspection_id TEXT NOT NULL,
                    frame_or_slice_index INTEGER NOT NULL,
                    track_id INTEGER,
                    x_center REAL NOT NULL,
                    y_center REAL NOT NULL,
                    width REAL NOT NULL,
                    height REAL NOT NULL,
                    confidence REAL NOT NULL,
                    confidence_tier TEXT NOT NULL,
                    review_status TEXT NOT NULL,
                    reviewed_by TEXT,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(detection_run_id) REFERENCES detection_runs(id),
                    FOREIGN KEY(inspection_id) REFERENCES inspections(id)
                );

                CREATE TABLE IF NOT EXISTS hitl_correction_batches (
                    id TEXT PRIMARY KEY,
                    inspection_id TEXT NOT NULL UNIQUE,
                    auditor_id TEXT NOT NULL,
                    confirmed_count INTEGER NOT NULL,
                    false_positive_removed_count INTEGER NOT NULL,
                    false_negative_added_count INTEGER NOT NULL,
                    net_delta INTEGER NOT NULL,
                    golden_sample_id TEXT NOT NULL,
                    submitted_at TEXT NOT NULL,
                    FOREIGN KEY(inspection_id) REFERENCES inspections(id)
                );

                CREATE TABLE IF NOT EXISTS golden_dataset_samples (
                    id TEXT PRIMARY KEY,
                    inspection_id TEXT NOT NULL UNIQUE,
                    hitl_batch_id TEXT NOT NULL UNIQUE,
                    media_gcs_uri TEXT NOT NULL,
                    yolo_labels_gcs_uri TEXT NOT NULL,
                    metadata_gcs_uri TEXT NOT NULL,
                    total_boxes INTEGER NOT NULL,
                    manual_corrections_count INTEGER NOT NULL,
                    base_model_version TEXT NOT NULL,
                    used_in_model_version TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(inspection_id) REFERENCES inspections(id)
                );

                CREATE TABLE IF NOT EXISTS model_versions (
                    version_tag TEXT PRIMARY KEY,
                    parent_version_tag TEXT,
                    weights_gcs_uri TEXT NOT NULL,
                    golden_samples_used INTEGER NOT NULL,
                    validation_map50 REAL NOT NULL,
                    validation_counting_accuracy REAL NOT NULL,
                    status TEXT NOT NULL,
                    promoted_at TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_reports (
                    id TEXT PRIMARY KEY,
                    inspection_id TEXT NOT NULL,
                    format TEXT NOT NULL,
                    report_gcs_uri TEXT NOT NULL,
                    sha256_checksum TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    FOREIGN KEY(inspection_id) REFERENCES inspections(id)
                );
                """
            )

    def _seed_default_model(self) -> None:
        row = self.conn.execute(
            "SELECT version_tag FROM model_versions WHERE status = 'ACTIVE' LIMIT 1"
        ).fetchone()
        if not row:
            now = utc_now_iso()
            baseline = ModelVersion(
                version_tag="yolo11m-agro-v1.0",
                parent_version_tag=None,
                weights_gcs_uri="gs://agrocount-storage/models/yolo11m-agro-v1.0/best.pt",
                golden_samples_used=0,
                validation_map50=0.952,
                validation_counting_accuracy=0.960,
                status="ACTIVE",
                promoted_at=now,
                created_at=now,
            )
            self.save_model_version(baseline)

    # --- Storage helpers (gs://agrocount-storage/... <-> local path) ---

    def resolve_gcs_uri(self, gcs_uri: str) -> Path:
        prefix = "gs://agrocount-storage/"
        rel = gcs_uri[len(prefix) :] if gcs_uri.startswith(prefix) else gcs_uri.lstrip("/")
        safe_parts = [p for p in Path(rel).parts if p not in ("..", ".", "/", "\\")]
        target = self.storage_root.joinpath(*safe_parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def write_gcs_artifact(self, gcs_uri: str, content: bytes | str) -> Path:
        """Escreve artefato de forma atômica (.tmp -> os.replace)."""
        target = self.resolve_gcs_uri(gcs_uri)
        tmp_path = target.with_suffix(target.suffix + f".{uuid.uuid4().hex[:8]}.tmp")
        data = content.encode("utf-8") if isinstance(content, str) else content
        with open(tmp_path, "wb") as f:
            f.write(data)
            f.flush()
        os.replace(tmp_path, target)
        return target

    def read_gcs_artifact(self, gcs_uri: str) -> bytes:
        target = self.resolve_gcs_uri(gcs_uri)
        if not target.exists():
            raise AgroCountError(
                code="ARTIFACT_NOT_FOUND",
                message=f"Artefato não encontrado em {gcs_uri}",
                http_status=404,
            )
        return target.read_bytes()

    # --- Farms & Paddocks ---

    def save_farm(self, farm: Farm, paddocks: Optional[List[Paddock]] = None) -> Dict[str, Any]:
        farm.validate()
        paddock_list = paddocks or []
        for p in paddock_list:
            p.validate()
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO farms (id, name, code, created_at) VALUES (?, ?, ?, ?)",
                    (farm.id, farm.name, farm.code, farm.created_at),
                )
                for p in paddock_list:
                    self.conn.execute(
                        """
                        INSERT INTO paddocks (id, farm_id, name, code, area_hectares, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (p.id, p.farm_id, p.name, p.code, p.area_hectares, p.created_at),
                    )
        except sqlite3.IntegrityError as exc:
            raise AgroCountError(
                code="DUPLICATE_FARM_OR_PADDOCK_CODE",
                message="Código de fazenda ou pasto já cadastrado.",
                http_status=409,
                details={"reason": str(exc)},
            ) from exc

        return {
            **farm.to_dict(),
            "paddocks": [p.to_dict() for p in paddock_list],
        }

    def list_farms(self) -> List[Dict[str, Any]]:
        farms = self.conn.execute("SELECT * FROM farms ORDER BY created_at DESC").fetchall()
        result: List[Dict[str, Any]] = []
        for f in farms:
            paddocks = self.conn.execute(
                "SELECT * FROM paddocks WHERE farm_id = ? ORDER BY code ASC",
                (f["id"],),
            ).fetchall()
            result.append(
                {
                    **dict(f),
                    "paddocks": [dict(p) for p in paddocks],
                }
            )
        return result

    def get_farm(self, farm_id: str) -> Optional[Farm]:
        row = self.conn.execute("SELECT * FROM farms WHERE id = ?", (farm_id,)).fetchone()
        return Farm(**dict(row)) if row else None

    def get_paddock(self, paddock_id: str) -> Optional[Paddock]:
        row = self.conn.execute("SELECT * FROM paddocks WHERE id = ?", (paddock_id,)).fetchone()
        return Paddock(**dict(row)) if row else None

    # --- Inspections & Detections ---

    def get_inspection_by_idempotency_key(self, idempotency_key: str) -> Optional[Inspection]:
        row = self.conn.execute(
            "SELECT * FROM inspections WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        return Inspection(**dict(row)) if row else None

    def get_inspection(self, inspection_id: str) -> Optional[Inspection]:
        row = self.conn.execute(
            "SELECT * FROM inspections WHERE id = ?",
            (inspection_id,),
        ).fetchone()
        return Inspection(**dict(row)) if row else None

    def list_inspections(
        self,
        farm_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Inspection]:
        query = "SELECT * FROM inspections WHERE 1=1"
        params: List[Any] = []
        if farm_id:
            query += " AND farm_id = ?"
            params.append(farm_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [Inspection(**dict(r)) for r in rows]

    def save_inspection(self, inspection: Inspection) -> Inspection:
        inspection.validate_metadata()
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO inspections (
                    id, farm_id, paddock_id, idempotency_key, media_type, source_uri,
                    file_size_bytes, flight_altitude_m, overlap_pct, status,
                    active_model_version, raw_ai_count, final_audited_count,
                    error_code, created_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    active_model_version = excluded.active_model_version,
                    raw_ai_count = excluded.raw_ai_count,
                    final_audited_count = excluded.final_audited_count,
                    error_code = excluded.error_code,
                    completed_at = excluded.completed_at
                """,
                (
                    inspection.id,
                    inspection.farm_id,
                    inspection.paddock_id,
                    inspection.idempotency_key,
                    inspection.media_type,
                    inspection.source_uri,
                    inspection.file_size_bytes,
                    inspection.flight_altitude_m,
                    inspection.overlap_pct,
                    inspection.status,
                    inspection.active_model_version,
                    inspection.raw_ai_count,
                    inspection.final_audited_count,
                    inspection.error_code,
                    inspection.created_at,
                    inspection.completed_at,
                ),
            )
        return inspection

    def save_detection_run_and_boxes(
        self,
        run: DetectionRun,
        boxes: List[BoundingBoxDetection],
    ) -> None:
        run.validate()
        for b in boxes:
            b.validate_geometry()
        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO detection_runs (
                    id, inspection_id, model_version, inference_mode,
                    total_slices_or_frames, high_confidence_count,
                    uncertain_count, execution_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.inspection_id,
                    run.model_version,
                    run.inference_mode,
                    run.total_slices_or_frames,
                    run.high_confidence_count,
                    run.uncertain_count,
                    run.execution_ms,
                    run.created_at,
                ),
            )
            self.conn.execute(
                "DELETE FROM bounding_box_detections WHERE inspection_id = ?",
                (run.inspection_id,),
            )
            for b in boxes:
                self.conn.execute(
                    """
                    INSERT INTO bounding_box_detections (
                        id, detection_run_id, inspection_id, frame_or_slice_index,
                        track_id, x_center, y_center, width, height,
                        confidence, confidence_tier, review_status, reviewed_by, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        b.id,
                        b.detection_run_id,
                        b.inspection_id,
                        b.frame_or_slice_index,
                        b.track_id,
                        b.x_center,
                        b.y_center,
                        b.width,
                        b.height,
                        b.confidence,
                        b.confidence_tier,
                        b.review_status,
                        b.reviewed_by,
                        b.updated_at,
                    ),
                )

    def get_detection_run(self, inspection_id: str) -> Optional[DetectionRun]:
        row = self.conn.execute(
            "SELECT * FROM detection_runs WHERE inspection_id = ?",
            (inspection_id,),
        ).fetchone()
        return DetectionRun(**dict(row)) if row else None

    def list_boxes_for_inspection(self, inspection_id: str) -> List[BoundingBoxDetection]:
        rows = self.conn.execute(
            "SELECT * FROM bounding_box_detections WHERE inspection_id = ? ORDER BY confidence ASC, id ASC",
            (inspection_id,),
        ).fetchall()
        return [BoundingBoxDetection(**dict(r)) for r in rows]

    def replace_boxes_and_save_hitl(
        self,
        inspection: Inspection,
        boxes: List[BoundingBoxDetection],
        batch: HitlCorrectionBatch,
        sample: GoldenDatasetSample,
    ) -> None:
        batch.validate()
        for b in boxes:
            b.validate_geometry()
        with self.conn:
            self.save_inspection(inspection)
            self.conn.execute(
                "DELETE FROM bounding_box_detections WHERE inspection_id = ?",
                (inspection.id,),
            )
            for b in boxes:
                self.conn.execute(
                    """
                    INSERT INTO bounding_box_detections (
                        id, detection_run_id, inspection_id, frame_or_slice_index,
                        track_id, x_center, y_center, width, height,
                        confidence, confidence_tier, review_status, reviewed_by, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        b.id,
                        b.detection_run_id,
                        b.inspection_id,
                        b.frame_or_slice_index,
                        b.track_id,
                        b.x_center,
                        b.y_center,
                        b.width,
                        b.height,
                        b.confidence,
                        b.confidence_tier,
                        b.review_status,
                        b.reviewed_by,
                        b.updated_at,
                    ),
                )
            self.conn.execute(
                """
                INSERT INTO hitl_correction_batches (
                    id, inspection_id, auditor_id, confirmed_count,
                    false_positive_removed_count, false_negative_added_count,
                    net_delta, golden_sample_id, submitted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch.id,
                    batch.inspection_id,
                    batch.auditor_id,
                    batch.confirmed_count,
                    batch.false_positive_removed_count,
                    batch.false_negative_added_count,
                    batch.net_delta,
                    batch.golden_sample_id,
                    batch.submitted_at,
                ),
            )
            self.conn.execute(
                """
                INSERT INTO golden_dataset_samples (
                    id, inspection_id, hitl_batch_id, media_gcs_uri,
                    yolo_labels_gcs_uri, metadata_gcs_uri, total_boxes,
                    manual_corrections_count, base_model_version,
                    used_in_model_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sample.id,
                    sample.inspection_id,
                    sample.hitl_batch_id,
                    sample.media_gcs_uri,
                    sample.yolo_labels_gcs_uri,
                    sample.metadata_gcs_uri,
                    sample.total_boxes,
                    sample.manual_corrections_count,
                    sample.base_model_version,
                    sample.used_in_model_version,
                    sample.created_at,
                ),
            )

    def get_hitl_batch(self, inspection_id: str) -> Optional[HitlCorrectionBatch]:
        row = self.conn.execute(
            "SELECT * FROM hitl_correction_batches WHERE inspection_id = ?",
            (inspection_id,),
        ).fetchone()
        return HitlCorrectionBatch(**dict(row)) if row else None

    def get_golden_sample_by_inspection(self, inspection_id: str) -> Optional[GoldenDatasetSample]:
        row = self.conn.execute(
            "SELECT * FROM golden_dataset_samples WHERE inspection_id = ?",
            (inspection_id,),
        ).fetchone()
        return GoldenDatasetSample(**dict(row)) if row else None

    def list_unused_golden_samples(self) -> List[GoldenDatasetSample]:
        rows = self.conn.execute(
            "SELECT * FROM golden_dataset_samples WHERE used_in_model_version IS NULL ORDER BY created_at ASC"
        ).fetchall()
        return [GoldenDatasetSample(**dict(r)) for r in rows]

    def list_all_golden_samples(self) -> List[GoldenDatasetSample]:
        rows = self.conn.execute(
            "SELECT * FROM golden_dataset_samples ORDER BY created_at ASC"
        ).fetchall()
        return [GoldenDatasetSample(**dict(r)) for r in rows]

    def mark_golden_samples_used(self, sample_ids: List[str], version_tag: str) -> None:
        if not sample_ids:
            return
        with self.conn:
            for sid in sample_ids:
                self.conn.execute(
                    "UPDATE golden_dataset_samples SET used_in_model_version = ? WHERE id = ?",
                    (version_tag, sid),
                )

    # --- Model Versions ---

    def get_active_model(self) -> ModelVersion:
        row = self.conn.execute(
            "SELECT * FROM model_versions WHERE status = 'ACTIVE' ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            self._seed_default_model()
            row = self.conn.execute(
                "SELECT * FROM model_versions WHERE status = 'ACTIVE' LIMIT 1"
            ).fetchone()
        return ModelVersion(**dict(row))

    def get_training_model(self) -> Optional[ModelVersion]:
        row = self.conn.execute(
            "SELECT * FROM model_versions WHERE status = 'TRAINING' LIMIT 1"
        ).fetchone()
        return ModelVersion(**dict(row)) if row else None

    def list_model_versions(self) -> List[ModelVersion]:
        rows = self.conn.execute(
            "SELECT * FROM model_versions ORDER BY created_at DESC"
        ).fetchall()
        return [ModelVersion(**dict(r)) for r in rows]

    def save_model_version(self, model: ModelVersion) -> ModelVersion:
        model.validate()
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO model_versions (
                    version_tag, parent_version_tag, weights_gcs_uri,
                    golden_samples_used, validation_map50,
                    validation_counting_accuracy, status, promoted_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(version_tag) DO UPDATE SET
                    status = excluded.status,
                    validation_map50 = excluded.validation_map50,
                    validation_counting_accuracy = excluded.validation_counting_accuracy,
                    promoted_at = excluded.promoted_at
                """,
                (
                    model.version_tag,
                    model.parent_version_tag,
                    model.weights_gcs_uri,
                    model.golden_samples_used,
                    model.validation_map50,
                    model.validation_counting_accuracy,
                    model.status,
                    model.promoted_at,
                    model.created_at,
                ),
            )
        return model

    def promote_candidate_model(self, candidate: ModelVersion, previous_active_tag: str) -> None:
        now = utc_now_iso()
        candidate.status = "ACTIVE"
        candidate.promoted_at = now
        with self.conn:
            self.conn.execute(
                "UPDATE model_versions SET status = 'ARCHIVED' WHERE version_tag = ?",
                (previous_active_tag,),
            )
            self.save_model_version(candidate)

    # --- Audit Reports ---

    def save_audit_report(self, report: AuditReport) -> AuditReport:
        report.validate()
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO audit_reports (
                    id, inspection_id, format, report_gcs_uri, sha256_checksum, generated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report.id,
                    report.inspection_id,
                    report.format,
                    report.report_gcs_uri,
                    report.sha256_checksum,
                    report.generated_at,
                ),
            )
        return report

    def list_audit_reports(self, inspection_id: str) -> List[AuditReport]:
        rows = self.conn.execute(
            "SELECT * FROM audit_reports WHERE inspection_id = ? ORDER BY generated_at DESC",
            (inspection_id,),
        ).fetchall()
        return [AuditReport(**dict(r)) for r in rows]
