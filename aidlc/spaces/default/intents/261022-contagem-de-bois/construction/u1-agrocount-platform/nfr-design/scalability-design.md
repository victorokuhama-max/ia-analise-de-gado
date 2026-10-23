# Projeto de Escalabilidade e Eficiência de Custos (Scalability Design — `u1-agrocount-platform`)

Elaborado a partir de `nfr-requirements/performance-requirements.md` (`performance-requirements.md`), `nfr-requirements/security-requirements.md` (`security-requirements.md`), `nfr-requirements/scalability-requirements.md` (`scalability-requirements.md`), `nfr-requirements/reliability-requirements.md` (`reliability-requirements.md`), `nfr-requirements/observability-requirements.md` (`observability-requirements.md`), `nfr-requirements/tech-stack-decisions.md` (`tech-stack-decisions.md`), `functional-design/functional-spec.md` (`functional-spec.md`) e `contract-design/contract-summary.md` (`contract-summary.md`).

## 1. Arquitetura Stateless e Scale-to-Zero na GCP (`NFR3.1`)

- **Serviço Stateless:** O processo de aplicação de `u1-agrocount-platform` não retém estado de sessão em memória local entre requisições; todo estado de vistoria, detecções e lotes *Human-in-the-Loop* reside no banco transacional e no armazenamento de objetos (`NFR3.1`).
- **Política de Auto-Scaling (`min-instances = 0`):** No Google Cloud Run, o serviço escala automaticamente de `0` a `N` instâncias sob demanda quando chegam uploads de mídia ou disparos de *fine-tuning*, retornando a `0` instâncias após o término, eliminando gastos com GPU ociosa.

---

## 2. Particionamento do Golden Dataset e Crescimento de Dados (`NFR3.2`)

- **Particionamento por Amostra no Object Store:** Cada revisão *Human-in-the-Loop* confirmada grava seus artefatos em um prefixo imutável `samples/{sample_id}/` contendo `frame.txt` (rótulos YOLO) e `provenance.json`, permitindo escalar para dezenas de milhares de amostras sem contenção de diretório ou lock de arquivo único (`NFR3.2`).
