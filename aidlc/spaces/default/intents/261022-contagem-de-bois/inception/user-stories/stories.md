# Histórias de Usuário e Critérios de Aceite (User Stories)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `practices-discovery/team-practices.md` (`team-practices.md`) e `personas.md`.

---

## Épico 1: Gestão de Fazendas, Piquetes e Vistorias (`FR1`)

### US1.1: Cadastro e Seleção de Fazendas e Piquetes
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero me autenticar no sistema e cadastrar, listar e selecionar **Fazendas** e seus respectivos **Piquetes/Lotes**, para organizar espacialmente cada inventário de rebanho.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR1.1`, `NFR2`, `NFR5`, `NFR6`
- **Critérios de Aceite:**
  - **AC1.1.1:** **Given** um auditor autenticado na aplicação web, **When** ele preenche o nome da fazenda, município/UF e cadastra um ou mais piquetes vinculados, **Then** o sistema persiste os registros com resposta da API $p95 < 500\text{ms}$ (`NFR2`) e exibe a fazenda e seus piquetes disponíveis para seleção imediata (`FR1.1`).
  - **AC1.1.2:** **Given** o formulário de cadastro de fazenda ou piquete, **When** o usuário navega utilizando apenas o teclado (`Tab`, `Enter`, `Esc`), **Then** todos os campos possuem foco visível, rótulos acessíveis e contraste $\ge 4{,}5:1$ conforme WCAG 2.1 AA (`NFR5`).

### US1.2: Criação e Acompanhamento de Vistorias por Status
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero criar uma **Vistoria** vinculada a uma Fazenda, um Piquete e uma Data/Hora e acompanhar a evolução do seu status (`pending`, `processing`, `needs_review`, `reviewed`, `failed`), para controlar o ciclo completo de auditoria de cada lote.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR1.2`, `NFR4`, `NFR6`
- **Critérios de Aceite:**
  - **AC1.2.1:** **Given** uma fazenda e um piquete selecionados, **When** o auditor inicia uma nova vistoria informando a data/hora, **Then** o sistema cria o registro da vistoria com status inicial `pending` e transiciona para `processing`, `needs_review`, `reviewed` ou `failed` conforme o avanço do pipeline (`FR1.2`).
  - **AC1.2.2:** **Given** uma requisição de criação de vistoria com chave de idempotência ou clique duplo no botão de envio, **When** a requisição é recebida em duplicidade, **Then** o sistema retorna a mesma vistoria sem criar registros duplicados (`NFR4`).

### US1.3: Filtragem, Paginação e Estado Vazio do Histórico de Vistorias
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero filtrar e paginar o histórico de vistorias por Fazenda, Piquete e status, para localizar rapidamente auditorias pendentes de revisão ou concluídas.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR1.3`, `NFR2`, `NFR5`
- **Critérios de Aceite:**
  - **AC1.3.1:** **Given** um histórico com múltiplas vistorias cadastradas, **When** o auditor aplica filtros por Fazenda, Piquete ou status (`needs_review`, `reviewed`), **Then** o sistema retorna a lista paginada correspondente em menos de $500\text{ms}$ ($p95$, `NFR2`, `FR1.3`).
  - **AC1.3.2:** **Given** uma fazenda recém-cadastrada sem vistorias registradas, **When** o auditor acessa o painel de vistorias, **Then** o sistema exibe um estado vazio informativo com botão de ação direta para criar a primeira vistoria (`FR1.3`).

---

## Épico 2: Ingestão e Validação de Mídias de Drone (`FR2`)

### US2.1: Upload Web e Importação GCP de Fotos e Vídeos Aéreos
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero enviar fotos aéreas (`.jpg`, `.jpeg`, `.png` até 50 MB) e vídeos de drone (`.mp4`, `.mov` até 5 minutos / 500 MB) via upload web ou referência no Google Cloud Storage, para submeter a mídia do piquete à contagem automatizada.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR2.1`, `NFR4`
- **Critérios de Aceite:**
  - **AC2.1.1:** **Given** uma vistoria ativa, **When** o auditor envia uma foto `.jpg`/`.jpeg`/`.png` de até 50 MB ou um vídeo `.mp4`/`.mov` de até 5 minutos e 500 MB, **Then** o arquivo é armazenado no bucket de mídias do projeto e vinculado à vistoria para inferência (`FR2.1`).
  - **AC2.1.2:** **Given** um reenvio acidental do mesmo arquivo na mesma vistoria, **When** o upload é processado, **Then** a operação é tratada de forma idempotente sem duplicar o disparo de processamento (`NFR4`).

