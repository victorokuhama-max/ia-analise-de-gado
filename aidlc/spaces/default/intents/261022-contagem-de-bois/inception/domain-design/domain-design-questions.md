# Projeto de Domínio e Catálogo de Componentes — Perguntas de Alinhamento (Domain Design)

Com base em `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`) e `practices-discovery/team-practices.md` (`team-practices.md`), definimos os blocos lógicos de construção e as fronteiras de propriedade de entidades do sistema.

---

## Question 1: Decomposição de Componentes Lógicos e Propriedade de Entidades

Qual decomposição de componentes de domínio devemos adotar para estruturar o código do sistema?

A. **(Recommended)** **4 Componentes Coesos Orientados a Domínio (`WebReviewStudioComponent`, `InspectionManagementComponent`, `CattleVisionEngineComponent`, `HitlActiveLearningComponent`)** — Separar claramente: (1) `WebReviewStudioComponent` (interface web e canvas interativo de revisão), (2) `InspectionManagementComponent` (proprietário de `Farm`, `Paddock`, `Inspection` e `AuditReport`), (3) `CattleVisionEngineComponent` (proprietário de `DetectionRun` e `BoundingBoxDetection`, executando YOLO+SAHI para fotos e YOLO+ByteTrack para vídeos) e (4) `HitlActiveLearningComponent` (proprietário de `HitlCorrectionBatch`, `GoldenDatasetSample` e `ModelVersion`, gerenciando a captura de amostras corrigidas no formato YOLO e o *fine-tuning* com trava de validação $\ge 95\%$).
B. **Componente Único Monolítico (`SingleAppComponent`)** — Concentrar todas as entidades de negócio, inferência de vídeo e treinamento em uma única classe/módulo sem separação de fronteiras.
C. **Decomposição Hiper-Fragmentada (15+ Micro-Componentes)** — Criar um componente separado para cada tabela e cada botão da tela.
X. Other (please specify)

[Answer]: A
