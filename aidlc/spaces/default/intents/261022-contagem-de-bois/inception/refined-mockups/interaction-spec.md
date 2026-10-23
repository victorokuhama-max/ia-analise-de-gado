# Especificação de Interação e Componentes (Interaction Specification)

Elaborado conforme `.agents/knowledge/aidlc-design-agent/component-spec-template.md`, evoluindo `rough-mockups/wireframes.md` (`wireframes.md`) e `rough-mockups/user-flow.md` (`user-flow.md`) em alinhamento com `user-stories/stories.md` (`stories.md`), `requirements-analysis/requirements.md` (`requirements.md`) e `practices-discovery/team-practices.md` (`team-practices.md`).

---

## InspectionDashboardTable

| Field | Value |
|---|---|
| Component | `InspectionDashboardTable` |
| Description | Tabela filtrável e paginada de vistorias de rebanho por Fazenda, Piquete e status (`US1.1`, `US1.2`, `US1.3`). |
| Category | display / navigation |

### States

| State | Description | Trigger |
|---|---|---|
| default | Exibe lista paginada de vistorias com badges semânticos de status | page load com registros |
| hover | Destaca a linha sob o cursor (`#F8FAFC`) | mouseover na linha |
| focus | Contorno azul visível (`2px solid #1D4ED8`) nos filtros e botões de ação | navegação via tecla `Tab` |
| disabled | Botões de paginação `< Anterior` ou `Próx >` desabilitados nos limites | primeira ou última página |
| loading | Esqueleto (*skeleton rows*) com `aria-busy="true"` | busca ou troca de filtro em andamento |
| error | Alerta inline com botão `[Tentar Novamente]` | falha de rede na API |
| empty | Ilustração e CTA `[+ Criar Primeira Vistoria]` (`FR1.3`) | nenhuma vistoria encontrada |

### Props / Inputs

| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| `inspections` | `InspectionSummary[]` | yes | `[]` | Lista de vistorias retornadas pela API |
| `farms` | `Farm[]` | yes | `[]` | Lista de fazendas para filtro |
| `selectedFarmId` | `string` | no | `""` | Filtro ativo de fazenda |
| `selectedStatus` | `string` | no | `""` | Filtro ativo de status |
| `onSelectInspection` | `(id: string) => void` | yes | — | Abre a vistoria no Estúdio de Revisão |

### Responsive Behaviour

| Breakpoint | Behaviour |
|---|---|
| mobile (<768px) | Converte linhas da tabela em cartões verticais com botão rápido de download PDF/CSV |
| tablet (768–1024px) | Tabela compacta com scroll horizontal suave e botões de toque $\ge 48\times 48\text{px}$ |
| desktop (>1024px) | Tabela completa de 6 colunas + barra horizontal de filtros e KPIs |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `table` com `thead`, `tbody`, `th scope="col"` e região de filtro `role="search"` |
| Keyboard interaction | `Tab` percorre filtros e ações de cada linha; `Enter` abre a vistoria |
| Label / aria-label | Seletores com `<label>` explícito e botões com `aria-label="Revisar vistoria #INS-104"` |
| Contrast ratio | WCAG 2.1 AA ($\ge 4{,}5:1$ em todos os textos e badges de status) |
| Screen reader | Anuncia quantidade de resultados filtrados via `aria-live="polite"` |
| Focus management | Mantém foco no controle de filtro após atualização da tabela |

### Usage Example

```tsx
<InspectionDashboardTable
  inspections={inspections}
  farms={farms}
  selectedFarmId={farmId}
  onSelectInspection={handleOpenStudio}
/>
```

---

## DroneMediaUploader

| Field | Value |
|---|---|
| Component | `DroneMediaUploader` |
| Description | Formulário e zona de upload/importação GCP com validação pré-GPU de formato e tamanho (`US2.1`, `US2.2`). |
| Category | input / feedback |

### States

