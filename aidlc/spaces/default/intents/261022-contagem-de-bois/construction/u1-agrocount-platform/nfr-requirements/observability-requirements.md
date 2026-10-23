# Requisitos de Observabilidade, Usabilidade e Acessibilidade (Observability & Accessibility Requirements — `u1-agrocount-platform`)

Elaborado a partir de `functional-design/functional-spec.md` (`functional-spec.md`), `functional-design/rules.md` (`rules.md`), `requirements-analysis/requirements.md` (`requirements.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `nfr-requirements-questions.md` [Q1].

## Sub-Requisitos de Acessibilidade WCAG 2.1 AA e Telemetria Operacional (`NFR5.*`)

| ID | Requisito Pai (`requirements.md`) | Especificação Quantitativa | Regra Relacionada (`rules.md`) |
|---|---|---|---|
| **NFR5.1** | `NFR5` | A interface web (`WebReviewStudioComponent`) deve cumprir **WCAG 2.1 Level AA**, com razão de contraste $\ge 4{,}5:1$ para textos, navegação completa por teclado (`Tab`, `Setas`, `Espaço`, `Delete`, `N`) e codificação tripla nas caixas delimitadoras (cor + estilo de borda + selo textual `OK`/`!`/`+`). | `BR1.1`, `BR1.3`, `BR4.1`, `BR4.2` |
| **NFR5.2** | `NFR5` | O sistema deve expor endpoint de saúde (`GET /api/v1/health`) e registrar métricas auditáveis de cada execução de inferência (`processingTimeMs`, `rawCount`, `uncertainCount`, `avgConfidence`) e de cada ciclo *Human-in-the-Loop* (`falseNegativesAdded`, `falsePositivesRemoved`, `validationAccuracy`). | `BR3.3`, `BR5.1`, `BR5.2`, `BR5.3` |

---

## Indicadores de Nível de Serviço (SLIs / SLOs)

- **SLI de Acurácia do Modelo Ativo:** `active_model.validation_accuracy >= 0.95` (exibido em tempo real no Painel de Evolução do Modelo IA).
- **SLI de Latência de Inferência:** `detection_run.processing_time_ms <= 5000` (fotos) e `<= 90000` (vídeos de 3 min).
- **SLI de Taxa de Intervenção Humana (HITL Drift):** Proporção de caixas `uncertain` + correções manuais (`+FN` / `-FP`) por vistoria, permitindo identificar quando acionar um novo ciclo de *fine-tuning*.
