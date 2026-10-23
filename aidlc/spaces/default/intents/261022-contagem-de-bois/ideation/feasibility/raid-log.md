# Matriz RAID — Riscos, Premissas, Problemas e Dependências (RAID Log)

Registro de Riscos (*Risks*), Premissas (*Assumptions*), Problemas (*Issues*) e Dependências (*Dependencies*) identificado para o MVP de contagem de bois com IA, alinhado a `intent-capture/intent-statement.md` (`intent-statement.md`) e às respostas confirmadas em `feasibility-questions.md`.

## Sources

- [desc] Initial description: "criar uma aplicação com IA de contagem de bois"
- [scope] Workflow-selected scope: `mvp`.
- [Q1] Resposta à pergunta Q1 em `feasibility-questions.md`: `B (GCP)` — Importação e armazenamento em nuvem apoiados no ecossistema Google Cloud Platform (GCP) para arquivos e vídeos grandes de drones.
- [Q2] Resposta à pergunta Q2 em `feasibility-questions.md`: `A` — Fotos aéreas em alta resolução (1080p a 4K) e vídeos curtos (até 3–5 minutos / até 500 MB por envio), processados sob demanda com suporte a aceleração gráfica.
- [Q3] Resposta à pergunta Q3 em `feasibility-questions.md`: `A` — Equipe enxuta com domínio de visão computacional/IA e desenvolvimento web moderno.
- [Q4] Resposta à pergunta Q4 em `feasibility-questions.md`: `D` — Sem restrições regulatórias específicas nesta fase inicial de validação, utilizando mídias de teste ou autorizadas por parceiros.
- [Q5] Resposta à pergunta Q5 em `feasibility-questions.md`: `D` — Prazo acelerado para demonstração comercial a parceiros, com orçamento flexível para serviços gerenciados que acelerem a entrega.
- [Q6] Resposta à pergunta Q6 em `feasibility-questions.md`: `C` — Conta Google Cloud (GCP) / Firebase disponível (ou preferencial) e acesso a mídias aéreas reais ou públicas para validação.

## Riscos (Risks)

| ID | Descrição do Risco | Probabilidade | Impacto | Estratégia de Mitigação (Estimativa Conservadora) |
|---|---|---|---|---|
| **RSK-01** | **Queda de acurácia abaixo de 95% em cenários complexos de campo:** Aglomeração intensa de bovinos (ex.: próximos a cochos), sombras de árvores ou altura excessiva do drone podem gerar subcontagem (oclusão) ou dupla contagem durante o movimento do vídeo (`intent-statement.md`) [Q2] [Q6]. | Média | Alto | Validar desde cedo com vídeos reais de parceiros [Q6], exibir visualmente as marcações de cada animal detectado/rastreado para conferência rápida do auditor e orientar as condições recomendadas de voo (altura, iluminação e velocidade). |
| **RSK-02** | **Dupla contagem de animais em vídeos em movimento:** Ao longo de um vídeo de 3 a 5 minutos, o mesmo boi permanece visível por vários segundos enquanto o drone se desloca; sem rastreamento contínuo eficaz entre quadros, o mesmo animal pode ser contabilizado múltiplas vezes [Q2]. | Média | Alto | Tratar a contagem em vídeo de forma distinta da contagem em foto estática, garantindo a identificação única de cada animal ao longo da trajetória do vídeo e permitindo inspeção visual do resultado final [Q2] [Q3]. |
| **RSK-03** | **Lentidão ou falha no envio (upload) de vídeos de até 500 MB:** Consultores e auditores em regiões rurais ou conexões instáveis podem enfrentar quedas de conexão ao transferir vídeos em alta resolução (1080p a 4K) [Q1] [Q2]. | Média | Médio | Apoiar o fluxo de entrada no armazenamento em nuvem do ecossistema GCP, permitindo importação direta a partir da nuvem ou envio resiliente com feedback claro de progresso [Q1] [Q6]. |
| **RSK-04** | **Tempo de espera na análise sob demanda com aceleração gráfica:** O acionamento sob demanda de recursos gráficos em nuvem pode sofrer atraso inicial de partida (*cold start*) durante demonstrações ao vivo para parceiros [Q2] [Q5]. | Baixa / Média | Médio | Exibir status claro das etapas de processamento na interface web e manter mídias de demonstração pré-validados além do fluxo em tempo real durante apresentações comerciais [Q5]. |
| **RSK-05** | **Consumo inesperado de custos em nuvem com vídeos de alta resolução:** Testes repetitivos em vídeos 4K usando aceleração gráfica gerenciada podem elevar os custos caso não haja limites de duração e tamanho por envio [Q2] [Q5]. | Baixa | Baixo / Médio | Impor de forma estrita os limites operacionais acordados para o MVP (até 3–5 minutos / até 500 MB por arquivo) e monitorar o uso na conta GCP [Q2] [Q6]. |

