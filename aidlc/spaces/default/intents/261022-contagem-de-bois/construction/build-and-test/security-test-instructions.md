# Instruções de Testes de Segurança — AgroCount IA (`u1-agrocount-platform`)

## Summary

Este documento define as verificações automatizadas de segurança (`NFR2.1`, `NFR2.2`, `NFR2.3`) da unidade `u1-agrocount-platform`, abrangendo autenticação Bearer Token, bloqueio de *path traversal* na resolução de URIs do Cloud Storage, validação estrita de payloads/mídias e imutabilidade de auditoria.

## Controles de Segurança Verificados

| ID NFR / Regra | Controle de Segurança | Teste Automatizado Correspondente |
|---|---|---|
| **`NFR2.1`** | Autenticação via Bearer Token (`401 UNAUTHORIZED` / `INVALID_TOKEN` quando ausente ou inválido) | `TestRestApiEndpoints.test_full_rest_api_lifecycle_and_error_envelopes` |
| **`NFR2.2`** | Sanitização de URI `gs://` contra *path traversal* e validação pré-GPU de formato/tamanho ($\le 2\text{ GiB}$) | `TestVisionAndHitlPipeline.test_pre_gpu_validation_gates_br2_2` & `AgroCountRepository.resolve_gcs_uri` |
| **`NFR2.3` & `BR4.3`** | Trilha de auditoria (`auditor_id`, timestamps UTC, `X-Correlation-Id`) e bloqueio `409 INSPECTION_ALREADY_AUDITED` | `TestVisionAndHitlPipeline.test_hitl_review_golden_dataset_export_and_fine_tuning_gates_br4_br5` |

## Comando de Execução dos Testes de Segurança

```bash
PYTHONPATH=src python3 -m unittest tests.test_agrocount.TestRestApiEndpoints tests.test_agrocount.TestVisionAndHitlPipeline -v
```
