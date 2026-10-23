# Avaliação de Viabilidade (Feasibility Assessment)

Baseado na declaração de intenção documentada em `intent-capture/intent-statement.md` (`intent-statement.md`) e nas respostas confirmadas em `feasibility-questions.md`.

## Sources

- [desc] Initial description: "criar uma aplicação com IA de contagem de bois"
- [scope] Workflow-selected scope: `mvp`.
- [Q1] Resposta à pergunta Q1 em `feasibility-questions.md`: `B (GCP)` — Importação e armazenamento em nuvem apoiados no ecossistema Google Cloud Platform (GCP) para arquivos e vídeos grandes de drones.
- [Q2] Resposta à pergunta Q2 em `feasibility-questions.md`: `A` — Fotos aéreas em alta resolução (1080p a 4K) e vídeos curtos (até 3–5 minutos / até 500 MB por envio), processados sob demanda com suporte a aceleração gráfica.
- [Q3] Resposta à pergunta Q3 em `feasibility-questions.md`: `A` — Equipe com domínio de visão computacional/IA e desenvolvimento de aplicações web modernas, atuando de forma enxuta e apoiada por IA.
- [Q4] Resposta à pergunta Q4 em `feasibility-questions.md`: `D` — Sem restrições regulatórias específicas nesta fase inicial de validação, utilizando mídias de teste ou autorizadas por parceiros.
- [Q5] Resposta à pergunta Q5 em `feasibility-questions.md`: `D` — Prazo acelerado para demonstração comercial a parceiros, com orçamento flexível para serviços gerenciados que acelerem a entrega.
- [Q6] Resposta à pergunta Q6 em `feasibility-questions.md`: `C` — Conta Google Cloud (GCP) / Firebase disponível (ou preferencial) e acesso a mídias aéreas reais ou públicas para validação.

## Resumo Executivo de Viabilidade

A iniciativa descrita em `intent-statement.md` — automatizar o inventário e a contagem de rebanhos bovinos em pastos e piquetes a partir de fotos e vídeos de drones para consultorias agropecuárias, técnicos e auditores — apresenta **alta viabilidade para um MVP** (`mvp`), desde que respeitadas as condições operacionais de captura aérea nítida [desc] [scope] [Q2] [Q6].

| Dimensão Avaliada | Classificação de Viabilidade | Justificativa Principal (Estimativa Conservadora) |
|---|---|---|
| **Viabilidade Técnica e de Visão Computacional** | **Viável com Condições Controladas** | A meta de acurácia igual ou superior a 95% definida em `intent-statement.md` é atingível em fotos (1080p–4K) e vídeos curtos (até 3–5 min / 500 MB) sob condições nítidas de voo, mas requer controle sobre aglomeração extrema de animais e sombras densas (hipótese operacional a ser validada com vídeos reais) [Q2] [Q6]. |
| **Viabilidade Operacional e de Infraestrutura** | **Alta** | A disponibilidade de conta em nuvem (GCP / Firebase) e a escolha por serviços gerenciados com aceleração gráfica sob demanda eliminam a necessidade de montar infraestrutura física própria [Q1] [Q2] [Q5] [Q6]. |
| **Viabilidade de Equipe e Execução** | **Alta** | A equipe combina competências em visão computacional/IA e desenvolvimento web, alinhadas exatamente ao escopo de uma aplicação web enxuta [Q3]. |
| **Viabilidade Financeira e de Cronograma** | **Alta** | O orçamento flexível para uso de recursos gerenciados em nuvem sob demanda viabiliza entregas rápidas voltadas a demonstrações comerciais para parceiros [Q5]. |
| **Viabilidade Regulatória e de Conformidade** | **Alta** | A etapa inicial de validação utiliza mídias de teste e acervos autorizados por parceiros, sem barreiras regulatórias bloqueantes para o lançamento do MVP [Q4]. |

## Análise de Viabilidade Técnica e Operacional

1. **Alinhamento entre o perfil das mídias e a meta de acurácia ($\ge 95\%$):**
   - Conforme estabelecido em `intent-statement.md`, o critério central de sucesso é atingir acurácia igual ou superior a 95% na contagem de bovinos em imagens e vídeos aéreos nítidos, reduzindo o retrabalho de conferência manual [desc].
   - O recorte operacional em fotos aéreas de alta definição (1080p a 4K) e vídeos curtos (até 3 a 5 minutos ou até 500 MB por envio) reduz substancialmente o risco de estouro de tempo de processamento e facilita a inspeção visual dos resultados pelo consultor agropecuário [Q2].
   - **Estimativa conservadora e hipótese técnica:** Em imagens aéreas abertas com boa iluminação e separação visual entre os animais, modelos modernos de visão computacional atingem facilmente patamares superiores a 95%. Contudo, assume-se como **hipótese** que vídeos com movimentação brusca do drone, animais fortemente agrupados (encostados uns nos outros em cochos ou sombras de árvores) ou voos excessivamente altos podem reduzir a precisão bruta, exigindo parâmetros claros de captura para o usuário e destaque visual das marcações na tela para conferência rápida [Q2] [Q6].

