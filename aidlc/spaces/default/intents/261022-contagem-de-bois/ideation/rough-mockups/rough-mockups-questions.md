# Rough Mockups — Perguntas de Esclarecimento

## [Design de Interface e Experiência do Usuário (UX/UI)]

### Q1: Quais devem ser as telas principais e a estrutura de navegação da aplicação web no MVP?
A. (Recomendado) Estrutura enxuta em 4 visões principais com barra de navegação superior: (1) Painel de Vistorias e Fazendas/Piquetes, (2) Nova Vistoria (Upload / Importação GCP), (3) Estúdio de Revisão Visual e Correção Human-in-the-Loop (Foto/Vídeo demarcado + Resumo + Exportação PDF/CSV) e (4) Painel do Modelo IA (Histórico de correções HITL e disparo de Fine-Tuning)
B. Tela única compacta sem divisão entre painel de histórico e área de revisão do modelo
C. Portal complexo com mais de 10 telas separadas para cadastros administrativos antes de acessar a contagem
D. Interface focada apenas em linha de comando sem navegação visual
X. Other (please specify)

[Answer]: A

### Q2: Na tela de Revisão Visual e Human-in-the-Loop, como o auditor deve interagir com as marcações de bois na foto ou vídeo?
A. (Recomendado) Visualizador interativo em tela dividida (Split-Screen): à esquerda o canvas de imagem/vídeo onde caixas verdes indicam alta confiança (>= 75%) e caixas amarelas/laranjas destacam casos duvidosos (permitindo 1 clique para remover falso positivo ou clicar/arrastar para adicionar falso negativo); à direita o painel com totalizador em tempo real, lista rápida de quadros/alertas de baixa confiança e botão "Confirmar Contagem & Salvar para Treinamento (HITL)"
B. Edição apenas por planilha de coordenadas numéricas (X, Y) sem clicar diretamente sobre a imagem ou vídeo
C. Visualização estática sem possibilidade de clicar nas marcações sobre a foto/vídeo (apenas um campo de texto livre para digitar outro número)
D. Exigir que o usuário redesenhe todas as marcações da imagem do zero a cada vistoria
X. Other (please specify)

[Answer]: A

### Q3: Quais dispositivos (form factors) e padrões visuais devem ser priorizados para uso pelos consultores e auditores?
A. (Recomendado) Web responsivo com prioridade para Desktop/Notebook e Tablet (telas amplas ideais para inspecionar fotos 4K e vídeos de drone e fazer ajustes Human-in-the-Loop), com visual limpo de alto contraste (tema agro/profissional legível mesmo em ambientes claros na sede da fazenda) e suporte móvel para consulta rápida de laudos
B. Exclusivo para telas pequenas de relógios ou celulares na vertical, sem otimização para tela grande de notebook
C. Sem padrão visual ou responsividade definida
D. Interface puramente escura sem contraste para leitura de relatórios impressos
X. Other (please specify)

[Answer]: A

### Q4: Quais requisitos de acessibilidade e atalhos de produtividade devem ser incluídos nos wireframes?
A. (Recomendado) Conformidade com WCAG 2.1 AA: indicadores não dependentes apenas de cor (uso combinado de cor + ícone/borda tracejada para detecções duvidosas), contraste mínimo de 4.5:1 e atalhos de teclado no Estúdio Human-in-the-Loop (ex.: Espaço para pausar/reproduzir vídeo, setas para avançar entre quadros duvidosos, Delete para remover falso positivo e N para adicionar boi)
B. Diferenciação exclusivamente por cor (verde vs. vermelho) sem ícones, rótulos ou atalhos de teclado
C. Operação exclusiva por mouse sem suporte a navegação por teclado (Tab/Enter/Escape)
D. Nenhum requisito de acessibilidade ou produtividade no MVP
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- **Arquitetura de Navegação e Telas Principais (Q1):** Aplicação web organizada em 4 visões principais com barra superior: (1) Painel de Vistorias e Fazendas/Piquetes, (2) Nova Vistoria (Upload / Importação GCP), (3) Estúdio de Revisão Visual e Correção Human-in-the-Loop e (4) Painel de Evolução do Modelo IA (acervo HITL e disparo de Fine-Tuning).
- **Interação no Estúdio Human-in-the-Loop (Q2):** Layout em tela dividida (*Split-Screen*) com canvas interativo de foto/vídeo à esquerda (caixas verdes para alta confiança $\ge 75\%$ e amarelas/tracejadas para casos duvidosos, suportando remoção de falsos positivos com 1 clique e inclusão de falsos negativos por clique/arraste) e painel lateral à direita com totalizador dinâmico, fila de alertas de baixa confiança, envio para o *Golden Dataset* na GCP e exportação de laudo (PDF/CSV).
- **Dispositivos e Padrão Visual (Q3):** Web responsivo otimizado para Desktop/Notebook e Tablet (inspeção de mídias 1080p–4K) com suporte móvel para leitura de laudos, utilizando tema profissional de alto contraste adequado ao uso em escritórios e sedes de fazenda.
- **Acessibilidade e Produtividade (Q4):** Conformidade WCAG 2.1 AA com diferenciação visual redundante (cor + estilo de borda/ícone), contraste mínimo de 4.5:1 e atalhos de teclado dedicados para revisão rápida pelo auditor (`Espaço`, `Setas`, `Delete`, `N`).

A. Looks correct
B. Request changes

[Answer]: Looks correct

