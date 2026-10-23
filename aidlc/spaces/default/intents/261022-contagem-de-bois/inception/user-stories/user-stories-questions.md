# Plano de Histórias de Usuário — Perguntas de Alinhamento (User Stories Plan)

Com base em `requirements.md` e `team-practices.md`, estruturamos o plano de elaboração de Personas e Histórias de Usuário seguindo os critérios **INVEST** e priorização **MoSCoW**.

---

## Question 1: Granularidade das Personas e Organização das Histórias de Usuário

Como você prefere organizar as personas e o agrupamento das histórias de usuário para o MVP?

A. **(Recommended)** **3 Personas Principais + Agrupamento por Épico Funcional (6 Épicos `US1` a `US6` espelhando `FR1` a `FR6`)** — Definir **P1: Consultor/Auditor Agropecuário** (usuário principal do fluxo de vistoria, revisão *Human-in-the-Loop* e emissão de laudo), **P2: Gestor Técnico / Curador de IA** (responsável por acompanhar o *Golden Dataset* e acionar o *fine-tuning* sob demanda na GCP) e **P3: Gestor de Fazenda / Cliente Final** (consumidor do laudo auditado PDF/CSV), organizando as histórias nos épicos `US1` (Fazendas/Vistorias), `US2` (Upload/Ingestão), `US3` (Inferência YOLO+SAHI/ByteTrack), `US4` (Estúdio de Revisão Visual), `US5` (Ciclo *Human-in-the-Loop* e *Fine-Tuning*) e `US6` (Exportação de Laudos), todas com critérios de aceite testáveis no formato `Given / When / Then`.
B. **Persona Única Generalista + Lista Plana de Histórias** — Concentrar todas as histórias em um único perfil de "Usuário do Sistema" sem divisão por épicos.
C. **Múltiplas Sub-Personas Detalhadas por Região** — Criar variações regionais de personas antes do MVP.
X. Other (please specify)

[Answer]: A