| State | Description | Trigger |
|---|---|---|
| default | Zona de arraste tracejada aguardando foto (`.jpg/.png`) ou vídeo (`.mp4/.mov`) | abertura da Tela 2 |
| hover | Borda verde `#15803D` e fundo `#F0FDF4` | arquivo arrastado sobre a zona ou mouseover |
| focus | Anel de foco `2px solid #1D4ED8` no botão `[Selecionar Arquivo]` | tecla `Tab` |
| disabled | Inputs bloqueados enquanto o upload está sendo transmitido | envio em andamento |
| loading | Barra de progresso percentual + status das 3 etapas de inferência | clique em `[Iniciar Contagem com IA]` |
| error | Mensagem específica de rejeição (`> 500 MB`, arquivo vazio ou extensão inválida) preservando Fazenda/Piquete (`FR2.2`) | validação pré-GPU reprovada |
| empty | Nenhum arquivo selecionado; botão de submissão desabilitado | estado inicial |

### Props / Inputs

| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| `farms` | `Farm[]` | yes | `[]` | Fazendas e piquetes disponíveis |
| `maxImageSizeMb` | `number` | no | `50` | Limite máximo para fotos em MB |
| `maxVideoSizeMb` | `number` | no | `500` | Limite máximo para vídeos em MB |
| `onSubmitInspection` | `(payload: CreateInspectionInput) => Promise<void>` | yes | — | Envia mídia validada para processamento |

### Responsive Behaviour

| Breakpoint | Behaviour |
|---|---|
| mobile (<768px) | Campos de Fazenda, Piquete e Data empilhados em 1 coluna |
| tablet (768–1024px) | Campos em grade de 2 colunas; zona de upload com altura de `180px` |
| desktop (>1024px) | Layout de 2 colunas com resumo técnico de validação ao lado da zona de upload |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `form` com `aria-describedby` apontando para os limites de formato/tamanho |
| Keyboard interaction | `Tab` + `Enter`/`Espaço` aciona o seletor nativo de arquivo sem exigir *drag-and-drop* |
| Label / aria-label | Todos os campos possuem `<label htmlFor="...">` visível |
| Contrast ratio | WCAG AA ($\ge 4{,}5:1$ para mensagens de erro em `#B91C1C` sobre `#FEF2F2`) |
| Screen reader | Erros de validação anunciados imediatamente com `role="alert"` |
| Focus management | Em caso de erro de validação, move o foco para o alerta de erro |

### Usage Example

```tsx
<DroneMediaUploader
  farms={farms}
  maxImageSizeMb={50}
  maxVideoSizeMb={500}
  onSubmitInspection={handleCreateInspection}
/>
```

---

## CattleReviewCanvas

| Field | Value |
|---|---|
| Component | `CattleReviewCanvas` |
| Description | Canvas interativo que sobrepõe *bounding boxes* de alta confiança, duvidosas e adicionadas manualmente, permitindo edição *Human-in-the-Loop* (`US4.1`, `US4.2`, `US4.3`). |
| Category | input / display |

### States

| State | Description | Trigger |
|---|---|---|
| default | Exibe mídia com *bounding boxes* renderizadas por categoria (`high_confidence`, `uncertain`, `manual_added`) | carregamento da vistoria na Tela 3 |
| hover | Destaca a caixa sob o cursor e exibe tooltip com `% de confiança` e `ID` | mouseover em uma caixa |
| focus | Caixa selecionada recebe contorno externo branco/azul pulsante e ações rápidas `[Confirmar]` / `[Remover]` | clique, seleção na barra lateral ou teclas `Setas` |
| disabled | Edição bloqueada quando a vistoria está em modo somente-leitura ou salvando | salvamento em progresso |
| loading | Spinner central sobre o canvas enquanto carrega mídia de alta resolução | abertura inicial da mídia |
| error | Mensagem de falha de renderização com botão `[Recarregar Mídia]` | erro ao carregar imagem/frame |
| empty | Aviso informativo caso nenhuma detecção tenha sido retornada pela IA, habilitando modo `[+ Adicionar Boi]` | `detections.length === 0` |

### Props / Inputs

| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| `mediaUrl` | `string` | yes | — | URL ou imagem base da vistoria |
| `detections` | `DetectionBox[]` | yes | `[]` | Lista de caixas (`high_confidence`, `uncertain`, `manual_added`) |
| `selectedBoxId` | `string \| null` | no | `null` | ID da caixa atualmente em foco |
| `activeTool` | `"select" \| "add"` | no | `"select"` | Ferramenta ativa no canvas |
| `onAddBox` | `(box: NormalizedBox) => void` | yes | — | Registra novo Falso Negativo (`+FN`) |
| `onRemoveBox` | `(boxId: string) => void` | yes | — | Remove Falso Positivo (`-FP`) |
| `onConfirmUncertain` | `(boxId: string) => void` | yes | — | Valida detecção duvidosa |

