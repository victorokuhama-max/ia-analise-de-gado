# Wireframes de Conceito e Arquitetura de Informação (Rough Mockups)

Elaborado a partir de `intent-capture/intent-statement.md` (`intent-statement.md`), `scope-definition/scope-document.md` (`scope-document.md`), `scope-definition/intent-backlog.md` (`intent-backlog.md`) e das decisões confirmadas em `rough-mockups-questions.md`.

## Sources

- [desc] Initial description: "criar uma aplicação com IA de contagem de bois"
- [scope] Workflow-selected scope: `mvp`.
- [Q1] Resposta à pergunta Q1 em `rough-mockups-questions.md`: `A` — Estrutura enxuta em 4 visões principais com barra de navegação superior: (1) Painel de Vistorias e Fazendas/Piquetes, (2) Nova Vistoria (Upload / Importação GCP), (3) Estúdio de Revisão Visual e Correção Human-in-the-Loop e (4) Painel do Modelo IA (Histórico HITL e Fine-Tuning).
- [Q2] Resposta à pergunta Q2 em `rough-mockups-questions.md`: `A` — Visualizador interativo em tela dividida (*Split-Screen*) com canvas de imagem/vídeo demarcado à esquerda (alta confiança $\ge 75\%$ vs. casos duvidosos) e painel lateral à direita com totalizador dinâmico, fila de alertas de baixa confiança, confirmação *Human-in-the-Loop* e exportação de laudo.
- [Q3] Resposta à pergunta Q3 em `rough-mockups-questions.md`: `A` — Web responsivo com prioridade para Desktop/Notebook e Tablet, visual limpo de alto contraste e suporte móvel para consulta rápida de laudos.
- [Q4] Resposta à pergunta Q4 em `rough-mockups-questions.md`: `A` — Conformidade WCAG 2.1 AA com indicadores redundantes (cor + borda/ícone), contraste mínimo de 4.5:1 e atalhos de teclado dedicados (`Espaço`, `Setas`, `Delete`, `N`).

## Arquitetura de Informação e Navegação Principal

A estrutura da aplicação web reflete diretamente as capacidades priorizadas em `intent-backlog.md` (`IB-01` a `IB-06`) e as fronteiras definidas em `scope-document.md`, mantendo no máximo 2 níveis de profundidade para que qualquer tela seja alcançada em até 2 cliques a partir do painel inicial [Q1].

```
+-------------------------------------------------------------------------+
| [Logo: AgroCount IA]   [1. Vistorias]  [2. + Nova Vistoria]  [3. Modelo IA (HITL)]   [Perfil/Sair] |
+-------------------------------------------------------------------------+
          |                     |                                     |
          v                     v                                     v
  (Tela 1: Painel de     (Tela 2: Envio / Importação        (Tela 4: Painel de Evolução
   Fazendas e Laudos)     de Foto ou Vídeo via GCP)          do Modelo & Golden Dataset)
          |                     |
          +----------+----------+
                     |
                     v
       (Tela 3: Estúdio de Revisão Visual,
        Correção Human-in-the-Loop e Exportação PDF/CSV)
```

---

## Tela 1: Painel de Vistorias e Fazendas/Piquetes (`IB-05`, `IB-06`)

Ponto de entrada do consultor agropecuário, técnico ou auditor após autenticação simples (`intent-statement.md`, `scope-document.md`) [Q1].

```
+-----------------------------------------------------------------------------------+
| HEADER / NAV: [AgroCount IA]  [*Vistorias*]  [+ Nova Vistoria]  [Modelo IA] [Sair]|
+-----------------------------------------------------------------------------------+
| MAIN: h1: Vistorias de Rebanho                                [+ Nova Vistoria]   |
|-----------------------------------------------------------------------------------|
| Filtros: [Fazenda: Todas v] [Piquete: Todos v] [Status: Todos v] [Buscar...     ] |
|-----------------------------------------------------------------------------------|
| h2: Resumo Recente                                                                |
| +-----------------------+ +-----------------------+ +---------------------------+ |
| | Vistorias no Mês: 18  | | Bois Contados: 4.320  | | Acurácia Média IA: 96,4%  | |
| +-----------------------+ +-----------------------+ +---------------------------+ |
|-----------------------------------------------------------------------------------|
| h2: Histórico de Vistorias Realizadas                                             |
| +-------------------------------------------------------------------------------+ |
| | Data       | Fazenda / Piquete        | Mídia      | Contagem Final | Status  | |
| |------------|--------------------------|------------|----------------|---------| |
| | 23/10/2026 | Faz. Santa Fé / Piquete 3| Vídeo 03:12| 248 bois (HITL)| [Abrir] | |
| | 22/10/2026 | Faz. Boa Vista / Retiro 1| Foto 4K    | 112 bois       | [Laudo] | |
| +-------------------------------------------------------------------------------+ |
| Mostrando 1-2 de 18 vistorias                         [< Anterior] [1] [2] [Próx >]|
+-----------------------------------------------------------------------------------+
| FOOTER: AgroCount IA — Inventário Aéreo de Precisão                               |
+-----------------------------------------------------------------------------------+
```

