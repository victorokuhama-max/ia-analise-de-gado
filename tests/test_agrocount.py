"""Suíte de testes unitários, de integração e de contrato HTTP — u1-agrocount-platform."""

from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from agrocount.api import AgroCountApp, create_http_server
from agrocount.hitl import HitlActiveLearningComponent
from agrocount.models import (
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
    ReviewSessionState,
)
from agrocount.repository import AgroCountRepository
from agrocount.service import InspectionManagementService
from agrocount.vision import (
    CattleVisionEngineComponent,
    classify_confidence_tier,
    compute_iou,
    non_max_suppression,
)


class TestDomainModels(unittest.TestCase):
    """Camada 1: Data model / database behavior — testes de entidades e invariantes (BR1.1–BR6.1)."""

    def test_farm_and_paddock_validation_happy_and_errors(self) -> None:
        farm = Farm(id="farm-1", name="  Fazenda Santa Fé  ", code=" fsf-01 ")
        farm.validate()
        self.assertEqual(farm.name, "Fazenda Santa Fé")
        self.assertEqual(farm.code, "FSF-01")
        self.assertEqual(farm.to_dict()["code"], "FSF-01")

        with self.assertRaises(AgroCountError) as ctx:
            Farm(id="f2", name="AB", code="C1").validate()
        self.assertEqual(ctx.exception.code, "INVALID_FARM_NAME")

        with self.assertRaises(AgroCountError) as ctx2:
            Farm(id="f3", name="Fazenda Boa", code="").validate()
        self.assertEqual(ctx2.exception.code, "INVALID_FARM_CODE")

        paddock = Paddock(id="p1", farm_id="farm-1", name="Piquete Norte", code="pn-01", area_hectares=45.5)
        paddock.validate()
        self.assertEqual(paddock.code, "PN-01")
        self.assertEqual(paddock.to_dict()["area_hectares"], 45.5)

        with self.assertRaises(AgroCountError):
            Paddock(id="p2", farm_id="", name="Piquete", code="P2").validate()
        with self.assertRaises(AgroCountError):
            Paddock(id="p3", farm_id="farm-1", name="A", code="P3").validate()
        with self.assertRaises(AgroCountError):
            Paddock(id="p4", farm_id="farm-1", name="Piquete", code="").validate()
        with self.assertRaises(AgroCountError):
            Paddock(id="p5", farm_id="farm-1", name="Piquete", code="P5", area_hectares=-5.0).validate()

    def test_inspection_and_detection_run_validation(self) -> None:
        insp = Inspection(
            id="insp-1",
            farm_id="farm-1",
            paddock_id="p1",
            idempotency_key="idem-001",
            media_type="IMAGE_4K",
            source_uri="gs://agrocount-storage/raw/voo1.jpg",
            file_size_bytes=102400,
            flight_altitude_m=60,
            overlap_pct=75,
        )
        insp.validate_metadata()
        self.assertEqual(insp.to_dict()["flight_altitude_m"], 60)

        with self.assertRaises(AgroCountError):
            Inspection(
                id="i2", farm_id="f", paddock_id="p", idempotency_key=" ", media_type="IMAGE_4K",
                source_uri="gs://a/b.jpg", file_size_bytes=100
            ).validate_metadata()

        with self.assertRaises(AgroCountError):
            Inspection(
                id="i3", farm_id="f", paddock_id="p", idempotency_key="k", media_type="IMAGE_4K",
                source_uri="gs://a/b.jpg", file_size_bytes=100, status="UNKNOWN"
            ).validate_metadata()

        with self.assertRaises(AgroCountError):
            Inspection(
                id="i4", farm_id="f", paddock_id="p", idempotency_key="k", media_type="IMAGE_4K",
                source_uri="gs://a/b.jpg", file_size_bytes=100, flight_altitude_m=5
            ).validate_metadata()

        with self.assertRaises(AgroCountError):
            Inspection(
                id="i5", farm_id="f", paddock_id="p", idempotency_key="k", media_type="IMAGE_4K",
                source_uri="gs://a/b.jpg", file_size_bytes=100, overlap_pct=99
            ).validate_metadata()

        run = DetectionRun(
            id="r1", inspection_id="insp-1", model_version="v1", inference_mode="SAHI_SLICED",
            total_slices_or_frames=12, high_confidence_count=10, uncertain_count=2, execution_ms=1200
        )
        run.validate()
        self.assertEqual(run.to_dict()["inference_mode"], "SAHI_SLICED")

        with self.assertRaises(AgroCountError):
            DetectionRun("r2", "i", "v1", "INVALID", 1, 0, 0, 10).validate()
        with self.assertRaises(AgroCountError):
            DetectionRun("r3", "i", "v1", "SAHI_SLICED", 0, 0, 0, 10).validate()

    def test_bounding_box_and_yolo_export_format(self) -> None:
        box = BoundingBoxDetection(
            id="b1", detection_run_id="r1", inspection_id="i1", frame_or_slice_index=0,
            x_center=0.5, y_center=0.25, width=0.05, height=0.08, confidence=0.88,
            confidence_tier="high_confidence", review_status="AI_AUTO"
        )
        box.validate_geometry()
        self.assertEqual(box.to_yolo_line(), "0 0.500000 0.250000 0.050000 0.080000")

        with self.assertRaises(AgroCountError):
            BoundingBoxDetection(
                "b2", "r1", "i1", 0, 1.5, 0.5, 0.1, 0.1, 0.9, "high_confidence", "AI_AUTO"
            ).validate_geometry()

        with self.assertRaises(AgroCountError):
            BoundingBoxDetection(
                "b3", "r1", "i1", 0, 0.5, 0.5, 0.0, 0.1, 0.9, "high_confidence", "AI_AUTO"
            ).validate_geometry()

        with self.assertRaises(AgroCountError):
            BoundingBoxDetection(
                "b4", "r1", "i1", 0, 0.5, 0.5, 0.1, 0.1, 0.9, "bad_tier", "AI_AUTO"
            ).validate_geometry()

        with self.assertRaises(AgroCountError):
            BoundingBoxDetection(
                "b5", "r1", "i1", 0, 0.5, 0.5, 0.1, 0.1, 0.9, "high_confidence", "BAD_STATUS"
            ).validate_geometry()

    def test_hitl_batch_model_version_and_audit_report_invariants(self) -> None:
        batch = HitlCorrectionBatch(
            id="hb1", inspection_id="i1", auditor_id="aud-1",
            confirmed_count=2, false_positive_removed_count=1, false_negative_added_count=3,
            net_delta=2, golden_sample_id="gds-1"
        )
        batch.validate()
        self.assertEqual(batch.to_dict()["net_delta"], 2)

        with self.assertRaises(AgroCountError):
            HitlCorrectionBatch("hb2", "i1", "aud-1", 1, 2, 1, 5, "gds-1").validate()

        mv = ModelVersion(
            version_tag="v1.1", parent_version_tag="v1.0", weights_gcs_uri="gs://a/b.pt",
            golden_samples_used=12, validation_map50=0.96, validation_counting_accuracy=0.97,
            status="ACTIVE"
        )
        mv.validate()
        with self.assertRaises(AgroCountError):
            ModelVersion("v", None, "gs://a", 0, 0.9, 0.9, "INVALID").validate()
        with self.assertRaises(AgroCountError):
            ModelVersion("v", None, "gs://a", 0, 1.5, 0.9, "ACTIVE").validate()

        rep = AuditReport(
            id="rep-1", inspection_id="i1", format="PDF",
            report_gcs_uri="gs://a/r.pdf", sha256_checksum="sha256:" + "a" * 64
        )
        rep.validate()
        with self.assertRaises(AgroCountError):
            AuditReport("rep-2", "i1", "DOCX", "gs://a", "sha256:" + "a" * 64).validate()
        with self.assertRaises(AgroCountError):
            AuditReport("rep-3", "i1", "PDF", "gs://a", "invalid-checksum").validate()


