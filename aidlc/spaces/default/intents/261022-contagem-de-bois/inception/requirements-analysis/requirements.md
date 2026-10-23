# Especificação de Requisitos (Requirements Analysis)

Elaborado a partir de `intent-capture/intent-statement.md` (`intent-statement.md`), `scope-definition/scope-document.md` (`scope-document.md`), `practices-discovery/team-practices.md` (`team-practices.md`) e `requirements-analysis-questions.md`.

## Sources

- [desc] Initial description: "criar uma aplicação com IA de contagem de bois"
- [scope] Workflow-selected scope: `mvp`.
- [Q1] Resposta à pergunta Q1 em `requirements-analysis-questions.md`: `A` — Formatos `.jpg/.jpeg/.png` (até 50 MB) e `.mp4/.mov` (até 5 min / 500 MB) com validação explícita.
- [Q2] Resposta à pergunta Q2 em `requirements-analysis-questions.md`: `A` — Classificação por faixa de confiança (`>= 0.75` alta confiança vs. `0.25–0.74` duvidosa) e exportação automática de correções humanas para o *Golden Dataset* no formato YOLO na GCP.
- [Q3] Resposta à pergunta Q3 em `requirements-analysis-questions.md`: `A` — Metas quantificáveis de acurácia ($\ge 95\%$), latência ($\le 5\text{s}$ foto / $\le 90\text{s}$ vídeo de 3 min), API p95 $< 500\text{ms}$, disponibilidade $\ge 99{,}0\%$ e cobertura de testes $\ge 80\%$.

## Análise de Intenção (Intent Analysis)

Conforme definido em `intent-statement.md` e delimitado em `scope-document.md`, o sistema tem como objetivo permitir que consultorias agropecuárias, técnicos e auditores realizem inventários rápidos e auditáveis de rebanhos bovinos em pastos e piquetes a partir de fotos e vídeos aéreos de drones, atingindo acurácia igual ou superior a 95% e aperfeiçoando continuamente o modelo de visão computacional por meio de um ciclo **Human-in-the-Loop (Active Learning)** executado sob demanda no Google Cloud Platform (GCP) [desc] [scope] [Q2] [Q3].

---

## Requisitos Funcionais (Functional Requirements)

### FR1: Gestão de Fazendas, Piquetes e Vistorias
- **FR1.1:** O sistema deve autenticar o consultor/auditor e permitir o cadastro, listagem e seleção de **Fazendas** (nome, município/UF, observações) e **Piquetes/Lotes** vinculados a cada fazenda (`scope-document.md`, `intent-statement.md`) [Q1].
- **FR1.2:** O sistema deve organizar cada análise de mídia como uma **Vistoria** associada a uma Fazenda, um Piquete e uma Data/Hora, mantendo o histórico completo de vistorias e seus respectivos status (`pending`, `processing`, `needs_review`, `reviewed`, `failed`) [Q1] [Q2].
- **FR1.3:** O sistema deve permitir filtrar e paginar o histórico de vistorias por Fazenda, Piquete e status, tratando listas vazias com instrução clara de criação da primeira vistoria [Q1].

### FR2: Ingestão e Armazenamento de Mídias de Drone (Upload e GCP)
- **FR2.1:** O sistema deve aceitar o envio via upload web ou importação via Google Cloud Storage (bucket GCP) de fotos aéreas nos formatos `.jpg`, `.jpeg` e `.png` (resolução mínima recomendada de $1920\times 1080$ até 4K/8K, tamanho até 50 MB) e vídeos aéreos nos formatos `.mp4` e `.mov` (duração até 5 minutos, tamanho máximo de 500 MB) [Q1].
- **FR2.2:** O sistema deve rejeitar arquivos vazios, corrompidos, com formato não suportado ou tamanho superior a 500 MB antes de iniciar o processamento em GPU, exibindo mensagem específica com a causa e preservando os dados já preenchidos no formulário [Q1].

### FR3: Motor de Detecção e Rastreamento de Bovinos por Visão Computacional
- **FR3.1:** Para fotos aéreas estáticas de alta resolução, o sistema deve executar detecção de objetos baseada em arquitetura YOLO combinada com inferência fatiada (*SAHI — Slicing Aided Hyper Inference*), identificando pequenos alvos bovinos em tomadas aéreas amplas sem perda de resolução [desc] [Q2] [Q3].
- **FR3.2:** Para vídeos aéreos de drones, o sistema deve executar detecção quadro a quadro combinada com rastreamento multi-objeto (*ByteTrack*), atribuindo um identificador único (`track_id`) a cada bovino ao longo do vídeo para contabilizar o total de animais únicos sem dupla contagem [desc] [Q2].
- **FR3.3:** O motor deve classificar cada detecção/rastreamento com seu grau de confiança (`confidence` entre `0.0` e `1.0`), categorizando detecções com `confidence >= 0.75` como **Alta Confiança (`high_confidence`)** e detecções entre `0.25` e `0.74` como **Duvidosas / Triagem Humana (`uncertain`)** [Q2].