- **Nota de Acessibilidade (Tela 1):** Hierarquia de títulos `h1` ("Vistorias de Rebanho") e `h2` ("Resumo Recente", "Histórico de Vistorias Realizadas"); regiões semânticas `header`, `nav`, `main` e `footer`; ponto de entrada de teclado via link *Skip to main content* seguido pelo botão primário `[+ Nova Vistoria]` e filtros navegáveis por `Tab` [Q4].

---

## Tela 2: Nova Vistoria — Envio / Importação de Mídia de Drone (`IB-02`, `IB-05`)

Permite selecionar a Fazenda e o Piquete (Lote) e enviar fotos aéreas (1080p–4K) ou vídeos curtos (até 3–5 min / até 500 MB) por upload direto ou importação a partir do Google Cloud Storage (GCP) (`scope-document.md`, `intent-backlog.md`) [Q1].

```
+-----------------------------------------------------------------------------------+
| HEADER / NAV: [AgroCount IA]  [Vistorias]  [*+ Nova Vistoria*]  [Modelo IA] [Sair]|
+-----------------------------------------------------------------------------------+
| MAIN: h1: Nova Vistoria Aérea de Rebanho                                          |
|-----------------------------------------------------------------------------------|
| h2: 1. Identificação do Local Auditado                                            |
| Fazenda *: [Fazenda Santa Fé          v] [+ Nova]   Data *: [23/10/2026]          |
| Piquete *: [Piquete 04 - Maternidade  v] [+ Novo]   Observação: [Opcional...    ] |
|-----------------------------------------------------------------------------------|
| h2: 2. Mídia do Drone (Foto 1080p-4K ou Vídeo até 5 min / 500 MB)                 |
| Fonte da Mídia: (x) Upload do Computador/Cartão SD   ( ) Importar Bucket GCP      |
| +-------------------------------------------------------------------------------+ |
| |                       [Ícone de Drone / Nuvem]                                | |
| |     Arraste a foto (.JPG, .PNG) ou vídeo (.MP4, .MOV) aqui                    | |
| |                  ou [Selecionar Arquivo do Dispositivo]                       | |
| |     Limites do MVP: Resolução 1080p a 4K | Tamanho máx.: 500 MB (3-5 min)     | |
| +-------------------------------------------------------------------------------+ |
| Dica de Captura (>95% acurácia): Voo diurno nítido, sem neblina densa.            |
|                                                                                   |
| [Cancelar]                                   [Iniciar Contagem com IA (GPU) ->]   |
+-----------------------------------------------------------------------------------+
```

- **Nota de Acessibilidade (Tela 2):** Hierarquia `h1` ("Nova Vistoria Aérea de Rebanho") e `h2` para os passos 1 e 2; regiões `header`, `nav`, `main` e `footer`; ponto de entrada de teclado no seletor `Fazenda *` com alternativa de botão explícito `[Selecionar Arquivo do Dispositivo]` para a área de *drag-and-drop* [Q4].

---

## Tela 3: Estúdio de Revisão Visual, Correção *Human-in-the-Loop* e Laudo (`IB-01`, `IB-03`, `IB-04`, `IB-06`)

Tela central do MVP em formato *Split-Screen* (`rough-mockups-questions.md` [Q2]): combina a visualização demarcada da contagem por IA (`IB-01`, `IB-03`), os ajustes de 1 clique que alimentam o *Golden Dataset* na GCP (`IB-04`) e a exportação do laudo auditado (`IB-06`).

