# Mapeamento de Design System e Tokens Visuais (Design System Mapping)

Elaborado a partir de `rough-mockups/wireframes.md` (`wireframes.md`), `rough-mockups/user-flow.md` (`user-flow.md`), `user-stories/stories.md` (`stories.md`), `requirements-analysis/requirements.md` (`requirements.md`), `practices-discovery/team-practices.md` (`team-practices.md`) e `refined-mockups-questions.md` [Q1].

## Tokens de Cores Semânticas e Contraste (WCAG 2.1 Level AA)

| Token CSS / Design | Valor Hex | Uso no Sistema (`mockups.md` / `interaction-spec.md`) | Razão de Contraste (sobre `#FFFFFF` ou fundo pareado) |
|---|---|---|---|
| `--color-bg-primary` | `#F8FAFC` | Fundo geral da aplicação web | — |
| `--color-surface` | `#FFFFFF` | Cartões, tabelas e painéis laterais | — |
| `--color-text-primary` | `#0F172A` | Títulos (`h1`–`h3`), contadores e texto principal | $17{,}8:1$ (AAA) |
| `--color-text-secondary` | `#334155` | Rótulos secundários, metadados de fazenda/piquete | $10{,}1:1$ (AAA) |
| `--color-primary-green` | `#15803D` | Botões primários e *bounding boxes* `high_confidence` ($\ge 0{,}75$) + selo `OK` | $5{,}1:1$ (AA) |
| `--color-warning-amber` | `#B45309` / `#D97706` | *Bounding boxes* `uncertain` ($0{,}25\text{–}0{,}74$) + borda tracejada + selo `!` | $5{,}0:1$ sobre `#FEF3C7` (AA) |
| `--color-manual-blue` | `#1D4ED8` | *Bounding boxes* adicionadas manualmente pelo auditor (`+FN`) + borda dupla + selo `+` e anel de foco | $6{,}7:1$ (AA) |
| `--color-danger-red` | `#B91C1C` | Remoção de falso positivo (`-FP`), alertas de erro de upload (`FR2.2`) e bloqueio de regressão | $6{,}4:1$ (AA) |

---

## Tipografia, Espaçamento e Grid Responsivo

- **Família Tipográfica Principal (`--font-sans`):** `'Inter', system-ui, -apple-system, sans-serif` — leitura limpa para formulários, tabelas e laudos.
- **Família Monoespaçada (`--font-mono`):** `'JetBrains Mono', monospace` — aplicada aos contadores de cabeças de gado, coordenadas YOLO (`x_center y_center width height`), IDs de rastreamento (`track_id`) e percentuais de acurácia (`96,4%`).
- **Escala Tipográfica:**
  - `h1`: `1.75rem` (`28px`), `font-weight: 700`, `line-height: 1.25`
  - `h2`: `1.25rem` (`20px`), `font-weight: 600`, `line-height: 1.35`
  - `h3`: `1.0rem` (`16px`), `font-weight: 600`, `line-height: 1.4`
  - `body`: `0.9375rem` (`15px`), `font-weight: 400`, `line-height: 1.5`
  - `kpi-counter`: `2.25rem` (`36px`), `font-weight: 800`, `--font-mono`
- **Sistema de Espaçamento (Base `4px` / `0.25rem`):** `4px` (`xs`), `8px` (`sm`), `16px` (`md`), `24px` (`lg`), `32px` (`xl`).
- **Breakpoints Responsivos (`wireframes.md`):**
  - `mobile`: `< 768px` (layout de 1 coluna, tabelas convertidas em cards)
  - `tablet`: `768px – 1024px` (alvos de toque $\ge 48\times 48\text{px}$, canvas `100%` acima do painel HITL)
  - `desktop`: `> 1024px` (layout *Split-Screen* `70%` Canvas / `30%` Painel HITL, largura máxima `1440px`).
