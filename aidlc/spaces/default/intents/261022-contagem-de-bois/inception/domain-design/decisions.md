# Registro de Decisões de Arquitetura (Architecture Decision Records — ADRs)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`), `practices-discovery/team-practices.md` (`team-practices.md`) e `components.md`.

---

## ADR-001: Decomposição em 4 Componentes de Domínio com Isolamento do Ciclo Human-in-the-Loop

### Context
O sistema precisa atender simultaneamente operações transacionais rápidas ($p95 < 500\text{ms}$ para gestão de fazendas, piquetes, fila de triagem e exportação de laudos conforme `NFR2` em `requirements.md`), processamento intensivo de visão computacional em fotos 4K e vídeos de drone (`FR3.1`, `FR3.2`) e um ciclo contínuo de **Human-in-the-Loop / Active Learning** que transforma revisões humanas em amostras de treinamento YOLO e governa o *fine-tuning* (`FR5.1`–`FR5.3`, `stories.md`).

### Decision
Decompor o domínio em quatro componentes lógicos acíclicos documentados em `components.md`:
1. `WebReviewStudioComponent` (Frontend React/TypeScript)
2. `InspectionManagementComponent` (Domínio de Fazendas, Piquetes, Vistorias e Laudos)
3. `HitlActiveLearningComponent` (Domínio de Revisão *Human-in-the-Loop*, *Golden Dataset* e Governança de Modelos)
4. `CattleVisionEngineComponent` (Domínio de Inferência YOLO+SAHI, Rastreamento ByteTrack e Avaliação de Modelos)

### Consequences
- **Positivas:** Cada entidade possui exatamente um componente proprietário; a lógica de curadoria do *Golden Dataset* e a trava de promoção $\ge 95\%$ ficam encapsuladas e 100% testáveis em `HitlActiveLearningComponent` sem depender de infraestrutura pesada durante testes unitários (`team-practices.md`).
- **Negativas:** Exige contratos bem definidos entre `InspectionManagementComponent`, `HitlActiveLearningComponent` e `CattleVisionEngineComponent`.

### Alternatives Rejected
- **Componente Único Monolítico (`SingleBackendComponent`):** Rejeitado por acoplar regras cadastrais e geração de relatórios PDF/CSV à manipulação de tensores de vídeo e rotinas de *fine-tuning*.
- **Decomposição em 10+ Micro-Componentes:** Rejeitada por introduzir sobrecarga desnecessária de coordenação para o escopo `mvp`.

---

## ADR-002: Pipeline Híbrido de Visão Computacional (YOLO + SAHI para Fotos 4K e YOLO + ByteTrack para Vídeos)

### Context
Em tomadas aéreas de drones sobre piquetes extensos (`FR3.1`, `FR3.2`), cada bovino pode ocupar apenas $20\times 20$ a $40\times 40$ pixels em uma imagem 4K, causando falsos negativos severos se a imagem for redimensionada diretamente para $640\times 640$. Já em vídeos de sobrevoo, a simples soma de detecções quadro a quadro causaria múltipla contagem do mesmo animal.

### Decision
Dentro do `CattleVisionEngineComponent`, adotar um pipeline dual orientado pelo tipo de mídia:
- **Fotos estáticas (`.jpg`, `.jpeg`, `.png`):** Inferência fatiada **SAHI (*Slicing Aided Hyper Inference*)** sobre o detector YOLO com sobreposição de recortes (*overlap* de 20%) e fusão via *Non-Maximum Suppression (NMS)*, preservando a resolução de pequenos alvos.
- **Vídeos aéreos (`.mp4`, `.mov`):** Detecção YOLO quadro a quadro acoplada ao algoritmo de associação multi-objeto **ByteTrack**, que mantém identidades persistentes (`track_id`) mesmo quando a confiança cai temporariamente sob sombra de árvores (associando caixas de baixa confiança entre `0.25` e `0.74`).

### Consequences
- **Positivas:** Viabiliza o cumprimento da meta de acurácia $\ge 95\%$ (`NFR1`) tanto em fotos abertas quanto em vídeos em movimento, além de expor naturalmente as detecções de confiança intermediária (`0.25–0.74`) para a fila de triagem humana (`FR3.3`, `FR4.2`).
- **Negativas:** O fatiamento SAHI aumenta o número de passagens de inferência por foto, exigindo aceleração GPU sob demanda para manter a latência $\le 5\text{s}$ (`NFR2`).

### Alternatives Rejected
- **Inferência YOLO padrão em passe único ($640\times 640$) sem SAHI:** Rejeitada porque perde animais pequenos ou distantes em fotos 4K, inviabilizando a meta de $\ge 95\%$.
- **Contagem por regressão de mapa de densidade (*Crowd Counting Density Maps*):** Rejeitada porque não produz caixas delimitadoras individuais auditáveis nem permite edição *Human-in-the-Loop* por animal (`FR4.1`–`FR4.3`).

---

## ADR-003: Formato Padronizado do Golden Dataset (YOLO Normalized Labels + Provenance JSON) e Trava Automática de Promoção ($\ge 95\%$)

### Context
O diferencial técnico central solicitado para a aplicação é o aperfeiçoamento contínuo do modelo com **Human-in-the-Loop (Active Learning)** (`FR5.1`–`FR5.3`). Sem padronização estrita das amostras corrigidas e sem uma trava de validação automatizada, correções ruidosas ou retreinamentos mal calibrados poderiam degradar o modelo em produção.

### Decision
No `HitlActiveLearningComponent`:
1. Toda confirmação de revisão humana gera de forma idempotente (`NFR4`) uma amostra curada (`GoldenDatasetSample`) contendo:
   - O quadro/imagem de referência;
   - O arquivo `.txt` no padrão nativo YOLO (`<class_id> <x_center> <y_center> <width> <height>` com coordenadas normalizadas em $[0, 1]$), contemplando todas as detecções de alta confiança mantidas, as detecções duvidosas confirmadas e os falsos negativos adicionados (`+FN`), já expurgados os falsos positivos removidos (`-FP`);
   - Um manifesto JSON de proveniência (`inspection_id`, `auditor_id`, `model_version`, `false_negatives_added`, `false_positives_removed`, `timestamp`).
2. Todo ciclo de *fine-tuning* avalia o modelo candidato contra o conjunto de validação de referência e **só promove o candidato a `active`** se $\text{validation\_accuracy} \ge 0{,}95$ **e** $\text{validation\_accuracy}_{\text{candidate}} \ge \text{validation\_accuracy}_{\text{active}}$ (`FR5.3`).

### Consequences
- **Positivas:** O *Golden Dataset* fica imediatamente pronto para consumo direto pelo treinador Ultralytics YOLO na GCP sem scripts manuais de conversão; a trava de não-regressão garante segurança operacional e auditabilidade completa.
- **Negativas:** Requer armazenamento estruturado de metadados de proveniência junto a cada arquivo `.txt` de rótulos.

### Alternatives Rejected
- **Armazenar correções apenas como delta numérico (+2 / -1) no banco de dados sem coordenadas espaciais:** Rejeitado porque deltas numéricos não ensinam o detector visual onde estavam os animais omitidos ou os falsos positivos na imagem.
- **Promoção automática incondicional após qualquer treinamento:** Rejeitada pelo risco de *catastrophic forgetting* ou regressão abaixo do piso de 95% (`NFR1`).