```
+-----------------------------------------------------------------------------------+
| HEADER / NAV: [<- Voltar às Vistorias]  Faz. Santa Fé > Piquete 04 (23/10/2026)   |
+-----------------------------------------------------------------------------------+
| MAIN: h1: Estúdio de Revisão e Auditoria Human-in-the-Loop                        |
+---------------------------------------------------+-------------------------------+
| h2: Visualizador Demarcado (Canvas Foto / Vídeo)  | h2: Painel de Contagem & HITL |
|---------------------------------------------------|-------------------------------|
| Ferramentas: [Cursor] [+ Adicionar Boi (N)] [Zoom]| TOTAL CONSOLIDADO:  248 BOIS  |
|---------------------------------------------------| - Contagem IA bruta: 247      |
| +-----------------------------------------------+ | - Adicionados (+):   +2       |
| |                                               | | - Removidos (-):     -1       |
| |   [===] #014 (98% OK)    [===] #015 (96% OK)  | |-------------------------------|
| |                                               | | h3: Triagem de Confiança      |
| |         [:::] #089 (58% ! Sombra - Revisar)   | | [x] Alta confiança (>=75%):244|
| |                                               | | [!] Duvidosos (25%-74%):     3|
| |   [===] #102 (94% OK)    [+] #248 (Manual)    | |  -> Quadro 01:14 (#089 - 58%) |
| |                                               | |     [Ir] [Confirmar] [Remover]|
| +-----------------------------------------------+ |  -> Quadro 02:05 (#142 - 61%) |
| Controles de Vídeo:                               |     [Ir] [Confirmar] [Remover]|
| [|> Play (Espaço)] [====|==!====] 01:14 / 03:10   |-------------------------------|
| Legenda (Cor + Borda + Ícone):                    | h3: Ciclo Human-in-the-Loop   |
| [===] Verde Sólido (OK): Alta Confiança (>=75%)   | 3 correções prontas para o    |
| [:::] Amarelo Tracejado (!): Duvidoso (Revisar)   | Golden Dataset na GCP.        |
| [ + ] Azul Duplo (+): Adicionado pelo Auditor     | [Salvar e Alimentar IA (HITL)]|
| Atalhos: [Espaço] Play/Pause | [Setas] Próximo !  |-------------------------------|
|          [N] Novo Boi        | [Del] Remover      | [Exportar PDF] [Exportar CSV] |
+---------------------------------------------------+-------------------------------+
```

- **Nota de Acessibilidade (Tela 3):** Hierarquia `h1` (título da tela), `h2` (Canvas e Painel Lateral) e `h3` (Triagem de Confiança e Ciclo HITL); regiões `header`, `main` e `aside`; ponto de entrada de teclado na barra de ferramentas do canvas e lista de itens duvidosos com atalhos `Espaço`, `Setas`, `N` e `Delete`, além de diferenciação visual tripla (cor + estilo da linha sólida/tracejada + ícone `OK`/`!`/`+`) para não depender apenas de cor [Q2] [Q4].

---

## Tela 4: Painel de Evolução do Modelo IA — Ciclo *Human-in-the-Loop* (`IB-04`)

Permite acompanhar os exemplos difíceis (*Hard Examples*) coletados durante as revisões dos auditores e acionar sob demanda na GCP o ajuste fino (*fine-tuning*) do modelo (`scope-document.md`, `intent-backlog.md`) [Q1] [Q2].

