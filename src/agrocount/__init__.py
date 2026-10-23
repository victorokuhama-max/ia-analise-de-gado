"""AgroCount IA — Plataforma de Contagem Bovina com Visão Computacional e Human-in-the-Loop."""

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
    ReviewSessionState,
)
from .repository import AgroCountRepository
from .vision import CattleVisionEngineComponent
from .hitl import HitlActiveLearningComponent
from .service import InspectionManagementService
from .api import create_http_server, AgroCountApp

__all__ = [
    "AgroCountError",
    "AuditReport",
    "BoundingBoxDetection",
    "DetectionRun",
    "Farm",
    "GoldenDatasetSample",
    "HitlCorrectionBatch",
    "Inspection",
    "ModelVersion",
    "Paddock",
    "ReviewSessionState",
    "AgroCountRepository",
    "CattleVisionEngineComponent",
    "HitlActiveLearningComponent",
    "InspectionManagementService",
    "create_http_server",
    "AgroCountApp",
]

__version__ = "1.0.0"