### US2.2: Validação Prévia de Formato, Integridade e Limite de Tamanho
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero que o sistema valide o formato, integridade e tamanho do arquivo antes de alocar GPU, para receber feedback imediato em caso de arquivo inválido sem perder os dados preenchidos.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR2.2`, `NFR3`
- **Critérios de Aceite:**
  - **AC2.2.1:** **Given** a tentativa de envio de um arquivo vazio (`0 bytes`), corrompido, com extensão não suportada (ex.: `.avi`, `.pdf`) ou tamanho $> 500\text{ MB}$, **When** a validação de entrada é executada, **Then** o sistema rejeita o arquivo com código HTTP `400`/`422`, exibe mensagem clara em português indicando a causa exata, preserva a Fazenda e o Piquete selecionados no formulário e não aciona processamento em GPU (`FR2.2`, `NFR3`).

---

## Épico 3: Motor de Detecção e Rastreamento por Visão Computacional (`FR3`)

### US3.1: Detecção em Fotos Aéreas de Alta Resolução com YOLO + SAHI
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero que fotos aéreas de alta resolução (1080p a 4K) sejam analisadas com modelo YOLO combinado com inferência fatiada (*SAHI*), para detectar com precisão $\ge 95\%$ mesmo bovinos pequenos em tomadas abertas.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR3.1`, `NFR1`, `NFR2`, `NFR3`
- **Critérios de Aceite:**
  - **AC3.1.1:** **Given** uma foto aérea diurna nítida de até 4K enviada em uma vistoria, **When** o motor de visão computacional executa a inferência YOLO com fatiamento SAHI e fusão NMS, **Then** o processamento conclui em $\le 5\text{ segundos}$ em GPU sob demanda (`NFR2`, `NFR3`) e produz a contagem e coordenadas normalizadas (`x_center, y_center, width, height`) com acurácia $\ge 95\%$ (`FR3.1`, `NFR1`).

### US3.2: Contagem Única em Vídeos de Drone com YOLO + ByteTrack
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero que vídeos aéreos de sobrevoo sejam processados quadro a quadro com rastreamento multi-objeto (*ByteTrack*), para contabilizar cada animal uma única vez (`track_id`) sem dupla contagem enquanto o drone se desloca.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR3.2`, `NFR1`, `NFR2`, `NFR3`
- **Critérios de Aceite:**
  - **AC3.2.1:** **Given** um vídeo aéreo diurno de até 3 minutos enviado em uma vistoria, **When** o pipeline executa detecção YOLO combinada ao rastreador *ByteTrack*, **Then** cada bovino recebe um `track_id` persistente entre quadros, o processamento termina em $\le 90\text{ segundos}$ (`NFR2`, `NFR3`), a contagem total reflete os animais únicos com acurácia $\ge 95\%$ (`FR3.2`, `NFR1`) e quadros representativos são extraídos para revisão visual.

### US3.3: Classificação Automática por Faixas de Confiança para Triagem Humana
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero que cada detecção seja classificada automaticamente em **Alta Confiança** (`confidence >= 0.75`) ou **Duvidosa / Triagem Humana** (`0.25 <= confidence <= 0.74`), para focar minha revisão visual nos casos onde o modelo teve incerteza.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR3.3`
- **Critérios de Aceite:**
  - **AC3.3.1:** **Given** o resultado bruto de detecções do motor de visão computacional, **When** o pós-processamento classifica as caixas delimitadoras, **Then** toda detecção com `confidence >= 0.75` recebe a categoria `high_confidence`, toda detecção com `0.25 <= confidence < 0.75` recebe a categoria `uncertain`, e a vistoria registra os totais separados de alta confiança e de triagem humana (`FR3.3`).

---

