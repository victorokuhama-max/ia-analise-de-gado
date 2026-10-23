# AgroCount IA — Contagem Bovina com Visão Computacional & *Human-in-the-Loop* (`u1-agrocount-platform`)

Plataforma web e motor de visão computacional para contagem automatizada de gado de corte a partir de fotos 4K e vídeos de drone, equipada com ciclo fechado de **Human-in-the-Loop (Active Learning)** para evolução contínua do modelo no ecossistema Google Cloud Platform (GCP) em regime *scale-to-zero*.

## Arquitetura da Unidade (`U1` / `u1-agrocount-platform`)

1. **`InspectionManagementComponent` (`src/agrocount/service.py`, `src/agrocount/repository.py`)**:
   - Cadastro de Fazendas (`Farm`) e Pastos/Piquetes (`Paddock`) com unicidade de códigos (`BR1.1`–`BR1.3`).
   - Criação idempotente de Inspeções (`Inspection`, `BR2.1`) e exportação de Laudos Oficiais (`AuditReport`) em **PDF** (`%PDF-1.4`) e **CSV** com checksum `SHA-256` (`BR6.1`).
2. **`CattleVisionEngineComponent` (`src/agrocount/vision.py`)**:
   - *Gate* de validação pré-GPU em CPU (`BR2.2`): bloqueia arquivos corrompidos, formatos inválidos, resoluções $< 1280 \times 720$, vídeos $> 600\text{s}$ ou arquivos $> 2\text{ GiB}$ antes de alocar GPU.
   - Inferência fatiada **SAHI** ($640 \times 640$, sobreposição de $20\%$) + fusão global **NMS** ($\text{IoU} \ge 0.50$) para fotos 4K (`BR3.1`).
   - Rastreamento multi-objeto **ByteTrack** (`track_id` persistente com buffer de oclusão de até 30 frames) para vídeos de drone (`BR3.2`).
   - Triagem automática de confiança (`BR3.3`): alta confiança ($\ge 0.75 \rightarrow$ `AI_AUTO`), dúvida da IA ($0.25\text{–}0.74 \rightarrow$ `AI_UNCERTAIN`) e descarte de ruído ($< 0.25$).
3. **`HitlActiveLearningComponent` (`src/agrocount/hitl.py`)**:
   - Processamento transacional e idempotente de lotes de revisão humana (`CONFIRM`, `REMOVE_FALSE_POSITIVE`, `ADD_FALSE_NEGATIVE`) e bloqueio de imutabilidade pós-auditoria (`BR4.1`–`BR4.3`).
   - Curadoria automática do **Golden Dataset** (`BR5.1`): exporta anotações normalizadas no formato **YOLO** (`.txt`: `0 <x_center> <y_center> <width> <height>`) e metadados de proveniência (`.json`) em escrita atômica.
   - Orquestração de *fine-tuning* sob demanda (`BR5.2`) com **Gate de Promoção Sem Regressão** (`BR5.3`: exige `validation_counting_accuracy >= 0.95` e `>= modelo ativo`).
4. **`WebReviewStudioComponent` (`src/agrocount/web/index.html`, `src/agrocount/web/app.js`, `src/agrocount/api.py`)**:
   - Estúdio Web responsivo com 4 telas, codificação tripla de acessibilidade WCAG 2.1 AA (`[✓]` verde sólido, `[?]` âmbar tracejado, `[+H]` azul duplo) e atalhos de teclado (`Setas`, `Espaço`, `Delete`, `N`).

## Como Executar Testes e Cobertura Localmente

```bash
bash scripts/verify.sh
```
