# Mockups Refinados de Média/Alta Fidelidade (Refined Mockups)

Evolução de `rough-mockups/wireframes.md` (`wireframes.md`) e `rough-mockups/user-flow.md` (`user-flow.md`), alinhada às histórias de usuário de `user-stories/stories.md` (`stories.md`), aos requisitos de `requirements-analysis/requirements.md` (`requirements.md`), às convenções de `practices-discovery/team-practices.md` (`team-practices.md`) e à decisão registrada em `refined-mockups-questions.md` [Q1].

## Mapeamento Histórias de Usuário $\rightarrow$ Telas Refinadas

| Tela Refinada | Histórias de Usuário Atendidas (`stories.md`) | Requisitos (`requirements.md`) |
|---|---|---|
| **Tela 1: Painel de Vistorias e Gestão de Fazendas/Piquetes** | `US1.1`, `US1.2`, `US1.3`, `US6.1` | `FR1.1`, `FR1.2`, `FR1.3`, `FR6.1`, `NFR2`, `NFR5` |
| **Tela 2: Nova Vistoria e Upload/Importação GCP** | `US2.1`, `US2.2`, `US3.1`, `US3.2`, `US3.3` | `FR2.1`, `FR2.2`, `FR3.1`, `FR3.2`, `FR3.3`, `NFR1`, `NFR2`, `NFR3`, `NFR4` |
| **Tela 3: Estúdio de Revisão Visual e Auditoria Human-in-the-Loop** | `US4.1`, `US4.2`, `US4.3`, `US5.1`, `US6.1` | `FR4.1`, `FR4.2`, `FR4.3`, `FR5.1`, `FR6.1`, `NFR2`, `NFR4`, `NFR5` |
| **Tela 4: Painel de Evolução do Modelo IA (Golden Dataset & Fine-Tuning)** | `US5.2`, `US5.3` | `FR5.2`, `FR5.3`, `NFR1`, `NFR2`, `NFR3`, `NFR6` |

---

## Tela 1: Painel de Vistorias e Fazendas/Piquetes (`US1.1`, `US1.2`, `US1.3`)

```
+===================================================================================================+
| [Skip to main content]                                                                            |
| HEADER: [AgroCount IA]   [*1. Vistorias*]   [2. + Nova Vistoria]   [3. Modelo IA (HITL)]  [Lucas] |
+===================================================================================================+
| MAIN (h1): Vistorias de Rebanho e Fazendas                      [+ Cadastrar Fazenda] [+ Vistoria]|
|---------------------------------------------------------------------------------------------------|
| KPI CARDS (h2: Indicadores Operacionais):                                                         |
| +-----------------------------+ +-----------------------------+ +-------------------------------+ |
| | TOTAL DE VISTORIAS          | | BOVINOS AUDITADOS           | | ACURÁCIA MÉDIA DO MODELO ATIVO| |
| | 18 vistorias (3 pendentes)  | | 4.320 cabeças               | | 96,4% (v1.2 | Meta >= 95,0%)  | |
| +-----------------------------+ +-----------------------------+ +-------------------------------+ |
|---------------------------------------------------------------------------------------------------|
| FILTROS (role="search"):                                                                          |
| Fazenda: [Todas as Fazendas v]  Piquete: [Todos os Piquetes v]  Status: [Todos v]  [Limpar Filtros]|
|---------------------------------------------------------------------------------------------------|
| TABELA (h2: Histórico de Vistorias Realizadas):                                                   |
| +-----------------------------------------------------------------------------------------------+ |
| | ID       | Data/Hora        | Fazenda / Piquete        | Mídia     | IA -> Auditado | Status  | |
| |----------|------------------|--------------------------|-----------|----------------|---------| |
| | #INS-104 | 23/10/2026 09:30 | Faz. Santa Fé / Piquete 4| Vídeo 4K  | 247 -> 248     | [Revisar!]|
| | #INS-103 | 22/10/2026 15:10 | Faz. Boa Vista / Retiro 1| Foto 4K   | 112 -> 112     | [PDF|CSV] |
| +-----------------------------------------------------------------------------------------------+ |
| Paginação: Exibindo 1–2 de 18 registros                              [< Anterior] [1] [2] [Próx >]|
+===================================================================================================+
```

