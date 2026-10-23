# Feasibility & Constraints — Perguntas de Esclarecimento

## [Arquitetura e Viabilidade Técnica]

### Q1: Com quais sistemas existentes o MVP precisará se integrar?
A. Nenhum no MVP — a aplicação funcionará de forma independente (standalone), permitindo upload das mídias, visualização da contagem na tela e exportação simples dos resultados (ex.: CSV/PDF)
B. Armazenamento em nuvem já utilizado pelos consultores (ex.: Google Drive, S3 ou links compartilhados) para importação de vídeos grandes de drones
C. Sistemas de gestão pecuária ou ERPs rurais já existentes por meio de API ou importação/exportação padronizada
D. Autenticação corporativa existente (SSO) da consultoria agropecuária
X. Other (please specify)

[Answer]: B (GCP)

### Q2: Qual é o perfil esperado das mídias de drone e do ambiente de execução do modelo de visão computacional no MVP?
A. Fotos aéreas em alta resolução (1080p a 4K) e vídeos curtos (ex.: até 3–5 minutos / até 500 MB por envio), processados sob demanda em ambiente com suporte a aceleração gráfica (GPU em nuvem ou servidor dedicado)
B. Vídeos longos de sobrevoo completo de pastos (ex.: 10 a 30 minutos / múltiplos gigabytes por arquivo), exigindo fila assíncrona robusta e armazenamento de grande volume
C. Processamento executado localmente na máquina do próprio usuário/desenvolvedor durante a fase inicial de validação do MVP, antes de ir para nuvem dedicada
D. Uso de APIs ou serviços gerenciados de inferência sob demanda (serverless GPU) para pagar apenas pelos minutos de vídeo processados
X. Other (please specify)

[Answer]: A

### Q3: Qual é o perfil técnico atual e a disponibilidade da equipe responsável por construir o MVP?
A. Desenvolvedor(es) com domínio de Python (visão computacional / IA) e desenvolvimento web moderno (ex.: TypeScript/React/Next.js ou FastAPI), atuando de forma enxuta e apoiada por IA
B. Foco principal em ciência de dados / visão computacional (Python), preferindo uma interface web mais simples e direta para o MVP
C. Foco principal em engenharia de software web/cloud, buscando utilizar modelos pré-treinados e bibliotecas prontas de detecção e rastreamento (como YOLO + SAHI + ByteTrack) sem treinar modelos do zero inicialmente
D. Combinação equilibrada de engenharia web full-stack e ajuste fino (fine-tuning) de modelos de visão computacional com dataset próprio
X. Other (please specify)

[Answer]: A

## [Conformidade, Custos e Operação]

### Q4: Existem requisitos regulatórios, de confidencialidade ou de residência de dados para as mídias e laudos das fazendas?
A. Conformidade básica com LGPD e controle de acesso por usuário/consultoria (isolamento dos vídeos e laudos de cada cliente, sem exigência de certificações formais no MVP)
B. Sigilo contratual estrito — vídeos e imagens das propriedades não devem ser retidos por longo prazo (exclusão automática após processamento ou período curto) nem usados para treinar modelos públicos
C. Exigência de residência de dados em território nacional (região de nuvem no Brasil) por política de clientes ou auditorias
D. Sem restrições regulatórias específicas nesta fase inicial de validação (uso de mídias de teste ou autorizadas pelos parceiros)
X. Other (please specify)

[Answer]: D

### Q5: Quais são as restrições de orçamento e prazo para a entrega e operação inicial do MVP?
A. Prazo curto (algumas semanas) e orçamento enxuto (bootstrapped), priorizando custos mínimos de infraestrutura (uso sob demanda / free tiers / GPU apenas durante inferência)
B. Prazo moderado (1 a 3 meses) com orçamento controlado para infraestrutura em nuvem e eventual rotulagem/ajuste fino de modelo
C. Sem prazo rígido externo, focado em atingir primeiro a meta de acurácia (>= 95%) com custo operacional próximo de zero em ambiente local/protótipo
D. Prazo acelerado para demonstração comercial a parceiros, com orçamento flexível para serviços gerenciados que acelerem a entrega
X. Other (please specify)

[Answer]: D

### Q6: Qual infraestrutura em nuvem já está em uso e qual é a disponibilidade de mídias reais de drones para validar a meta de >= 95% de acurácia?
A. Ambiente ainda a definir (ou execução local inicial) e uso inicial de datasets públicos de gado aéreo combinados com vídeos de teste obtidos com parceiros
B. Conta AWS já disponível (ou preferencial) e acesso direto a vídeos/imagens reais de drones capturados em fazendas parceiras
C. Conta Google Cloud (GCP) / Firebase já disponível (ou preferencial) e acesso a mídias aéreas reais ou públicas para validação
D. Sem conta de nuvem dedicada ainda e sem acervo próprio de vídeos de drone no momento (dependência de datasets abertos de visão computacional para o MVP inicial)
X. Other (please specify)

[Answer]: C

## Consolidated Summary Confirmation

- **Integrações externas e armazenamento (Q1):** Integração focada no ecossistema Google Cloud Platform (GCP), permitindo importação/armazenamento em nuvem de arquivos e vídeos de drones.
- **Perfil das mídias e processamento de IA (Q2):** Fotos aéreas de alta resolução (1080p a 4K) e vídeos curtos (até 3–5 minutos / até 500 MB por envio), processados sob demanda em ambiente com aceleração gráfica (GPU em nuvem ou servidor dedicado).
- **Perfil técnico da equipe (Q3):** Desenvolvedor(es) com domínio de Python (visão computacional / IA) e desenvolvimento web moderno (ex.: TypeScript/React/Next.js ou FastAPI), operando de forma enxuta e apoiada por IA.
- **Conformidade e restrições regulatórias (Q4):** Sem restrições regulatórias específicas nesta fase inicial de validação do MVP, utilizando mídias de teste ou autorizadas pelos parceiros.
- **Prazo e orçamento (Q5):** Prazo acelerado voltado à demonstração comercial a parceiros, com orçamento flexível para o uso de serviços gerenciados que acelerem a entrega.
- **Infraestrutura em nuvem e dados de validação (Q6):** Conta Google Cloud (GCP) / Firebase já disponível (ou preferencial) e acesso a mídias aéreas reais ou públicas para validar a meta de acurácia igual ou superior a 95%.

A. Looks correct
B. Request changes

[Answer]: Looks correct

