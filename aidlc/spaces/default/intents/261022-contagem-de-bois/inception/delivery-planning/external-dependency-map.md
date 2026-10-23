# Mapa de Dependências Externas (External Dependency Map)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`), `refined-mockups/mockups.md` (`mockups.md`), `domain-design/components.md` (`components.md`), `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-dependency.md` (`unit-of-work-dependency.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `practices-discovery/team-practices.md` (`team-practices.md`).

## Dependências Externas Mapeadas por Entrega (Bolt)

A tabela abaixo relaciona os recursos de infraestrutura externa descritos em `components.md` ao **Bolt** (passagem de construção que resulta em software executável) que os consome, bem como a estratégia de isolamento local para que a construção e os testes automatizados não sofram bloqueios externos.

| Dependência Externa (`components.md`) | Proprietário | Bolt Consumidor | Lead Time | Estratégia de Isolamento / Contingência para Construção Local e CI |
|---|---|---|---|---|
| **Google Cloud Storage (`DroneMediaObjectStore` & `GoldenDatasetObjectStore`)** | Infraestrutura GCP do Projeto | Bolt 1 (`u1-agrocount-platform`) | Imediato (Local Adapter) | Adaptador de armazenamento configurável: grava em sistema de arquivos local estruturado durante execução local/CI e em buckets `gs://` em produção na GCP. |
| **Google Cloud Run GPU (Inferência YOLO+SAHI/ByteTrack e Fine-Tuning)** | Infraestrutura GCP do Projeto | Bolt 1 (`u1-agrocount-platform`) | Imediato (CPU/Deterministic Adapter) | Motor de visão e avaliador de *fine-tuning* funcionam localmente em CPU / modo determinístico para testes automatizados rápidos (`pytest`) e utilizam GPU sob demanda no Cloud Run em produção. |
| **Banco de Dados Operacional (`OperationalDatabase`)** | Aplicação (`u1-agrocount-platform`) | Bolt 1 (`u1-agrocount-platform`) | Imediato (0 dias) | Persistência relacional/documental embarcada (SQLite / repositório transacional) para testes locais e CI sem dependência de rede externa. |

---

## Status de Desbloqueio para Construção

- **Bloqueios Externos Pendentes:** Nenhum (`0` bloqueios).
- Todas as dependências possuem adaptadores locais determinísticos, permitindo que o `aidlc-developer-agent` execute 100% da construção e da verificação automatizada de `u1-agrocount-platform` sem aguardar provisionamento manual externo.
