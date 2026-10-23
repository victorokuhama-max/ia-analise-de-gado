# Personas do Sistema (User Personas)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `practices-discovery/team-practices.md` (`team-practices.md`) e `user-stories-questions.md`.

## Perfil das Personas Principais

### P1: Lucas Mendes — Consultor e Auditor Agropecuário (Persona Primária)
- **Papel:** Engenheiro Agrônomo / Zootecnista em consultoria pecuária e auditoria rural.
- **Contexto de Uso:** Realiza vistorias presenciais em fazendas de gado de corte com drone DJI/similar e retorna ao escritório ou sede da fazenda com dezenas de fotos 4K (`.jpg`/`.png`) e vídeos curtos (`.mp4`/`.mov`) por piquete.
- **Objetivos:**
  - Obter a contagem rápida e auditável de cabeças de gado por piquete (`FR1`, `FR2`, `FR3`).
  - Revisar apenas as detecções duvidosas (`uncertain` entre `0.25` e `0.74`) e corrigir eventuais oclusões sob árvores ou falsos positivos com poucos cliques no Estúdio de Revisão Visual (`FR4`).
  - Exportar laudos oficiais em PDF e CSV com memória de cálculo auditada (`FR6`).
- **Dores (Pain Points):**
  - Contagem manual em tela leva horas por fazenda e sofre com fadiga visual e dupla contagem de animais em movimento.
  - Ferramentas genéricas de IA erram em gado adensado ou sombreado e não permitem corrigir o resultado nem ensinar o modelo.

### P2: Dra. Helena Costa — Gestora Técnica e Curadora de IA (Persona Secundária)
- **Papel:** Líder Técnica / Engenheira de Machine Learning da operação de consultoria.
- **Contexto de Uso:** Monitora a qualidade do modelo de visão computacional no Google Cloud Platform (GCP), acompanha o acúmulo de amostras corrigidas pelos auditores no *Golden Dataset* e dispara ciclos de *fine-tuning* sob demanda.
- **Objetivos:**
  - Garantir que cada correção *Human-in-the-Loop* dos auditores gere automaticamente rótulos YOLO normalizados e rastreáveis no *Golden Dataset* (`FR5.1`).
  - Acionar o *fine-tuning* sob demanda na GCP sem manter GPUs ociosas ligadas (`FR5.2`, `NFR3`).
  - Assegurar que um novo modelo candidato só substitua o modelo em produção se atingir acurácia $\ge 95\%$ e não regredir (`FR5.3`, `NFR1`).
- **Dores (Pain Points):**
  - Alto custo de anotação manual externa para treinar modelos YOLO em novos biomas, pelagens (Nelore, Angus, Girolando) e épocas do ano (seca vs. águas).
  - Risco de promover um modelo retreinado que piore a acurácia em cenários já dominados.

### P3: Roberto Almeida — Gestor de Fazenda / Pecuarista (Persona Consumidora)
- **Papel:** Proprietário rural, gerente de fazenda ou analista de crédito/seguro rural.
- **Contexto de Uso:** Recebe os relatórios de vistoria emitidos pela consultoria para conferência de estoque bovino, manejo de pastagem e comprovação patrimonial.
- **Objetivos:**
  - Receber laudos claros em PDF e planilhas CSV com a imagem demarcada do rebanho, contagem bruta da IA, ajustes do auditor e contagem final auditada (`FR6.1`).

---

## Relacionamento e Priorização de Personas

1. **Prioridade 1 (Foco central de UX e fluxo diário):** **P1 — Consultor e Auditor Agropecuário (`Lucas Mendes`)** — conduz 90% das interações na plataforma web (cadastro de fazenda/piquete, upload, revisão *Human-in-the-Loop* e exportação de laudos).
2. **Prioridade 2 (Governança de IA e *Active Learning*):** **P2 — Gestora Técnica e Curadora de IA (`Dra. Helena Costa`)** — opera o Painel de Evolução do Modelo IA e governa o ciclo de *fine-tuning* no GCP.
3. **Prioridade 3 (Consumo de artefatos exportados):** **P3 — Gestor de Fazenda (`Roberto Almeida`)** — consome os relatórios PDF/CSV gerados pelo sistema.
