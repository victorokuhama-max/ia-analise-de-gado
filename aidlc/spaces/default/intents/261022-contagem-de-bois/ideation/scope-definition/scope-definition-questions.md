# Scope Definition — Perguntas de Esclarecimento

## [Produto e Fronteira do MVP]

### Q1: Qual é o escopo mínimo viável (jornada principal) que já entrega valor real para o consultor/auditor e para as demonstrações comerciais?
A. Fluxo completo de vistoria: envio/importação de foto ou vídeo curto de drone (via upload ou GCP), execução da contagem com IA, visualização do vídeo/imagem com os bois demarcados na tela, totalizador da contagem e exportação de um laudo/resumo (PDF/CSV)
B. Foco inicial apenas em fotos estáticas aéreas com contagem e marcação visual, deixando vídeos de sobrevoo para uma segunda etapa
C. Painel analítico completo de múltiplas fazendas com histórico comparativo de evolução de rebanho ao longo dos meses antes de liberar o fluxo de laudo individual
D. Apenas um motor de linha de comando / API sem interface visual dedicada para o consultor
X. Other (please specify)

[Answer]: A

### Q2: Entre as capacidades complementares abaixo, o que é obrigatório já na primeira entrega (Must-Have) versus desejável para depois (Should/Could-Have)?
A. Must-Have: revisão/ajuste manual rápido da contagem pelo auditor na tela (caso queira corrigir 1 ou 2 animais em sombra/oclusão antes de emitir o laudo) e indicador de confiança da análise; Should/Could-Have: classificação por categoria/idade do animal e integração com mapas/georreferenciamento (GPS do drone)
B. Must-Have: georreferenciamento automático em mapa interativo e separação de bezerros vs. bois adultos já na primeira versão
C. Must-Have: apenas o número bruto final na tela, sem exibir marcações visuais no vídeo/foto nem permitir ajuste manual pelo auditor
D. Must-Have: emissão de alertas automáticos por WhatsApp/e-mail e relatórios financeiros de cotação da arroba junto com a contagem
X. Other (please specify)

[Answer]: A (incluindo ciclo Human-in-the-Loop / Active Learning no Must-Have: as correções feitas pelo auditor na tela retroalimentam um conjunto curado de dados no GCP para ajuste fino e melhoria contínua do modelo de IA)

### Q3: Quais são as dependências funcionais mínimas de organização e acesso para operar o MVP?
A. Login simples do consultor/auditor e organização básica de cada análise por "Fazenda / Piquete (Lote) / Data da Vistoria", mantendo o histórico das contagens realizadas e seus respectivos vídeos/fotos no GCP
B. Acesso aberto sem login e sem histórico salvo (apenas enviar o arquivo, ver o número na hora e descartar)
C. Sistema completo de gestão multi-empresa com hierarquia de permissões (administrador, supervisor, operador de drone, proprietário da fazenda) e faturamento integrado por assinatura (billing) já no primeiro dia
D. Dependência obrigatória de importação prévia de planilhas cadastrais de brincos eletrônicos (RFID) de cada animal antes de rodar a contagem aérea
X. Other (please specify)

[Answer]: A

## [Priorização, Sequenciamento e Prazos]

### Q4: Qual é a sua preferência de sequenciamento para construir e validar as entregas do MVP?
A. Risco e Valor primeiro (Risk-first + Value-first): validar e demonstrar primeiro o núcleo de visão computacional (contagem em fotos e vídeos de drone atingindo >= 95% de acurácia com visualização das marcações) integrado a uma interface web enxuta, adicionando em seguida a organização de vistorias e exportação de laudo
B. Dependência estrutural primeiro (Dependency-first): construir primeiro todo o cadastro de usuários, permissões, banco de dados de fazendas e relatórios em PDF antes de conectar o motor de contagem por IA
C. Interface primeiro (UI-first): construir todas as telas navegáveis com dados simulados antes de implementar o processamento real de imagens e vídeos no GCP
D. Entregar tudo em um único bloco indivisível apenas no final do projeto, sem entregas intermediárias demonstráveis
X. Other (please specify)

[Answer]: A

### Q5: Existem prazos rígidos (hard deadlines) atrelados a capacidades específicas do MVP?
A. O marco prioritário de curto prazo é ter o fluxo principal de upload + contagem automática em vídeo/foto + visualização demarcada pronto o quanto antes para demonstrações comerciais a parceiros, sem uma data externa fixa imutável, mas com senso de urgência comercial
B. Existe uma feira agropecuária ou contrato com data fixa inegociável que exige todas as funcionalidades (incluindo relatórios e histórico) 100% finalizadas até um dia específico
C. Há um prazo contratual rígido apenas para a entrega de relatórios em PDF, enquanto a contagem por IA pode ficar para depois
D. Não há nenhuma prioridade de curto prazo para demonstração; o foco é puramente acadêmico/experimental
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- **Jornada Mínima Viável (Q1):** Fluxo de ponta a ponta permitindo envio/importação de foto ou vídeo curto de drone (via upload ou GCP), execução da contagem com IA, visualização do vídeo/imagem com os bois demarcados na tela, totalizador da contagem e exportação de laudo/resumo (PDF/CSV).
- **Priorização Must-Have e Ciclo Human-in-the-Loop (Q2):** Inclusão obrigatória (Must-Have) de revisão/ajuste manual na tela pelo auditor, indicador de confiança da análise (destacando quadros/detecções de menor confiança) e **ciclo Human-in-the-Loop (HITL / Active Learning)**, em que cada correção manual do usuário (inclusão de falso negativo ou remoção de falso positivo) é salva como exemplo rotulado no GCP para re-treinamento/ajuste fino (*fine-tuning*) contínuo do modelo. Classificação por idade/categoria e mapa GPS ficam como evolução futura (Should/Could-Have).
- **Organização e Acesso (Q3):** Autenticação simples do consultor/auditor e organização das vistorias por Fazenda, Piquete (Lote) e Data da Vistoria, preservando o histórico no GCP.
- **Sequenciamento da Construção (Q4):** Abordagem *Risk-first + Value-first*, priorizando primeiro o núcleo de visão computacional ($\ge 95\%$ de acurácia em fotos e vídeos) com interface web enxuta e revisão *Human-in-the-Loop*, seguido pela gestão de vistorias e exportação de laudos.
- **Prazos e Marcos (Q5):** Prioridade imediata em disponibilizar o fluxo central para demonstrações comerciais a parceiros, sem data externa rígida imutável, mas com urgência comercial.

A. Looks correct
B. Request changes

[Answer]: Looks correct

