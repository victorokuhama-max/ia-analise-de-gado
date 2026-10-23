# Instruções de Testes Unitários e de Integração — `u1-agrocount-platform` (`U1`)

## Summary

Este documento define os comandos exatos no escopo da unidade `u1-agrocount-platform` (`U1`) para execução dos testes unitários, de integração e de contrato HTTP, bem como a verificação determinística do piso mínimo de **80% de cobertura de linhas** (*line coverage*) estabelecido na entrevista de práticas (`team.md`).

## Comandos de Execução por Camada Testável

| Camada Testável | Comando Escopado para a Unidade (`u1-agrocount-platform`) | Critério de Sucesso |
|---|---|---|
| **1. Data model / database behavior** (`models.py`) | `PYTHONPATH=src python3 -m unittest tests.test_agrocount.TestDomainModels -v` | 100% dos testes de invariantes de entidades e serialização aprovados (`exit 0`) |
| **2. Repository / data access** (`repository.py`) | `PYTHONPATH=src python3 -m unittest tests.test_agrocount.TestRepositoryLayer -v` | 100% dos testes de persistência SQLite, unicidade e idempotência aprovados (`exit 0`) |
| **3. Business logic — Visão Computacional & HITL** (`vision.py`, `hitl.py`, `service.py`) | `PYTHONPATH=src python3 -m unittest tests.test_agrocount.TestVisionAndHitlPipeline tests.test_agrocount.TestInspectionAndReportService -v` | 100% dos testes de SAHI, ByteTrack, triagem de confiança, *Golden Dataset* YOLO, *fine-tuning* com *gate* $\ge 0.95$ e laudos PDF/CSV aprovados (`exit 0`) |
| **4. API / endpoint** (`api.py`) | `PYTHONPATH=src python3 -m unittest tests.test_agrocount.TestRestApiEndpoints -v` | 100% dos testes de contrato OpenAPI `/api/v1/*`, códigos HTTP (`200`, `201`, `202`, `400`, `409`, `422`) e cabeçalhos `X-Correlation-Id` aprovados (`exit 0`) |
| **5. Frontend behavior** (`web/index.html`, `web/app.js`, `ReviewSessionState`) | `PYTHONPATH=src python3 -m unittest tests.test_agrocount.TestWebReviewStudioFrontend -v` | 100% dos testes de entrega do Estúdio Web, atributos `data-testid`, acessibilidade WCAG 2.1 AA e estado de revisão aprovados (`exit 0`) |
| **Suíte Completa + Gate de Cobertura ($\ge 80\%$)** | `bash scripts/verify.sh` | Todos os testes aprovados (`OK`) e cobertura de linhas de `src/agrocount/` $\ge 80\%$ (`exit 0`) |

## Pré-requisitos e Isolamento de Ambiente

1. **Runtime:** Python 3.11+ (validado em Python 3.13 no ambiente local) utilizando exclusivamente módulos nativos da biblioteca padrão para zero dependência externa obrigatória em testes locais e CI.
2. **Isolamento de Dados:** Cada caso de teste cria um banco SQLite temporário e um diretório de armazenamento temporário (`tempfile.TemporaryDirectory`) para o *Golden Dataset* e laudos, garantindo execução determinística, paralelizável e sem efeitos colaterais no repositório.
