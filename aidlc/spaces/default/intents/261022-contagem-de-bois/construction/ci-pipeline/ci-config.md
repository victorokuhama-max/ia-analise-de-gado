# Configuração do Pipeline de Integração Contínua (`ci-config`) — AgroCount IA (`u1-agrocount-platform`)

## Summary

Este documento especifica a arquitetura e a configuração do pipeline de Integração Contínua (`.github/workflows/ci.yml`) para a unidade `u1-agrocount-platform` (`U1`), integrando as saídas de geração de código (`code-summary.md`) e os resultados verificados de build e testes (`build-and-test-summary.md` e `test-results.md`).

## 1. Estratégia de Branches e Gatilhos (*Triggers*)

Seguindo a prática afirmada pela equipe em `aidlc/spaces/default/memory/team.md` (*trunk-based development* com branch principal `main` e *squash-merge*):
- **`pull_request` para `main`:** Executa obrigatoriamente os jobs de compilação sintática, testes unitários/integração por camada, *gate* de cobertura de linhas ($\ge 80\%$) e build de verificação do container Docker.
- **`push` na `main`:** Executa toda a suíte de validação (`bash scripts/verify.sh`) e prepara a imagem container imutável (`agrocount-platform:<git-sha>`) para homologação no Google Cloud Run (`southamerica-east1`).

## 2. Etapas do Workflow (`.github/workflows/ci.yml`)

| Etapa (*Step*) | Comando Executado | Artefato / Referência Upstream | Critério de Bloqueio |
|---|---|---|---|
| **1. Checkout & Setup Python 3.11+** | `actions/setup-python@v5` (`python-version: "3.11"`) | `code-summary.md` (`pyproject.toml`) | Falha se o ambiente Python não inicializar |
| **2. Bytecode & Import Verification** | `PYTHONPATH=src python3 -m compileall -q src/ tests/ scripts/` | `build-instructions.md` (`test-results.md`) | Qualquer erro de sintaxe ou importação (`exit != 0`) |
| **3. Unit, Integration & Coverage Gate ($\ge 80\%$)** | `bash scripts/verify.sh` | `build-and-test-summary.md` (`TGT-COV-80`, `TGT-VOL-STD`, `TGT-CI-MERGE`) | Qualquer teste reprovado ou cobertura de linhas $< 80,0\%$ em `src/agrocount/` |
| **4. Container Image Build Verification** | `docker build -t agrocount-platform:${GITHUB_SHA} .` | `Dockerfile` (`NFR3.1`) | Falha na construção multi-stage ou execução com usuário não-root |

## 3. Repositório de Artefatos e Versionamento

- **Google Artifact Registry (`southamerica-east1`):** `southamerica-east1-docker.pkg.dev/<PROJECT_ID>/agrocount-repo/agrocount-platform:<git-sha>`
- **Artefatos de Modelos e *Golden Dataset* (`gs://agrocount-storage`):** Versionados de forma imutável sob `models/yolo11m-agro-v1.x/best.pt` e `golden-dataset/{sample_id}/{labels.txt,metadata.json}`.
