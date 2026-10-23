# Mapeamento de Histórias de Usuário por Unidade (Unit of Work Story Map)

Elaborado a partir de `domain-design/components.md` (`components.md`), `domain-design/decisions.md` (`decisions.md`), `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`) e `unit-of-work.md`.

## Matriz de Alocação de Histórias (`USx.y` $\rightarrow$ `Unit ID` e `Directory`)

| Story ID | Unit ID | Directory | Resumo da Funcionalidade (`stories.md`) |
|---|---|---|---|
| US1.1 | U1 | u1-agrocount-platform | Cadastro e seleção de Fazendas e Piquetes (`FR1.1`, `NFR2`, `NFR5`, `NFR6`) |
| US1.2 | U1 | u1-agrocount-platform | Criação e acompanhamento de Vistorias por status (`FR1.2`, `NFR4`, `NFR6`) |
| US1.3 | U1 | u1-agrocount-platform | Filtragem, paginação e estado vazio do histórico de vistorias (`FR1.3`, `NFR2`, `NFR5`) |
| US2.1 | U1 | u1-agrocount-platform | Upload web e importação GCP de fotos e vídeos aéreos (`FR2.1`, `NFR4`) |
| US2.2 | U1 | u1-agrocount-platform | Validação prévia de formato, integridade e limite de 500 MB (`FR2.2`, `NFR3`) |
| US3.1 | U1 | u1-agrocount-platform | Detecção em fotos aéreas 4K com YOLO + SAHI (`FR3.1`, `NFR1`, `NFR2`, `NFR3`) |
| US3.2 | U1 | u1-agrocount-platform | Contagem única em vídeos de drone com YOLO + ByteTrack (`FR3.2`, `NFR1`, `NFR2`, `NFR3`) |
| US3.3 | U1 | u1-agrocount-platform | Classificação automática por faixas de confiança (`>= 0.75` vs. `0.25-0.74`) (`FR3.3`) |
| US4.1 | U1 | u1-agrocount-platform | Visualização de bounding boxes com diferenciação semântica acessível (`FR4.1`, `NFR5`) |
| US4.2 | U1 | u1-agrocount-platform | Fila lateral de triagem rápida e atalhos de teclado (`FR4.2`, `NFR5`) |
| US4.3 | U1 | u1-agrocount-platform | Adição de falsos negativos (+FN) e remoção de falsos positivos (-FP) (`FR4.3`, `NFR2`) |
| US5.1 | U1 | u1-agrocount-platform | Exportação automática de correções humanas para o Golden Dataset YOLO (`FR5.1`, `NFR4`, `NFR6`) |
| US5.2 | U1 | u1-agrocount-platform | Painel de evolução do modelo IA e disparo sob demanda de fine-tuning (`FR5.2`, `NFR2`, `NFR3`) |
| US5.3 | U1 | u1-agrocount-platform | Validação de acurácia ($\ge 95\%$) e trava automática contra regressão (`FR5.3`, `NFR1`, `NFR6`) |
| US6.1 | U1 | u1-agrocount-platform | Geração e download de laudo auditado em PDF e CSV (`FR6.1`, `NFR2`, `NFR6`) |

---

## Sequência Interna de Implementação e Verificação de Cobertura

### Sequência Interna dentro de `U1` (`u1-agrocount-platform`)
1. **Camada de Domínio e Persistência (`InspectionManagementComponent`):** Entidades `Farm`, `Paddock`, `Inspection`, `AuditReport` e validação de mídia (`US1.1`–`US1.3`, `US2.1`–`US2.2`).
2. **Camada de Visão Computacional (`CattleVisionEngineComponent`):** Motor YOLO + SAHI para imagens, YOLO + ByteTrack para vídeos e categorização `high_confidence` / `uncertain` (`US3.1`–`US3.3`).
3. **Camada *Human-in-the-Loop* e *Active Learning* (`HitlActiveLearningComponent`):** Lotes de correção (`HitlCorrectionBatch`), geração de arquivos `.txt` YOLO e proveniência JSON no *Golden Dataset* (`GoldenDatasetSample`) e *fine-tuning* com trava $\ge 95\%$ (`ModelVersion`) (`US4.3`, `US5.1`–`US5.3`).
4. **Camada de Exportação e Interface Web (`WebReviewStudioComponent` + Relatórios):** Laudos PDF/CSV (`US6.1`) e Estúdio de Revisão Visual (`US4.1`, `US4.2`).

### Verificação de Cobertura
- **Total de Histórias Enumeradas em `stories.md`:** 15 (`US1.1` a `US6.1`).
- **Histórias Atribuídas a `U1` (`u1-agrocount-platform`):** 15 de 15 (100% de cobertura, zero órfãos ou lacunas).