```
+-----------------------------------------------------------------------------------+
| HEADER / NAV: [AgroCount IA]  [Vistorias]  [+ Nova Vistoria]  [*Modelo IA*] [Sair]|
+-----------------------------------------------------------------------------------+
| MAIN: h1: Evolução do Modelo de IA (Human-in-the-Loop / Active Learning)          |
|-----------------------------------------------------------------------------------|
| h2: Status do Modelo em Produção                                                  |
| +--------------------------+ +------------------------+ +-----------------------+ |
| | Versão Ativa: v1.2       | | Acurácia Validação:    | | Quadros Corrigidos    | |
| | Atualizado em 20/10/2026 | | 96,4% (Meta: >= 95,0%) | | Pendentes (GCP): 64   | |
| +--------------------------+ +------------------------+ +-----------------------+ |
|-----------------------------------------------------------------------------------|
| h2: Ciclo de Re-treinamento Sob Demanda (Fine-Tuning na GCP)                      |
| Há 64 novos quadros corrigidos pelos auditores (falsos negativos em sombra e      |
| falsos positivos removidos) prontos no Golden Dataset.                            |
| [Acionar Fine-Tuning Sob Demanda (GPU GCP)]  (Tempo est.: ~20 min | Custo: ~$0,25)|
|-----------------------------------------------------------------------------------|
| h2: Histórico de Versões e Treinamentos                                           |
| +-------------------------------------------------------------------------------+ |
| | Versão | Data       | Exemplos HITL Usados | Acurácia Ant. -> Nova | Status   | |
| |--------|------------|----------------------|-----------------------|----------| |
| | v1.2   | 20/10/2026 | +120 quadros campo   | 94,8% -> 96,4%        | Ativo    | |
| | v1.1   | 10/10/2026 | +85 quadros campo    | 92,1% -> 94,8%        | Arquivado| |
| +-------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

- **Nota de Acessibilidade (Tela 4):** Hierarquia `h1` ("Evolução do Modelo de IA") e `h2` (Status, Ciclo de Re-treinamento e Histórico); regiões `header`, `nav`, `main` e `footer`; ponto de entrada de teclado no botão `[Acionar Fine-Tuning Sob Demanda (GPU GCP)]` com anúncio de progresso via `aria-live="polite"` [Q4].

---

## Especificação dos 5 Estados de Tela e Casos de Borda

Todas as 4 visões contemplam os cinco estados obrigatórios para evitar falhas silenciosas durante o uso de campo e demonstrações comerciais:

| Estado | Comportamento Visual nas Telas do MVP |
|---|---|
| **1. Estado Vazio (*Empty State*)** | - **Tela 1 (Sem vistorias):** Exibe ilustração de drone sobre pasto, mensagem *"Nenhuma vistoria registrada ainda"* e botão de destaque `[+ Criar Primeira Vistoria]`.<br>- **Tela 3 (Zero casos duvidosos):** Exibe selo verde *"Nenhuma detecção duvidosa encontrada — todas as marcações têm confiança >= 75%"*.<br>- **Tela 4 (Zero correções acumuladas):** Exibe *"0 novos quadros pendentes; botão de Fine-Tuning desabilitado até acumular novas revisões"*. |
| **2. Estado de Carregamento (*Loading State*)** | - **Tela 2 -> 3 (Upload e Inferência IA):** Barra de progresso percentual durante o envio ao Google Cloud Storage seguida de indicador passo a passo (*"1/3 Vídeo recebido na GCP -> 2/3 Analisando quadros e rastreando animais -> 3/3 Gerando marcações visuais"*), com tempo estimado. |
| **3. Estado Populado / Sucesso (*Populated State*)** | - Operação normal ilustrada nos wireframes das Telas 1 a 4, com confirmação visual imediata (*toast* acessível) ao salvar correções *Human-in-the-Loop* ou exportar laudo PDF/CSV. |
| **4. Estado de Erro (*Error State*)** | - **Arquivo fora do limite (> 500 MB ou formato inválido):** Mensagem clara abaixo do seletor (*"Este vídeo possui 680 MB. No MVP, envie vídeos de até 500 MB (3–5 min) ou divida o sobrevoo em clipes menores"*).<br>- **Queda de conexão no upload:** Opção `[Tentar Novamente]` sem perder os campos de Fazenda/Piquete já preenchidos. |
| **5. Estado Parcial / Caso de Borda (*Partial / Edge State*)** | - **Mídia escura/borrada com baixa confiança geral:** Alerta amarelo no topo da Tela 3 (*"Atenção: 35% das detecções estão com baixa confiança devido a sombra/altitude. Recomendamos revisar os itens destacados em amarelo antes de emitir o laudo"*).<br>- **Nomes longos de fazendas/piquetes ou 1.000+ animais:** Truncamento com *tooltip* em tabelas e paginação/virtualização na lista lateral de alertas. |

## Adaptação Responsiva por Dispositivo (Breakpoints)

| Faixa de Tela | Adaptação de Layout (`rough-mockups-questions.md` [Q3]) |
|---|---|
| **Desktop / Notebook ($\ge 1024\text{px}$)** | Layout completo: Tela 3 em *Split-Screen* horizontal ($70\%$ Canvas interativo à esquerda / $30\%$ Painel de Contagem e HITL à direita); tabelas completas na Tela 1 e Tela 4. |
| **Tablet ($768\text{px} - 1023\text{px}$)** | Barra de navegação compacta; na Tela 3, o Canvas ocupa a largura superior ($100\%$) e o Painel de Contagem/HITL fica logo abaixo em duas colunas, com alvos de toque mínimos de $48\times 48\text{px}$ para adicionar/remover marcações com o dedo ou caneta. |
| **Mobile ($< 768\text{px}$)** | Menu recolhido (*hamburger*); tabelas convertidas em cartões verticais (*cards*) para consulta rápida de vistorias concluídas e download/compartilhamento de laudos PDF/CSV em campo. |

## Assumptions & Open Questions

- **Premissa WIR-A01 (Limiar visual padrão de confiança):** Assume-se o limiar inicial de $75\%$ para separar visualmente detecções de alta confiança (verde sólido) de detecções duvidosas (amarelo tracejado), podendo esse percentual ser calibrado nas etapas técnicas com base nos dados reais [assumption] [Q2].
- **Premissa WIR-A02 (Edição simplificada em vídeo):** Assume-se que, ao revisar um vídeo na Tela 3, a lista de "Duvidosos" posiciona o vídeo automaticamente no quadro exato em que o animal teve menor confiança de rastreamento, evitando que o auditor precise assistir ao vídeo inteiro manualmente [assumption] [Q2].
