# Modelo Lógico de Entidades (Functional Design Entities — `u1-agrocount-platform`)

Elaborado a partir de `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `user-stories/stories.md` (`stories.md`), `requirements-analysis/requirements.md` (`requirements.md`), `domain-design/components.md` (`components.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `functional-design-questions.md` [Q1].

## Bloco Fonte de Verdade de Entidades (Source-of-Truth YAML Entity Model)

```yaml
entities:
  - name: Farm
    owning_component: InspectionManagementComponent
    description: Propriedade rural cadastrada para realização de inventários aéreos de gado.
    attributes:
      - name: farmId
        type: string
        required: true
        unique: true
        constraints: Identificador único imutável (UUID/slug)
      - name: name
        type: string
        required: true
        min_length: 2
        max_length: 120
      - name: municipality
        type: string
        required: true
        max_length: 80
      - name: stateUf
        type: string
        required: true
        min_length: 2
        max_length: 2
      - name: ownerName
        type: string
        required: false
        max_length: 120
      - name: notes
        type: string
        required: false
      - name: createdAt
        type: timestamp
        required: true
    relationships:
      - target: Paddock
        cardinality: 1:N
        direction: Farm -> Paddock
      - target: Inspection
        cardinality: 1:N
        direction: Farm -> Inspection

  - name: Paddock
    owning_component: InspectionManagementComponent
    description: Divisão de pastagem ou lote bovino pertencente a uma Fazenda.
    attributes:
      - name: paddockId
        type: string
        required: true
        unique: true
      - name: farmId
        type: string
        required: true
        references: Farm.farmId
      - name: name
        type: string
        required: true
        min_length: 1
        max_length: 100
      - name: areaHectares
        type: decimal
        required: false
        min: 0.1
      - name: notes
        type: string
        required: false
      - name: createdAt
        type: timestamp
        required: true
    relationships:
      - target: Farm
        cardinality: N:1
        direction: Paddock -> Farm
      - target: Inspection
        cardinality: 1:N
        direction: Paddock -> Inspection

  - name: Inspection
    owning_component: InspectionManagementComponent
    description: Sessão de vistoria aérea de um piquete a partir de foto ou vídeo de drone.
    attributes:
      - name: inspectionId
        type: string
        required: true
        unique: true
      - name: farmId
        type: string
        required: true
        references: Farm.farmId
      - name: paddockId
        type: string
        required: true
        references: Paddock.paddockId
      - name: auditorId
        type: string
        required: true
      - name: mediaType
        type: enum
        required: true
        allowed_values: [image, video]
      - name: mediaUri
        type: string
        required: true
      - name: mediaSizeBytes
        type: integer
        required: true
        min: 1
        max: 524288000
      - name: status
        type: enum
        required: true
        allowed_values: [pending, processing, needs_review, reviewed, failed]
        default: pending
      - name: rawAiCount
        type: integer
        required: true
        default: 0
        min: 0
      - name: highConfidenceCount
        type: integer
        required: true
        default: 0
        min: 0
      - name: uncertainCount
        type: integer
        required: true
        default: 0
        min: 0
      - name: addedFnCount
        type: integer
        required: true
        default: 0
        min: 0
      - name: removedFpCount
        type: integer
        required: true
        default: 0
        min: 0
      - name: finalAuditedCount
        type: integer
        required: true
        default: 0
        min: 0
      - name: avgConfidence
        type: decimal
        required: true
        default: 0.0
        min: 0.0
        max: 1.0
      - name: modelVersionUsed
        type: string
        required: true
      - name: idempotencyKey
        type: string
        required: false
        unique: true
      - name: createdAt
        type: timestamp
        required: true
      - name: updatedAt
        type: timestamp
        required: true
    entity_constraints:
      - "finalAuditedCount == highConfidenceCount + uncertainConfirmed + addedFnCount (ou rawAiCount + addedFnCount - removedFpCount quando todas as duvidosas restantes são resolvidas)"

  - name: DetectionRun
    owning_component: CattleVisionEngineComponent
    description: Execução de inferência de visão computacional (YOLO+SAHI ou YOLO+ByteTrack) sobre a mídia de uma vistoria.
    attributes:
      - name: runId
        type: string
        required: true
        unique: true
      - name: inspectionId
        type: string
        required: true
        references: Inspection.inspectionId
      - name: modelVersionTag
        type: string
        required: true
      - name: pipelineMode
        type: enum
        required: true
        allowed_values: [yolo_sahi_image, yolo_bytetrack_video]
      - name: processingTimeMs
        type: integer
        required: true
        min: 0
      - name: rawCount
        type: integer
        required: true
        min: 0
      - name: highConfidenceCount
        type: integer
        required: true
        min: 0
      - name: uncertainCount
        type: integer
        required: true
        min: 0
      - name: avgConfidence
        type: decimal
        required: true
        min: 0.0
        max: 1.0
      - name: representativeFrameUri
        type: string
        required: true
      - name: completedAt
        type: timestamp
        required: true

  - name: BoundingBoxDetection
    owning_component: CattleVisionEngineComponent
    description: Caixa delimitadora individual detectada pela IA ou adicionada manualmente pelo auditor.
    attributes:
      - name: detectionId
        type: string
        required: true
        unique: true
      - name: runId
        type: string
        required: true
        references: DetectionRun.runId
      - name: inspectionId
        type: string
        required: true
        references: Inspection.inspectionId
      - name: frameIndex
        type: integer
        required: true
        default: 0
        min: 0
      - name: timestampSec
        type: decimal
        required: true
        default: 0.0
        min: 0.0
      - name: trackId
        type: integer
        required: false
      - name: classId
        type: integer
        required: true
        default: 0
      - name: xCenter
        type: decimal
        required: true
        min: 0.0
        max: 1.0
      - name: yCenter
        type: decimal
        required: true
        min: 0.0
        max: 1.0
      - name: width
        type: decimal
        required: true
        min: 0.001
        max: 1.0
      - name: height
        type: decimal
        required: true
        min: 0.001
        max: 1.0
      - name: confidence
        type: decimal
        required: true
        min: 0.0
        max: 1.0
      - name: confidenceTier
        type: enum
        required: true
        allowed_values: [high_confidence, uncertain, manual_added]
      - name: reviewStatus
        type: enum
        required: true
        allowed_values: [auto_accepted, pending_triage, confirmed, removed_fp, added_fn]

  - name: HitlCorrectionBatch
    owning_component: HitlActiveLearningComponent
    description: Registro auditável de uma revisão humana (Human-in-the-Loop) confirmada pelo auditor.
    attributes:
      - name: batchId
        type: string
        required: true
        unique: true
      - name: inspectionId
        type: string
        required: true
        references: Inspection.inspectionId
      - name: auditorId
        type: string
        required: true
      - name: modelVersionUsed
        type: string
        required: true
      - name: falseNegativesAdded
        type: integer
        required: true
        min: 0
      - name: falsePositivesRemoved
        type: integer
        required: true
        min: 0
      - name: uncertainConfirmed
        type: integer
        required: true
        min: 0
      - name: finalCount
        type: integer
        required: true
        min: 0
      - name: idempotencyKey
        type: string
        required: false
        unique: true
      - name: createdAt
        type: timestamp
        required: true

  - name: GoldenDatasetSample
    owning_component: HitlActiveLearningComponent
    description: Amostra curada no formato YOLO normalizado + proveniência JSON salva no Golden Dataset para Active Learning.
    attributes:
      - name: sampleId
        type: string
        required: true
        unique: true
      - name: batchId
        type: string
        required: true
        references: HitlCorrectionBatch.batchId
      - name: inspectionId
        type: string
        required: true
        references: Inspection.inspectionId
      - name: imageUri
        type: string
        required: true
      - name: yoloLabelsUri
        type: string
        required: true
      - name: provenanceJsonUri
        type: string
        required: true
      - name: yoloAnnotationsText
        type: string
        required: true
      - name: boxCount
        type: integer
        required: true
        min: 0
      - name: usedInTrainingVersion
        type: string
        required: false
      - name: createdAt
        type: timestamp
        required: true

  - name: ModelVersion
    owning_component: HitlActiveLearningComponent
    description: Versão do modelo de visão computacional YOLO e seu status de validação/promoção.
    attributes:
      - name: versionId
        type: string
        required: true
        unique: true
      - name: versionTag
        type: string
        required: true
        unique: true
      - name: baseVersionTag
        type: string
        required: false
      - name: weightsUri
        type: string
        required: true
      - name: goldenSamplesCount
        type: integer
        required: true
        min: 0
      - name: validationAccuracy
        type: decimal
        required: true
        min: 0.0
        max: 1.0
      - name: precisionScore
        type: decimal
        required: true
        min: 0.0
        max: 1.0
      - name: recallScore
        type: decimal
        required: true
        min: 0.0
        max: 1.0
      - name: status
        type: enum
        required: true
        allowed_values: [active, archived, rejected_regression, training]
      - name: promotedAt
        type: timestamp
        required: false
      - name: createdAt
        type: timestamp
        required: true

  - name: AuditReport
    owning_component: InspectionManagementComponent
    description: Relatório oficial exportado em PDF ou CSV comprovando o inventário auditado do piquete.
    attributes:
      - name: reportId
        type: string
        required: true
        unique: true
      - name: inspectionId
        type: string
        required: true
        references: Inspection.inspectionId
      - name: format
        type: enum
        required: true
        allowed_values: [pdf, csv]
      - name: generatedUri
        type: string
        required: true
      - name: checksumSha256
        type: string
        required: true
      - name: generatedBy
        type: string
        required: true
      - name: generatedAt
        type: timestamp
        required: true

  - name: ReviewSessionState
    owning_component: WebReviewStudioComponent
    description: Estado de sessão interativa do Estúdio de Revisão Visual no cliente web.
    attributes:
      - name: sessionId
        type: string
        required: true
        unique: true
      - name: inspectionId
        type: string
        required: true
        references: Inspection.inspectionId
      - name: activeTool
        type: enum
        required: true
        allowed_values: [select, add]
        default: select
      - name: selectedBoxId
        type: string
        required: false
      - name: zoomLevel
        type: decimal
        required: true
        default: 1.0
        min: 0.5
        max: 4.0
      - name: pendingAdditions
        type: integer
        required: true
        default: 0
      - name: pendingRemovals
        type: integer
        required: true
        default: 0
      - name: dirtyFlag
        type: boolean
        required: true
        default: false
```

