# Perguntas de Configuração do Pipeline de Integração Contínua (`ci-pipeline`)

## Summary

Este documento registra as decisões de configuração do pipeline de Integração Contínua (CI) e *Quality Gates* para a unidade `u1-agrocount-platform`, alinhadas às práticas de *trunk-based development* (`main`), piso mínimo de 80% de cobertura de linhas e deploy no ecossistema Google Cloud Platform (GCP).

## Questões e Respostas Registradas

### Question 1: Orquestrador de CI, Gates de Qualidade e Registro de Artefatos
Qual configuração de pipeline de CI, *quality gates* de bloqueio antes do merge na `main` e repositório de imagens deve ser adotada para a plataforma AgroCount IA (`u1-agrocount-platform`)?

- **A (Recommended):** GitHub Actions (`.github/workflows/ci.yml`) em estratégia *trunk-based* (`main`), executando compilação de bytecode (`python3 -m compileall`), suíte completa de testes unitários/integração e *gate* bloqueante de cobertura de linhas $\ge 80\%$ (`bash scripts/verify.sh`), além de validação do `Dockerfile` multi-stage para publicação no Google Artifact Registry (`southamerica-east1-docker.pkg.dev`).
- **B:** Google Cloud Build (`cloudbuild.yaml`) acionado exclusivamente em *tags* manuais de versão, sem execução automática em *Pull Requests*.
- **C:** Execução manual de testes locais sem workflow automatizado no repositório.

[Answer]: A (Selecionado conforme instrução do usuário: "Faça 1 em todos, não pergunte mais para mim, quero ele finalizado até a ponta")
