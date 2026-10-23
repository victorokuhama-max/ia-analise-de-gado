# Mockups Refinados e Especificação de Interação — Perguntas de Alinhamento (Refined Mockups)

Com base em `rough-mockups/wireframes.md` (`wireframes.md`), `rough-mockups/user-flow.md` (`user-flow.md`), `user-stories/stories.md` (`stories.md`), `requirements-analysis/requirements.md` (`requirements.md`) e `practices-discovery/team-practices.md` (`team-practices.md`), definimos as escolhas de especificação visual e de componentes para a etapa de **Refined Mockups**.

---

## Question 1: Padrão de Componentes, Tokens Visuais e Interação no Estúdio Human-in-the-Loop

Qual especificação de design system, estados de tela e comportamento interativo devemos adotar nos mockups refinados?

A. **(Recommended)** **Design System AgroCount IA (Alto Contraste Rural WCAG 2.1 AA) + Estúdio Split-Screen com Canvas Interativo SVG/HTML5** — Adotar paleta semântica de alto contraste (Verde Floresta `#15803D` para ações primárias e marcações `high_confidence` com borda sólida + selo `OK`, Âmbar `#D97706` para `uncertain` com borda tracejada + selo `!`, Azul `#1D4ED8` para adições manuais `+FN` com borda dupla + selo `+`, Vermelho `#B91C1C` para exclusões/erros), tipografia `Inter` + `JetBrains Mono` para contadores/métricas, especificando os 5 componentes principais (`InspectionDashboardTable`, `DroneMediaUploader`, `CattleReviewCanvas`, `HitlTriageSidebar`, `ModelEvolutionPanel`) com todos os 7 estados (`default`, `hover`, `focus`, `disabled`, `loading`, `error`, `empty`), breakpoints responsivos (`<768px`, `768–1024px`, `>1024px`) e checklist completo WCAG 2.1 AA.
B. **Layout Minimalista Somente Tabela sem Canvas Interativo** — Substituir o canvas visual por edição numérica simples em tabela.
C. **Tema Escuro Exclusivo para Todas as Telas** — Forçar tema escuro único sem versão clara de alto contraste para leitura de laudos.
X. Other (please specify)

[Answer]: A
