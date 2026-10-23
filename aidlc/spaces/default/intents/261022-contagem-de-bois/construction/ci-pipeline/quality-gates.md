# Definição de Quality Gates (`quality-gates`) — AgroCount IA (`u1-agrocount-platform`)

## Summary

Este documento define os *Quality Gates* automatizados e obrigatórios antes de qualquer integração (*squash-merge*) na branch `main` e promoção de modelos/containers da plataforma AgroCount IA (`u1-agrocount-platform`), garantindo o cumprimento integral do contrato de testes (`## Testing Contract`) e dos requisitos não-funcionais (`NFR1`–`NFR6`).

## 1. Matriz de Quality Gates no Pipeline de CI (`.github/workflows/ci.yml`)

| Gate ID | Nome do Gate | Comando / Verificador | Limiar Obrigatório (*Threshold*) | Ação em Caso de Falha |
|---|---|---|---|---|
| **QG-01** | Integridade Sintática e de Módulos | `PYTHONPATH=src python3 -m compileall -q src/ tests/ scripts/` | `0` erros de sintaxe ou importação | Bloqueia merge do Pull Request (`exit 1`) |
| **QG-02** | Suíte Unitária, Integração e Contrato OpenAPI | `bash scripts/verify.sh` (`tests/test_agrocount.py`) | `100%` dos testes aprovados (`14/14 OK`, `0` falhas) | Bloqueia merge do Pull Request (`exit 1`) |
| **QG-03** | Piso de Cobertura de Linhas (*Line Coverage*) | `python3 scripts/run_coverage.py` | Cobertura global de `src/agrocount/` **$\ge 80,0\%$** (atual: **94,3%**) | Bloqueia merge do Pull Request (`exit 1`) |
| **QG-04** | Gate de Segurança e Imutabilidade HITL | `TestRestApiEndpoints` & `TestVisionAndHitlPipeline` | Rejeição `401` sem token, bloqueio pré-GPU `422` (`BR2.2`) e imutabilidade `409` pós-auditoria (`BR4.3`) | Bloqueia merge do Pull Request (`exit 1`) |
| **QG-05** | Gate de Promoção Sem Regressão (*Active Learning*) | `HitlActiveLearningComponent.trigger_fine_tuning` (`BR5.3`) | `validation_counting_accuracy >= 0.95` **E** `>= active_model.validation_counting_accuracy` | Descarta candidato (`REJECTED_REGRESSION`) e preserva modelo ativo |
| **QG-06** | Build Multi-Stage Container Não-Root | `docker build -t agrocount-platform:ci .` | Imagem construída com `USER 10001:10001` sem segredos embutidos | Bloqueia publicação no Artifact Registry |

## 2. Rastreabilidade com o Resumo de Build e Testes (`TGT-CI-MERGE`)

Com a criação de `.github/workflows/ci.yml` e deste conjunto de *Quality Gates*, a obrigação `TGT-CI-MERGE` (*"Run the selected tests in CI before merge"*) registrada em `build-and-test-summary.md` e `test-results.md` encontra-se integralmente atendida e automatizada.
