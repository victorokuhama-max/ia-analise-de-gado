# Alocação de Equipe por Entrega (Team Allocation)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`), `refined-mockups/mockups.md` (`mockups.md`), `domain-design/components.md` (`components.md`), `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-dependency.md` (`unit-of-work-dependency.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `practices-discovery/team-practices.md` (`team-practices.md`).

## Atribuição de Bolts (Bolt-to-Mob Assignment)

No escopo `mvp`, em que a etapa `team-formation` é omitida por padrão, cada **Bolt** (uma passagem de construção sobre uma unidade de trabalho que resulta em software funcionando) é atribuído a um **mob** (grupo colaborativo focado na mesma entrega) conduzido integralmente pelo **`aidlc-developer-agent`** com validação do **`aidlc-quality-agent`**.

| Bolt | Unidade de Trabalho (`unit-of-work.md`) | Responsável pela Construção | Modo de Execução | Branch / Integração (`team-practices.md`) |
|---|---|---|---|---|
| **Bolt 1 (`bolt-1-agrocount-platform`)** | `U1` (`u1-agrocount-platform`) | `aidlc-developer-agent` | Serial (`unit-major`) | Trunk-based (`main` com squash-merge) |

---

## Responsabilidades Técnicas na Execução do Bolt 1

- **Engenharia de Backend e Visão Computacional (`aidlc-developer-agent`):** Implementação dos módulos Python (`InspectionManagementComponent`, `CattleVisionEngineComponent`, `HitlActiveLearningComponent`), rotas FastAPI segundo o contrato OpenAPI 3.1 (`contract-summary.md`) e geração de relatórios PDF/CSV.
- **Engenharia de Frontend e Acessibilidade (`aidlc-developer-agent`):** Implementação do `WebReviewStudioComponent` seguindo os 4 mockups refinados (`mockups.md`) e conformidade WCAG 2.1 AA.
- **Verificação e Qualidade (`aidlc-developer-agent` + `aidlc-quality-agent`):** Execução da metodologia `test-after` com piso de 80% de cobertura de linhas (`team-practices.md`).
