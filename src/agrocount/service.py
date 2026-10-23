"""Serviço de Gestão de Inspeções, Fazendas e Exportação de Laudos (`InspectionManagementComponent`)."""

from __future__ import annotations

import csv
import hashlib
import io
import uuid
from typing import Any, Dict, List, Optional

from .hitl import HitlActiveLearningComponent
from .models import (
    AgroCountError,
    AuditReport,
    Farm,
    Inspection,
    Paddock,
    utc_now_iso,
)
from .repository import AgroCountRepository
from .vision import CattleVisionEngineComponent


class InspectionManagementService:
    """Fachada de aplicação integrando Gestão de Fazendas/Inspeções, Visão Computacional, HITL e Laudos."""

    def __init__(
        self,
        repo: Optional[AgroCountRepository] = None,
        vision: Optional[CattleVisionEngineComponent] = None,
        hitl: Optional[HitlActiveLearningComponent] = None,
    ) -> None:
        self.repo = repo or AgroCountRepository()
        self.vision = vision or CattleVisionEngineComponent()
        self.hitl = hitl or HitlActiveLearningComponent(self.repo)

    # --- Fazendas e Pastos (BR1.1, BR1.2, BR1.3) ---

    def create_farm(
        self,
        name: str,
        code: str,
        paddocks_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        farm_id = f"farm-{uuid.uuid4().hex[:10]}"
        now = utc_now_iso()
        farm = Farm(id=farm_id, name=name, code=code, created_at=now)
        paddocks: List[Paddock] = []
        seen_codes = set()
        for p_item in paddocks_data or []:
            p_code = str(p_item.get("code") or "").strip().upper()
            if p_code in seen_codes:
                raise AgroCountError(
                    code="DUPLICATE_PADDOCK_CODE_IN_REQUEST",
                    message=f"Código de pasto duplicado na requisição: {p_code}",
                    http_status=409,
                )
            seen_codes.add(p_code)
            paddocks.append(
                Paddock(
                    id=f"pad-{uuid.uuid4().hex[:10]}",
                    farm_id=farm_id,
                    name=str(p_item.get("name") or ""),
                    code=p_code,
                    area_hectares=float(p_item["area_hectares"])
                    if p_item.get("area_hectares") is not None
                    else None,
                    created_at=now,
                )
            )
        return self.repo.save_farm(farm, paddocks)

    def list_farms(self) -> List[Dict[str, Any]]:
        return self.repo.list_farms()

    # --- Inspeções e Inferência IA (BR2.1, BR2.2, BR3.1, BR3.2, BR3.3) ---

    def create_inspection(
        self,
        farm_id: str,
        paddock_id: str,
        idempotency_key: str,
        media_type: str,
        source_uri: str,
        file_size_bytes: int,
        flight_altitude_m: Optional[int] = None,
        overlap_pct: Optional[int] = None,
        media_metadata: Optional[Dict[str, Any]] = None,
        custom_detections: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        # 1. Idempotência de submissão (BR2.1)
        existing = self.repo.get_inspection_by_idempotency_key(idempotency_key)
        if existing:
            return self.get_inspection_details(existing.id)

        # 2. Validação de vínculo Fazenda -> Pasto (BR1.2)
        farm = self.repo.get_farm(farm_id)
        if not farm:
            raise AgroCountError(
                code="FARM_NOT_FOUND",
                message=f"Fazenda '{farm_id}' não encontrada.",
                http_status=404,
            )
        paddock = self.repo.get_paddock(paddock_id)
        if not paddock or paddock.farm_id != farm_id:
            raise AgroCountError(
                code="PADDOCK_NOT_IN_FARM",
                message=f"O pasto '{paddock_id}' não pertence à fazenda '{farm_id}'.",
                http_status=422,
                details={"farm_id": farm_id, "paddock_id": paddock_id},
            )

        active_model = self.repo.get_active_model()
        inspection_id = f"insp-{uuid.uuid4().hex[:12]}"
        inspection = Inspection(
            id=inspection_id,
            farm_id=farm_id,
            paddock_id=paddock_id,
            idempotency_key=idempotency_key,
            media_type=media_type,
            source_uri=source_uri,
            file_size_bytes=int(file_size_bytes),
            flight_altitude_m=flight_altitude_m,
            overlap_pct=overlap_pct,
            status="VALIDATING",
            active_model_version=active_model.version_tag,
            raw_ai_count=0,
        )
        inspection.validate_metadata()

        # 3. Gate de validação pré-GPU em CPU (BR2.2)
        try:
            self.vision.validate_media_pre_gpu(
                media_type=media_type,
                source_uri=source_uri,
                file_size_bytes=int(file_size_bytes),
                media_metadata=media_metadata,
            )
        except AgroCountError as exc:
            inspection.status = "FAILED_VALIDATION"
            inspection.error_code = exc.code
            self.repo.save_inspection(inspection)
            raise

        # 4. Execução de Inferência IA (SAHI + NMS para 4K ou ByteTrack para Vídeo) (BR3.1–BR3.3)
        inspection.status = "INFERRING"
        self.repo.save_inspection(inspection)

        run, boxes = self.vision.run_inference(inspection, custom_detections=custom_detections)
        inspection.raw_ai_count = len(boxes)
        inspection.status = "READY_FOR_REVIEW"
        self.repo.save_inspection(inspection)
        self.repo.save_detection_run_and_boxes(run, boxes)

        return self.get_inspection_details(inspection.id)

    def list_inspections(
        self,
        farm_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        inspections = self.repo.list_inspections(farm_id=farm_id, status=status)
        return [i.to_dict() for i in inspections]

    def get_inspection_details(self, inspection_id: str) -> Dict[str, Any]:
        inspection = self.repo.get_inspection(inspection_id)
        if not inspection:
            raise AgroCountError(
                code="INSPECTION_NOT_FOUND",
                message=f"Inspeção '{inspection_id}' não encontrada.",
                http_status=404,
            )
        run = self.repo.get_detection_run(inspection_id)
        boxes = self.repo.list_boxes_for_inspection(inspection_id)
        high_cnt = sum(1 for b in boxes if b.confidence_tier == "high_confidence" and b.review_status != "HUMAN_REMOVED_FP")
        uncertain_cnt = sum(1 for b in boxes if b.review_status == "AI_UNCERTAIN")

        return {
            "id": inspection.id,
            "farm_id": inspection.farm_id,
            "paddock_id": inspection.paddock_id,
            "idempotency_key": inspection.idempotency_key,
            "media_type": inspection.media_type,
            "source_uri": inspection.source_uri,
            "file_size_bytes": inspection.file_size_bytes,
            "flight_altitude_m": inspection.flight_altitude_m,
            "overlap_pct": inspection.overlap_pct,
            "status": inspection.status,
            "active_model_version": inspection.active_model_version,
            "raw_ai_count": inspection.raw_ai_count,
            "final_audited_count": inspection.final_audited_count,
            "error_code": inspection.error_code,
            "created_at": inspection.created_at,
            "completed_at": inspection.completed_at,
            "summary": {
                "high_confidence_count": run.high_confidence_count if run else high_cnt,
                "uncertain_count": uncertain_cnt,
                "inference_mode": run.inference_mode if run else None,
                "execution_ms": run.execution_ms if run else 0,
            },
            "detections": [b.to_dict() for b in boxes],
        }

    # --- HITL & Active Learning (BR4.1–BR5.3) ---

    def submit_hitl_review(
        self,
        inspection_id: str,
        auditor_id: str,
        actions: List[Dict[str, Any]],
        idempotent_retry: bool = False,
    ) -> Dict[str, Any]:
        return self.hitl.submit_hitl_review(
            inspection_id=inspection_id,
            auditor_id=auditor_id,
            actions=actions,
            idempotent_retry=idempotent_retry,
        )

    def get_active_model_status(self) -> Dict[str, Any]:
        active = self.repo.get_active_model()
        unused = self.repo.list_unused_golden_samples()
        total_samples = self.repo.list_all_golden_samples()
        history = [m.to_dict() for m in self.repo.list_model_versions()]
        return {
            "active_model": {
                "version_tag": active.version_tag,
                "parent_version_tag": active.parent_version_tag,
                "validation_map50": active.validation_map50,
                "validation_counting_accuracy": active.validation_counting_accuracy,
                "promoted_at": active.promoted_at,
            },
            "golden_dataset_status": {
                "total_curated_samples": len(total_samples),
                "new_samples_since_last_train": len(unused),
                "ready_for_fine_tuning": len(unused) >= 10,
            },
            "version_history": history,
        }

    def trigger_fine_tuning(
        self,
        min_new_golden_samples: int = 10,
        target_epochs: int = 30,
        candidate_metrics: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        return self.hitl.trigger_fine_tuning(
            min_new_golden_samples=min_new_golden_samples,
            target_epochs=target_epochs,
            candidate_metrics=candidate_metrics,
        )

    # --- Exportação de Laudos Auditáveis PDF e CSV (BR6.1) ---

    def export_audit_report(self, inspection_id: str, fmt: str = "PDF") -> Dict[str, Any]:
        clean_fmt = (fmt or "PDF").strip().upper()
        if clean_fmt not in ("PDF", "CSV"):
            raise AgroCountError(
                code="INVALID_REPORT_FORMAT",
                message="O formato do laudo deve ser PDF ou CSV.",
                http_status=400,
                details={"format": fmt},
            )

        inspection = self.repo.get_inspection(inspection_id)
        if not inspection:
            raise AgroCountError(
                code="INSPECTION_NOT_FOUND",
                message=f"Inspeção '{inspection_id}' não encontrada.",
                http_status=404,
            )

        if inspection.status != "AUDITED":
            raise AgroCountError(
                code="INSPECTION_NOT_AUDITED",
                message="Laudos oficiais PDF/CSV só podem ser emitidos para inspeções com status AUDITED.",
                http_status=422,
                details={"inspection_id": inspection_id, "status": inspection.status},
            )

        farm = self.repo.get_farm(inspection.farm_id)
        paddock = self.repo.get_paddock(inspection.paddock_id)
        batch = self.repo.get_hitl_batch(inspection_id)
        boxes = self.repo.list_boxes_for_inspection(inspection_id)
        now = utc_now_iso()
        report_id = f"rep-{uuid.uuid4().hex[:12]}"

        if clean_fmt == "CSV":
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(
                [
                    "report_id",
                    "inspection_id",
                    "farm_code",
                    "paddock_code",
                    "active_model_version",
                    "raw_ai_count",
                    "confirmed_uncertain",
                    "false_positives_removed",
                    "false_negatives_added",
                    "final_audited_count",
                    "auditor_id",
                    "completed_at",
                ]
            )
            writer.writerow(
                [
                    report_id,
                    inspection.id,
                    farm.code if farm else inspection.farm_id,
                    paddock.code if paddock else inspection.paddock_id,
                    inspection.active_model_version,
                    inspection.raw_ai_count,
                    batch.confirmed_count if batch else 0,
                    batch.false_positive_removed_count if batch else 0,
                    batch.false_negative_added_count if batch else 0,
                    inspection.final_audited_count,
                    batch.auditor_id if batch else "N/A",
                    inspection.completed_at or now,
                ]
            )
            writer.writerow([])
            writer.writerow(["box_id", "x_center", "y_center", "width", "height", "confidence", "review_status"])
            for b in boxes:
                if b.review_status != "HUMAN_REMOVED_FP":
                    writer.writerow(
                        [b.id, b.x_center, b.y_center, b.width, b.height, b.confidence, b.review_status]
                    )
            raw_bytes = buf.getvalue().encode("utf-8")
            ext = "csv"
            content_type = "text/csv; charset=utf-8"
        else:
            raw_bytes = self._build_pdf_bytes(inspection, farm, paddock, batch, report_id, now)
            ext = "pdf"
            content_type = "application/pdf"

        digest = hashlib.sha256(raw_bytes).hexdigest()
        checksum = f"sha256:{digest}"
        report_uri = f"gs://agrocount-storage/reports/{inspection.id}/{report_id}.{ext}"
        self.repo.write_gcs_artifact(report_uri, raw_bytes)

        report = AuditReport(
            id=report_id,
            inspection_id=inspection.id,
            format=clean_fmt,
            report_gcs_uri=report_uri,
            sha256_checksum=checksum,
            generated_at=now,
        )
        self.repo.save_audit_report(report)

        return {
            **report.to_dict(),
            "content_type": content_type,
            "size_bytes": len(raw_bytes),
            "inspection_summary": {
                "farm_name": farm.name if farm else inspection.farm_id,
                "paddock_name": paddock.name if paddock else inspection.paddock_id,
                "raw_ai_count": inspection.raw_ai_count,
                "final_audited_count": inspection.final_audited_count,
                "active_model_version": inspection.active_model_version,
                "auditor_id": batch.auditor_id if batch else None,
            },
        }

    def _build_pdf_bytes(
        self,
        inspection: Inspection,
        farm: Optional[Farm],
        paddock: Optional[Paddock],
        batch: Optional[Any],
        report_id: str,
        generated_at: str,
    ) -> bytes:
        """Gera um documento PDF 1.4 válido com o laudo técnico de contagem bovina auditada."""
        lines = [
            "LAUDO OFICIAL DE AUDITORIA PECUARIA - AGROCOUNT IA",
            f"Relatorio ID: {report_id} | Emissao: {generated_at}",
            f"Fazenda: {farm.name if farm else inspection.farm_id} ({farm.code if farm else '-'})",
            f"Pasto / Piquete: {paddock.name if paddock else inspection.paddock_id} ({paddock.code if paddock else '-'})",
            f"Inspecao ID: {inspection.id} | Modelo IA: {inspection.active_model_version}",
            f"Contagem Bruta IA: {inspection.raw_ai_count} cabecas",
            (
                f"Ajustes HITL: +{batch.false_negative_added_count if batch else 0} FN / "
                f"-{batch.false_positive_removed_count if batch else 0} FP / "
                f"{batch.confirmed_count if batch else 0} confirmados"
            ),
            f"CONTAGEM FINAL AUDITADA: {inspection.final_audited_count} cabecas",
            f"Auditor Responsavel: {batch.auditor_id if batch else 'N/A'}",
        ]
        text_ops = ["BT", "/F1 11 Tf", "50 760 Td", "16 TL"]
        for line in lines:
            safe_line = line.replace("(", "\\(").replace(")", "\\)")
            text_ops.append(f"({safe_line}) Tj T*")
        text_ops.append("ET")
        stream_content = "\n".join(text_ops).encode("latin-1", errors="replace")

        pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
            b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
            + f"5 0 obj << /Length {len(stream_content)} >> stream\n".encode("ascii")
            + stream_content
            + b"\nendstream endobj\n"
            b"xref\n0 6\n0000000000 65535 f \n"
            b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n"
        )
        return pdf
