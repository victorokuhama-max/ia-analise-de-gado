# Especificação do Pipeline de CI/CD (CI/CD Pipeline Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-design/performance-design.md` (`performance-design.md`), `nfr-design/security-design.md` (`security-design.md`), `nfr-design/scalability-design.md` (`scalability-design.md`), `nfr-design/reliability-design.md` (`reliability-design.md`), `nfr-design/observability-design.md` (`observability-design.md`), `nfr-design/logical-components.md` (`logical-components.md`), `domain-design/components.md` (`components.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

## 1. Estágios do Pipeline e Gates de Qualidade (Stage-to-Gate Mapping)

| Stage | Comando / Ação Executada | Gate de Aprovação (Critério de Passagem) | Requisitos Atendidos |
|---|---|---|---|
| **1. Static & Security Check** | Verificação de sintaxe Python (`py_compile`), validação de ausência de segredos hardcoded e checagem de arquivos HTML/JS do Estúdio Web | Zero erros de sintaxe e zero segredos expostos | `NFR6.1` |
| **2. Automated Unit & Integration Tests** | Execução da suíte automatizada (`bash scripts/verify.sh`) cobrindo Fazendas/Piquetes, Validação Pré-GPU, YOLO+SAHI, YOLO+ByteTrack, Ciclo HITL (*Golden Dataset*), Trava de *Fine-Tuning* ($\ge 95\%$) e Exportação PDF/CSV | 100% dos testes passando (`0` falhas) | `NFR1.1`, `NFR1.2`, `NFR4.1`, `NFR6.2` |
| **3. Line Coverage Gate ($\ge 80\%$)** | Cálculo determinístico de cobertura de linhas sobre os módulos de `src/agrocount/` via `trace` / verificador de cobertura | **Cobertura de linhas $\ge 80{,}0\%$** (falha imediata se $< 80\%$) | `NFR6.2` |
| **4. Container Build & Cloud Run Deploy** | Build da imagem containerizada e deploy para Google Cloud Run (`staging` automático na `main`; `production` mediante aprovação) | Health check `GET /api/v1/health` retornando `200 OK` | `NFR3.1`, `NFR4.2`, `NFR5.2` |

---

## 2. Estratégia de Deploy, Promoção e Rollback

1. **Integração Trunk-Based (`main`):** Todo código da unidade `u1-agrocount-platform` passa obrigatoriamente pelo script `bash scripts/verify.sh` antes da integração na `main`.
2. **Estratégia de Rollout no Cloud Run:** Revisões imutáveis do Cloud Run com migração de tráfego controlada e *health check* em `/api/v1/health`.
3. **Procedimento de Rollback:**
   - **Rollback de Infraestrutura/Código:** Redirecionamento instantâneo de 100% do tráfego para a revisão anterior do Cloud Run (`gcloud run services update-traffic --to-revisions=PREVIOUS=100`).
   - **Rollback de Modelo de IA (`BR5.3`):** Impedido preventivamente pela trava automática que rejeita qualquer candidato com acurácia $< 95\%$ ou inferior ao modelo em produção (`rejected_regression`).