---

## Tela 2: Nova Vistoria e Upload/Importação GCP (`US2.1`, `US2.2`, `US3.1`, `US3.2`)

```
+===================================================================================================+
| HEADER: [AgroCount IA]   [1. Vistorias]   [*2. + Nova Vistoria*]   [3. Modelo IA (HITL)]  [Lucas] |
+===================================================================================================+
| MAIN (h1): Nova Vistoria Aérea de Rebanho                                                         |
|---------------------------------------------------------------------------------------------------|
| PASSO 1 (h2): Localização e Contexto do Lote                                                      |
| Fazenda *: [Fazenda Santa Fé (Ribas do Rio Pardo/MS) v]   Piquete *: [Piquete 04 - Maternidade v] |
| Data/Hora do Voo *: [2026-10-23T09:30]                    Observações: [Voo 60m altitude, sol  ]  |
|---------------------------------------------------------------------------------------------------|
| PASSO 2 (h2): Mídia Aérea do Drone (Upload Local ou Bucket GCP)                                   |
| Origem: (x) Upload Direto (.jpg, .jpeg, .png <= 50MB | .mp4, .mov <= 500MB)  ( ) URI GCS (gs://)  |
| +-----------------------------------------------------------------------------------------------+ |
| |  [Ícone Drone 4K]  Arraste o arquivo aéreo aqui ou clique em [Selecionar Arquivo]             | |
| |  Arquivo selecionado: sobrevoo_piquete04.mp4 (184 MB | 02:45 min | 3840x2160) [Remover]       | |
| |  Validação pré-GPU: [OK] Formato .mp4 suportado | [OK] Tamanho <= 500 MB                      | |
| +-----------------------------------------------------------------------------------------------+ |
| Pipeline selecionado automaticamente: YOLO + ByteTrack (Rastreamento Único de Vídeo)              |
|                                                                                                   |
| [Cancelar]                                              [Iniciar Contagem com IA (GPU GCP) ->]    |
+===================================================================================================+
```

---

## Tela 3: Estúdio de Revisão Visual e Auditoria Human-in-the-Loop (`US4.1`–`US4.3`, `US5.1`, `US6.1`)

```
+===================================================================================================+
| HEADER: [<- Voltar] Vistoria #INS-104 | Faz. Santa Fé > Piquete 04 | Modelo: yolo-cattle-v1.2     |
+===================================================================================================+
| MAIN (h1): Estúdio de Revisão Visual e Auditoria Human-in-the-Loop                                |
+-------------------------------------------------------------------+-------------------------------+
| CANVAS INTERATIVO (h2: Mídia Demarcada — 70% largura Desktop)     | PAINEL LATERAL (h2 — 30%)     |
|-------------------------------------------------------------------|-------------------------------|
| Barra de Ferramentas:                                             | CONTAGEM CONSOLIDADA          |
| [Modo Cursor (V)] [+ Adicionar Boi / FN (N)] [Zoom +] [Desfazer]  | +---------------------------+ |
|-------------------------------------------------------------------| |   248 CABEÇAS AUDITADAS   | |
| +---------------------------------------------------------------+ | | IA Bruta: 247 | Conf: 96% | |
| |                                                               | | | +2 FN Adicionados         | |
| |  +------------------+          +------------------+           | | | -1 FP Removido            | |
| |  | [OK] #014 (98%)  |          | [OK] #015 (96%)  |           | | +---------------------------+ |
| |  | Borda Verde Sól. |          | Borda Verde Sól. |           | |-------------------------------|
| |  +------------------+          +------------------+           | | FILA DE TRIAGEM (h3)          |
| |                                                               | | Duvidosos (0.25–0.74): 2 itens|
| |           +- - - - - - - - - - - +                            | | 1. [!] #089 (58% - Quadro 42) |
| |           | [!] #089 (58% Sombra)| <-- Foco ativo (Tecla Seta)| |    [Focar] [Confirmar] [Del]  |
| |           | Borda Amarela Tracej.|                            | | 2. [!] #142 (64% - Quadro 88) |
| |           +- - - - - - - - - - - +                            | |    [Focar] [Confirmar] [Del]  |
| |                                                               | |-------------------------------|
| |                                +==================+           | | CICLO HUMAN-IN-THE-LOOP (h3)  |
| |                                | [+] #248 (Manual)|           | | 3 ajustes humanos prontos     |
| |                                | Borda Azul Dupla |           | | para o Golden Dataset (YOLO). |
| |                                +==================+           | | [Confirmar Contagem e         |
| +---------------------------------------------------------------+ |  Alimentar Golden Dataset]    |
| Legenda Acessível (Cor + Estilo de Borda + Ícone):                |-------------------------------|
| [OK] Verde Sólido (#15803D): Alta Confiança (>= 0.75)             | EXPORTAÇÃO DE LAUDO (h3)      |
| [!]  Âmbar Tracejado (#D97706): Duvidoso / Revisar (0.25–0.74)    | [Baixar PDF]   [Baixar CSV]   |
| [+]  Azul Duplo (#1D4ED8): Adicionado pelo Auditor (+FN)          |                               |
+-------------------------------------------------------------------+-------------------------------+
```