---

## Resumo Legível por Humanos do Modelo de Entidades

| Entidade | Componente Proprietário (`components.md`) | Identificador | Relacionamentos Principais |
|---|---|---|---|
| `Farm` | `InspectionManagementComponent` | `farmId` | `1:N` com `Paddock` e `Inspection` |
| `Paddock` | `InspectionManagementComponent` | `paddockId` | `N:1` com `Farm`; `1:N` com `Inspection` |
| `Inspection` | `InspectionManagementComponent` | `inspectionId` | `N:1` com `Farm` e `Paddock`; `1:N` com `DetectionRun`, `HitlCorrectionBatch`, `AuditReport` |
| `DetectionRun` | `CattleVisionEngineComponent` | `runId` | `N:1` com `Inspection`; `1:N` com `BoundingBoxDetection` |
| `BoundingBoxDetection` | `CattleVisionEngineComponent` | `detectionId` | `N:1` com `DetectionRun` e `Inspection` |
| `HitlCorrectionBatch` | `HitlActiveLearningComponent` | `batchId` | `N:1` com `Inspection`; `1:1` com `GoldenDatasetSample` |
| `GoldenDatasetSample` | `HitlActiveLearningComponent` | `sampleId` | `1:1` com `HitlCorrectionBatch` |
| `ModelVersion` | `HitlActiveLearningComponent` | `versionId` | Registra versões `active`, `archived` e `rejected_regression` |
| `AuditReport` | `InspectionManagementComponent` | `reportId` | `N:1` com `Inspection` |
| `ReviewSessionState` | `WebReviewStudioComponent` | `sessionId` | `N:1` com `Inspection` |
