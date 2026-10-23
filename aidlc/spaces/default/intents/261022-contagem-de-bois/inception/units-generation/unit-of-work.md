# Definição de Unidades de Trabalho (Units of Work)

Elaborado a partir de `domain-design/components.md` (`components.md`), `domain-design/decisions.md` (`decisions.md`), `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`) e `units-generation-questions.md` [Q1].

## Tabela de Identificação de Unidades (Unit Catalogue)

| Unit ID | Directory | Kind | Complexity | Deployment Model | Components Included (`components.md`) |
|---|---|---|---|---|---|
| `U1` | `u1-agrocount-platform` | `service` | `L` | Standalone / Cloud Run On-Demand (`scale-to-zero`) | `InspectionManagementComponent`, `CattleVisionEngineComponent`, `HitlActiveLearningComponent`, `WebReviewStudioComponent` |

---

## Detalhamento da Unidade `U1` (`u1-agrocount-platform`)

### Descrição e Fronteira
A unidade `U1` (`u1-agrocount-platform`, `kind: service`) empacota a plataforma ponta a ponta **AgroCount IA**, integrando em uma única unidade de trabalho coesa os quatro componentes de domínio definidos em `components.md` e justificados em `decisions.md` (`ADR-001` a `ADR-003`):
1. **`InspectionManagementComponent`:** Gestão de Fazendas (`Farm`), Piquetes (`Paddock`), ciclo de vida de Vistorias (`Inspection`), validação de mídia pré-GPU (`FR2.1`, `FR2.2`) e geração de laudos auditados em PDF e CSV (`AuditReport`, `FR6.1`).
2. **`CattleVisionEngineComponent`:** Motor de visão computacional executando detecção fatiada **YOLO + SAHI** para fotos aéreas de alta resolução (`FR3.1`), detecção e rastreamento único **YOLO + ByteTrack** para vídeos de drone (`FR3.2`) e classificação automática nas faixas de confiança `high_confidence` ($\ge 0{,}75$) e `uncertain` ($0{,}25\text{–}0{,}74$) (`FR3.3`).
3. **`HitlActiveLearningComponent`:** Ciclo **Human-in-the-Loop (Active Learning)** que converte correções humanas (`+FN` falsos negativos adicionados, `-FP` falsos positivos removidos e detecções duvidosas confirmadas) em amostras normalizadas no padrão YOLO (`class_id x_center y_center width height`) acompanhadas de manifesto JSON de proveniência no **Golden Dataset** (`FR5.1`), além de orquestrar o *fine-tuning* sob demanda e impor a trava automática de não-regressão ($\text{accuracy} \ge 0{,}95$ e $\ge \text{modelo ativo}$, `FR5.2`, `FR5.3`).
4. **`WebReviewStudioComponent`:** Aplicação e interface web responsiva com as 4 telas do MVP (Painel de Vistorias, Upload de Mídia, Estúdio de Revisão *Split-Screen* com canvas interativo WCAG 2.1 AA e Painel de Evolução do Modelo IA).

### Responsabilidades e Entregáveis
- Entregar a API REST/HTTP completa em Python (FastAPI + Pydantic) e a camada de apresentação web, mantendo separação modular estrita entre os 4 componentes internos (`components.md`).
- Garantir cobertura automatizada de linhas $\ge 80\%$ (`NFR6`) verificável por comando único de teste.
- Operar de forma 100% compatível com execução *serverless / scale-to-zero* no Google Cloud Run e armazenamento no Google Cloud Storage (`NFR3`).
