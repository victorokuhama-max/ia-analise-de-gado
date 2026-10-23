# Projeto de Desempenho e Precisão (Performance Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-requirements/performance-requirements.md` (`performance-requirements.md`), `nfr-requirements/security-requirements.md` (`security-requirements.md`), `nfr-requirements/scalability-requirements.md` (`scalability-requirements.md`), `nfr-requirements/reliability-requirements.md` (`reliability-requirements.md`), `nfr-requirements/observability-requirements.md` (`observability-requirements.md`), `nfr-requirements/tech-stack-decisions.md` (`tech-stack-decisions.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

## 1. Arquitetura de Inferência Fatiada SAHI e Rastreamento ByteTrack (`NFR1.1`, `NFR2.1`)

- **Fatiamento SAHI com Fusão NMS Vetorizada (`yolo_sahi_image`):**
  - Divide fotos aéreas 4K ($3840\times 2160$) em fatias sobrepostas (*overlap ratio* de `0.20`), preserva a escala dos pequenos alvos bovinos e funde detecções redundantes nas bordas das fatias via *Non-Maximum Suppression (NMS)* com limiar $\text{IoU} = 0{,}50$, mantendo acurácia $\ge 95\%$ (`NFR1.1`) e tempo de resposta $\le 5\text{s}$ (`NFR2.1`).
- **Associação Multi-Objeto ByteTrack (`yolo_bytetrack_video`):**
  - Associa caixas de alta confiança ($\ge 0{,}75$) na primeira passagem e caixas de confiança intermediária ($0{,}25\text{–}0{,}74$, ex.: animal passando sob copa de árvore) na segunda passagem, garantindo que cada bovino mantenha um único `track_id` ao longo do vídeo ($\le 90\text{s}$ para vídeos de 3 minutos).

---

## 2. Otimização de Latência da API Web e Consultas (`NFR1.2`, `NFR2.2`)

- **Validação Pré-GPU Fail-Fast (`< 10ms`):** O filtro de borda inspeciona extensão, tamanho em bytes e duração antes de tocar no motor de visão computacional, economizando ciclos de GPU.
- **Índices Compostos e Paginação Cursor/Offset (`p95 < 500ms`):** Consultas de histórico de vistorias utilizam índices sobre `(farm_id, paddock_id, status, created_at DESC)` para garantir resposta $< 50\text{ms}$ local e $p95 < 500\text{ms}$ em rede (`NFR2.2`).