class TestRepositoryLayer(unittest.TestCase):
    """Camada 2: Repository / data access — persistência SQLite, unicidade e escrita atômica."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.repo = AgroCountRepository(db_path=":memory:", storage_dir=self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_farm_uniqueness_and_atomic_gcs_artifacts(self) -> None:
        f1 = Farm(id="f1", name="Fazenda Um", code="FAZ-01")
        p1 = Paddock(id="p1", farm_id="f1", name="Pasto 1", code="P-01", area_hectares=30.0)
        saved = self.repo.save_farm(f1, [p1])
        self.assertEqual(saved["code"], "FAZ-01")
        self.assertEqual(len(self.repo.list_farms()), 1)

        # Código duplicado deve lançar 409 DUPLICATE_FARM_OR_PADDOCK_CODE
        with self.assertRaises(AgroCountError) as ctx:
            self.repo.save_farm(Farm(id="f2", name="Fazenda Dois", code="FAZ-01"), [])
        self.assertEqual(ctx.exception.http_status, 409)

        # Escrita e leitura atômica de artefato GCS
        uri = "gs://agrocount-storage/golden-dataset/test-sample/labels.txt"
        path = self.repo.write_gcs_artifact(uri, "0 0.5 0.5 0.1 0.1\n")
        self.assertTrue(path.exists())
        self.assertEqual(self.repo.read_gcs_artifact(uri).decode("utf-8"), "0 0.5 0.5 0.1 0.1\n")

        with self.assertRaises(AgroCountError) as ctx_404:
            self.repo.read_gcs_artifact("gs://agrocount-storage/non-existent/file.txt")
        self.assertEqual(ctx_404.exception.http_status, 404)


class TestVisionAndHitlPipeline(unittest.TestCase):
    """Camada 3: Business logic — Visão Computacional (SAHI, ByteTrack, Pré-GPU) e HITL / Active Learning."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.repo = AgroCountRepository(db_path=":memory:", storage_dir=self.tmp_dir.name)
        self.vision = CattleVisionEngineComponent()
        self.hitl = HitlActiveLearningComponent(self.repo)
        self.service = InspectionManagementService(repo=self.repo, vision=self.vision, hitl=self.hitl)
        farm_res = self.service.create_farm(
            name="Fazenda Modelo Nelore",
            code="FMN-01",
            paddocks_data=[{"name": "Piquete Maternidade", "code": "PM-01", "area_hectares": 50.0}],
        )
        self.farm_id = farm_res["id"]
        self.paddock_id = farm_res["paddocks"][0]["id"]

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_pre_gpu_validation_gates_br2_2(self) -> None:
        # Formato inválido
        with self.assertRaises(AgroCountError) as c1:
            self.vision.validate_media_pre_gpu("AUDIO", "gs://b/a.mp3", 1024)
        self.assertEqual(c1.exception.code, "INVALID_MEDIA_FORMAT")

        # URI sem gs://
        with self.assertRaises(AgroCountError) as c2:
            self.vision.validate_media_pre_gpu("IMAGE_4K", "http://example.com/a.jpg", 1024)
        self.assertEqual(c2.exception.code, "INVALID_SOURCE_URI")

        # Extensão incompatível
        with self.assertRaises(AgroCountError) as c3:
            self.vision.validate_media_pre_gpu("IMAGE_4K", "gs://b/video.mp4", 1024)
        self.assertEqual(c3.exception.code, "INVALID_MEDIA_FORMAT")

        # Arquivo acima de 2 GiB
        with self.assertRaises(AgroCountError) as c4:
            self.vision.validate_media_pre_gpu("IMAGE_4K", "gs://b/foto.jpg", 3 * 1024**3)
        self.assertEqual(c4.exception.code, "FILE_TOO_LARGE")

        # Cabeçalho corrompido / tamanho zero
        with self.assertRaises(AgroCountError) as c5:
            self.vision.validate_media_pre_gpu("IMAGE_4K", "gs://b/foto.jpg", 0)
        self.assertEqual(c5.exception.code, "CORRUPTED_MEDIA_HEADER")

        with self.assertRaises(AgroCountError) as c5b:
            self.vision.validate_media_pre_gpu(
                "IMAGE_4K", "gs://b/corrupted_img.jpg", 5000
            )
        self.assertEqual(c5b.exception.code, "CORRUPTED_MEDIA_HEADER")

        # Resolução abaixo de HD (1280x720)
        with self.assertRaises(AgroCountError) as c6:
            self.vision.validate_media_pre_gpu(
                "IMAGE_4K", "gs://b/foto.jpg", 5000, media_metadata={"width_px": 640, "height_px": 480}
            )
        self.assertEqual(c6.exception.code, "RESOLUTION_TOO_LOW")

        # Vídeo acima de 600s
        with self.assertRaises(AgroCountError) as c7:
            self.vision.validate_media_pre_gpu(
                "VIDEO_DRONE", "gs://b/voo.mp4", 50000, media_metadata={"duration_s": 720}
            )
        self.assertEqual(c7.exception.code, "DURATION_EXCEEDED")

    def test_sahi_nms_deduplication_and_confidence_tiers_br3_1_br3_3(self) -> None:
        # Duas caixas quase idênticas na fronteira de duas fatias SAHI (IoU > 0.8) + 1 incerta + 1 ruído (<0.25)
        raw_dets = [
            {"id": "b-high-1", "slice_index": 0, "x_center": 0.30, "y_center": 0.30, "width": 0.05, "height": 0.05, "confidence": 0.92},
            {"id": "b-high-1-dup", "slice_index": 1, "x_center": 0.302, "y_center": 0.301, "width": 0.05, "height": 0.05, "confidence": 0.85},
            {"id": "b-unc-1", "slice_index": 2, "x_center": 0.70, "y_center": 0.70, "width": 0.05, "height": 0.05, "confidence": 0.55},
            {"id": "b-noise", "slice_index": 3, "x_center": 0.10, "y_center": 0.10, "width": 0.04, "height": 0.04, "confidence": 0.12},
        ]
        created = self.service.create_inspection(
            farm_id=self.farm_id,
            paddock_id=self.paddock_id,
            idempotency_key="idem-sahi-test",
            media_type="IMAGE_4K",
            source_uri="gs://agrocount-storage/flights/ortomosaico_4k.tiff",
            file_size_bytes=52428800,
            flight_altitude_m=70,
            overlap_pct=80,
            custom_detections=raw_dets,
        )
        # Duplicata fundida pelo NMS e ruído <0.25 descartado -> restam exatamente 2 animais (1 high, 1 uncertain)
        self.assertEqual(created["raw_ai_count"], 2)
        self.assertEqual(created["summary"]["high_confidence_count"], 1)
        self.assertEqual(created["summary"]["uncertain_count"], 1)
        self.assertEqual(classify_confidence_tier(0.10)[0], "discarded")
        self.assertEqual(compute_iou(raw_dets[0], raw_dets[2]), 0.0)

    def test_bytetrack_video_multi_frame_unique_tracking_br3_2(self) -> None:
        # Mesmo animal aparece em 3 frames (incluindo oclusão de 15 frames < max_age=30)
        video_dets = [
            {"frame_index": 1, "x_center": 0.400, "y_center": 0.400, "width": 0.05, "height": 0.05, "confidence": 0.82},
            {"frame_index": 5, "x_center": 0.405, "y_center": 0.402, "width": 0.05, "height": 0.05, "confidence": 0.91},
            {"frame_index": 20, "x_center": 0.410, "y_center": 0.405, "width": 0.05, "height": 0.05, "confidence": 0.88},
            # Segundo animal (baixa confiança / sombra)
            {"frame_index": 2, "x_center": 0.800, "y_center": 0.800, "width": 0.05, "height": 0.05, "confidence": 0.48},
        ]
        created = self.service.create_inspection(
            farm_id=self.farm_id,
            paddock_id=self.paddock_id,
            idempotency_key="idem-video-test",
            media_type="VIDEO_DRONE",
            source_uri="gs://agrocount-storage/flights/voo_drone.mp4",
            file_size_bytes=104857600,
            custom_detections=video_dets,
        )
        self.assertEqual(created["summary"]["inference_mode"], "BYTETRACK_VIDEO")
        self.assertEqual(created["raw_ai_count"], 2)

    def test_hitl_review_golden_dataset_export_and_fine_tuning_gates_br4_br5(self) -> None:
        # Cria inspeção com 2 detecções de alta confiança + 2 incertas (raw_ai_count = 4)
        dets = [
            {"id": "box-h1", "slice_index": 0, "x_center": 0.20, "y_center": 0.20, "width": 0.05, "height": 0.05, "confidence": 0.90},
            {"id": "box-h2", "slice_index": 0, "x_center": 0.40, "y_center": 0.20, "width": 0.05, "height": 0.05, "confidence": 0.85},
            {"id": "box-u1", "slice_index": 1, "x_center": 0.60, "y_center": 0.60, "width": 0.05, "height": 0.05, "confidence": 0.52},
            {"id": "box-u2", "slice_index": 1, "x_center": 0.80, "y_center": 0.60, "width": 0.05, "height": 0.05, "confidence": 0.38},
        ]
        insp = self.service.create_inspection(
            farm_id=self.farm_id,
            paddock_id=self.paddock_id,
            idempotency_key="idem-hitl-1",
            media_type="IMAGE_4K",
            source_uri="gs://agrocount-storage/flights/hitl_1.jpg",
            file_size_bytes=2048000,
            custom_detections=dets,
        )
        insp_id = insp["id"]

        # Tentativa de finalizar deixando box-u2 sem revisão deve falhar com PENDING_UNCERTAIN_BOXES (BR4.1)
        with self.assertRaises(AgroCountError) as ctx_pending:
            self.service.submit_hitl_review(
                inspection_id=insp_id,
                auditor_id="auditor-victor",
                actions=[{"action": "CONFIRM", "box_id": "box-u1"}],
            )
        self.assertEqual(ctx_pending.exception.code, "PENDING_UNCERTAIN_BOXES")

        # Submissão completa: confirma box-u1, remove box-u2 (falso positivo: cupinzeiro) e adiciona 2 falsos negativos
        # Contagem esperada: raw(4) - FP(1) + FN(2) = 5 animais válidos!
        res = self.service.submit_hitl_review(
            inspection_id=insp_id,
            auditor_id="auditor-victor",
            actions=[
                {"action": "CONFIRM", "box_id": "box-u1"},
                {"action": "REMOVE_FALSE_POSITIVE", "box_id": "box-u2"},
                {
                    "action": "ADD_FALSE_NEGATIVE",
                    "new_box": {"x_center": 0.15, "y_center": 0.85, "width": 0.045, "height": 0.055},
                },
                {
                    "action": "ADD_FALSE_NEGATIVE",
                    "new_box": {"x_center": 0.35, "y_center": 0.85, "width": 0.045, "height": 0.055},
                },
            ],
        )
        self.assertEqual(res["status"], "AUDITED")
        self.assertEqual(res["raw_ai_count"], 4)
        self.assertEqual(res["hitl_summary"]["confirmed_count"], 1)
        self.assertEqual(res["hitl_summary"]["false_positive_removed_count"], 1)
        self.assertEqual(res["hitl_summary"]["false_negative_added_count"], 2)
        self.assertEqual(res["hitl_summary"]["net_delta"], 1)
        self.assertEqual(res["final_audited_count"], 5)

        # Verifica artefatos do Golden Dataset (YOLO .txt com 5 linhas e .json de proveniência) (BR5.1)
        labels_uri = res["golden_dataset_sample"]["yolo_labels_gcs_uri"]
        meta_uri = res["golden_dataset_sample"]["metadata_gcs_uri"]
        yolo_text = self.repo.read_gcs_artifact(labels_uri).decode("utf-8").strip().splitlines()
        self.assertEqual(len(yolo_text), 5)
        for line in yolo_text:
            self.assertTrue(line.startswith("0 "))

        meta_json = json.loads(self.repo.read_gcs_artifact(meta_uri).decode("utf-8"))
        self.assertEqual(meta_json["hitl_metrics"]["final_audited_count"], 5)
        self.assertEqual(len(meta_json["annotations"]), 5)

        # Imutabilidade pós-auditoria (BR4.3): nova mutação deve retornar 409 INSPECTION_ALREADY_AUDITED
        with self.assertRaises(AgroCountError) as ctx_immutable:
            self.service.submit_hitl_review(
                inspection_id=insp_id,
                auditor_id="auditor-victor",
                actions=[],
            )
        self.assertEqual(ctx_immutable.exception.http_status, 409)

        # Retry idempotente explícito deve retornar 200 com o mesmo resultado
        retry_res = self.service.submit_hitl_review(
            inspection_id=insp_id,
            auditor_id="auditor-victor",
            actions=[],
            idempotent_retry=True,
        )
        self.assertEqual(retry_res["final_audited_count"], 5)

        # Fine-tuning com amostra insuficiente (1 < 5) deve falhar com INSUFFICIENT_GOLDEN_SAMPLES (BR5.2)
        with self.assertRaises(AgroCountError) as ctx_insuf:
            self.service.trigger_fine_tuning(min_new_golden_samples=5, target_epochs=20)
        self.assertEqual(ctx_insuf.exception.code, "INSUFFICIENT_GOLDEN_SAMPLES")

        # Fine-tuning com candidato que sofre regressão (0.91 < 0.95) deve ser REJECTED_REGRESSION (BR5.3)
        reg_res = self.service.trigger_fine_tuning(
            min_new_golden_samples=1,
            target_epochs=20,
            candidate_metrics={"validation_map50": 0.90, "validation_counting_accuracy": 0.91},
        )
        self.assertEqual(reg_res["status"], "REJECTED_REGRESSION")
        self.assertEqual(self.service.get_active_model_status()["active_model"]["version_tag"], "yolo11m-agro-v1.0")

        # Fine-tuning com candidato superior (0.978 >= 0.95 e >= 0.960) deve ser PROMOTED para ACTIVE (BR5.3)
        prom_res = self.service.trigger_fine_tuning(
            min_new_golden_samples=1,
            target_epochs=30,
            candidate_metrics={"validation_map50": 0.971, "validation_counting_accuracy": 0.978},
        )
        self.assertEqual(prom_res["status"], "ACTIVE")
        self.assertEqual(prom_res["promotion_gate_result"], "PROMOTED")
        active_now = self.service.get_active_model_status()["active_model"]
        self.assertEqual(active_now["version_tag"], prom_res["candidate_version_tag"])
        self.assertEqual(active_now["validation_counting_accuracy"], 0.978)


