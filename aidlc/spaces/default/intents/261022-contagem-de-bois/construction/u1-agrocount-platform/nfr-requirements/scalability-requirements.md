# Requisitos de Escalabilidade e Eficiência de Custos (Scalability Requirements — `u1-agrocount-platform`)

Elaborado a partir de `functional-design/functional-spec.md` (`functional-spec.md`), `functional-design/rules.md` (`rules.md`), `requirements-analysis/requirements.md` (`requirements.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `nfr-requirements-questions.md` [Q1].

## Sub-Requisitos de Escalabilidade Sob Demanda (`NFR3.*`)

| ID | Requisito Pai (`requirements.md`) | Especificação Quantitativa | Regra Relacionada (`rules.md`) |
|---|---|---|---|
| **NFR3.1** | `NFR3` | Os serviços de inferência de visão computacional e de *fine-tuning* na GCP devem operar com configuração `min-instances = 0` (*scale-to-zero*), reduzindo o custo de GPU para **US$ 0,00/hora** sempre que não houver vistorias ou treinamentos em execução. | `BR3.1`, `BR3.2`, `BR5.2` |
| **NFR3.2** | `NFR3` | A aplicação deve suportar o crescimento contínuo do *Golden Dataset* (de dezenas a $10.000+$ amostras corrigidas) e listagens paginadas de vistorias sem degradação da latência $p95 < 500\text{ms}$. | `BR1.3`, `BR5.1`, `BR5.2` |

---

## Projeção de Carga e Gatilhos de Escalonamento

- **Volume Inicial do MVP:** 10 a 200 vistorias aéreas por mês (consultorias agropecuárias e auditorias de rebanho).
- **Gatilho de Escalonamento Horizontal:** No Cloud Run, uma nova instância é provisionada sob demanda quando há requisição de inferência ou *fine-tuning* ativa, encerrando-se automaticamente após janela de ociosidade configurada (`300s`).
