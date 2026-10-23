# Requisitos de Confiabilidade e Idempotência (Reliability Requirements — `u1-agrocount-platform`)

Elaborado a partir de `functional-design/functional-spec.md` (`functional-spec.md`), `functional-design/rules.md` (`rules.md`), `requirements-analysis/requirements.md` (`requirements.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `nfr-requirements-questions.md` [Q1].

## Sub-Requisitos de Disponibilidade, Idempotência e Tolerância a Falhas (`NFR4.*`)

| ID | Requisito Pai (`requirements.md`) | Especificação Quantitativa | Regra Relacionada (`rules.md`) |
|---|---|---|---|
| **NFR4.1** | `NFR4` | Todas as operações de criação de vistoria (`POST /api/v1/inspections`) e confirmação de revisão *Human-in-the-Loop* (`POST /api/v1/inspections/{id}/hitl-review`) devem ser estritamente idempotentes via `Idempotency-Key`, garantindo **zero duplicações** de vistorias ou de amostras no *Golden Dataset* sob cliques duplos ou retentativas de rede. | `BR1.2`, `BR2.1`, `BR5.1` |
| **NFR4.2** | `NFR4` | O serviço deve manter disponibilidade operacional $\ge 99{,}0\%$ em horário comercial e preservar 100% da integridade do modelo ativo caso um job de *fine-tuning* falhe ou seja reprovado pela trava de regressão ($< 95\%$). | `BR5.3` |

---

## Estratégia de Degradação Graciosa e Recuperação

- **Isolamento de Falhas de Mídia (`BR2.2`):** Um arquivo corrompido ou fora do limite de 500 MB nunca afeta outras vistorias em andamento; retorna erro determinístico HTTP `400` e mantém o serviço saudável.
- **Rollback Automático de Modelo (`BR5.3`):** O ponteiro da versão ativa (`status = active`) só é alterado atomicamente após a validação completa do candidato atingir $\ge 95\%$ sem regressão.
