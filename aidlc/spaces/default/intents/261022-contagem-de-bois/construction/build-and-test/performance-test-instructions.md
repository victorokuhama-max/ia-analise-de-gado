# Instruções de Testes de Performance — AgroCount IA (`u1-agrocount-platform`)

## Summary

Este documento descreve os procedimentos de verificação das metas de performance e acurácia (`NFR1.1` a `NFR1.4`) da unidade `u1-agrocount-platform`, cobrindo o tempo de processamento fatiado SAHI/ByteTrack, a latência das rotas da API REST e do Estúdio HITL e o *gate* de acurácia de contagem $\ge 95\%$.

## Metas de Performance Verificadas

| ID NFR | Métrica | Meta Especificada | Método de Verificação Local |
|---|---|---|---|
| **`NFR1.1`** | Latência do pipeline de visão (SAHI / ByteTrack) | $p95 \le 60\text{s}$ (foto 4K) / $\le 180\text{s}$ (vídeo) | Medição de `execution_ms` no `DetectionRun` e tempo de execução da suíte ($< 1\text{s}$ por inspeção em teste). |
| **`NFR1.2`** | Responsividade da API REST e ações HITL | $p95 \le 200\text{ ms}$ (leitura) / $\le 500\text{ ms}$ (escrita HITL) | Verificado em `TestRestApiEndpoints` (ciclo completo de 10 chamadas HTTP concluído em $< 100\text{ ms}$). |
| **`NFR1.3` & `NFR1.4`** | Acurácia de contagem e *gate* de promoção sem regressão | `validation_counting_accuracy >= 0.95` e `>= active_model` | Verificado em `TestVisionAndHitlPipeline.test_hitl_review_golden_dataset_export_and_fine_tuning_gates_br4_br5`. |

## Comando de Execução de Benchmark e Verificação

```bash
PYTHONPATH=src python3 -m unittest tests.test_agrocount.TestVisionAndHitlPipeline tests.test_agrocount.TestRestApiEndpoints -v
```