## Épico 4: Estúdio de Revisão Visual e Auditoria Assistida (`FR4`)

### US4.1: Visualização de Bounding Boxes com Diferenciação Semântica e Acessível
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero visualizar a imagem ou quadro do vídeo no Estúdio de Revisão com caixas delimitadoras diferenciadas por cor, estilo de borda e ícone para detecções de Alta Confiança, Duvidosas e Adicionadas Manualmente, para inspecionar o rebanho com clareza visual e acessibilidade.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR4.1`, `NFR5`
- **Critérios de Aceite:**
  - **AC4.1.1:** **Given** uma vistoria aberta no Estúdio de Revisão Visual, **When** o canvas renderiza as marcações sobre a mídia, **Then** detecções `high_confidence` exibem borda sólida verde e selo `OK`, detecções `uncertain` exibem borda tracejada amarela/laranja e selo `!`, e marcações `manual_added` exibem borda dupla azul e selo `+`, garantindo distinção não dependente apenas de cor (`FR4.1`, `NFR5`).

### US4.2: Fila Lateral de Triagem Rápida e Atalhos de Teclado
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero ver todas as detecções duvidosas (`uncertain`) listadas na barra lateral e navegar entre elas para confirmar ou excluir com 1 clique ou atalho de teclado (`Delete`, `N`, `Setas`, `Espaço`), para auditar centenas de cabeças em poucos segundos.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR4.2`, `NFR5`
- **Critérios de Aceite:**
  - **AC4.2.1:** **Given** uma vistoria contendo detecções `uncertain`, **When** o auditor clica em um item da fila lateral ou usa as teclas de seta e `Espaço`/`Delete`, **Then** o canvas destaca a caixa delimitadora correspondente e confirma (promovendo a `confirmed`) ou remove a detecção imediatamente (`FR4.2`, `NFR5`).

### US4.3: Adição de Falsos Negativos e Remoção de Falsos Positivos com Recálculo Instantâneo
- **História:** Como **Consultor e Auditor Agropecuário (P1)**, quero desenhar novas caixas delimitadoras sobre animais omitidos pela IA (falsos negativos) e remover marcações incorretas sobre pedras/cupinzeiros (falsos positivos), vendo o total de bois recalculado instantaneamente na tela.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR4.3`, `NFR2`
- **Critérios de Aceite:**
  - **AC4.3.1:** **Given** o Estúdio de Revisão Visual ativo, **When** o auditor ativa o modo de adição (`N` ou botão `+ Adicionar Boi`), desenha uma nova caixa sobre um animal não detectado ou exclui uma caixa existente, **Then** o contador de `Contagem Final Auditada`, `Adicionados (+FN)` e `Removidos (-FP)` é atualizado instantaneamente na interface e salvo via API com latência $p95 < 500\text{ms}$ (`FR4.3`, `NFR2`).

---

## Épico 5: Ciclo *Human-in-the-Loop (HITL)* e Aprendizado Ativo (`FR5`)

### US5.1: Exportação Automática de Correções Humanas para o Golden Dataset (Padrão YOLO)
- **História:** Como **Gestora Técnica e Curadora de IA (P2)**, quero que toda revisão confirmada com correções humanas (falso negativo adicionado, falso positivo removido ou detecção duvidosa validada) salve automaticamente o frame e o arquivo de rótulos YOLO normalizados no **Golden Dataset**, para acumular dados reais de treinamento de alta qualidade sem retrabalho manual.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR5.1`, `NFR4`, `NFR6`
- **Critérios de Aceite:**
  - **AC5.1.1:** **Given** uma vistoria em que o auditor realizou correções *Human-in-the-Loop* ou validou detecções duvidosas, **When** o auditor clica em `Confirmar Contagem e Alimentar IA`, **Then** o sistema gera e persiste de forma idempotente no *Golden Dataset* a imagem/frame, o arquivo `.txt` no formato YOLO (`0 x_center y_center width height` com coordenadas normalizadas em $[0, 1]$) e o manifesto JSON de proveniência contendo `inspection_id`, `auditor_id`, `model_version`, `false_positives_removed`, `false_negatives_added` e timestamp (`FR5.1`, `NFR4`).

