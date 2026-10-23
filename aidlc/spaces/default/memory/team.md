# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.

## Way of Working

Adotamos desenvolvimento **trunk-based** com branch base `main` e alvo de integração `main`. Cada unidade/entrega (*Bolt*) é integrada na `main` via **squash-merge** como um commit único identificado pelo slug da entrega, mantendo o histórico da `main` linear e rastreável às entregas planejadas [Q1].

## Walking Skeleton

Seguimos a postura de **walking skeleton** quando aplicável ao escopo: a primeira Unidade construída representa a menor fatia funcional integrada de ponta a ponta (ingestão de mídia de drone $\rightarrow$ contagem por visão computacional com triagem de confiança $\rightarrow$ revisão *Human-in-the-Loop* na interface web), verificada de ponta a ponta antes das unidades complementares [Q2].

## Testing Posture

Tratamos testes automatizados como entregável de primeira classe em cada unidade construída:
- **Methodology**: test-after
- **Methodology evidence**: Afirmado na entrevista de práticas (`practices-discovery-questions.md` [Q3]) a partir do padrão organizacional de `aidlc/spaces/default/memory/org.md` para o escopo `mvp`.
- **Ordering**: Implementar cada camada testável aplicável (pipeline de visão computacional / *Human-in-the-Loop* e serviços/interface web) e, em seguida, escrever e executar os testes automatizados daquela camada antes de concluir a unidade.
- **Cobertura e estratégia (`mvp`):** Piso mínimo de **80% de cobertura de linhas** (*line coverage*) verificado pela suíte automatizada antes do merge, cobrindo testes unitários e de integração dos fluxos de contagem por IA, captura do *Golden Dataset* (*Human-in-the-Loop*) e exportação de laudos [Q3].

## Guard Policy

<!-- Affirmed by the team. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless project.md or the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

Realizamos deploy em ambiente de homologação/demonstração no ecossistema **Google Cloud Platform (GCP)** (Cloud Run com suporte a aceleração gráfica sob demanda, Cloud Storage e Firebase/Firestore) a cada integração na `main`, mantendo a promoção para produção sob aprovação explícita do líder do projeto [Q4].

## Code Style

Seguimos as convenções idiomáticas e configurações de ferramentas na raiz do repositório:
- **Python (Motor de Visão Computacional YOLO + SAHI + ByteTrack e Pipeline *Human-in-the-Loop*):** `snake_case` para funções/variáveis, `PascalCase` para classes, tipagem estática (`typing` / Pydantic), formatação e linting via `ruff` / `black` e testes via `pytest` [Q5].
- **TypeScript / React (Aplicação Web e Estúdio de Revisão *Human-in-the-Loop*):** `camelCase` para variáveis/funções, `PascalCase` para componentes/tipos, linting e formatação via `ESLint` / `Prettier` e testes via `Vitest` [Q5].
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
