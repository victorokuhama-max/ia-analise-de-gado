# Regras Descobertas do Projeto (Discovered Rules)

## Mandated

- ALWAYS incluir o ciclo *Human-in-the-Loop (Active Learning)* na arquitetura técnica do MVP, permitindo que ajustes manuais do auditor na interface web retroalimentem um conjunto curado (*Golden Dataset*) na GCP para melhoria contínua do modelo de contagem de bois.
- ALWAYS priorizar execução sob demanda (*scale-to-zero*) no ecossistema Google Cloud Platform (GCP) para o processamento de vídeos/imagens de drone e para o ajuste fino (*fine-tuning*) do modelo, evitando custos fixos de GPU ociosa.

## Forbidden

- NEVER incluir processamento contínuo 24/7 de câmeras IP/RTSP fixas ou aplicativo móvel nativo offline no escopo desta primeira versão (`mvp`).
