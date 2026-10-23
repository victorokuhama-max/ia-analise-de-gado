# Projeto Arquitetural de Requisitos Não Funcionais — Perguntas de Alinhamento (NFR Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-requirements/performance-requirements.md` (`performance-requirements.md`), `nfr-requirements/security-requirements.md` (`security-requirements.md`), `nfr-requirements/scalability-requirements.md` (`scalability-requirements.md`), `nfr-requirements/reliability-requirements.md` (`reliability-requirements.md`), `nfr-requirements/observability-requirements.md` (`observability-requirements.md`), `nfr-requirements/tech-stack-decisions.md` (`tech-stack-decisions.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

---

## Question 1: Padrões de Resiliência, Desempenho, Isolamento de Falhas e Governança do Golden Dataset

Qual arquitetura de padrões não funcionais devemos aplicar em `u1-agrocount-platform`?

A. **(Recommended)** **Isolamento de Domínio de Falha (API/CRUD vs. Inferência/Fine-Tuning) + Cache de Metadados + Deduplicação Atômica por `Idempotency-Key` + Trava Transacional de Promoção de Modelo ($\ge 95\%$)** — Implementar validação fail-fast na borda HTTP (`< 10ms`), fatiamento SAHI vetorizado e deduplicação IoU/ByteTrack, persistência atômica de chaves de idempotência (`NFR4.1`), troca atômica de ponteiro de versão ativa apenas após aprovação no gate de validação $\ge 95\%$ (`NFR1.2`, `NFR4.2`) e logs estruturados JSON com `request_id` / `inspection_id`.
B. **Execução sem Isolamento de Falhas e sem Deduplicação Atômica** — Processar todas as chamadas sem controle de idempotência ou proteção de estado do modelo ativo.
X. Other (please specify)

[Answer]: A
