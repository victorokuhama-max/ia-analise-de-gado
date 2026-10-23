# Catálogo de Regras de Negócio (Functional Design Business Rules — `u1-agrocount-platform`)

Elaborado a partir de `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `user-stories/stories.md` (`stories.md`), `requirements-analysis/requirements.md` (`requirements.md`), `domain-design/components.md` (`components.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `functional-design-questions.md` [Q1].

## Bloco Fonte de Verdade de Regras de Negócio (Source-of-Truth YAML Rules)

```yaml
rules:
  - id: BR1.1
    statement: Cadastro validado e acessível de Fazendas e Piquetes com baixa latência.
    category: validation
    applies_to: Farm, Paddock
    trigger: Solicitação de criação ou listagem de Fazenda ou Piquete
    logic: >
      IF o auditor autenticado informa nome válido da Fazenda (>= 2 caracteres), município e UF (2 letras) e ao menos um Paddock vinculado
      THEN persistir Farm e Paddock com resposta p95 < 500ms e disponibilizar em controles acessíveis por teclado com contraste >= 4.5:1 (WCAG 2.1 AA).
    violation_behaviour: Rejeitar com erro de validação 400 informando o campo ausente ou inválido.
    source: FR1.1, NFR2, NFR5, NFR6

  - id: BR1.2
    statement: Máquina de estados e idempotência na criação de Vistorias.
    category: constraint
    applies_to: Inspection
    trigger: Criação ou transição de status de uma Inspection
    logic: >
      IF uma requisição de criação de Inspection é recebida com um idempotencyKey já processado
      THEN retornar a Inspection existente sem duplicar registros; caso contrário, iniciar em status pending e transicionar apenas para processing, needs_review, reviewed ou failed.
    violation_behaviour: Bloquear transição inválida de estado e retornar o registro original em chamadas idempotentes repetidas.
    source: FR1.2, NFR4, NFR6

  - id: BR1.3
    statement: Filtragem paginada do histórico de vistorias e tratamento de lista vazia.
    category: calculation
    applies_to: Inspection
    trigger: Consulta ao histórico de vistorias no painel principal
    logic: >
      IF existem vistorias correspondentes aos filtros (farmId, paddockId, status)
      THEN retornar a página solicitada ordenada por data decrescente em p95 < 500ms;
      IF o resultado for vazio THEN retornar lista vazia acompanhada de metadado de estado vazio orientando a criação da primeira vistoria.
    violation_behaviour: Nunca retornar erro 500 para listas vazias.
    source: FR1.3, NFR2, NFR5

  - id: BR2.1
    statement: Ingestão idempotente de fotos e vídeos de drone para armazenamento.
    category: policy
    applies_to: Inspection
    trigger: Upload web ou importação via URI de bucket GCP de mídia aérea
    logic: >
      IF o arquivo atende aos limites de formato e tamanho e possui chave de idempotência válida
      THEN persistir a referência da mídia no armazenamento de objetos e associá-la à Inspection sem reprocessamento duplicado.
    violation_behaviour: Ignorar reenvios duplicados com a mesma chave de idempotência.
    source: FR2.1, NFR4

  - id: BR2.2
    statement: Validação pré-GPU de formato, integridade, duração e tamanho máximo de mídia.
    category: validation
    applies_to: Inspection
    trigger: Submissão de arquivo de mídia antes da alocação de GPU
    logic: >
      IF mediaSizeBytes <= 0 OR extensão não pertence a {.jpg, .jpeg, .png, .mp4, .mov}
      OR (mediaType == image AND mediaSizeBytes > 52428800)
      OR (mediaType == video AND (mediaSizeBytes > 524288000 OR durationSeconds > 300))
      THEN rejeitar imediatamente antes de acionar inferência em GPU.
    violation_behaviour: Retornar HTTP 400 com código de erro explícito (EMPTY_FILE, UNSUPPORTED_FORMAT, IMAGE_TOO_LARGE, VIDEO_TOO_LARGE ou VIDEO_TOO_LONG), preservando os dados do formulário.
    source: FR2.2, NFR3

  - id: BR3.1
    statement: Inferência fatiada YOLO + SAHI para fotos aéreas de alta resolução.
    category: calculation
    applies_to: DetectionRun, BoundingBoxDetection
    trigger: Processamento de Inspection com mediaType == image
    logic: >
      IF a mídia validada é uma imagem estática (.jpg, .jpeg, .png)
      THEN executar o modo yolo_sahi_image (fatiamento com sobreposição e fusão NMS para pequenos alvos) sob demanda (scale-to-zero) em <= 5 segundos, produzindo coordenadas normalizadas em [0, 1] com meta de acurácia >= 95%.
    violation_behaviour: Marcar Inspection como failed e registrar motivo técnico caso a imagem esteja ilegível.
    source: FR3.1, NFR1, NFR2, NFR3

  - id: BR3.2
    statement: Detecção e rastreamento multi-objeto único YOLO + ByteTrack para vídeos de drone.
    category: calculation
    applies_to: DetectionRun, BoundingBoxDetection
    trigger: Processamento de Inspection com mediaType == video
    logic: >
      IF a mídia validada é um vídeo aéreo (.mp4, .mov)
      THEN executar o modo yolo_bytetrack_video sob demanda em <= 90 segundos (para vídeos de até 3 min), atribuindo trackId único a cada animal e contabilizando animais distintos (deduplicados por trackId) para evitar dupla contagem entre quadros.
    violation_behaviour: Rejeitar dupla contagem do mesmo trackId em quadros distintos.
    source: FR3.2, NFR1, NFR2, NFR3

  - id: BR3.3
    statement: Classificação automática por faixa de confiança para triagem humana.
    category: calculation
    applies_to: BoundingBoxDetection, Inspection
    trigger: Conclusão de cada DetectionRun
    logic: >
      IF detection.confidence >= 0.75 THEN classificar confidenceTier = high_confidence e reviewStatus = auto_accepted;
      IF 0.25 <= detection.confidence < 0.75 THEN classificar confidenceTier = uncertain e reviewStatus = pending_triage;
      IF detection.confidence < 0.25 THEN descartar ruído abaixo do limiar mínimo.
      Se houver qualquer detecção uncertain, definir status da Inspection como needs_review.
    violation_behaviour: Rejeitar coordenadas ou valores de confiança fora do intervalo [0.0, 1.0].
    source: FR3.3

  - id: BR4.1
    statement: Codificação visual tripla e acessível das caixas delimitadoras no Estúdio de Revisão.
    category: policy
    applies_to: BoundingBoxDetection, ReviewSessionState
    trigger: Renderização do CattleReviewCanvas
    logic: >
      IF confidenceTier == high_confidence THEN exibir borda verde sólida (#15803D) + selo OK;
      IF confidenceTier == uncertain THEN exibir borda âmbar tracejada (#D97706) + selo !;
      IF confidenceTier == manual_added THEN exibir borda azul dupla (#1D4ED8) + selo +;
      garantindo conformidade WCAG 2.1 AA sem depender exclusivamente de cor.
    violation_behaviour: Impedir renderização de caixas sem rótulo textual/ícone redundante.
    source: FR4.1, NFR5

  - id: BR4.2
    statement: Triagem rápida de detecções duvidosas por clique ou atalhos de teclado.
    category: policy
    applies_to: BoundingBoxDetection, ReviewSessionState
    trigger: Interação do auditor na fila lateral de triagem ou via teclas Setas, Espaço, Delete e N
    logic: >
      IF o auditor confirma uma detecção uncertain (clique em Confirmar ou tecla Espaço)
      THEN atualizar reviewStatus = confirmed;
      IF o auditor remove uma detecção (clique em Remover ou tecla Delete)
      THEN atualizar reviewStatus = removed_fp.
    violation_behaviour: Ignorar comandos de edição caso a sessão esteja bloqueada durante salvamento.
    source: FR4.2, NFR5

  - id: BR4.3
    statement: Adição de falsos negativos (+FN), remoção de falsos positivos (-FP) e recálculo instantâneo da contagem auditada.
    category: calculation
    applies_to: Inspection, BoundingBoxDetection
    trigger: Adição de nova caixa delimitadora ou remoção de caixa existente pelo auditor
    logic: >
      IF o auditor adiciona manualmente N_fn novas caixas (confidenceTier = manual_added, reviewStatus = added_fn) e remove N_fp caixas incorretas (reviewStatus = removed_fp)
      THEN recalcular finalAuditedCount = (total de detecções originais mantidas/confirmadas) + N_fn, ou equivalentemente rawAiCount + N_fn - N_fp, atualizando os contadores instantaneamente com resposta p95 < 500ms.
    violation_behaviour: Rejeitar caixas manuais com largura ou altura <= 0 ou coordenadas fora de [0, 1].
    source: FR4.3, NFR2

  - id: BR5.1
    statement: Geração e persistência idempotente de amostra YOLO e manifesto de proveniência no Golden Dataset.
    category: policy
    applies_to: HitlCorrectionBatch, GoldenDatasetSample
    trigger: Confirmação da revisão Human-in-the-Loop pelo auditor
    logic: >
      IF o auditor confirma a revisão da vistoria
      THEN criar de forma idempotente um HitlCorrectionBatch e exportar uma GoldenDatasetSample contendo todas as caixas ativas (reviewStatus in {auto_accepted, confirmed, added_fn}) formatadas no padrão YOLO normalizado ("0 x_center y_center width height" com 6 casas decimais) e o arquivo JSON de proveniência, promovendo o status da Inspection para reviewed.
    violation_behaviour: Nunca incluir caixas com reviewStatus == removed_fp no arquivo .txt do Golden Dataset; nunca duplicar amostras em cliques repetidos.
    source: FR5.1, NFR4, NFR6

  - id: BR5.2
    statement: Governança do Painel de Evolução do Modelo e disparo sob demanda de Fine-Tuning.
    category: policy
    applies_to: ModelVersion, GoldenDatasetSample
    trigger: Consulta ao painel do modelo ou solicitação de início de fine-tuning
    logic: >
      IF existem amostras acumuladas no GoldenDatasetSample e a gestora aciona o fine-tuning sob demanda
      THEN executar o job de treinamento combinando o modelo base com as amostras curadas do Golden Dataset em regime scale-to-zero (desligando recursos computacionais imediatamente após o término).
    violation_behaviour: Rejeitar com erro 400 (NO_GOLDEN_SAMPLES_AVAILABLE) caso o fine-tuning seja disparado com zero amostras no Golden Dataset.
    source: FR5.2, NFR2, NFR3

  - id: BR5.3
    statement: Trava automática de validação de acurácia (>= 95%) e não-regressão para promoção de modelo.
    category: constraint
    applies_to: ModelVersion
    trigger: Conclusão da avaliação do modelo candidato após o fine-tuning
    logic: >
      IF candidate.validationAccuracy >= 0.95 AND candidate.validationAccuracy >= activeModel.validationAccuracy
      THEN promover o candidato para status = active e alterar o modelo anterior para status = archived;
      ELSE manter o modelo anterior como status = active e registrar o candidato como status = rejected_regression.
    violation_behaviour: Jamais promover para produção um modelo candidato com acurácia < 0.95 ou inferior à versão ativa.
    source: FR5.3, NFR1, NFR6

  - id: BR6.1
    statement: Exportação de Laudo Auditado oficial em PDF e CSV com memória de cálculo completa.
    category: calculation
    applies_to: AuditReport, Inspection
    trigger: Solicitação de download de relatório em formato pdf ou csv
    logic: >
      IF o auditor solicita a exportação do laudo de uma Inspection
      THEN gerar o artefato no formato solicitado (PDF ou CSV) contendo farmName, paddockName, inspectionId, auditorId, modelVersionUsed, rawAiCount, addedFnCount, removedFpCount, finalAuditedCount, avgConfidence, timestamp e hash SHA-256 de integridade.
    violation_behaviour: Retornar HTTP 404 caso a vistoria não exista ou HTTP 400 caso o formato solicitado não seja pdf ou csv.
    source: FR6.1, NFR2, NFR6
```

