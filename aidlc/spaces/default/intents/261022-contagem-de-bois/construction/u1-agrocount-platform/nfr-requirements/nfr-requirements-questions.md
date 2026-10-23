# Requisitos Não Funcionais — Perguntas de Alinhamento (NFR Requirements — `u1-agrocount-platform`)

Elaborado a partir de `functional-design/functional-spec.md` (`functional-spec.md`), `functional-design/rules.md` (`rules.md`), `requirements-analysis/requirements.md` (`requirements.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

---

## Question 1: Metas Quantitativas Detalhadas de Desempenho, Segurança, Escalabilidade, Confiabilidade, Observabilidade e Stack

Qual conjunto de metas quantitativas (`NFR1.1` a `NFR6.2`) e decisões de stack tecnológico devemos confirmar para `u1-agrocount-platform`?

A. **(Recommended)** **Metas Quantificáveis Alinhadas ao Escopo MVP (`NFR1.1`–`NFR6.2`) + Stack Python 3.13 / FastAPI / SQLite-Firestore / GCS / TypeScript-React** — Formalizar: `NFR1.1`/`NFR1.2` (acurácia $\ge 95\%$ e trava de não-regressão), `NFR2.1`/`NFR2.2` ($\le 5\text{s}$ foto 4K com SAHI, $\le 90\text{s}$ vídeo 3 min com ByteTrack, API $p95 < 500\text{ms}$), `NFR3.1`/`NFR3.2` (Cloud Run GPU *scale-to-zero* em ociosidade), `NFR4.1`/`NFR4.2` (disponibilidade $\ge 99{,}0\%$ e idempotência por `Idempotency-Key`), `NFR5.1`/`NFR5.2` (WCAG 2.1 AA, logs estruturados JSON e métricas SLI/SLO) e `NFR6.1`/`NFR6.2` (segurança de entrada, variáveis de ambiente sem segredos fixos e cobertura de testes $\ge 80\%$).
B. **Metas Qualitativas Genéricas** — Não fixar SLAs numéricos por sub-requisito.
X. Other (please specify)

[Answer]: A
