# Planejamento de Entrega e Sequenciamento — Perguntas de Alinhamento (Delivery Planning)

Elaborado a partir de `requirements-analysis/requirements.md` (`requirements.md`), `user-stories/stories.md` (`stories.md`), `refined-mockups/mockups.md` (`mockups.md`), `domain-design/components.md` (`components.md`), `units-generation/unit-of-work.md` (`unit-of-work.md`), `units-generation/unit-of-work-dependency.md` (`unit-of-work-dependency.md`), `units-generation/unit-of-work-story-map.md` (`unit-of-work-story-map.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `practices-discovery/team-practices.md` (`team-practices.md`).

---

## Question 1: Sequenciamento de Entrega (Bolt), Alocação e Critérios de Conclusão

Como devemos organizar o passe de construção (*Bolt* — uma passagem completa de construção sobre uma parte do trabalho que resulta em software executável e verificado) para a unidade `U1` (`u1-agrocount-platform`)?

A. **(Recommended)** **Bolt Único Integrado (`Bolt 1: u1-agrocount-platform` como *Walking Skeleton* Completo, WSJF / Risk-First + Value-First)** — Construir `U1` (`u1-agrocount-platform`) em um único Bolt de ponta a ponta executado pelo `aidlc-developer-agent`, validando simultaneamente os dois maiores riscos técnicos (motor de visão YOLO + SAHI / ByteTrack com triagem de confiança $\ge 0{,}75$ vs. $0{,}25\text{–}0{,}74$ e ciclo *Human-in-the-Loop* com exportação para o *Golden Dataset* e trava de *fine-tuning* $\ge 95\%$) e entregando toda a superfície web e exportação PDF/CSV com suíte automatizada `pytest` atingindo cobertura de linhas $\ge 80\%$.
B. **Múltiplos Bolts Fragmentados sem Verificação Integrada Inicial** — Postergar a integração do ciclo *Human-in-the-Loop* para o final sem validação conjunta.
X. Other (please specify)

[Answer]: A
