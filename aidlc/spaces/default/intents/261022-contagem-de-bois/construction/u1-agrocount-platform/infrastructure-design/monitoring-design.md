# Projeto de Monitoramento e Observabilidade (Monitoring Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-design/performance-design.md` (`performance-design.md`), `nfr-design/security-design.md` (`security-design.md`), `nfr-design/scalability-design.md` (`scalability-design.md`), `nfr-design/reliability-design.md` (`reliability-design.md`), `nfr-design/observability-design.md` (`observability-design.md`), `nfr-design/logical-components.md` (`logical-components.md`), `domain-design/components.md` (`components.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

## 1. Métricas e Indicadores Operacionais (Metrics & KPIs)

| Metric | Source | Threshold | Why it matters |
|---|---|---|---|
| `active_model_validation_accuracy` | `HitlActiveLearningComponent` (`/api/v1/models/active`) | $\ge 0{,}95$ ($95{,}0\%$) | Garante que o modelo ativo cumpre a meta de acurácia do negócio (`NFR1.1`, `NFR1.2`). |
| `vision_inference_duration_ms` | `CattleVisionEngineComponent` (`DetectionRun.processingTimeMs`) | $\le 5000\text{ms}$ (foto) / $\le 90000\text{ms}$ (vídeo 3 min) | Verifica cumprimento do SLA de processamento em GPU (`NFR2.1`). |
| `api_request_latency_p95_ms` | HTTP Server / Cloud Run Metrics | $< 500\text{ms}$ | Assegura responsividade no Estúdio de Revisão Visual e listagens (`NFR2.2`). |
| `hitl_golden_samples_total` | `HitlActiveLearningComponent` (`GoldenDatasetSample`) | Informativo (gatilho sugerido a cada $+25$ amostras) | Indica volume de novos *Hard Examples* prontos para *fine-tuning* (`NFR3.2`, `NFR5.2`). |
| `cloud_run_idle_gpu_instances` | Cloud Run Autoscaler | $0$ quando sem jobs ativos | Comprova eficiência financeira *scale-to-zero* (`NFR3.1`). |

---

## 2. Regras de Alerta e SLIs / SLOs

### Alertas Operacionais (Alerts)

| Alert | Condition | Severity | Routes to |
|---|---|---|---|
| `ModelCandidateRejectedRegression` | `candidate.validationAccuracy < 0.95` ou `< active.validationAccuracy` | `WARNING` | Painel de Evolução do Modelo IA + Log de Auditoria (`NFR1.2`, `NFR4.2`) |
| `InferenceLatencyBreach` | `processingTimeMs > 5000` (foto) ou `> 90000` (vídeo) | `WARNING` | Equipe Técnica / Cloud Monitoring (`NFR2.1`) |
| `ServiceHealthCheckFailed` | `GET /api/v1/health != 200` por 2 verificações consecutivas | `CRITICAL` | Engenheiro de Plantão / Cloud Run Health Probe (`NFR4.2`, `NFR5.2`) |

### SLIs e SLOs

| SLI | SLO target | Measurement window |
|---|---|---|
| Acurácia de Contagem do Modelo Ativo | $\ge 95{,}0\%$ no conjunto de validação | Contínuo por versão promovida (`NFR1.1`) |
| Latência de Rotas REST Síncronas ($p95$) | $< 500\text{ms}$ em $99\%$ das janelas | Janela móvel de 7 dias (`NFR2.2`) |
| Disponibilidade do Serviço (`/api/v1/health`) | $\ge 99{,}0\%$ | Mensal (30 dias) (`NFR4.2`) |

### Logs Estruturados e Rastreamento (Logs & Tracing)

- **Formato:** JSON estruturado em `stdout` compatível com Google Cloud Logging, contendo `timestamp`, `level`, `event`, `inspection_id`, `batch_id` e `model_version`.
