# Registro de Restrições (Constraint Register)

Registro consolidado de restrições técnicas, operacionais, organizacionais e regulatórias aplicáveis ao MVP de contagem de bois por visão computacional, derivado de `intent-capture/intent-statement.md` (`intent-statement.md`) e das respostas confirmadas em `feasibility-questions.md`.

## Sources

- [desc] Initial description: "criar uma aplicação com IA de contagem de bois"
- [scope] Workflow-selected scope: `mvp`.
- [Q1] Resposta à pergunta Q1 em `feasibility-questions.md`: `B (GCP)` — Importação e armazenamento em nuvem apoiados no ecossistema Google Cloud Platform (GCP) para arquivos e vídeos grandes de drones.
- [Q2] Resposta à pergunta Q2 em `feasibility-questions.md`: `A` — Fotos aéreas em alta resolução (1080p a 4K) e vídeos curtos (até 3–5 minutos / até 500 MB por envio), processados sob demanda com suporte a aceleração gráfica.
- [Q3] Resposta à pergunta Q3 em `feasibility-questions.md`: `A` — Equipe enxuta com domínio de visão computacional/IA e desenvolvimento web moderno.
- [Q4] Resposta à pergunta Q4 em `feasibility-questions.md`: `D` — Sem restrições regulatórias específicas nesta fase inicial de validação, com uso de mídias de teste ou autorizadas por parceiros.
- [Q5] Resposta à pergunta Q5 em `feasibility-questions.md`: `D` — Prazo acelerado para demonstração comercial a parceiros, com orçamento flexível para serviços gerenciados que acelerem a entrega.
- [Q6] Resposta à pergunta Q6 em `feasibility-questions.md`: `C` — Conta Google Cloud (GCP) / Firebase disponível (ou preferencial) e acesso a mídias aéreas reais ou públicas para validação.

## Restrições Técnicas e Operacionais

| ID | Categoria | Restrição | Origem / Evidência | Impacto no Produto (Nível de Problema / Oportunidade) |
|---|---|---|---|---|
| **CON-T01** | Mídia de Entrada | Os envios na versão inicial limitam-se a fotos aéreas em alta resolução (1080p a 4K) e vídeos curtos de drones (até 3–5 minutos ou até 500 MB por envio). | `feasibility-questions.md` [Q2] | Impõe limites claros de validação no envio de arquivos para evitar travamentos e tempos de espera excessivos durante as vistorias dos consultores. |
| **CON-T02** | Meta de Qualidade (Acurácia) | O sistema deve alcançar acurácia igual ou superior a 95% na contagem de bois em imagens e vídeos aéreos nítidos. | `intent-statement.md` [desc] [Q6] | Exige validação rigorosa com mídias reais de campo e apresentação visual clara das detecções para reduzir o retrabalho de conferência manual. |
| **CON-T03** | Ambiente de Nuvem e Armazenamento | A infraestrutura em nuvem e o armazenamento/importação de mídias grandes devem priorizar o ecossistema Google Cloud Platform (GCP) / Firebase já disponível. | `feasibility-questions.md` [Q1] [Q6] | Direciona a operação do MVP para serviços gerenciados do ecossistema GCP, evitando dispersão em múltiplos provedores de nuvem. |
| **CON-T04** | Capacidade Computacional | O processamento de vídeos aéreos em alta resolução requer ambiente sob demanda com suporte a aceleração gráfica (GPU). | `feasibility-questions.md` [Q2] [Q5] | A execução da análise de vídeo não pode depender exclusivamente do navegador ou do dispositivo do usuário final; deve ocorrer em retaguarda com capacidade gráfica dedicada sob demanda. |
| **CON-T05** | Fronteira de Canal (Web) | A entrega do MVP é restrita a uma aplicação web para upload e análise assíncrona/sob demanda de mídias de drones, excluindo câmeras fixas contínuas (24/7) e aplicativos móveis nativos offline. | `intent-statement.md` [scope] | Mantém o foco na jornada do consultor agropecuário/auditor que processa os arquivos coletados após o voo do drone. |

## Restrições Organizacionais, de Prazo e de Orçamento

| ID | Categoria | Restrição | Origem / Evidência | Impacto no Produto (Nível de Problema / Oportunidade) |
|---|---|---|---|---|
| **CON-O01** | Cronograma e Time-to-Market | Prazo acelerado voltado à realização de demonstrações comerciais periódicas para parceiros de negócio e potenciais clientes. | `intent-statement.md`, `feasibility-questions.md` [Q5] | Prioriza entregas funcionais rápidas e o uso de serviços gerenciados prontos em vez de desenvolvimentos customizados de infraestrutura. |
| **CON-O02** | Orçamento e Modelo de Custos | Orçamento flexível para serviços gerenciados que acelerem a entrega do MVP, condicionado ao uso eficiente sob demanda para demonstrações e primeiras vistorias. | `feasibility-questions.md` [Q5] | Permite contratar recursos gerenciados de nuvem e aceleração gráfica no GCP sem bloqueios financeiros imediatos, mantendo custos proporcionais ao uso. |
| **CON-O03** | Estrutura da Equipe | Desenvolvimento conduzido por equipe enxuta com perfil híbrido (visão computacional/IA e aplicação web), apoiada por ferramentas de IA. | `feasibility-questions.md` [Q3] | Exige simplicidade operacional e baixa carga de manutenção para que uma equipe enxuta sustente tanto a precisão do modelo quanto a experiência web. |

## Restrições Regulatórias, de Privacidade e de Dados

| ID | Categoria | Restrição | Origem / Evidência | Impacto no Produto (Nível de Problema / Oportunidade) |
|---|---|---|---|---|
| **CON-R01** | Conformidade na Fase de Validação | Ausência de exigências regulatórias ou certificações formais bloqueantes no estágio atual do MVP, operando com mídias de teste ou autorizadas por parceiros. | `feasibility-questions.md` [Q4] | Permite focar o esforço inicial na acurácia da contagem ($\ge 95\%$) e na usabilidade para consultorias e auditores rurais. |
| **CON-R02** | Uso Autorizado de Acervos de Campo | As mídias aéreas utilizadas para calibração, testes e demonstrações comerciais devem provir de conjuntos de dados públicos ou de parceiros que autorizaram seu uso. | `feasibility-questions.md` [Q4] [Q6] | Garante segurança jurídica nas demonstrações comerciais sem exigir processos complexos de anonimização nesta primeira versão. |

## Assumptions & Open Questions

- **Premissa CON-A01 (Hipótese sobre limites de envio):** Assume-se que o teto operacional de 3–5 minutos ou 500 MB por vídeo atende integralmente às demonstrações comerciais e vistorias de piquetes/lotes individuais no MVP, podendo um sobrevoo mais longo ser dividido em clipes menores pelo operador do drone [assumption] [Q2].
- **Premissa CON-A02 (Hipótese sobre evolução futura de privacidade):** Embora não haja restrições regulatórias bloqueantes na validação inicial [Q4], assume-se como boa prática que os vídeos enviados por consultores parceiros terão acesso restrito aos usuários autorizados no ambiente em nuvem [assumption] [Q1] [Q4].
