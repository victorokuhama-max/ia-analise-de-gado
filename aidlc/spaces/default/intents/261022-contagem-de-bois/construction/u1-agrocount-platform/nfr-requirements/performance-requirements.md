# Requisitos de Desempenho e Precisão (Performance Requirements — `u1-agrocount-platform`)

Elaborado a partir de `functional-design/functional-spec.md` (`functional-spec.md`), `functional-design/rules.md` (`rules.md`), `requirements-analysis/requirements.md` (`requirements.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `nfr-requirements-questions.md` [Q1].

## Sub-Requisitos de Acurácia e Latência (`NFR1.*`, `NFR2.*`)

| ID | Requisito Pai (`requirements.md`) | Especificação Quantitativa | Regra Relacionada (`rules.md`) |
|---|---|---|---|
| **NFR1.1** | `NFR1` | O pipeline de visão computacional (YOLO + SAHI para fotos e YOLO + ByteTrack para vídeos) deve atingir acurácia de contagem $\ge 95\%$ ($\text{Acurácia} = 1 - \frac{|\text{Contagem IA} - \text{Contagem Real}|}{\text{Contagem Real}} \ge 0{,}95$) em mídias diurnas nítidas. | `BR3.1`, `BR3.2` |
| **NFR1.2** | `NFR1` | O avaliador de *fine-tuning* do ciclo *Human-in-the-Loop* deve bloquear qualquer modelo candidato cuja acurácia no conjunto de validação seja $< 95\%$ ou inferior à versão ativa em produção. | `BR5.3` |
| **NFR2.1** | `NFR2` | O tempo de inferência sob demanda em GPU deve ser $\le 5\text{ segundos}$ para fotos aéreas de até 4K ($3840\times 2160$, até 50 MB) com fatiamento SAHI e $\le 90\text{ segundos}$ para vídeos aéreos de até 3 minutos (até 500 MB) com ByteTrack. | `BR3.1`, `BR3.2` |
| **NFR2.2** | `NFR2` | Todas as rotas síncronas da API REST (`/api/v1/farms`, `/api/v1/inspections`, `/api/v1/inspections/{id}/hitl-review`, `/api/v1/models/active`, `/api/v1/inspections/{id}/report`) devem responder com latência $p95 < 500\text{ms}$ e $p99 < 1000\text{ms}$. | `BR1.1`, `BR1.3`, `BR4.3`, `BR6.1` |

---

## Orçamento de Recursos e Benchmarks de Verificação

- **Memória por Instância de API/Worker:** $\le 2\text{ GB}$ RAM para operações CRUD/HITL em CPU; até $16\text{ GB}$ RAM + $1\times \text{NVIDIA L4}$ ($24\text{ GB}$ VRAM) durante janelas ativas de inferência 4K ou *fine-tuning*.
- **Rejeição Rápida Pré-GPU (`BR2.2`):** Validação de tamanho e extensão executada em $< 10\text{ms}$ sem carregar arquivos inválidos na memória de vídeo.
