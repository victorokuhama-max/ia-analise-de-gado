# Evidências de Descoberta de Práticas (Practices Discovery Evidence)

## Sources Scanned

- **Tipo de projeto:** `greenfield` (confirmado em `aidlc/spaces/default/intents/261022-contagem-de-bois/aidlc-state.md`).
- **Fonte base de padrões organizacionais:** `aidlc/spaces/default/memory/org.md` (seções `Way of Working`, `Walking Skeleton`, `Testing Posture`, `Deployment` e `Code Style`).
- **Artefatos de Ideation consultados:**
  - `aidlc/spaces/default/intents/261022-contagem-de-bois/ideation/intent-capture/intent-statement.md`
  - `aidlc/spaces/default/intents/261022-contagem-de-bois/ideation/feasibility/feasibility-assessment.md`
  - `aidlc/spaces/default/intents/261022-contagem-de-bois/ideation/feasibility/constraint-register.md`
  - `aidlc/spaces/default/intents/261022-contagem-de-bois/ideation/scope-definition/scope-document.md`
  - `aidlc/spaces/default/intents/261022-contagem-de-bois/ideation/rough-mockups/wireframes.md`
- **Participação:** Execução *lead-only* (`aidlc-pipeline-deploy-agent`, sem agentes de suporte ativos pois `collaborators: off` no escopo `mvp`).

## Interview Decisions & Uncertainties

- **Decisões confirmadas (`practices-discovery-questions.md`):**
  - **Q1 (Way of Working):** Desenvolvimento trunk-based na branch `main` com squash-merge (`A`).
  - **Q2 (Walking Skeleton):** Validação prioritária de fatia fina integrada de ponta a ponta (`A`).
  - **Q3 (Testing Posture):** Metodologia `test-after` com piso de 80% de cobertura de linhas no escopo `mvp` (`A`).
  - **Q4 (Deployment):** Deploy em homologação na GCP sob demanda após merge e gate humano para produção (`A`).
  - **Q5 (Code Style):** Convenções idiomáticas Python (`snake_case`, Ruff/pytest) e TypeScript/React (`camelCase`/`PascalCase`, ESLint/Vitest) (`A`).
- **Incertezas pendentes:** Nenhuma incerteza pendente.
