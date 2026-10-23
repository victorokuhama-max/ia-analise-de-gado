# Resumo e Especificação Formal de Contratos (Contract Summary)

Elaborado a partir de `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-dependency.md` (`unit-of-work-dependency.md`), `domain-design/components.md` (`components.md`), `requirements-analysis/requirements.md` (`requirements.md`) e `contract-design-questions.md` [Q1].

## Tabela de Contratos (Contracts Table)

| # | Provider Unit | Consumer | Mechanism | Owner |
|---|---|---|---|---|
| 1 | `u1-agrocount-platform` | `External: public web & API clients` | Synchronous REST/HTTP (OpenAPI 3.1 JSON `/api/v1`) | `u1-agrocount-platform` |
| 2 | `u1-agrocount-platform` | `External: GCP Golden Dataset & YOLO Trainer` | Shared Schema (Normalized YOLO `.txt` + Provenance JSON) | `u1-agrocount-platform` |

---

## Contrato #1: API Pública REST/HTTP (`u1-agrocount-platform` $\rightarrow$ `External: public web & API clients`)

```yaml
openapi: 3.1.0
info:
  title: AgroCount IA — Cattle Counting & Human-in-the-Loop API
  version: 1.0.0
  description: >
    API REST/HTTP da unidade u1-agrocount-platform cobrindo Gestão de Fazendas e Piquetes,
    Ingestão Validada de Mídias de Drone, Inferência YOLO + SAHI / ByteTrack, Revisão
    Human-in-the-Loop (Golden Dataset & Fine-Tuning) e Exportação de Laudos PDF/CSV.
paths:
  /api/v1/farms:
    get:
      summary: Lista todas as fazendas e seus piquetes vinculados (FR1.1)
      responses:
        "200":
          description: Lista de fazendas
    post:
      summary: Cadastra uma nova fazenda e piquetes (FR1.1)
      responses:
        "201":
          description: Fazenda criada
  /api/v1/inspections:
    get:
      summary: Lista vistorias com filtros por fazenda, piquete, status e paginação (FR1.3)
      parameters:
        - name: farm_id
          in: query
          schema: { type: string }
        - name: paddock_id
          in: query
          schema: { type: string }
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, processing, needs_review, reviewed, failed]
      responses:
        "200":
          description: Lista paginada de vistorias
    post:
      summary: Cria vistoria, valida mídia pré-GPU e dispara inferência YOLO+SAHI/ByteTrack (FR1.2, FR2.1, FR2.2, FR3.1, FR3.2)
      parameters:
        - name: Idempotency-Key
          in: header
          required: false
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateInspectionRequest"
      responses:
        "201":
          description: Vistoria criada e processada
        "400":
          description: Mídia rejeitada na validação pré-GPU (formato inválido, arquivo vazio ou > 500 MB)
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
  /api/v1/inspections/{inspection_id}/hitl-review:
    post:
      summary: Submete revisão Human-in-the-Loop (+FN, -FP, confirmação de duvidosos) e exporta amostra para o Golden Dataset (FR4.2, FR4.3, FR5.1)
      parameters:
        - name: inspection_id
          in: path
          required: true
          schema: { type: string }
        - name: Idempotency-Key
          in: header
          required: false
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/HitlReviewSubmission"
      responses:
        "200":
          description: Contagem auditada atualizada e amostra YOLO persistida no Golden Dataset
  /api/v1/models/active:
    get:
      summary: Retorna métricas da versão ativa do modelo, estatísticas do Golden Dataset e histórico de versões (FR5.2)
      responses:
        "200":
          description: Estado atual da governança do modelo e Golden Dataset
  /api/v1/models/fine-tune:
    post:
      summary: Dispara fine-tuning sob demanda com o Golden Dataset e aplica trava de promoção >= 95% (FR5.2, FR5.3)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/FineTuneRequest"
      responses:
        "200":
          description: Resultado do fine-tuning e decisão da trava de não-regressão (promoted vs. rejected_regression)
  /api/v1/inspections/{inspection_id}/report:
    get:
      summary: Exporta o laudo auditado da vistoria em formato PDF ou CSV (FR6.1)
      parameters:
        - name: inspection_id
          in: path
          required: true
          schema: { type: string }
        - name: format
          in: query
          required: true
          schema:
            type: string
            enum: [pdf, csv]
      responses:
        "200":
          description: Conteúdo do relatório auditado em PDF ou CSV
components:
  schemas:
    CreateInspectionRequest:
      type: object
      required: [farm_id, paddock_id, filename, media_size_bytes]
      properties:
        farm_id: { type: string }
        paddock_id: { type: string }
        auditor_id: { type: string }
        filename: { type: string }
        media_size_bytes: { type: integer }
        duration_seconds: { type: number }
        simulated_detections:
          type: array
          items:
            $ref: "#/components/schemas/BoundingBoxInput"
    BoundingBoxInput:
      type: object
      required: [x_center, y_center, width, height, confidence]
      properties:
        track_id: { type: integer }
        frame_index: { type: integer, default: 0 }
        x_center: { type: number, minimum: 0.0, maximum: 1.0 }
        y_center: { type: number, minimum: 0.0, maximum: 1.0 }
        width: { type: number, minimum: 0.001, maximum: 1.0 }
        height: { type: number, minimum: 0.001, maximum: 1.0 }
        confidence: { type: number, minimum: 0.0, maximum: 1.0 }
    HitlReviewSubmission:
      type: object
      required: [auditor_id]
      properties:
        auditor_id: { type: string }
        confirmed_detection_ids:
          type: array
          items: { type: string }
        removed_detection_ids:
          type: array
          items: { type: string }
        added_false_negatives:
          type: array
          items:
            $ref: "#/components/schemas/NormalizedYoloBox"
    NormalizedYoloBox:
      type: object
      required: [x_center, y_center, width, height]
      properties:
        class_id: { type: integer, default: 0 }
        x_center: { type: number, minimum: 0.0, maximum: 1.0 }
        y_center: { type: number, minimum: 0.0, maximum: 1.0 }
        width: { type: number, minimum: 0.001, maximum: 1.0 }
        height: { type: number, minimum: 0.001, maximum: 1.0 }
    FineTuneRequest:
      type: object
      properties:
        candidate_validation_accuracy: { type: number, minimum: 0.0, maximum: 1.0 }
        epochs: { type: integer, default: 25 }
    ErrorResponse:
      type: object
      required: [code, message]
      properties:
        code: { type: string }
        message: { type: string }
        details: { type: object }
```

