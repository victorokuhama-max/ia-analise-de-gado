# Decisões de Stack Tecnológico (Tech Stack Decisions — `u1-agrocount-platform`)

Elaborado a partir de `functional-design/functional-spec.md` (`functional-spec.md`), `functional-design/rules.md` (`rules.md`), `requirements-analysis/requirements.md` (`requirements.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `nfr-requirements-questions.md` [Q1].

## Matriz de Seleção de Tecnologias

| Camada | Tecnologia Selecionada | Requisitos Atendidos | Racional de Escolha |
|---|---|---|---|
| **Linguagem Principal de Backend e IA** | **Python 3.13** (`typing`, `dataclasses`, `sqlite3`, `http.server` / FastAPI-compatible routing) | `NFR1.1`, `NFR2.1`, `NFR6.1`, `NFR6.2` | Ecossistema nativo de Visão Computacional (YOLO / SAHI / ByteTrack) com execução imediata sem dependências binárias frágeis em CI. |
| **Motor de Visão Computacional** | **Pipeline Modular YOLO + SAHI (Slicing NMS) + ByteTrack (Multi-Object IoU Tracker)** | `NFR1.1`, `NFR2.1`, `NFR3.1` | Implementa o fatiamento com sobreposição e fusão NMS para fotos 4K, associação de `track_id` entre quadros para vídeos e adaptador para pesos Ultralytics YOLO em GPU Cloud Run. |
| **Ciclo Human-in-the-Loop & Golden Dataset** | **Gerador Nativo YOLO Normalized Labels (`.txt`) + Provenance JSON + Avaliador de Fine-Tuning ($\ge 95\%$)** | `NFR1.2`, `NFR3.2`, `NFR4.1` | Garante compatibilidade direta com treinamento YOLO na GCP e aplica a trava determinística de não-regressão (`BR5.3`). |
| **Persistência Transacional e Objetos** | **SQLite Transacional Embarcado (Local/CI) + Adaptador Google Cloud Storage / Firestore (GCP)** | `NFR2.2`, `NFR3.2`, `NFR4.1` | Permite execução 100% autocontida e determinística em desenvolvimento/CI com latência $< 5\text{ms}$ e mapeamento direto para Cloud Storage/Firestore na GCP. |
| **Frontend Web e Estúdio de Revisão** | **HTML5 / CSS3 (Design Tokens WCAG 2.1 AA) + TypeScript / JavaScript Modular (Canvas SVG Interativo)** | `NFR2.2`, `NFR5.1` | Renderiza as 4 telas (`mockups.md`), o canvas interativo com codificação tripla (`OK`, `!`, `+`) e os atalhos de teclado (`Setas`, `Espaço`, `Delete`, `N`). |
| **Testes e Cobertura Automatizada** | **Suíte Automatizada Python (`unittest` + `trace` / `pytest` compatível) com Verificador de Cobertura $\ge 80\%$** | `NFR6.2` | Cumpre a postura `test-after` e verifica deterministicamente o piso mínimo de 80% de cobertura de linhas sem depender de pacotes externos indisponíveis no ambiente. |

---

## Alinhamento com a Infraestrutura Alvo (Google Cloud Platform)

- **Compute:** Container `u1-agrocount-platform` implantável no **Google Cloud Run** (`min-instances=0`, `scale-to-zero`).
- **Storage:** Diretório estruturado do *Golden Dataset* (`samples/{sample_id}/frame.txt` e `provenance.json`) espelhando exatamente o layout do bucket `gs://` especificado em `contract-summary.md`.