## Premissas (Assumptions)

| ID | Premissa (Rotulada Explicitamente) | Justificativa / Base | Impacto se Invalidada |
|---|---|---|---|
| **ASM-01** | **Nitidez e condições mínimas das mídias aéreas (Hipótese Operacional):** Assume-se que os vídeos e fotos avaliados para a meta de $\ge 95\%$ de acurácia (`intent-statement.md`) possuem foco nítido, captura diurna e ângulo aéreo superior/oblíquo adequado para distinguir os animais [assumption] [Q2] [Q6]. | A meta de sucesso em `intent-statement.md` especifica explicitamente "vídeos e imagens aéreas nítidas" [desc]. | Vídeos noturnos, borrados ou gravados a altitudes extremas exigirão recusa assistida ou aviso de baixa confiança na contagem. |
| **ASM-02** | **Conectividade mínima para uso da aplicação web (Hipótese de Uso):** Assume-se que os consultores agropecuários e auditores realizarão a importação/envio das mídias em ambiente com acesso à internet (sede da fazenda ou escritório), já que o modo nativo offline está fora do escopo do MVP (`intent-statement.md`) [assumption] [Q1]. | Fronteira confirmada para a v1 no `intent-statement.md` [scope]. | Caso o consultor precise operar 100% sem internet no meio do pasto, terá de aguardar o retorno à sede/escritório para enviar os arquivos do cartão de memória do drone. |
| **ASM-03** | **Representatividade das mídias de validação (Hipótese de Dados):** Assume-se que as mídias reais obtidas com parceiros e datasets públicos cobrem os padrões visuais típicos dos rebanhos auditados (pelagem clara/escura e pastagens variadas) [assumption] [Q6]. | Confirmada disponibilidade de acesso a mídias aéreas reais ou públicas em Q6 [Q6]. | Se o cenário real de um parceiro divergir fortemente dos dados de teste, será necessário um ciclo curto de ajuste fino (*fine-tuning*) com imagens daquele ambiente [Q3] [Q6]. |

## Problemas e Questões em Aberto (Issues)

| ID | Descrição | Severidade | Status | Ação Necessária |
|---|---|---|---|---|
| **ISS-01** | Nenhum bloqueio técnico, organizacional ou regulatório impeditivo foi identificado nesta etapa de viabilidade [Q4] [Q5] [Q6]. | Nenhuma | Fechado | Seguir para a definição de escopo detalhado (`Scope Definition`) mantendo as restrições de tamanho/duração de mídia e meta de acurácia de $\ge 95\%$. |

## Dependências (Dependencies)

| ID | Dependência | Tipo | Responsável / Origem | Impacto no Cronograma do MVP |
|---|---|---|---|---|
| **DEP-01** | **Ambiente Google Cloud Platform (GCP) / Firebase ativo:** Disponibilidade de projeto configurado no GCP com permissões para armazenamento de arquivos de mídia e execução de cargas de trabalho com aceleração gráfica [Q1] [Q6]. | Infraestrutura Externa | Fundador / Líder do Projeto [Q6] | Necessário para os testes integrados de envio de vídeos grandes (até 500 MB) e execução sob demanda em nuvem. |
| **DEP-02** | **Acesso ao conjunto de vídeos e fotos aéreas reais de drones:** Disponibilização de amostras representativas de sobrevoo de pastos e piquetes com contagem real conhecida (*ground truth*) para aferir a meta de $\ge 95\%$ de acurácia (`intent-statement.md`) [Q6]. | Dados de Validação | Fundador / Parceiros Comerciais [Q6] | Essencial para comprovar a eficácia da solução antes das demonstrações comerciais periódicas. |
| **DEP-03** | **Pesos base de modelos de visão computacional e bibliotecas abertas:** Disponibilidade de modelos pré-treinados de detecção e rastreamento de objetos para especialização na contagem de bovinos em tomada aérea [Q3]. | Tecnológica Externa | Ecossistema Open-Source / Equipe Técnica [Q3] | Baixo risco de bloqueio; amplamente disponível e dominado pela equipe técnica do projeto. |

## Assumptions & Open Questions

- As premissas operacionais (`ASM-01`, `ASM-02`, `ASM-03`) estão documentadas na seção `## Premissas (Assumptions)` acima como hipóteses explícitas a serem acompanhadas nas próximas etapas de definição de escopo e requisitos [assumption] [Q1] [Q2] [Q6].