---

## Tela 4: Painel de Evolução do Modelo IA e Active Learning (`US5.2`, `US5.3`)

```
+===================================================================================================+
| HEADER: [AgroCount IA]   [1. Vistorias]   [2. + Nova Vistoria]   [*3. Modelo IA (HITL)*]  [Helena]|
+===================================================================================================+
| MAIN (h1): Governança do Modelo IA e Ciclo Human-in-the-Loop (Active Learning)                    |
|---------------------------------------------------------------------------------------------------|
| STATUS DO MODELO EM PRODUÇÃO (h2):                                                                |
| +------------------------------+ +------------------------------+ +-----------------------------+ |
| | VERSÃO ATIVA EM PRODUÇÃO     | | ACURÁCIA AFERIDA (VAL SET)   | | GOLDEN DATASET (GCS BUCKET) | |
| | yolo-cattle-v1.2             | | 96,4% (Piso exigido: >=95,0%)| | 64 amostras corrigidas      | |
| | Promovido em 20/10/2026      | | Status: Saudável [OK]        | | Formato: YOLO .txt + .json  | |
| +------------------------------+ +------------------------------+ +-----------------------------+ |
|---------------------------------------------------------------------------------------------------|
| DISPARO DE FINE-TUNING SOB DEMANDA NA GCP (h2):                                                   |
| Novas amostras corrigidas pelos auditores: +18 falsos negativos em sombra, -9 falsos positivos.   |
| Regra de Promoção: O candidato só substitui a versão ativa se Acurácia >= 95% e >= versão atual.  |
| [Iniciar Fine-Tuning Sob Demanda (Cloud Run GPU)]   (Escala a zero automática após conclusão)     |
|---------------------------------------------------------------------------------------------------|
| HISTÓRICO DE VERSÕES E TREINAMENTOS (h2):                                                         |
| +-----------------------------------------------------------------------------------------------+ |
| | Versão            | Data       | Amostras HITL | Acurácia Antes -> Depois | Decisão / Status  | |
| |-------------------|------------|---------------|--------------------------|-------------------| |
| | yolo-cattle-v1.2  | 20/10/2026 | 120 quadros   | 94,8% -> 96,4%           | [ATIVO - Promovido]|
| | yolo-cattle-v1.2rc| 15/10/2026 | 95 quadros    | 94,8% -> 93,9%           | [Bloqueado < 95%] |
| | yolo-cattle-v1.1  | 10/10/2026 | 85 quadros    | 92,1% -> 94,8%           | [Arquivado]       |
| +-----------------------------------------------------------------------------------------------+ |
+===================================================================================================+
```
