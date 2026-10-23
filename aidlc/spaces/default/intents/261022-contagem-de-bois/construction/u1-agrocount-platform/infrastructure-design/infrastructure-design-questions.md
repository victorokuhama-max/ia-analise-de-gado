# Projeto de Infraestrutura e Nuvem — Perguntas de Alinhamento (Infrastructure Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-design/performance-design.md` (`performance-design.md`), `nfr-design/security-design.md` (`security-design.md`), `nfr-design/scalability-design.md` (`scalability-design.md`), `nfr-design/reliability-design.md` (`reliability-design.md`), `nfr-design/observability-design.md` (`observability-design.md`), `nfr-design/logical-components.md` (`logical-components.md`), `domain-design/components.md` (`components.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

---

## Question 1: Arquitetura de Implantação Google Cloud Platform (GCP), Monitoramento e Pipeline CI/CD

Qual especificação de infraestrutura devemos consolidar para `u1-agrocount-platform`?

A. **(Recommended)** **Google Cloud Run Serverless (`scale-to-zero` com GPU L4 sob demanda) + Google Cloud Storage (Mídias & Golden Dataset) + GitHub Actions CI/CD com Gate de Cobertura $\ge 80\%$** — Provisionar `u1-agrocount-platform` em Cloud Run (`min-instances=0`, `max-instances=4`), buckets GCS segregados (`agrocount-drone-media` e `agrocount-golden-dataset`), Cloud Monitoring para métricas de acurácia/latência e pipeline CI/CD trunk-based que bloqueia merge caso a cobertura de testes fique abaixo de 80%.
B. **Cluster Kubernetes Dedicado 24/7 com GPUs Fixas** — Manter nós de GPU sempre ligados com alto custo fixo mensal.
X. Other (please specify)

[Answer]: A
