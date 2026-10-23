# Checklist de Conformidade de Acessibilidade (Accessibility Checklist — WCAG 2.1 Level AA)

Verificação de acessibilidade das 4 telas e dos 5 componentes definidos em `mockups.md`, `interaction-spec.md` e `design-system-mapping.md`, rastreada a `rough-mockups/wireframes.md` (`wireframes.md`), `rough-mockups/user-flow.md` (`user-flow.md`), `user-stories/stories.md` (`stories.md`), `requirements-analysis/requirements.md` (`requirements.md`, especialmente `NFR5`) e `practices-discovery/team-practices.md` (`team-practices.md`).

## 1. Perceptível (Perceivable)

- [x] **1.1.1 Conteúdo Não Textual (Level A):** O `CattleReviewCanvas` expõe texto alternativo dinâmico e lista estruturada de todas as detecções (`high_confidence`, `uncertain`, `manual_added`) com ID, confiança e status.
- [x] **1.3.1 Informações e Relações (Level A):** Todas as 4 telas utilizam landmarks semânticos (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`), hierarquia estrita `h1` $\rightarrow$ `h2` $\rightarrow$ `h3` e tabelas com `<th scope="col">`.
- [x] **1.4.1 Uso de Cor (Level A):** Nenhuma informação no Estúdio de Revisão Visual depende exclusivamente de cor (`FR4.1`, `NFR5`):
  - **Alta Confiança ($\ge 0{,}75$):** Cor Verde (`#15803D`) + **Borda Sólida** + **Selo `[OK]`**.
  - **Duvidosa ($0{,}25\text{–}0{,}74$):** Cor Âmbar (`#D97706`) + **Borda Tracejada** + **Selo `[!]`**.
  - **Adicionada Manualmente (`+FN`):** Cor Azul (`#1D4ED8`) + **Borda Dupla** + **Selo `[+]`**.
- [x] **1.4.3 Contraste Mínimo (Level AA):** Todos os textos possuem contraste $\ge 4{,}5:1$ e elementos gráficos de UI possuem contraste $\ge 3{,}0:1$ (`design-system-mapping.md`).
- [x] **1.4.10 Reflow / Responsividade (Level AA):** Layout adapta-se sem perda de funcionalidade de `320px` (mobile) até `1440px+` (desktop).

---

## 2. Operável (Operable) e Compreensível / Robusto (Understandable & Robust)

- [x] **2.1.1 Teclado (Level A):** Todas as ações do fluxo de vistoria e revisão *Human-in-the-Loop* são operáveis exclusivamente por teclado:
  - `Tab` / `Shift+Tab`: navegação entre regiões, filtros, fila de triagem e botões.
  - `Setas`: alternam entre as detecções duvidosas (`uncertain`) no `CattleReviewCanvas` (`FR4.2`).
  - `Espaço` / `Enter`: confirma a detecção duvidosa selecionada.
  - `Delete` / `Backspace`: remove falso positivo (`-FP`).
  - `N`: ativa o modo de adição de falso negativo (`+FN`).
- [x] **2.4.1 Ignorar Blocos (Level A):** Link `[Skip to main content]` presente como primeiro elemento focável em todas as telas.
- [x] **2.4.7 Foco Visível (Level AA):** Indicador de foco `2px solid #1D4ED8` com `offset: 2px` em todos os elementos interativos.
- [x] **2.5.5 Tamanho do Alvo em Tablet/Touch:** Botões de revisão e triagem possuem área clicável mínima de $48\times 48\text{px}$ no breakpoint tablet (`768px–1024px`).
- [x] **3.3.1 e 3.3.3 Identificação e Sugestão de Erro (Level A/AA):** O `DroneMediaUploader` anuncia erros de tamanho (`> 500 MB`) ou formato não suportado via `role="alert"` indicando exatamente como corrigir sem apagar os campos já preenchidos (`FR2.2`).
- [x] **4.1.3 Mensagens de Status (Level AA):** Recálculo do contador consolidado de bois, salvamento no *Golden Dataset* e conclusão do *fine-tuning* utilizam regiões `aria-live="polite"` / `role="status"`.