class TestInspectionAndReportService(unittest.TestCase):
    """Camada 3 (continuação): Idempotência de inspeção e exportação de laudos PDF/CSV (BR2.1, BR6.1)."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.repo = AgroCountRepository(db_path=":memory:", storage_dir=self.tmp_dir.name)
        self.service = InspectionManagementService(repo=self.repo)
        farm = self.service.create_farm(
            name="Fazenda Alvorada",
            code="FALV-01",
            paddocks_data=[{"name": "Pasto Sul", "code": "PS-01", "area_hectares": 80.0}],
        )
        self.farm_id = farm["id"]
        self.paddock_id = farm["paddocks"][0]["id"]

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_idempotency_and_pdf_csv_report_generation_br6_1(self) -> None:
        insp1 = self.service.create_inspection(
            farm_id=self.farm_id,
            paddock_id=self.paddock_id,
            idempotency_key="idem-unique-100",
            media_type="IMAGE_4K",
            source_uri="gs://agrocount-storage/flights/voo_100.jpg",
            file_size_bytes=4096000,
        )
        # Submissão repetida com mesmo idempotency_key retorna a mesma inspeção sem reexecutar inferência
        insp2 = self.service.create_inspection(
            farm_id=self.farm_id,
            paddock_id=self.paddock_id,
            idempotency_key="idem-unique-100",
            media_type="IMAGE_4K",
            source_uri="gs://agrocount-storage/flights/voo_100.jpg",
            file_size_bytes=4096000,
        )
        self.assertEqual(insp1["id"], insp2["id"])

        # Não deve permitir exportar laudo antes da auditoria HITL (BR6.1)
        with self.assertRaises(AgroCountError) as ctx_unau:
            self.service.export_audit_report(insp1["id"], fmt="PDF")
        self.assertEqual(ctx_unau.exception.code, "INSPECTION_NOT_AUDITED")

        # Confirma todas as detecções incertas para concluir a auditoria
        uncertain_actions = [
            {"action": "CONFIRM", "box_id": b["id"]}
            for b in insp1["detections"]
            if b["review_status"] == "AI_UNCERTAIN"
        ]
        self.service.submit_hitl_review(insp1["id"], auditor_id="auditor-2", actions=uncertain_actions)

        # Exporta PDF e CSV verificando cabeçalho %PDF-1.4 e checksum SHA-256
        pdf_rep = self.service.export_audit_report(insp1["id"], fmt="PDF")
        self.assertEqual(pdf_rep["format"], "PDF")
        self.assertTrue(pdf_rep["sha256_checksum"].startswith("sha256:"))
        pdf_bytes = self.repo.read_gcs_artifact(pdf_rep["report_gcs_uri"])
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))

        csv_rep = self.service.export_audit_report(insp1["id"], fmt="CSV")
        self.assertEqual(csv_rep["format"], "CSV")
        csv_text = self.repo.read_gcs_artifact(csv_rep["report_gcs_uri"]).decode("utf-8")
        self.assertIn("final_audited_count", csv_text)
        self.assertEqual(len(self.repo.list_audit_reports(insp1["id"])), 2)


class TestRestApiEndpoints(unittest.TestCase):
    """Camada 4: API / endpoint — testes de contrato OpenAPI /api/v1/*, HTTP Server real e segurança."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.repo = AgroCountRepository(db_path=":memory:", storage_dir=self.tmp_dir.name)
        self.service = InspectionManagementService(repo=self.repo)
        self.app = AgroCountApp(service=self.service, require_auth=False)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_full_rest_api_lifecycle_and_error_envelopes(self) -> None:
        # 1. Health check
        st, hdrs, body = self.app.handle_request("GET", "/api/v1/health", {"X-Correlation-Id": "test-corr-1"})
        self.assertEqual(st, 200)
        self.assertEqual(hdrs["X-Correlation-Id"], "test-corr-1")
        self.assertEqual(json.loads(body)["status"], "ok")

        # 2. POST /api/v1/farms
        st, _, body = self.app.handle_request(
            "POST",
            "/api/v1/farms",
            body=json.dumps(
                {
                    "name": "Fazenda Rio Verde",
                    "code": "FRV-01",
                    "paddocks": [{"name": "Pasto Central", "code": "PC-01", "area_hectares": 64.0}],
                }
            ),
        )
        self.assertEqual(st, 201)
        farm_data = json.loads(body)
        farm_id = farm_data["id"]
        paddock_id = farm_data["paddocks"][0]["id"]

        # GET /api/v1/farms
        st, _, body = self.app.handle_request("GET", "/api/v1/farms")
        self.assertEqual(st, 200)
        self.assertEqual(len(json.loads(body)["items"]), 1)

        # 3. POST /api/v1/inspections
        st, _, body = self.app.handle_request(
            "POST",
            "/api/v1/inspections",
            body=json.dumps(
                {
                    "farm_id": farm_id,
                    "paddock_id": paddock_id,
                    "idempotency_key": "api-idem-1",
                    "media_type": "IMAGE_4K",
                    "source_uri": "gs://agrocount-storage/flights/api_1.jpg",
                    "file_size_bytes": 1024000,
                    "flight_altitude_m": 55,
                    "overlap_pct": 75,
                }
            ),
        )
        self.assertEqual(st, 202)
        insp_data = json.loads(body)
        insp_id = insp_data["id"]

        # Chamada idempotente retorna 200
        st_idem, _, _ = self.app.handle_request(
            "POST",
            "/api/v1/inspections",
            body=json.dumps(
                {
                    "farm_id": farm_id,
                    "paddock_id": paddock_id,
                    "idempotency_key": "api-idem-1",
                    "media_type": "IMAGE_4K",
                    "source_uri": "gs://agrocount-storage/flights/api_1.jpg",
                    "file_size_bytes": 1024000,
                }
            ),
        )
        self.assertEqual(st_idem, 200)

        # GET /api/v1/inspections & GET /api/v1/inspections/{id}
        st_list, _, body_list = self.app.handle_request("GET", f"/api/v1/inspections?farm_id={farm_id}")
        self.assertEqual(st_list, 200)
        self.assertEqual(len(json.loads(body_list)["items"]), 1)

        st_det, _, body_det = self.app.handle_request("GET", f"/api/v1/inspections/{insp_id}")
        self.assertEqual(st_det, 200)
        det_json = json.loads(body_det)

        # 4. POST /api/v1/inspections/{id}/hitl-review
        actions = [
            {"action": "CONFIRM", "box_id": b["id"]}
            for b in det_json["detections"]
            if b["review_status"] == "AI_UNCERTAIN"
        ]
        st_hitl, _, body_hitl = self.app.handle_request(
            "POST",
            f"/api/v1/inspections/{insp_id}/hitl-review",
            body=json.dumps({"auditor_id": "auditor-api", "actions": actions}),
        )
        self.assertEqual(st_hitl, 200)
        self.assertEqual(json.loads(body_hitl)["status"], "AUDITED")

        # 5. GET /api/v1/inspections/{id}/report?format=PDF
        st_rep, _, body_rep = self.app.handle_request("GET", f"/api/v1/inspections/{insp_id}/report?format=PDF")
        self.assertEqual(st_rep, 200)
        self.assertEqual(json.loads(body_rep)["format"], "PDF")

        # 6. GET /api/v1/models/active & POST /api/v1/models/fine-tune
        st_mod, _, body_mod = self.app.handle_request("GET", "/api/v1/models/active")
        self.assertEqual(st_mod, 200)
        self.assertEqual(json.loads(body_mod)["golden_dataset_status"]["total_curated_samples"], 1)

        st_ft, _, body_ft = self.app.handle_request(
            "POST",
            "/api/v1/models/fine-tune",
            body=json.dumps({"min_new_golden_samples": 1, "target_epochs": 15}),
        )
        self.assertEqual(st_ft, 202)
        self.assertEqual(json.loads(body_ft)["promotion_gate_result"], "PROMOTED")

        # 7. Erros 400 (JSON malformado), 404 (rota inexistente) e 401 (autenticação)
        st_bad_json, _, _ = self.app.handle_request("POST", "/api/v1/farms", body="{invalid-json")
        self.assertEqual(st_bad_json, 400)

        st_404, _, _ = self.app.handle_request("GET", "/api/v1/unknown-route")
        self.assertEqual(st_404, 404)

        auth_app = AgroCountApp(service=self.service, require_auth=True)
        st_401, _, _ = auth_app.handle_request("GET", "/api/v1/farms")
        self.assertEqual(st_401, 401)
        st_401_bad, _, _ = auth_app.handle_request(
            "GET", "/api/v1/farms", headers={"Authorization": "Bearer wrong-token"}
        )
        self.assertEqual(st_401_bad, 401)
        st_200_ok, _, _ = auth_app.handle_request(
            "GET", "/api/v1/farms", headers={"Authorization": "Bearer agrocount-dev-token"}
        )
        self.assertEqual(st_200_ok, 200)

    def test_live_http_server_socket_requests(self) -> None:
        server = create_http_server(host="127.0.0.1", port=0, app=self.app)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/health", timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data["service"], "u1-agrocount-platform")
        finally:
            server.shutdown()
            server.server_close()


class TestWebReviewStudioFrontend(unittest.TestCase):
    """Camada 5: Frontend behavior — Estúdio Web HITL, atributos data-testid, WCAG 2.1 AA e atalhos de teclado."""

    def setUp(self) -> None:
        self.app = AgroCountApp()

    def test_web_studio_html_and_js_delivery_with_required_testids(self) -> None:
        st_html, hdrs_html, body_html = self.app.handle_request("GET", "/")
        self.assertEqual(st_html, 200)
        self.assertIn("text/html", hdrs_html["Content-Type"])
        html_text = body_html.decode("utf-8")

        required_testids = [
            "kpi-raw-count",
            "kpi-uncertain-count",
            "kpi-audited-count",
            "upload-dropzone",
            "hitl-canvas-container",
            "uncertain-queue-list",
            "btn-approve-finalize",
            "btn-trigger-finetune",
            "btn-export-pdf",
            "btn-export-csv",
        ]
        for tid in required_testids:
            self.assertIn(f'data-testid="{tid}"', html_text)

        # Verifica presença da codificação tripla WCAG 2.1 AA ([✓], [?], [+H])
        self.assertIn("[✓]", html_text)
        self.assertIn("[?]", html_text)
        self.assertIn("[+H]", html_text)

        st_js, hdrs_js, body_js = self.app.handle_request("GET", "/app.js")
        self.assertEqual(st_js, 200)
        self.assertIn("application/javascript", hdrs_js["Content-Type"])
        self.assertIn("AgroCountStudio", body_js.decode("utf-8"))

    def test_review_session_state_keyboard_shortcuts_and_zoom(self) -> None:
        session = ReviewSessionState(inspection_id="insp-100")
        session.set_zoom(2.5)
        self.assertEqual(session.zoom_level, 2.5)
        with self.assertRaises(AgroCountError):
            session.set_zoom(12.0)

        session.set_filter("MANUAL_EDITS")
        self.assertEqual(session.active_filter, "MANUAL_EDITS")
        with self.assertRaises(AgroCountError):
            session.set_filter("INVALID_FILTER")

        uncertain_ids = ["u-1", "u-2", "u-3"]
        nav1 = session.apply_keyboard_shortcut("ArrowRight", uncertain_ids)
        self.assertEqual(nav1["selected_box_id"], "u-1")
        nav2 = session.apply_keyboard_shortcut("ArrowRight", uncertain_ids)
        self.assertEqual(nav2["selected_box_id"], "u-2")
        nav_prev = session.apply_keyboard_shortcut("ArrowLeft", uncertain_ids)
        self.assertEqual(nav_prev["selected_box_id"], "u-1")

        conf = session.apply_keyboard_shortcut("Space", uncertain_ids)
        self.assertEqual(conf["action"], "CONFIRM")
        rem = session.apply_keyboard_shortcut("Delete", uncertain_ids)
        self.assertEqual(rem["action"], "REMOVE_FALSE_POSITIVE")
        draw = session.apply_keyboard_shortcut("KeyN", uncertain_ids)
        self.assertEqual(draw["action"], "DRAW_MODE_NEW_BOX")
        self.assertEqual(session.dirty_changes_count, 2)
        self.assertEqual(session.to_dict()["inspection_id"], "insp-100")

        session.keyboard_shortcuts_enabled = False
        ignored = session.apply_keyboard_shortcut("Space", uncertain_ids)
        self.assertEqual(ignored["action"], "IGNORED")


if __name__ == "__main__":
    unittest.main()
