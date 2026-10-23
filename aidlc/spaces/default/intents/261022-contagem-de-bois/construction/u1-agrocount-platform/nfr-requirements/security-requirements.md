# Requisitos de Segurança e Governança (Security Requirements — `u1-agrocount-platform`)

Elaborado a partir de `functional-design/functional-spec.md` (`functional-spec.md`), `functional-design/rules.md` (`rules.md`), `requirements-analysis/requirements.md` (`requirements.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `nfr-requirements-questions.md` [Q1].

## Sub-Requisitos de Segurança, Validação e Qualidade de Código (`NFR6.*`)

| ID | Requisito Pai (`requirements.md`) | Especificação Quantitativa e Técnica | Regra Relacionada (`rules.md`) |
|---|---|---|---|
| **NFR6.1** | `NFR6` | Zero segredos, chaves de API ou credenciais GCP fixos no código-fonte (*hardcoded secrets = 0*); toda configuração sensível deve vir de variáveis de ambiente validadas na inicialização, e todas as entradas de upload/JSON devem ser sanitizadas contra *path traversal* e payloads malformados. | `BR1.1`, `BR2.2` |
| **NFR6.2** | `NFR6` | A suíte de testes automatizados (`test-after`) deve comprovar cobertura de linhas $\ge 80\%$ (*line coverage*) em todos os módulos de domínio, visão computacional, *Human-in-the-Loop* e API antes da integração na branch `main`. | `BR1.1`, `BR1.2`, `BR5.1`, `BR5.3`, `BR6.1` |

---

## Modelo de Controle de Acesso e Proteção de Dados

- **Autenticação e Rastreabilidade de Auditoria:** Toda revisão *Human-in-the-Loop* (`HitlCorrectionBatch`) e todo laudo exportado (`AuditReport`) registram obrigatoriamente o `auditor_id` responsável e o hash `SHA-256` de integridade.
- **Proteção de Armazenamento (`Golden Dataset`):** Os arquivos de rótulos YOLO (`.txt`) e manifestos de proveniência (`.json`) são gravados apenas após validação estrita de coordenadas normalizadas em $[0{,}0, 1{,}0]$, prevenindo injeção de dados corrompidos no pipeline de *Active Learning* (`BR5.1`).
