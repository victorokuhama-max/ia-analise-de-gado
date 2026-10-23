# Plano de Decomposição em Unidades de Trabalho — Perguntas de Alinhamento (Units Generation)

Com base no catálogo de componentes em `domain-design/components.md` (`components.md`), nas decisões arquiteturais em `domain-design/decisions.md` (`decisions.md`), nos requisitos em `requirements-analysis/requirements.md` (`requirements.md`) e nas histórias de usuário em `user-stories/stories.md` (`stories.md`), definimos o agrupamento dos componentes em Unidades de Trabalho (*Units of Work*).

---

## Question 1: Estratégia de Fronteira e Granularidade das Unidades de Trabalho

Como você prefere agrupar os 4 componentes de domínio (`WebReviewStudioComponent`, `InspectionManagementComponent`, `HitlActiveLearningComponent` e `CattleVisionEngineComponent`) em unidades de construção e deploy para o MVP?

A. **(Recommended)** **Unidade Integrada Ponta a Ponta (`U1` / `u1-agrocount-platform`, `kind: service`)** — Empacotar os 4 componentes lógicos em uma única unidade de trabalho coesa e autocontida (`u1-agrocount-platform`), entregando em um único ciclo integrado o backend Python/FastAPI (Gestão de Fazendas/Vistorias + Motor de Visão YOLO+SAHI/ByteTrack + Ciclo *Human-in-the-Loop* / *Golden Dataset* / *Fine-Tuning*) e o Estúdio Web React/TypeScript, garantindo uma fatia funcional completa (*walking skeleton* integral) sem sobrecarga de orquestração multi-repositório no MVP.
B. **2 Unidades Separadas (`u1-backend-api` e `u2-frontend-ui`)** — Dividir a construção em duas unidades sequenciais, exigindo dois ciclos separados de design funcional, NFR e geração de código.
C. **4 Micro-Unidades Independentes (`u1` a `u4`, uma por componente)** — Criar quatro unidades independentes com múltiplos contratos inter-unidades.
X. Other (please specify)

[Answer]: A
