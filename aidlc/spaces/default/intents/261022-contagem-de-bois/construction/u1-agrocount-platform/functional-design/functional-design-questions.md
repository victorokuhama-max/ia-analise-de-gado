# Especificação Funcional — Perguntas de Alinhamento (Functional Design — `u1-agrocount-platform`)

Elaborado a partir de `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `user-stories/stories.md` (`stories.md`), `requirements-analysis/requirements.md` (`requirements.md`), `domain-design/components.md` (`components.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

---

## Question 1: Regras de Negócio para Fatiamento SAHI, Rastreamento ByteTrack, Golden Dataset e Trava de Fine-Tuning

Como devemos formalizar as regras de negócio (`BR1.1`–`BR6.1`) e as transições de estado da vistoria em `u1-agrocount-platform`?

A. **(Recommended)** **Modelo de Regras Determinísticas `BR1.1` a `BR6.1` com Validação Pré-GPU, Limiares de Confiança (`>= 0.75` vs. `0.25–0.74`), Conversão YOLO Idempotente e Trava Automática de Não-Regressão (`>= 95%`)** — Formalizar as 10 entidades de `components.md` com restrições completas em `entities.md`, as regras `BR1.1`–`BR6.1` em `rules.md` cobrindo 100% dos 19 critérios de aceite (`AC1.1.1` a `AC6.1.1`) de `stories.md` e a máquina de estados da vistoria (`pending -> processing -> needs_review -> reviewed` ou `failed`) em `functional-spec.md`.
B. **Regras Informais sem Limiares Quantitativos** — Deixar os limiares de confiança e tamanho de arquivo abertos para decisão em tempo de execução.
X. Other (please specify)

[Answer]: A
