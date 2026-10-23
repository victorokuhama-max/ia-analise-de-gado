# Requirements Analysis — Perguntas de Esclarecimento

## Q1. [Produto] Quais são os critérios exatos de validação de entrada para fotos e vídeos de drone no MVP?
A. (Recomendado) Formatos de imagem `.jpg`, `.jpeg`, `.png` (resolução mínima 1920x1080 até 4K/8K, tamanho até 50 MB) e formatos de vídeo `.mp4`, `.mov` (duração até 5 minutos, tamanho máximo 500 MB), rejeitando arquivos corrompidos ou fora do limite com mensagem explicativa
B. Aceitar qualquer tipo de arquivo sem validação prévia de formato ou tamanho
X. Other (please specify)

[Answer]: A

## Q2. [Arquitetura e IA] Como o motor de visão computacional e o ciclo Human-in-the-Loop devem classificar e persistir as detecções e correções?
A. (Recomendado) Cada detecção recebe `confidence` (0.0 a 1.0): `>= 0.75` classificada como `high_confidence` (verde sólido) e `0.25 a 0.74` como `uncertain` (amarelo tracejado para triagem humana). Ao revisar, cada adição (`false_negative_added`) ou remoção (`false_positive_removed`) atualiza a contagem imediatamente e exporta o frame + anotações no formato YOLO (`.txt` normalizado + metadados JSON) para o *Golden Dataset* no Google Cloud Storage para re-treinamento incremental
B. Salvar apenas o número final sem coordenadas de caixas delimitadoras (bounding boxes) e sem alimentar o *Golden Dataset*
X. Other (please specify)

[Answer]: A

## Q3. [Engenharia e NFRs] Quais são as metas quantificáveis de desempenho, confiabilidade e cobertura de testes do MVP?
A. (Recomendado) Acurácia de contagem >= 95% em mídias aéreas nítidas; tempo de inferência <= 5s por foto 4K e <= 90s para vídeo de 3 minutos em GPU sob demanda na GCP; tempo de resposta da API web (leituras/cadastros) p95 < 500ms; disponibilidade >= 99,0% no ambiente Cloud Run; e cobertura de testes automatizados >= 80% de linhas
B. Sem metas quantificáveis de latência, acurácia ou cobertura de testes
X. Other (please specify)

[Answer]: A
