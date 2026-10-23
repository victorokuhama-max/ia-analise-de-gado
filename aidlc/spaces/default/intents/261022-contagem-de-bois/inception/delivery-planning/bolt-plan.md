# Plano de Entregas de Construção (Bolt Plan)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`), `refined-mockups/mockups.md` (`mockups.md`), `domain-design/components.md` (`components.md`), `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-dependency.md` (`unit-of-work-dependency.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `contract-design/contract-summary.md` (`contract-summary.md`), `practices-discovery/team-practices.md` (`team-practices.md`) e `delivery-planning-questions.md` [Q1].

## Visão Geral do Sequenciamento de Bolts

Um **Bolt** (uma passagem completa de construção sobre uma parte do trabalho que termina em software executável e verificado) agrupa as unidades planejadas com critérios claros de conclusão. Como o sistema foi consolidado na unidade integrada `U1` (`u1-agrocount-platform`), o plano de entrega executa o **Bolt 1**, que opera simultaneamente como o **walking skeleton** (a menor fatia funcional integrada de ponta a ponta que prova a arquitetura funcionando em conjunto) e como a entrega completa do MVP.

| Bolt | Unidades Incluídas (`unit-of-work.md`) | Walking Skeleton? | Histórias Cobertas (`unit-of-work-story-map.md`) | Executor Responsável |
|---|---|---|---|---|
| **Bolt 1 (`bolt-1-agrocount-platform`)** | `U1` (`u1-agrocount-platform`) | Sim — fatia integrada ponta a ponta | `US1.1` a `US6.1` (`FR1.1`–`FR6.1`, `NFR1`–`NFR6`) | `aidlc-developer-agent` |

---

## Detalhamento do Bolt 1: `u1-agrocount-platform`

### Escopo e Componentes Integrados
- **`InspectionManagementComponent`:** Cadastro de Fazendas e Piquetes, controle de status de Vistorias (`pending`, `processing`, `needs_review`, `reviewed`, `failed`), validação pré-GPU de arquivos de foto ($\le 50\text{ MB}$) e vídeo ($\le 500\text{ MB}$ / $5\text{ min}$) e geração de laudos PDF e CSV.
- **`CattleVisionEngineComponent`:** Inferência fatiada YOLO + SAHI para fotos aéreas de alta resolução, detecção e rastreamento único YOLO + ByteTrack para vídeos de drone e separação automática em `high_confidence` ($\ge 0{,}75$) e `uncertain` ($0{,}25\text{–}0{,}74$).
- **`HitlActiveLearningComponent`:** Submissão idempotente de correções humanas (`+FN` falsos negativos adicionados, `-FP` falsos positivos removidos e confirmação de duvidosos), exportação de anotações normalizadas no formato YOLO (`0 x_center y_center width height`) e manifesto JSON de proveniência para o *Golden Dataset* e *fine-tuning* sob demanda com trava de promoção ($\text{acurácia} \ge 95\%$ e sem regressão).
- **`WebReviewStudioComponent`:** Interface web com as 4 telas (`mockups.md`) e acessibilidade WCAG 2.1 AA.

### Hipótese de Confiança (Confidence Hypothesis)
- Entregar o **Bolt 1** comprova que:
  1. O pipeline de visão computacional classifica corretamente detecções de alta confiança ($\ge 0{,}75$) e isola os casos duvidosos ($0{,}25\text{–}0{,}74$) para revisão rápida;
  2. As edições feitas pelo auditor no Estúdio de Revisão recalculam instantaneamente a contagem auditada e geram amostras `.txt` YOLO + `.json` válidas e idempotentes no *Golden Dataset*;
  3. A trava de governança do *fine-tuning* promove modelos candidatos com acurácia $\ge 95\%$ e bloqueia automaticamente qualquer candidato regressivo.

### Demonstração Esperada e Verificação Integrada (Definition of Done)
- **Demonstração Ponta a Ponta:** Criar uma fazenda e piquete via API/UI $\rightarrow$ enviar mídia aérea validada $\rightarrow$ executar a contagem com IA $\rightarrow$ aplicar revisão *Human-in-the-Loop* (+2 falsos negativos, -1 falso positivo) $\rightarrow$ verificar a amostra salva no *Golden Dataset* $\rightarrow$ executar o ciclo de *fine-tuning* validando a trava $\ge 95\%$ $\rightarrow$ exportar o laudo em PDF e CSV.
- **Critério de Pronto (Definition of Done):** Todos os endpoints de `contract-summary.md` implementados, interface web construída, suíte automatizada `pytest` passando com 100% de sucesso e cobertura de linhas $\ge 80\%$ (`team-practices.md`, `NFR6`).