### Responsive Behaviour

| Breakpoint | Behaviour |
|---|---|
| mobile (<768px) | Canvas em largura total (`100%`) no topo com gestos de pinça para zoom |
| tablet (768–1024px) | Canvas em largura total (`100%`) acima do painel lateral, botões de ação $\ge 48\times 48\text{px}$ |
| desktop (>1024px) | Ocupa `70%` da largura à esquerda em *Split-Screen* ao lado da `HitlTriageSidebar` (`30%`) |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `region` com `aria-label="Canvas de revisão de bovinos"` e lista de caixas acessível por teclado |
| Keyboard interaction | `Setas` alternam entre caixas duvidosas; `Espaço` confirma; `Delete`/`Backspace` remove; `N` ativa adição |
| Label / aria-label | Cada caixa possui `aria-label="Boi #089, confiança 58%, status duvidoso"` |
| Contrast ratio | Tripla codificação: Cor + Estilo de Borda (sólida, tracejada, dupla) + Selo textual (`OK`, `!`, `+`) |
| Screen reader | Anuncia o total recalculado a cada adição ou remoção via `aria-live="assertive"` |
| Focus management | Ao remover uma caixa, move o foco automaticamente para a próxima detecção `uncertain` |

### Usage Example

```tsx
<CattleReviewCanvas
  mediaUrl={inspection.mediaUrl}
  detections={detections}
  selectedBoxId={selectedId}
  activeTool={tool}
  onAddBox={handleAddFalseNegative}
  onRemoveBox={handleRemoveFalsePositive}
  onConfirmUncertain={handleConfirmDetection}
/>
```

---

## HitlTriageSidebar

| Field | Value |
|---|---|
| Component | `HitlTriageSidebar` |
| Description | Painel lateral com totalizador em tempo real, fila de triagem de baixa confiança (`0.25–0.74`), confirmação para o *Golden Dataset* e exportação PDF/CSV (`US4.2`, `US5.1`, `US6.1`). |
| Category | navigation / input / feedback |

### States

| State | Description | Trigger |
|---|---|---|
| default | Exibe contador consolidado, fila de itens `uncertain` e botões HITL/Exportação | abertura da Tela 3 |
| hover | Destaca o item na fila lateral e simultaneamente pulsa a caixa correspondente no canvas | mouseover no item da fila |
| focus | Item da fila ou botão de ação focado via teclado | tecla `Tab` / `Setas` |
| disabled | Botão `[Confirmar Contagem e Alimentar Golden Dataset]` desabilitado durante submissão | requisição HTTP em voo |
| loading | Indicador *"Salvando amostra YOLO no Golden Dataset..."* no botão principal | clique em confirmar revisão |
| error | Alerta caso o salvamento falhe, mantendo todas as edições em memória local | erro na API |
| empty | Selo verde *"0 detecções duvidosas pendentes — todas as marcações têm alta confiança"* | `uncertainCount === 0` |

### Props / Inputs

| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| `rawAiCount` | `number` | yes | `0` | Contagem bruta original da IA |
| `addedCount` | `number` | yes | `0` | Total de falsos negativos adicionados (`+FN`) |
| `removedCount` | `number` | yes | `0` | Total de falsos positivos removidos (`-FP`) |
| `uncertainDetections` | `DetectionBox[]` | yes | `[]` | Filtra detecções com `0.25 <= confidence < 0.75` |
| `onCommitHitlReview` | `() => Promise<void>` | yes | — | Persiste revisão e exporta amostra para o *Golden Dataset* |
| `onExportReport` | `(format: "pdf" \| "csv") => void` | yes | — | Baixa o laudo auditado |

### Responsive Behaviour

