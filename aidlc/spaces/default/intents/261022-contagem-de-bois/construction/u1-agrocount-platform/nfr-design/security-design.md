# Projeto de Segurança e Qualidade de Código (Security Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-requirements/performance-requirements.md` (`performance-requirements.md`), `nfr-requirements/security-requirements.md` (`security-requirements.md`), `nfr-requirements/scalability-requirements.md` (`scalability-requirements.md`), `nfr-requirements/reliability-requirements.md` (`reliability-requirements.md`), `nfr-requirements/observability-requirements.md` (`observability-requirements.md`), `nfr-requirements/tech-stack-decisions.md` (`tech-stack-decisions.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

## 1. Defesa em Profundidade, Sanitização de Entrada e Gestão de Segredos (`NFR6.1`)

- **Configuração via Ambiente (Zero Hardcoded Secrets):** Caminhos de armazenamento, diretórios do *Golden Dataset*, porta HTTP e credenciais de nuvem são lidos exclusivamente de variáveis de ambiente (`AGROCOUNT_DB_PATH`, `AGROCOUNT_STORAGE_DIR`, `AGROCOUNT_PORT`) com defaults locais seguros para desenvolvimento/testes (`NFR6.1`).
- **Sanitização Estrita de Upload e Coordenadas YOLO:**
  - Nomes de arquivos enviados passam por normalização `basename` e validação de lista branca de extensões (`.jpg`, `.jpeg`, `.png`, `.mp4`, `.mov`), bloqueando qualquer tentativa de *path traversal* (`../`).
  - Todas as coordenadas de *bounding boxes* (`x_center, y_center, width, height`) são validadas matematicamente no intervalo $[0{,}0, 1{,}0]$ antes de serem gravadas no `.txt` do *Golden Dataset*.

---

## 2. Verificação Automatizada de Qualidade e Cobertura $\ge 80\%$ (`NFR6.2`)

- **Gate Determinístico de Cobertura:** O script de verificação (`scripts/verify.sh`) executa a suíte completa de testes unitários e de integração e calcula a cobertura de linhas executadas sobre os módulos de produção, falhando com código diferente de zero caso a cobertura fique abaixo de **80,0%** (`NFR6.2`).
- **Integridade de Laudos Auditados:** Cada laudo PDF/CSV exportado recebe um checksum `SHA-256` calculado sobre seu conteúdo, garantindo não-repúdio e rastreabilidade ao `auditor_id`.
