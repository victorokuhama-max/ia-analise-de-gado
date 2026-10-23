# Especificação de Contratos de Integração e API — Perguntas de Alinhamento (Contract Design)

Elaborado a partir de `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-dependency.md` (`unit-of-work-dependency.md`), `domain-design/components.md` (`components.md`) e `requirements-analysis/requirements.md` (`requirements.md`).

## Contexto das Fronteiras de Contrato

A unidade `U1` (`u1-agrocount-platform`) expõe uma superfície pública HTTP/REST consumida pelo cliente web e clientes externos, além do contrato de armazenamento e dados de treinamento *Human-in-the-Loop* no Google Cloud Storage (*Golden Dataset*).

---

## Question 1: Mecanismo de Contrato, Versionamento e Semântica de Erros/Idempotência

Qual padrão de contrato formal devemos adotar para a API de `u1-agrocount-platform` e para o manifesto do *Golden Dataset*?

A. **(Recommended)** **OpenAPI 3.1 REST/JSON Versionado (`/api/v1/...`) com Cabeçalho `Idempotency-Key` + Contrato de Schema do Golden Dataset (YOLO `.txt` + Provenance JSON)** — Definir contrato síncrono OpenAPI 3.1 sob propriedade de `u1-agrocount-platform` cobrindo Fazendas/Piquetes (`/api/v1/farms`), Vistorias e Inferência (`/api/v1/inspections`), Revisão *Human-in-the-Loop* (`/api/v1/inspections/{id}/hitl-review`), Evolução/Fine-Tuning do Modelo (`/api/v1/models/active`, `/api/v1/models/fine-tune`) e Exportação de Laudos (`/api/v1/inspections/{id}/report`), com suporte a `Idempotency-Key` (`NFR4`), evolução compatível aditiva e respostas de erro padronizadas (`code`, `message`, `details`).
B. **Endpoints sem Versionamento e sem Chave de Idempotência** — Expor rotas sem prefixo `/api/v1` e sem proteção contra cliques duplos.
C. **Protocolo Exclusivamente Binário (gRPC Puro no Navegador)** — Exigir proxy gRPC-Web para todas as chamadas de formulário.
X. Other (please specify)

[Answer]: A
