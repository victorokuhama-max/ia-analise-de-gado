# Especificação de Infraestrutura (Infrastructure Specification — `u1-agrocount-platform`)

Elaborado a partir de `nfr-design/performance-design.md` (`performance-design.md`), `nfr-design/security-design.md` (`security-design.md`), `nfr-design/scalability-design.md` (`scalability-design.md`), `nfr-design/reliability-design.md` (`reliability-design.md`), `nfr-design/observability-design.md` (`observability-design.md`), `nfr-design/logical-components.md` (`logical-components.md`), `domain-design/components.md` (`components.md`), `functional-design/functional-spec.md` (`functional-spec.md`), `contract-design/contract-summary.md` (`contract-summary.md`) e `infrastructure-design-questions.md` [Q1].

## 1. Arquitetura de Implantação (Deployment)

| Facet | Choice | Rationale |
|---|---|---|
| **Compute Model** | **Google Cloud Run Serverless (`scale-to-zero`) + Cloud Run Jobs (Fine-Tuning)** | Elimina custo de GPU ociosa (`min-instances=0`, `NFR3.1`) e escala automaticamente sob demanda para inferência 4K e treinamento. |
| **Networking Topology** | **HTTPS TLS 1.3 Ingress Managed Load Balancer (Cloud Run) + Service Account IAM Egress** | Criptografia em trânsito ponta a ponta e acesso aos buckets GCS restrito via Service Account com privilégio mínimo (`NFR6.1`). |
| **Storage Strategy** | **Google Cloud Storage (2 Buckets: `drone-media` e `golden-dataset`) + Banco Transacional (SQLite local / Firestore-Cloud SQL GCP)** | Isola as mídias brutas enviadas das amostras curadas YOLO (`.txt` + `.json`) do *Golden Dataset* (`NFR3.2`, `NFR4.1`). |
| **Environments** | **`local/ci` (SQLite + Local Storage Adapter), `staging` (GCP Homologação), `production` (GCP Produção)** | Paridade comportamental completa entre execução local/CI e nuvem GCP. |
| **IaC Approach** | **Dockerfile Multi-Stage + Manifestos Declarativos Cloud Run (`service.yaml`)** | Versionado junto ao código-fonte na branch `main`. |
| **Resource Sizing** | **API/Web: `2 vCPU / 2 GB RAM` (`min=0, max=4`); Worker GPU: `4 vCPU / 16 GB RAM / 1x NVIDIA L4 (24 GB VRAM)` (`min=0, max=2`)** | Atende ao SLA $\le 5\text{s}$ para fotos 4K (SAHI) e $\le 90\text{s}$ para vídeos de 3 min (ByteTrack) (`NFR2.1`, `NFR2.2`). |

---

## 2. Serviços de Infraestrutura (Infrastructure Services)

| Service | Role | Configuration | Notes |
|---|---|---|---|
| **Google Cloud Run (`agrocount-platform`)** | `compute / load-balancer` | `min-instances: 0`, `max-instances: 4`, `timeout: 300s`, `concurrency: 10` | Serve a API `/api/v1/*` e o Estúdio Web (`LC-01`, `LC-02`, `LC-03`). |
| **Google Cloud Storage (`agrocount-drone-media`)** | `object-store` | Standard Storage, Lifecycle 90d Coldline, limite de objeto $\le 500\text{ MB}$ | Armazena fotos `.jpg/.png` e vídeos `.mp4/.mov` (`DroneMediaObjectStore`). |
| **Google Cloud Storage (`agrocount-golden-dataset`)** | `object-store` | Object Versioning habilitado, layout `samples/{sample_id}/{frame.txt,provenance.json}` | Repositório curado *Human-in-the-Loop* e pesos versionados do modelo YOLO (`GoldenDatasetObjectStore`, `NFR3.2`). |
| **Operational Database (`SQLite / Firestore`)** | `database` | Índices sobre `(farm_id, paddock_id, status)` e `UNIQUE(idempotency_key)` | Garante $p95 < 500\text{ms}$ (`NFR2.2`) e idempotência atômica (`NFR4.1`). |
| **Google Secret Manager / Env Config** | `security` | Injeção via variáveis de ambiente (`AGROCOUNT_*`) em tempo de execução | Zero credenciais fixas no código (`NFR6.1`). |