| Breakpoint | Behaviour |
|---|---|
| mobile (<768px) | Painel empilhado abaixo do canvas com barra fixa inferior para o totalizador |
| tablet (768–1024px) | Painel dividido em 2 colunas (Fila de Triagem à esquerda, Ações HITL/Laudo à direita) abaixo do canvas |
| desktop (>1024px) | Coluna fixa à direita (`30%` de largura) com rolagem independente na fila de triagem |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `complementary` (`<aside>`) com contador `role="status"` (`aria-live="polite"`) |
| Keyboard interaction | `Tab` navega pelos itens da fila e botões `[Confirmar]` / `[Remover]` |
| Label / aria-label | Botões explícitos: `aria-label="Confirmar detecção #089"` e `aria-label="Remover falso positivo #089"` |
| Contrast ratio | WCAG 2.1 AA ($\ge 4{,}5:1$) |
| Screen reader | Confirmação de envio ao *Golden Dataset* anunciada via toast `role="status"` |
| Focus management | Foco permanece no próximo item da fila após confirmar ou excluir um item |

### Usage Example

```tsx
<HitlTriageSidebar
  rawAiCount={247}
  addedCount={2}
  removedCount={1}
  uncertainDetections={uncertainList}
  onCommitHitlReview={handleSaveHitl}
  onExportReport={handleExport}
/>
```

---

## ModelEvolutionPanel

| Field | Value |
|---|---|
| Component | `ModelEvolutionPanel` |
| Description | Painel de governança do ciclo *Human-in-the-Loop / Active Learning*, exibindo amostras do *Golden Dataset*, disparo de *fine-tuning* sob demanda e trava de não-regressão $\ge 95\%$ (`US5.2`, `US5.3`). |
| Category | display / input / feedback |

### States

| State | Description | Trigger |
|---|---|---|
| default | Exibe métricas da versão ativa, contagem do *Golden Dataset* e tabela de versões | abertura da Tela 4 |
| hover | Destaque visual no botão `[Iniciar Fine-Tuning Sob Demanda]` e linhas de histórico | mouseover |
| focus | Contorno `2px solid #1D4ED8` nos controles | navegação por `Tab` |
| disabled | Botão de *Fine-Tuning* desabilitado quando há `0` novas amostras no *Golden Dataset* | `pendingGoldenSamples === 0` |
| loading | Barra de progresso de treinamento e validação contra o conjunto de referência | job de *fine-tuning* em execução |
| error | Banner explicativo caso um modelo candidato seja bloqueado pela trava de regressão ($< 95\%$) | candidato reprovado na validação |
| empty | Mensagem inicial antes do primeiro ciclo de *fine-tuning* | histórico com apenas o modelo base `v1.0` |

### Props / Inputs

| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| `activeModel` | `ModelVersionInfo` | yes | — | Dados e acurácia do modelo ativo em produção |
| `goldenDatasetStats` | `GoldenDatasetStats` | yes | — | Total de amostras, `+FN` e `-FP` acumulados |
| `modelHistory` | `ModelVersionInfo[]` | yes | `[]` | Histórico de treinamentos e decisões de promoção |
| `onTriggerFineTuning` | `() => Promise<void>` | yes | — | Inicia job de *fine-tuning* e avaliação de acurácia |

### Responsive Behaviour

| Breakpoint | Behaviour |
|---|---|
| mobile (<768px) | Cartões de KPIs empilhados em 1 coluna; histórico em formato de cards |
| tablet (768–1024px) | KPIs em 2 colunas + tabela de histórico com rolagem horizontal |
| desktop (>1024px) | 3 cartões de KPI no topo + seção de disparo de *fine-tuning* + tabela completa de versões |

### Accessibility

| Requirement | Implementation |
|---|---|
| ARIA role | `region` com tabelas semânticas e status de treinamento `aria-live="polite"` |
| Keyboard interaction | `Tab` e `Enter` acionam o disparo de *fine-tuning* e filtros de histórico |
| Label / aria-label | Badges de status com texto explícito (`Ativo - Promovido`, `Bloqueado < 95%`) |
| Contrast ratio | WCAG 2.1 AA ($\ge 4{,}5:1$) |
| Screen reader | Informa resultado da avaliação do modelo candidato assim que o job conclui |
| Focus management | Mantém foco no resumo do resultado após conclusão do *fine-tuning* |

### Usage Example

```tsx
<ModelEvolutionPanel
  activeModel={activeModel}
  goldenDatasetStats={stats}
  modelHistory={history}
  onTriggerFineTuning={handleFineTune}
/>
```