### US5.2: Painel de Evolução do Modelo IA e Disparo Sob Demanda de Fine-Tuning
- **História:** Como **Gestora Técnica e Curadora de IA (P2)**, quero visualizar em um painel dedicado a versão ativa do modelo, sua acurácia de validação, o total de amostras acumuladas no *Golden Dataset* e um botão para acionar o *fine-tuning* sob demanda na GCP, para evoluir o modelo com controle total de custos.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR5.2`, `NFR2`, `NFR3`
- **Critérios de Aceite:**
  - **AC5.2.1:** **Given** o Painel de Evolução do Modelo IA, **When** a gestora consulta o painel ou aciona `Iniciar Fine-Tuning com Novas Amostras`, **Then** o sistema exibe as métricas vigentes da versão ativa, a quantidade de amostras HITL prontas para treino e registra/executa o job de *fine-tuning* sob demanda (*scale-to-zero* após conclusão) (`FR5.2`, `NFR2`, `NFR3`).

### US5.3: Validação de Acurácia ($\ge 95\%$) e Trava Automática contra Regressão de Modelo
- **História:** Como **Gestora Técnica e Curadora de IA (P2)**, quero que cada modelo candidato gerado pelo *fine-tuning* seja avaliado automaticamente contra o conjunto de validação de referência e só seja promovido à produção se atingir acurácia $\ge 95\%$ e não apresentar regressão em relação ao modelo ativo.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR5.3`, `NFR1`, `NFR6`
- **Critérios de Aceite:**
  - **AC5.3.1:** **Given** a conclusão de um ciclo de *fine-tuning* com as amostras do *Golden Dataset*, **When** o avaliador automático mede a acurácia do modelo candidato no conjunto de referência, **Then** o sistema promove o candidato a `active` somente se $\text{accuracy} \ge 0{,}95$ e $\text{accuracy}_{\text{candidato}} \ge \text{accuracy}_{\text{atual}}$; caso contrário, mantém o modelo anterior ativo e registra o candidato como `rejected_regression` (`FR5.3`, `NFR1`).

---

## Épico 6: Exportação de Laudo Auditado (`FR6`)

### US6.1: Geração e Download de Laudo Auditado em PDF e CSV
- **História:** Como **Consultor e Auditor Agropecuário (P1)** (em atendimento ao **Gestor de Fazenda P3**), quero exportar o laudo oficial da vistoria revisada nos formatos **PDF** e **CSV**, contendo os dados da Fazenda/Piquete, contagem bruta da IA, ajustes *Human-in-the-Loop*, contagem final auditada e confiança média, para comprovar formalmente o inventário do rebanho.
- **Prioridade MoSCoW:** Must Have
- **Requisitos Rastreados:** `FR6.1`, `NFR2`, `NFR6`
- **Critérios de Aceite:**
  - **AC6.1.1:** **Given** uma vistoria revisada, **When** o auditor solicita a exportação em **CSV** ou **PDF**, **Then** o sistema gera o arquivo contendo identificação da Fazenda, Piquete, data/hora, auditor, versão do modelo IA, contagem inicial da IA, falsos negativos adicionados, falsos positivos removidos, contagem final auditada e confiança média, disponibilizando o download imediato (`FR6.1`, `NFR2`).

---

## Conformidade INVEST e Dependências entre Histórias

- **Conformidade INVEST:** Todas as 15 histórias (`US1.1` a `US6.1`) são **I**ndependentes dentro de seus contratos de dados, **N**egociáveis nos detalhes visuais, **V**aliosas diretamente para as personas P1/P2/P3, **E**stimáveis, **S**uficientemente pequenas para implementação e verificação em ciclo único e **T**estáveis via critérios `Given/When/Then` com piso de 80% de cobertura (`NFR6`).
- **Ordem de Dependência Lógica:** `US1.*` (Fazendas/Vistorias) $\rightarrow$ `US2.*` (Upload/Validação) $\rightarrow$ `US3.*` (Inferência CV) $\rightarrow$ `US4.*` (Estúdio de Revisão) $\rightarrow$ `US5.*` (Ciclo HITL / *Golden Dataset* / *Fine-Tuning*) e `US6.1` (Exportação PDF/CSV).
