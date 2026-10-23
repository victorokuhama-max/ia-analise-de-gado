# Instruções de Testes de Integração — AgroCount IA (`u1-agrocount-platform`)

## Summary

Este documento detalha a execução dos testes de integração entre os 4 componentes internos da unidade `u1-agrocount-platform` (`InspectionManagementComponent`, `CattleVisionEngineComponent`, `HitlActiveLearningComponent` e `WebReviewStudioComponent`), verificando a persistência SQLite, o armazenamento atômico do *Golden Dataset*, o *gate* de promoção sem regressão e os contratos HTTP `/api/v1/*`.

## Cenários de Integração Cobertos

| ID do Cenário | Fronteira de Integração | Requisitos / Regras Verificados |
|---|---|---|
| **INT-01** | `InspectionManagementService` $\leftrightarrow$ `CattleVisionEngineComponent` $\leftrightarrow$ `AgroCountRepository` | `FR1.1`–`FR3.2`, `BR1.1`–`BR3.3` (Validação pré-GPU, SAHI + NMS, ByteTrack e persistência SQLite) |
| **INT-02** | `HitlActiveLearningComponent` $\leftrightarrow$ `AgroCountRepository` (*Golden Dataset* YOLO `.txt` + `.json`) | `FR4.1`–`FR5.3`, `BR4.1`–`BR5.3` (Reconciliação matemática exata, imutabilidade pós-auditoria, exportação YOLO e *fine-tuning* com *gate* $\ge 0,95$) |
| **INT-03** | `AgroCountApp` / `ThreadingHTTPServer` $\leftrightarrow$ `InspectionManagementService` $\leftrightarrow$ `WebReviewStudioComponent` | `FR6.1`, `BR6.1`, Contrato OpenAPI 3.1 `/api/v1/*`, entrega de HTML/JS com seletores `data-testid` e laudos PDF/CSV com checksum `SHA-256` |

## Comandos de Execução dos Testes de Integração

```bash
PYTHONPATH=src python3 -m unittest \
  tests.test_agrocount.TestVisionAndHitlPipeline \
  tests.test_agrocount.TestInspectionAndReportService \
  tests.test_agrocount.TestRestApiEndpoints \
  tests.test_agrocount.TestWebReviewStudioFrontend -v
```
