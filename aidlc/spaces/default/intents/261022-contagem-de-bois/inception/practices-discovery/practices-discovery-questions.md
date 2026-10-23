# Practices Discovery — Perguntas sobre Práticas da Equipe

## Q1. [Engenharia de Release] Como organizamos branches e merges no Git (Way of Working)?
A. (Recomendado) Desenvolvimento trunk-based na branch `main`, com squash-merge por entrega (Bolt) mantendo histórico linear
B. GitFlow com branches `develop`, `release/*` e `hotfix/*` de longa duração
C. Branches por ambiente (`dev`, `staging`, `prod`)
X. Other (please specify)

[Answer]: A

## Q2. [Arquitetura e Entrega] Devemos construir primeiro uma fatia fina de ponta a ponta (Walking Skeleton)? Um walking skeleton é uma versão mínima que atravessa todas as camadas do sistema para provar que as peças se conectam antes das funcionalidades completas entrarem.
A. (Recomendado) Sim — validar primeiro a fatia mínima integrada (upload -> inferência YOLO/HITL -> visualização web) antes de expandir as demais unidades
B. Não — construir cada camada isoladamente sem validar integração inicial
X. Other (please specify)

[Answer]: A

## Q3. [Qualidade e Testes] Qual postura e ordem de testes devemos adotar (Testing Posture)?
A. (Recomendado) `test-after` — implementar cada camada testável (motor de visão computacional / ciclo HITL, API backend e componentes web) e em seguida escrever e executar os testes automatizados daquela camada, garantindo piso mínimo de 80% de cobertura de linhas no escopo `mvp`
B. TDD estrito (`tdd`) — escrever todos os testes falhando antes de qualquer linha de código
C. BDD (`bdd`) — escrever cenários Gherkin executáveis antes da implementação
X. Other (please specify)

[Answer]: A

## Q4. [Operação e Deploy] Como funciona o fluxo de implantação na GCP (Deployment)?
A. (Recomendado) Deploy automatizado em ambiente de homologação/demonstração na GCP (Cloud Run / Cloud Storage / Firestore) a cada merge na `main`, com promoção para produção mediante aprovação humana
B. Deploy 100% manual via upload de arquivos avulsos
X. Other (please specify)

[Answer]: A

## Q5. [Desenvolvimento] Quais padrões de formatação e estilo de código devemos seguir (Code Style)?
A. (Recomendado) Idiomático por linguagem com linters/formatadores de projeto: Python (`snake_case`, Ruff/Black/pytest) para o serviço de visão computacional e ciclo *Human-in-the-Loop*, e TypeScript/React (`camelCase`/`PascalCase`, ESLint/Prettier/Vitest) para a aplicação web
B. Sem linter ou formatador automatizado
X. Other (please specify)

[Answer]: A
