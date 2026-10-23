# Plano de Geração de Código — `u1-agrocount-platform` (`U1`)

## Summary

Este plano detalha a implementação completa da unidade `u1-agrocount-platform` (`U1` — Plataforma Integrada AgroCount IA & Estúdio HITL) seguindo a postura `test-after` afirmada pela equipe (piso mínimo de 80% de cobertura de linhas). A implementação compreende a estrutura do pacote Python `src/agrocount/`, o modelo de dados e banco SQLite (`models.py` e `repository.py`), o motor de visão computacional com fatiamento SAHI, rastreamento ByteTrack e classificação de confiança (`vision.py`), o orquestrador *Human-in-the-Loop (Active Learning)* com curadoria do *Golden Dataset*, ajuste fino sob demanda e *gate* de promoção sem regressão (`hitl.py`), o serviço de gestão de inspeções e exportação de laudos auditáveis PDF/CSV (`service.py`), a API RESTful `/api/v1/*` (`api.py`) e o Estúdio Web de Revisão HITL responsivo (`web/index.html` e `web/app.js`), acompanhados da suíte automatizada de testes unitários, de integração e de contrato (`tests/test_agrocount.py`) e do script de verificação de cobertura (`scripts/verify.sh`).

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "Implementar cada camada testável aplicável (pipeline de visão computacional / *Human-in-the-Loop* e serviços/interface web) e, em seguida, escrever e executar os testes automatizados daquela camada antes de concluir a unidade.",
  "scope": "mvp",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "Tratamos testes automatizados como entregável de primeira classe em cada unidade construída:\n- **Methodology**: test-after\n- **Methodology evidence**: Afirmado na entrevista de práticas (`practices-discovery-questions.md` [Q3]) a partir do padrão organizacional de `aidlc/spaces/default/memory/org.md` para o escopo `mvp`.\n- **Ordering**: Implementar cada camada testável aplicável (pipeline de visão computacional / *Human-in-the-Loop* e serviços/interface web) e, em seguida, escrever e executar os testes automatizados daquela camada antes de concluir a unidade.\n- **Cobertura e estratégia (`mvp`):** Piso mínimo de **80% de cobertura de linhas** (*line coverage*) verificado pela suíte automatizada antes do merge, cobrindo testes unitários e de integração dos fluxos de contagem por IA, captura do *Golden Dataset* (*Human-in-the-Loop*) e exportação de laudos [Q3]."
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Meet an 80% line-coverage floor.",
      "Run the selected tests in CI before merge."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:c186488084db00f27630fccc2773ee2fecc6ca6cd52c283575a977c475689e6c",
  "contract_sha256": "sha256:9f5857eb9a4a9e61c25b861737df9fbf96f433e53ba4fd2e8825622d323824ac"
}
```

## Etapas de Execução (`u1-agrocount-platform`)

- [x] Step 1: Project structure and production configuration skeleton (`src/agrocount/__init__.py`, diretórios `src/agrocount/web/`, `tests/`, `scripts/`).
- [x] Step 2: Bootstrap the minimal test runner/configuration and record the exact unit-scoped command (`scripts/verify.sh` e `scripts/run_coverage.py` com medição determinística de cobertura de linhas $\ge 80\%$).
- [x] Step 3: Data model / database behavior - implement (`src/agrocount/models.py` com as 10 entidades de domínio `Farm`, `Paddock`, `Inspection`, `DetectionRun`, `BoundingBoxDetection`, `HitlCorrectionBatch`, `GoldenDatasetSample`, `ModelVersion`, `AuditReport`, `ReviewSessionState` e invariantes `BR1.1`–`BR6.1`).
- [x] Step 4: Data model / database behavior - write and run its tests after implementation (testes unitários de entidades, invariantes e serialização em `tests/test_agrocount.py`).
- [x] Step 5: Repository / data access - implement (`src/agrocount/repository.py` com persistência transacional SQLite, controle de idempotência e armazenamento local/GCS simulado para artefatos do *Golden Dataset* e laudos).
- [x] Step 6: Repository / data access - write and run its tests after implementation (testes de persistência SQLite, unicidade, idempotência e escrita atômica em `tests/test_agrocount.py`).
- [x] Step 7: Business logic - implement (`src/agrocount/vision.py` para `CattleVisionEngineComponent` com validação pré-GPU `BR2.2`, SAHI + NMS `BR3.1`, ByteTrack `BR3.2` e classificação de confiança `BR3.3`; `src/agrocount/hitl.py` para `HitlActiveLearningComponent` com exportação YOLO `.txt` + `.json` para o *Golden Dataset* `BR5.1`, *fine-tuning* sob demanda `BR5.2` e *gate* de promoção sem regressão `BR5.3`; `src/agrocount/service.py` para `InspectionManagementComponent` e exportação PDF/CSV `BR6.1`).
- [x] Step 8: Business logic - write and run its tests after implementation (testes unitários e de integração das regras `BR1.1`–`BR6.1` e critérios `AC1.1.1`–`AC6.1.1` em `tests/test_agrocount.py`).
- [x] Step 9: API / endpoint - implement (`src/agrocount/api.py` expondo `/api/v1/health`, `/api/v1/farms`, `/api/v1/inspections`, `/api/v1/inspections/{id}/hitl-review`, `/api/v1/models/active`, `/api/v1/models/fine-tune` e `/api/v1/inspections/{id}/report` com envelopes JSON estruturados e cabeçalhos `X-Correlation-Id`).
- [x] Step 10: API / endpoint - write and run its tests after implementation (testes de contrato e integração HTTP de todos os endpoints `/api/v1/*`, códigos de erro 400/404/409/422 e segurança em `tests/test_agrocount.py`).
- [x] Step 11: Frontend behavior - implement (`src/agrocount/web/index.html` e `src/agrocount/web/app.js` implementando o `WebReviewStudioComponent` com as 4 telas responsivas, tripla codificação WCAG 2.1 AA, atalhos de teclado `Setas`/`Espaço`/`Delete`/`N`, fila de triagem de baixa confiança e Painel de Evolução do Modelo).
- [x] Step 12: Frontend behavior - write and run its tests after implementation (testes de servidor web, renderização dos seletores `data-testid` e fluxo de estado de revisão `ReviewSessionState` em `tests/test_agrocount.py`).
- [x] Step 13: Environment/build configuration (`Dockerfile` multi-stage, `.dockerignore` e `pyproject.toml`).
- [x] Step 14: Documentation and traceability (`README.md`, `code-summary.md`, `source-manifest.json` e `traceability.json` da unidade `u1-agrocount-platform`).
