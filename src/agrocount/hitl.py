"""Orquestrador Human-in-the-Loop e Active Learning (`HitlActiveLearningComponent`) — BR4.1 a BR5.3."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

from .models import (
    AgroCountError,
    BoundingBoxDetection,
    GoldenDatasetSample,
    HitlCorrectionBatch,
    ModelVersion,
    utc_now_iso,
)
from .repository import AgroCountRepository


class HitlActiveLearningComponent:
    """Gerencia revisão HITL, curadoria automática do Golden Dataset (YOLO + JSON) e fine-tuning com gate de não-regressão."""

    def __init__(self, repo: AgroCountRepository) -> None:
        self.repo = repo

    def submit_hitl_review(
        self,
        inspection_id: str,
        auditor_id: str,
        actions: List[Dict[str, Any]],
        idempotent_retry: bool = False,
    ) -> Dict[str, Any]:
        """
        Processa o lote de revisão humana (BR4.1, BR4.2, BR4.3) e exporta automaticamente
        a amostra curada para o Golden Dataset (BR5.1).
        """
        if not auditor_id or not auditor_id.strip():
            raise AgroCountError(
                code="MISSING_AUDITOR_ID",
                message="A identificação do auditor (auditor_id) é obrigatória.",
                http_status=400,
            )
        auditor_id = auditor_id.strip()

        inspection = self.repo.get_inspection(inspection_id)
        if not inspection:
            raise AgroCountError(
                code="INSPECTION_NOT_FOUND",
                message=f"Inspeção '{inspection_id}' não encontrada.",
                http_status=404,
            )

        if inspection.status == "AUDITED":
            existing_batch = self.repo.get_hitl_batch(inspection_id)
            existing_sample = self.repo.get_golden_sample_by_inspection(inspection_id)
            if idempotent_retry and existing_batch and existing_sample and existing_batch.auditor_id == auditor_id:
                return self._format_hitl_response(inspection, existing_batch, existing_sample)
            raise AgroCountError(
                code="INSPECTION_ALREADY_AUDITED",
                message=f"A inspeção '{inspection_id}' já foi auditada e encontra-se imutável (AUDITED).",
                http_status=409,
                details={"inspection_id": inspection_id, "status": inspection.status},
            )

        if inspection.status != "READY_FOR_REVIEW":
            raise AgroCountError(
                code="INSPECTION_NOT_READY_FOR_REVIEW",
                message=f"A inspeção deve estar em READY_FOR_REVIEW para auditoria HITL (atual: {inspection.status}).",
                http_status=409,
                details={"status": inspection.status},
            )

        run = self.repo.get_detection_run(inspection_id)
        run_id = run.id if run else f"run-{inspection.id}"
        boxes = self.repo.list_boxes_for_inspection(inspection_id)
        box_map: Dict[str, BoundingBoxDetection] = {b.id: b for b in boxes}

        confirmed_count = 0
        fp_removed_count = 0
        fn_added_count = 0
        now = utc_now_iso()

        for act in actions:
            action_type = str(act.get("action") or "").strip().upper()
            if action_type == "CONFIRM":
                box_id = str(act.get("box_id") or "")
                if box_id not in box_map:
                    raise AgroCountError(
                        code="BOX_NOT_FOUND",
                        message=f"Caixa delimitadora '{box_id}' não encontrada na inspeção.",
                        http_status=422,
                        details={"box_id": box_id},
                    )
                target = box_map[box_id]
                target.review_status = "HUMAN_CONFIRMED"
                target.reviewed_by = auditor_id
                target.updated_at = now
                confirmed_count += 1

            elif action_type == "REMOVE_FALSE_POSITIVE":
                box_id = str(act.get("box_id") or "")
                if box_id not in box_map:
                    raise AgroCountError(
                        code="BOX_NOT_FOUND",
                        message=f"Caixa delimitadora '{box_id}' não encontrada na inspeção.",
                        http_status=422,
                        details={"box_id": box_id},
                    )
                target = box_map[box_id]
                if target.review_status != "HUMAN_REMOVED_FP":
                    target.review_status = "HUMAN_REMOVED_FP"
                    target.reviewed_by = auditor_id
                    target.updated_at = now
                    fp_removed_count += 1

            elif action_type == "ADD_FALSE_NEGATIVE":
                new_box_data = act.get("new_box")
                if not isinstance(new_box_data, dict):
                    raise AgroCountError(
                        code="MISSING_NEW_BOX_GEOMETRY",
                        message="A ação ADD_FALSE_NEGATIVE exige o objeto 'new_box' com geometria normalizada.",
                        http_status=422,
                    )
                new_id = str(new_box_data.get("id") or f"box-fn-{uuid.uuid4().hex[:10]}")
                new_box = BoundingBoxDetection(
                    id=new_id,
                    detection_run_id=run_id,
                    inspection_id=inspection_id,
                    frame_or_slice_index=int(new_box_data.get("frame_or_slice_index", 0)),
                    track_id=new_box_data.get("track_id"),
                    x_center=round(float(new_box_data.get("x_center", -1.0)), 6),
                    y_center=round(float(new_box_data.get("y_center", -1.0)), 6),
                    width=round(float(new_box_data.get("width", -1.0)), 6),
                    height=round(float(new_box_data.get("height", -1.0)), 6),
                    confidence=1.0,
                    confidence_tier="high_confidence",
                    review_status="HUMAN_ADDED",
                    reviewed_by=auditor_id,
                    updated_at=now,
                )
                new_box.validate_geometry()
                boxes.append(new_box)
                box_map[new_box.id] = new_box
                fn_added_count += 1

            else:
                raise AgroCountError(
                    code="INVALID_HITL_ACTION",
                    message=f"Ação HITL inválida: '{action_type}'. Use CONFIRM, REMOVE_FALSE_POSITIVE ou ADD_FALSE_NEGATIVE.",
                    http_status=422,
                    details={"action": action_type},
                )

        # Verifica se restou alguma detecção incerta pendente de triagem (BR4.1)
        pending_uncertain = [b.id for b in boxes if b.review_status == "AI_UNCERTAIN"]
        if pending_uncertain:
            raise AgroCountError(
                code="PENDING_UNCERTAIN_BOXES",
                message="Todas as detecções incertas (AI_UNCERTAIN) devem ser confirmadas ou removidas antes de finalizar.",
                http_status=422,
                details={"pending_box_ids": pending_uncertain},
            )

        # Reconciliação matemática exata da contagem final (BR4.2)
        net_delta = fn_added_count - fp_removed_count
        final_audited_count = inspection.raw_ai_count + net_delta
        valid_boxes = [
            b for b in boxes if b.review_status in ("AI_AUTO", "HUMAN_CONFIRMED", "HUMAN_ADDED")
        ]
        if len(valid_boxes) != final_audited_count or final_audited_count < 0:
            raise AgroCountError(
                code="COUNT_RECONCILIATION_MISMATCH",
                message="Divergência na reconciliação entre raw_ai_count, delta HITL e total de caixas válidas.",
                http_status=422,
                details={
                    "raw_ai_count": inspection.raw_ai_count,
                    "net_delta": net_delta,
                    "valid_boxes_count": len(valid_boxes),
                },
            )

        batch_id = f"hitl-{uuid.uuid4().hex[:12]}"
        sample_id = f"gds-{uuid.uuid4().hex[:12]}"

        # Exportação do Golden Dataset no padrão YOLO (.txt) + Proveniência (.json) (BR5.1)
        yolo_lines = [b.to_yolo_line() for b in valid_boxes]
        yolo_content = "\n".join(yolo_lines) + ("\n" if yolo_lines else "")

        labels_uri = f"gs://agrocount-storage/golden-dataset/{sample_id}/labels.txt"
        metadata_uri = f"gs://agrocount-storage/golden-dataset/{sample_id}/metadata.json"

        provenance_payload: Dict[str, Any] = {
            "schema_version": "1.0",
            "sample_id": sample_id,
            "inspection_id": inspection.id,
            "farm_id": inspection.farm_id,
            "paddock_id": inspection.paddock_id,
            "source_media_gcs_uri": inspection.source_uri,
            "yolo_labels_gcs_uri": labels_uri,
            "base_model_version": inspection.active_model_version,
            "auditor_id": auditor_id,
            "audited_at": now,
            "flight_telemetry": {
                "altitude_m": inspection.flight_altitude_m,
                "overlap_pct": inspection.overlap_pct,
            },
            "hitl_metrics": {
                "raw_ai_count": inspection.raw_ai_count,
                "confirmed_uncertain": confirmed_count,
                "false_positives_removed": fp_removed_count,
                "false_negatives_added": fn_added_count,
                "final_audited_count": final_audited_count,
            },
            "annotations": [
                {
                    "class_id": 0,
                    "class_name": "cattle",
                    "x_center": b.x_center,
                    "y_center": b.y_center,
                    "width": b.width,
                    "height": b.height,
                    "provenance": b.review_status,
                }
                for b in valid_boxes
            ],
        }

        self.repo.write_gcs_artifact(labels_uri, yolo_content)
        self.repo.write_gcs_artifact(metadata_uri, json.dumps(provenance_payload, indent=2, ensure_ascii=False))

        batch = HitlCorrectionBatch(
            id=batch_id,
            inspection_id=inspection.id,
            auditor_id=auditor_id,
            confirmed_count=confirmed_count,
            false_positive_removed_count=fp_removed_count,
            false_negative_added_count=fn_added_count,
            net_delta=net_delta,
            golden_sample_id=sample_id,
            submitted_at=now,
        )

        sample = GoldenDatasetSample(
            id=sample_id,
            inspection_id=inspection.id,
            hitl_batch_id=batch_id,
            media_gcs_uri=inspection.source_uri,
            yolo_labels_gcs_uri=labels_uri,
            metadata_gcs_uri=metadata_uri,
            total_boxes=len(valid_boxes),
            manual_corrections_count=confirmed_count + fp_removed_count + fn_added_count,
            base_model_version=inspection.active_model_version,
            used_in_model_version=None,
            created_at=now,
        )

        inspection.status = "AUDITED"
        inspection.final_audited_count = final_audited_count
        inspection.completed_at = now

        self.repo.replace_boxes_and_save_hitl(
            inspection=inspection,
            boxes=boxes,
            batch=batch,
            sample=sample,
        )

        return self._format_hitl_response(inspection, batch, sample)

    def _format_hitl_response(
        self,
        inspection: Any,
        batch: HitlCorrectionBatch,
        sample: GoldenDatasetSample,
    ) -> Dict[str, Any]:
        return {
            "inspection_id": inspection.id,
            "status": inspection.status,
            "raw_ai_count": inspection.raw_ai_count,
            "hitl_summary": {
                "confirmed_count": batch.confirmed_count,
                "false_positive_removed_count": batch.false_positive_removed_count,
                "false_negative_added_count": batch.false_negative_added_count,
                "net_delta": batch.net_delta,
            },
            "final_audited_count": inspection.final_audited_count,
            "golden_dataset_sample": {
                "sample_id": sample.id,
                "yolo_labels_gcs_uri": sample.yolo_labels_gcs_uri,
                "metadata_gcs_uri": sample.metadata_gcs_uri,
                "total_boxes": sample.total_boxes,
            },
        }

    def _next_version_tag(self, parent_tag: str) -> str:
        existing_tags = {m.version_tag for m in self.repo.list_model_versions()}
        if "-v" in parent_tag:
            prefix, ver = parent_tag.rsplit("-v", 1)
            parts = ver.split(".")
            try:
                major = int(parts[0])
                minor = int(parts[1]) + 1 if len(parts) > 1 else 1
                candidate = f"{prefix}-v{major}.{minor}"
                while candidate in existing_tags:
                    minor += 1
                    candidate = f"{prefix}-v{major}.{minor}"
                return candidate
            except ValueError:
                pass
        return f"yolo11m-agro-v1.{len(existing_tags)}"

    def trigger_fine_tuning(
        self,
        min_new_golden_samples: int = 10,
        target_epochs: int = 30,
        candidate_metrics: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Dispara job efêmero de fine-tuning sob demanda (BR5.2) e aplica o gate automático
        de promoção sem regressão (BR5.3: validation_counting_accuracy >= 0.95 e >= modelo ativo).
        """
        if min_new_golden_samples < 1:
            raise AgroCountError(
                code="INVALID_MIN_GOLDEN_SAMPLES",
                message="O parâmetro min_new_golden_samples deve ser >= 1.",
                http_status=400,
            )
        if not (5 <= target_epochs <= 100):
            raise AgroCountError(
                code="INVALID_TARGET_EPOCHS",
                message="O parâmetro target_epochs deve estar entre 5 e 100.",
                http_status=400,
            )

        running = self.repo.get_training_model()
        if running:
            raise AgroCountError(
                code="TRAINING_JOB_ALREADY_RUNNING",
                message=f"Já existe um job de treinamento em andamento para {running.version_tag}.",
                http_status=409,
                details={"candidate_version_tag": running.version_tag},
            )

        unused_samples = self.repo.list_unused_golden_samples()
        if len(unused_samples) < min_new_golden_samples:
            raise AgroCountError(
                code="INSUFFICIENT_GOLDEN_SAMPLES",
                message=(
                    f"Amostras inéditas insuficientes no Golden Dataset: "
                    f"{len(unused_samples)} disponíveis, mínimo exigido: {min_new_golden_samples}."
                ),
                http_status=422,
                details={
                    "available_new_samples": len(unused_samples),
                    "min_new_golden_samples": min_new_golden_samples,
                },
            )

        active_model = self.repo.get_active_model()
        all_samples = self.repo.list_all_golden_samples()
        candidate_tag = self._next_version_tag(active_model.version_tag)
        job_id = f"ft-job-{uuid.uuid4().hex[:10]}"
        weights_uri = f"gs://agrocount-storage/models/{candidate_tag}/best.pt"

        # Calcula ganho de acurácia determinístico a partir do volume do Golden Dataset ou usa métricas de teste
        if candidate_metrics is not None:
            val_map50 = round(float(candidate_metrics.get("validation_map50", 0.965)), 4)
            val_acc = round(float(candidate_metrics.get("validation_counting_accuracy", 0.972)), 4)
        else:
            gain = min(0.032, 0.0015 * len(unused_samples))
            val_map50 = round(min(0.995, active_model.validation_map50 + gain), 4)
            val_acc = round(min(0.995, active_model.validation_counting_accuracy + gain), 4)

        now = utc_now_iso()
        candidate = ModelVersion(
            version_tag=candidate_tag,
            parent_version_tag=active_model.version_tag,
            weights_gcs_uri=weights_uri,
            golden_samples_used=len(all_samples),
            validation_map50=val_map50,
            validation_counting_accuracy=val_acc,
            status="TRAINING",
            promoted_at=None,
            created_at=now,
        )
        self.repo.save_model_version(candidate)

        # Persiste pesos simulados e manifesto de avaliação no storage
        self.repo.write_gcs_artifact(
            weights_uri,
            json.dumps(
                {
                    "version_tag": candidate_tag,
                    "parent_version_tag": active_model.version_tag,
                    "target_epochs": target_epochs,
                    "golden_samples_used": len(all_samples),
                    "validation_map50": val_map50,
                    "validation_counting_accuracy": val_acc,
                },
                indent=2,
            ),
        )

        # Gate de Promoção Sem Regressão (BR5.3)
        passes_floor = val_acc >= 0.95
        passes_non_regression = val_acc >= active_model.validation_counting_accuracy

        if passes_floor and passes_non_regression:
            self.repo.promote_candidate_model(candidate, previous_active_tag=active_model.version_tag)
            self.repo.mark_golden_samples_used([s.id for s in unused_samples], candidate.version_tag)
            promotion_gate_result = "PROMOTED"
        else:
            candidate.status = "REJECTED_REGRESSION"
            self.repo.save_model_version(candidate)
            promotion_gate_result = "REJECTED_REGRESSION"

        return {
            "job_id": job_id,
            "candidate_version_tag": candidate.version_tag,
            "parent_version_tag": active_model.version_tag,
            "status": candidate.status,
            "promotion_gate_result": promotion_gate_result,
            "golden_samples_queued": len(unused_samples),
            "total_golden_samples_used": len(all_samples),
            "validation_map50": candidate.validation_map50,
            "validation_counting_accuracy": candidate.validation_counting_accuracy,
            "promotion_gate": "validation_counting_accuracy >= 0.95 and >= parent",
        }