---

## Tabela Resumo de Regras de Negócio (Human-Readable Rules Summary)

| Rule ID | Categoria | Entidades Alvo | Resumo da Regra | Requisitos Fonte |
|---|---|---|---|---|
| `BR1.1` | `validation` | `Farm`, `Paddock` | Cadastro validado e acessível de Fazendas e Piquetes ($p95 < 500\text{ms}$, WCAG AA) | `FR1.1`, `NFR2`, `NFR5`, `NFR6` |
| `BR1.2` | `constraint` | `Inspection` | Máquina de estados da vistoria e idempotência na criação | `FR1.2`, `NFR4`, `NFR6` |
| `BR1.3` | `calculation` | `Inspection` | Filtragem paginada por Fazenda/Piquete/Status e estado vazio | `FR1.3`, `NFR2`, `NFR5` |
| `BR2.1` | `policy` | `Inspection` | Upload e importação GCP idempotente de fotos e vídeos | `FR2.1`, `NFR4` |
| `BR2.2` | `validation` | `Inspection` | Validação pré-GPU ($\le 50\text{ MB}$ foto, $\le 500\text{ MB}$ / $5\text{ min}$ vídeo, extensões permitidas) | `FR2.2`, `NFR3` |
| `BR3.1` | `calculation` | `DetectionRun`, `BoundingBoxDetection` | Inferência fatiada YOLO + SAHI para fotos aéreas 4K ($\le 5\text{s}$, $\ge 95\%$) | `FR3.1`, `NFR1`, `NFR2`, `NFR3` |
| `BR3.2` | `calculation` | `DetectionRun`, `BoundingBoxDetection` | Contagem única em vídeo via YOLO + ByteTrack por `trackId` ($\le 90\text{s}$, $\ge 95\%$) | `FR3.2`, `NFR1`, `NFR2`, `NFR3` |
| `BR3.3` | `calculation` | `BoundingBoxDetection`, `Inspection` | Separação em `high_confidence` ($\ge 0{,}75$) e `uncertain` ($0{,}25\text{–}0{,}74$) | `FR3.3` |
| `BR4.1` | `policy` | `BoundingBoxDetection`, `ReviewSessionState` | Codificação visual tripla acessível (cor + borda + selo `OK`/`!`/`+`) | `FR4.1`, `NFR5` |
| `BR4.2` | `policy` | `BoundingBoxDetection`, `ReviewSessionState` | Fila lateral de triagem e confirmação/remoção por 1 clique ou atalho | `FR4.2`, `NFR5` |
| `BR4.3` | `calculation` | `Inspection`, `BoundingBoxDetection` | Adição de `+FN`, remoção de `-FP` e recálculo imediato de `finalAuditedCount` | `FR4.3`, `NFR2` |
| `BR5.1` | `policy` | `HitlCorrectionBatch`, `GoldenDatasetSample` | Exportação idempotente de rótulos YOLO normalizados + JSON para o *Golden Dataset* | `FR5.1`, `NFR4`, `NFR6` |
| `BR5.2` | `policy` | `ModelVersion`, `GoldenDatasetSample` | Painel de evolução do modelo e disparo sob demanda de *fine-tuning* (*scale-to-zero*) | `FR5.2`, `NFR2`, `NFR3` |
| `BR5.3` | `constraint` | `ModelVersion` | Trava automática de promoção: exige acurácia $\ge 95\%$ e ausência de regressão | `FR5.3`, `NFR1`, `NFR6` |
| `BR6.1` | `calculation` | `AuditReport`, `Inspection` | Geração e exportação de laudo auditado em PDF e CSV com hash SHA-256 | `FR6.1`, `NFR2`, `NFR6` |