### FR4: Estúdio de Revisão Visual e Auditoria Assistida
- **FR4.1:** O sistema deve exibir na interface web o mídia analisada com caixas delimitadoras (*bounding boxes*) sobre cada animal contabilizado, diferenciando visualmente por cor, estilo de borda e ícone as detecções de Alta Confiança (verde sólido + `OK`), Duvidosas (amarelo tracejado + `!`) e Adicionadas Manualmente (azul duplo + `+`) [Q2].
- **FR4.2:** O sistema deve listar na barra lateral todas as detecções classificadas como Duvidosas (`uncertain`), permitindo que o auditor navegue diretamente para o quadro/região correspondente e confirme ou remova a marcação com 1 clique ou atalho de teclado (`Delete`, `N`, `Setas`, `Espaço`) [Q2].
- **FR4.3:** O sistema deve permitir ao auditor adicionar manualmente novas caixas delimitadoras (**Falso Negativo corrigido**) sobre animais não detectados (ex.: sob sombra ou oclusão) e remover marcações incorretas (**Falso Positivo removido**, ex.: cupinzeiros ou pedras), recalculando instantaneamente o total consolidado de bois da vistoria [Q2].

### FR5: Ciclo *Human-in-the-Loop (HITL)* e Aprendizado Ativo (*Active Learning*)
- **FR5.1:** Sempre que o auditor confirmar uma revisão contendo correções manuais (adição de falso negativo, remoção de falso positivo ou validação de detecção duvidosa), o sistema deve persistir automaticamente a amostra corrigida (imagem/quadro extraído + arquivo de rótulos normalizados no padrão YOLO `class_id x_center y_center width height` + manifesto de proveniência JSON) no repositório curado **Golden Dataset** no Google Cloud Storage [Q2].
- **FR5.2:** O sistema deve disponibilizar um Painel de Evolução do Modelo IA exibindo a versão ativa do modelo, a acurácia aferida no conjunto de referência, o total de novas amostras *Human-in-the-Loop* acumuladas e a ação para disparar sob demanda o trabalho de ajuste fino (*fine-tuning*) na GCP [Q2].
- **FR5.3:** Ao executar o ajuste fino (*fine-tuning*) com as amostras do *Golden Dataset*, o sistema deve avaliar automaticamente o novo modelo candidato contra o conjunto de validação de referência e promovê-lo como versão ativa somente se a acurácia for igual ou superior a 95% e não apresentar regressão em relação ao modelo em produção [Q2] [Q3].

### FR6: Exportação de Laudo Auditado (PDF e CSV)
- **FR6.1:** O sistema deve gerar e exportar o laudo da vistoria em formato **PDF** e **CSV**, contendo identificação da Fazenda e Piquete, data/hora, nome do auditor, contagem bruta da IA, quantidade de adições/remoções *Human-in-the-Loop*, contagem final auditada, acurácia/confiança média e imagem representativa demarcada (`scope-document.md`) [Q1] [Q2].

---

## Requisitos Não Funcionais (Non-Functional Requirements)

- **NFR1 (Acurácia de Contagem):** O modelo de visão computacional deve atingir acurácia igual ou superior a **95%** ($\text{Acurácia} = 1 - \frac{|\text{Contagem IA} - \text{Contagem Real}|}{\text{Contagem Real}} \ge 0{,}95$) em fotos e vídeos aéreos diurnos nítidos (`intent-statement.md`) [Q3].
- **NFR2 (Desempenho e Latência de Inferência):** O tempo de processamento sob demanda com aceleração gráfica deve ser $\le 5\text{ segundos}$ para fotos aéreas de até 4K (com fatiamento SAHI) e $\le 90\text{ segundos}$ para vídeos de até 3 minutos; as rotas de leitura e revisão da API web devem responder com latência $p95 < 500\text{ms}$ [Q3].
- **NFR3 (Eficiência de Custos e Escala a Zero na GCP):** Os serviços de inferência e de *fine-tuning* *Human-in-the-Loop* na GCP devem operar sob demanda (*scale-to-zero*), não mantendo instâncias de GPU pagas ativas quando não houver vistorias ou treinamentos em execução (`team-practices.md`) [Q3].
- **NFR4 (Confiabilidade e Idempotência):** Submissões repetidas de upload, cliques duplos na confirmação *Human-in-the-Loop* ou reexecuções de tarefas de inferência devem ser idempotentes, nunca duplicando vistorias ou amostras no *Golden Dataset* [Q2] [Q3].
- **NFR5 (Acessibilidade e Usabilidade):** A interface web deve atender ao padrão **WCAG 2.1 Level AA**, incluindo contraste mínimo de $4{,}5:1$, navegação integral por teclado e indicadores visuais não dependentes exclusivamente de cor [Q2] [Q3].
- **NFR6 (Testabilidade e Cobertura de Código):** A base de código construída deve manter piso mínimo de **80% de cobertura de linhas** (*line coverage*) em testes automatizados (`pytest` no backend/IA e `Vitest` no frontend), seguindo a postura `test-after` afirmada em `team-practices.md` [Q3].

---

## Restrições, Premissas, Fora de Escopo e Questões em Aberto

### Constraints
- Limite máximo de arquivo no MVP: **500 MB** / **5 minutos** por vídeo e **50 MB** por imagem [Q1].
- Infraestrutura alvo baseada no ecossistema **Google Cloud Platform (GCP)** (Cloud Run, Cloud Storage, Firestore/Firebase) (`scope-document.md`).

### Assumptions
- Assume-se que vídeos e fotos utilizados para aferição da meta de $\ge 95\%$ são capturados em condições diurnas nítidas (`intent-statement.md`) [assumption] [Q3].

### Out of Scope
- Streaming contínuo 24/7 de câmeras IP/RTSP fixas e aplicativo móvel nativo offline (`intent-statement.md`, `scope-document.md`).
- Classificação etária automática e plotagem em mapa GPS na versão inicial (`scope-document.md`).

### Assumptions & Open Questions

None.
