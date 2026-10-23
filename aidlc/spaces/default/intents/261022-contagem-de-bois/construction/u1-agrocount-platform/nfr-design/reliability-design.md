# Projeto de Confiabilidade, Idempotência e Resiliência (Reliability Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-requirements/performance-requirements.md` (`performance-requirements.md`), `nfr-requirements/security-requirements.md` (`security-requirements.md`), `nfr-requirements/scalability-requirements.md` (`scalability-requirements.md`), `nfr-requirements/reliability-requirements.md` (`reliability-requirements.md`), `nfr-requirements/observability-requirements.md` (`observability-requirements.md`), `nfr-requirements/tech-stack-decisions.md` (`tech-stack-decisions.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

## 1. Deduplicação Atômica por Chave de Idempotência (`NFR4.1`)

- **Idempotência na Criação de Vistorias:** A tabela `inspections` possui restrição `UNIQUE(idempotency_key)`. Quando uma requisição `POST /api/v1/inspections` traz uma chave já registrada, o serviço retorna imediatamente a vistoria existente sem reexecutar a inferência (`NFR4.1`).
- **Idempotência no Ciclo Human-in-the-Loop:** A tabela `hitl_batches` possui restrição `UNIQUE(idempotency_key)`. Se o auditor clicar duas vezes em `Confirmar Contagem e Alimentar Golden Dataset` com a mesma chave (ou se houver retentativa automática de rede), o `HitlActiveLearningComponent` retorna o mesmo `HitlCorrectionBatch` e `GoldenDatasetSample` sem duplicar arquivos no *Golden Dataset* (`NFR4.1`).

---

## 2. Promoção Transacional de Modelo com Trava Contra Regressão (`NFR1.2`, `NFR4.2`)

- **Shadow Evaluation & Atomic Pointer Swap:**
  - Durante o *fine-tuning*, o modelo ativo (`status = active`) permanece intocado atendendo às vistorias em produção (`NFR4.2`).
  - Somente quando o avaliador comprova $\text{validation\_accuracy}_{\text{candidate}} \ge 0{,}95$ **e** $\text{validation\_accuracy}_{\text{candidate}} \ge \text{validation\_accuracy}_{\text{active}}$ (`NFR1.2`), uma única transação atômica promove o candidato para `active` e marca o anterior como `archived`.
  - Caso contrário, o candidato é gravado como `rejected_regression` e o modelo ativo nunca sofre degradação.