---

## Contrato #2: Schema do Golden Dataset (`u1-agrocount-platform` $\rightarrow$ `External: GCP Golden Dataset & YOLO Trainer`)

```yaml
shared_schema:
  name: GoldenDatasetSampleContract
  version: 1.0.0
  owner: u1-agrocount-platform
  storage_layout:
    image_path: "gs://<golden-bucket>/samples/{sample_id}/frame.jpg"
    yolo_labels_path: "gs://<golden-bucket>/samples/{sample_id}/frame.txt"
    provenance_json_path: "gs://<golden-bucket>/samples/{sample_id}/provenance.json"
  yolo_label_line_format: "<class_id:int> <x_center:float[0..1]> <y_center:float[0..1]> <width:float(0..1]> <height:float(0..1]>"
  provenance_schema:
    type: object
    required:
      - sample_id
      - batch_id
      - inspection_id
      - auditor_id
      - model_version_used
      - false_negatives_added
      - false_positives_removed
      - uncertain_confirmed
      - final_audited_count
      - created_at
```

---

## Regras de Propriedade, Evolução, Timeouts e Questões em Aberto

### Regras de Propriedade de Contrato (Contract Ownership Rules)
- **Propriedade:** A unidade `u1-agrocount-platform` detém ambos os contratos (OpenAPI `/api/v1` e `GoldenDatasetSampleContract`).
- **Mudanças Aditivas vs. Quebras de Compatibilidade:** Mudanças aditivas (novos campos opcionais nos JSONs de resposta) são permitidas na versão `v1` (consumidores ignoram campos desconhecidos). Qualquer alteração incompatível exige incremento para `/api/v2`.
- **Idempotência, Timeouts e Retentativas (`NFR2`, `NFR4`):**
  - Leituras e submissões de revisão operam com SLA $p95 < 500\text{ms}$ e timeout HTTP de $5\text{s}$.
  - Requisições `POST /api/v1/inspections` e `POST /api/v1/inspections/{id}/hitl-review` aceitam o cabeçalho `Idempotency-Key` para impedir duplicação em caso de retentativa de rede ou clique duplo.

### Questões em Aberto (Open Questions)

| Contract | Question | Blocks |
|---|---|---|
| None | Nenhuma questão pendente — todos os schemas de entrada/saída estão fechados para construção. | None |
