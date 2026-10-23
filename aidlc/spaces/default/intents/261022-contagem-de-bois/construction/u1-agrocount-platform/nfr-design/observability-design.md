# Projeto de Observabilidade, Acessibilidade e Telemetria (Observability Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-requirements/performance-requirements.md` (`performance-requirements.md`), `nfr-requirements/security-requirements.md` (`security-requirements.md`), `nfr-requirements/scalability-requirements.md` (`scalability-requirements.md`), `nfr-requirements/reliability-requirements.md` (`reliability-requirements.md`), `nfr-requirements/observability-requirements.md` (`observability-requirements.md`), `nfr-requirements/tech-stack-decisions.md` (`tech-stack-decisions.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

## 1. Arquitetura de Acessibilidade WCAG 2.1 AA no Frontend (`NFR5.1`)

- **Tripla Codificação Visual e Semântica:** O `WebReviewStudioComponent` renderiza cada caixa delimitadora com atributos `data-tier`, estilo de borda distinto (`solid`, `dashed`, `double`), cor de alto contraste ($\ge 4{,}5:1$) e badge textual (`OK`, `!`, `+`), além de `aria-label` descritivo e regiões `aria-live="polite"` para anunciar alterações na contagem auditada (`NFR5.1`).
- **Gerenciador de Atalhos de Teclado:** Listener acessível para `ArrowDown`/`ArrowUp` (navegar entre detecções duvidosas), `Space` (confirmar detecção), `Delete` (remover falso positivo) e `KeyN` (adicionar falso negativo).

---

## 2. Telemetria de IA, Logs Estruturados e Health Check (`NFR5.2`)

- **Endpoint de Saúde e Métricas Operacionais (`GET /api/v1/health` e `GET /api/v1/models/active`):**
  - Expõe status operacional do banco, diretório do *Golden Dataset*, versão ativa do modelo, acurácia de validação vigente e total de amostras *Human-in-the-Loop* acumuladas (`NFR5.2`).
- **Auditoria Completa de Inferência e HITL:** Cada `DetectionRun` persiste `processingTimeMs`, `rawCount`, `highConfidenceCount`, `uncertainCount` e `avgConfidence`, permitindo monitorar continuamente o *drift* do modelo em campo.
