# Racional de Risco e Sequenciamento (Risk and Sequencing Rationale)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`), `refined-mockups/mockups.md` (`mockups.md`), `domain-design/components.md` (`components.md`), `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-dependency.md` (`unit-of-work-dependency.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `practices-discovery/team-practices.md` (`team-practices.md`).

## Heurística de Sequenciamento Adotada (WSJF + Walking-Skeleton-First)

Para definir a ordem dos **Bolts** (passagens de construção que entregam fatias executáveis do sistema), aplicamos a combinação de **walking-skeleton-first** (construir primeiro a fatia integrada que conecta todas as camadas de ponta a ponta) com o modelo **WSJF** (*Weighted Shortest Job First* — priorização que divide a soma de valor de negócio, urgência e redução de risco pelo tamanho do trabalho).

| Unidade (`unit-of-work.md`) | Valor de Negócio (1–10) | Criticidade de Tempo (1–10) | Redução de Risco Técnico (1–10) | Custo do Atraso (CoD) | Tamanho Relativo | Score WSJF | Ordem |
|---|---|---|---|---|---|---|---|
| `U1` (`u1-agrocount-platform`) | 10 | 9 | 10 | 29 | 5 (`L`) | **5,8** | **1º (Bolt 1)** |

---

## Mitigação Precoce dos Riscos Técnicos Críticos

1. **Risco de Precisão em Tomadas Aéreas e Dupla Contagem em Vídeo (`FR3.1`, `FR3.2`, `NFR1`):** Mitigado no núcleo do Bolt 1 pela combinação de inferência fatiada SAHI para fotos 4K e rastreamento único ByteTrack (`track_id`) para vídeos.
2. **Risco de Qualidade e Regressão no Ciclo Human-in-the-Loop (`FR5.1`–`FR5.3`):** Mitigado desde o primeiro passe de construção pela geração determinística de rótulos YOLO normalizados no *Golden Dataset* e pela trava de avaliação que exige acurácia $\ge 95\%$ e ausência de regressão antes de promover qualquer modelo candidato.
3. **Conformidade Topológica:** O sequenciamento respeita integralmente o DAG de `unit-of-work-dependency.md` (`u1-agrocount-platform` possui `depends_on: []`, zero desvios topológicos).