2. **Capacidade de processamento e armazenamento de arquivos de drone:**
   - Vídeos de drones de até 500 MB demandam transferência estável e processamento intensivo quadro a quadro [Q1] [Q2].
   - O uso de armazenamento em nuvem já integrado ao ecossistema Google Cloud Platform (GCP) permite receber arquivos grandes sem sobrecarregar a aplicação principal, enquanto o processamento sob demanda com aceleração gráfica garante que a análise de um vídeo curto seja concluída em poucos minutos, sem manter servidores caros ociosos [Q1] [Q2] [Q5] [Q6].

3. **Capacidade de validação com dados reais:**
   - A confirmação de acesso a mídias aéreas reais de parceiros combinadas a conjuntos de dados públicos permite aferir a meta de $\ge 95\%$ de acurácia desde as primeiras entregas funcionais, mitigando o risco de construir uma ferramenta desconectada da realidade do campo [Q6].

## Análise de Viabilidade Econômica, Organizacional e de Prazo

- **Aceleração de entrega (Time-to-Market):** A prioridade de negócio é realizar demonstrações comerciais rápidas para parceiros e usuários do setor agropecuário (`intent-statement.md`). A flexibilidade orçamentária para adotar serviços gerenciados em nuvem evita semanas de trabalho com configuração manual de servidores [Q5] [Q6].
- **Sustentabilidade de custos no MVP:** Como o processamento de vídeo ocorre apenas sob demanda (quando um consultor ou auditor envia uma mídia de até 500 MB), o custo operacional escala proporcionalmente ao volume de vistorias demonstradas, evitando custos fixos elevados durante a validação inicial [Q2] [Q5].
- **Adequação da equipe:** O domínio interno tanto da camada de inteligência artificial quanto da camada de aplicação web elimina dependências de terceiros ou contratações externas para entregar o escopo `mvp` [scope] [Q3].

## Glossário de Termos (Para Leitura Executiva e Não Técnica)

- **Acurácia de contagem ($\ge 95\%$):** Percentual de acerto da contagem automática em relação ao número real de bois presentes na foto ou vídeo aéreo (por exemplo, em um lote real de 100 animais, o sistema identifica corretamente entre 95 e 100 animais).
- **Aceleração gráfica (GPU):** Uso de processadores especializados em cálculos visuais e inteligência artificial que permitem analisar centenas de quadros de um vídeo de drone em minutos, em vez de horas.
- **Processamento sob demanda:** Modelo em que os recursos computacionais em nuvem são acionados apenas no momento em que o usuário envia uma foto ou vídeo para contagem, reduzindo desperdícios financeiros.
- **Oclusão visual:** Situação em que um boi fica parcialmente escondido atrás de outro animal, de árvores ou de sombras no pasto durante o voo do drone.
- **Rastreamento entre quadros:** Capacidade da inteligência artificial de reconhecer que o mesmo boi visto no segundo 1 do vídeo é o mesmo animal visto no segundo 2, evitando que ele seja contado duas vezes enquanto o drone se move.

## Assumptions & Open Questions

- **Premissa 1 (Hipótese de qualidade de captura aérea):** Assume-se que as mídias consideradas "nítidas" para fins da meta de $\ge 95\%$ de acurácia (`intent-statement.md`) serão capturadas em condições de luz diurna, sem neblina densa e a uma altura em que os animais sejam visualmente distinguíveis [assumption] [Q2] [Q6].
- **Premissa 2 (Hipótese de conectividade no momento do envio):** Como o aplicativo móvel nativo offline está fora do escopo desta primeira versão (`intent-statement.md`), assume-se que o consultor ou auditor realizará o envio (upload) das fotos e vídeos a partir de um local com conexão estável à internet (escritório, sede da fazenda com Wi-Fi/Starlink ou rede móvel adequada para arquivos de até 500 MB) [assumption] [Q1] [Q2].
- **Premissa 3 (Hipótese de calibração do modelo):** Assume-se que o conjunto inicial de imagens públicas e vídeos reais de parceiros será suficiente para calibrar a detecção de raças bovinas predominantes no Brasil (como Nelore/zebuínos de pelagem clara e cruzamentos em pastagem verde ou seca) [assumption] [Q6].
