# BoardHub on Kubernetes — kubectl runbook

Plain, portable manifests that deploy the whole BoardHub stack on **any**
Kubernetes cluster (EKS, GKE, Alibaba ACK, Oracle OKE, kind, minikube). No Helm,
no Kustomize, no cloud-specific fields.

> These manifests were validated with `kubectl apply --dry-run=client` only.
> **No cloud access was used to test them — validate on your own cluster.**

The topology mirrors `docker-compose.dev.yml` (main branch): 7 services.

| Component | Kind | Image | Port(s) | Persistence |
|---|---|---|---|---|
| postgres | StatefulSet | `pgvector/pgvector:pg15` | 5432 | 5Gi PVC |
| redis | StatefulSet | `redis:7-alpine` | 6379 | 1Gi PVC (AOF) |
| minio | StatefulSet | `minio/minio:latest` | 9000, 9001 | 10Gi PVC |
| opensearch | StatefulSet | `opensearchproject/opensearch:2.17.1` | 9200 | 10Gi PVC |
| api | Deployment | `ghcr.io/masarcorp/boardhub-api:develop` | 8080 | — |
| ai-services | Deployment | `ghcr.io/masarcorp/boardhub-ai-services:develop` | 8081 | 10Gi PVC (model cache) |
| ui | Deployment | `ghcr.io/masarcorp/boardhub-ui:develop` | 80 | — |

Everything runs in the `boardhub` namespace. Services talk to each other by
in-cluster DNS Service name (`postgres`, `redis`, `minio`, `opensearch`, `api`,
`ai-services`) — no hardcoded IPs.

---

## 1. Prerequisites

- **kubectl** ≥ 1.24 and a working kubeconfig (`kubectl get nodes` succeeds).
- A running **Kubernetes cluster** with at least ~4 vCPU / ~6 GiB allocatable
  (OpenSearch + the JVM api + ai-services are the heavy ones).
- A **default StorageClass** for dynamic PVC provisioning
  (`kubectl get storageclass` shows one marked `(default)`). If none is default,
  see [Per-cloud notes](#6-per-cloud-notes).
- Ability to set **`vm.max_map_count=262144`** for OpenSearch. The manifest does
  this with a privileged initContainer; if your cluster blocks privileged pods,
  use the node-level workaround in [Per-cloud notes](#6-per-cloud-notes).
- A **GitHub token with `read:packages`** — the `ghcr.io/masarcorp/*` images are
  private.

---

## 2. Create namespace, pull secret, and app secret

```bash
# 2a. Namespace
kubectl apply -f k8s/namespace.yaml

# 2b. GHCR image pull secret (private images). Use a PAT with read:packages.
kubectl create secret docker-registry ghcr-creds \
  --namespace boardhub \
  --docker-server=ghcr.io \
  --docker-username='<your-github-username>' \
  --docker-password='<GHCR_TOKEN>' \
  --docker-email='<you@example.com>'

# 2c. App secret. PREFERRED: create it imperatively (values never touch git).
#     The full command with every key is in k8s/secret.example.yaml.
kubectl create secret generic boardhub-secrets \
  --namespace boardhub \
  --from-literal=POSTGRES_DB=magales \
  --from-literal=POSTGRES_USER=magales \
  --from-literal=POSTGRES_PASSWORD='CHANGE-ME' \
  --from-literal=DB_USER=magales \
  --from-literal=DB_PASSWORD='CHANGE-ME' \
  --from-literal=JWT_SECRET='CHANGE-ME-32-chars-or-more-please-rotate' \
  --from-literal=MINIO_ROOT_USER=magales \
  --from-literal=MINIO_ROOT_PASSWORD='CHANGE-ME-secret' \
  --from-literal=S3_ACCESS_KEY=magales \
  --from-literal=S3_SECRET_KEY='CHANGE-ME-secret' \
  --from-literal=AI_SERVICE_HMAC_SECRET='CHANGE-ME-hmac-32-chars-min' \
  --from-literal=SAYNEE_WEBHOOK_SECRET='' \
  --from-literal=BOOTSTRAP_SUPER_ADMIN_EMAIL='' \
  --from-literal=BOOTSTRAP_SUPER_ADMIN_PASSWORD='' \
  --from-literal=OPENROUTER_API_KEY='' \
  --from-literal=ANTHROPIC_API_KEY='' \
  --from-literal=GROQ_API_KEY=''
```

Constraints (they share credentials): `POSTGRES_USER/PASSWORD` == `DB_USER/PASSWORD`,
`MINIO_ROOT_USER/PASSWORD` == `S3_ACCESS_KEY/SECRET_KEY`, and
`AI_SERVICE_HMAC_SECRET` must be identical for api and ai-services.

> Alternatively, edit `k8s/secret.example.yaml` and
> `kubectl apply -f k8s/secret.example.yaml` — fine for a throwaway eval, but it
> puts secrets in a file. Do not commit real values.

---

## 3. Deploy

Recommended order: **namespace → secrets/config → stateful → apps.**

```bash
# config (namespace + secret already created in step 2)
kubectl apply -f k8s/configmap.yaml

# stateful/infra
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/minio.yaml
kubectl apply -f k8s/opensearch.yaml

# app services
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/ai-services.yaml
kubectl apply -f k8s/ui.yaml
```

Or apply everything at once (kubectl orders by kind well enough; readiness
probes and restarts absorb the startup race):

```bash
kubectl apply -f k8s/
```

> Skip `secret.example.yaml` in a bulk apply if you created the Secret
> imperatively in step 2c (otherwise the template's placeholder values overwrite
> your real ones). e.g. `kubectl apply -f k8s/ --prune` is **not** recommended;
> just delete the example file locally or apply the specific files above.

---

## 4. Verify

```bash
# Watch pods come up (postgres/redis/minio/opensearch first, then apps).
kubectl get pods -n boardhub -w

# All should reach Running + READY 1/1:
kubectl get pods -n boardhub

# If a pod is stuck, inspect it:
kubectl describe pod -n boardhub <pod>
kubectl logs -n boardhub <pod>
```

Hit the health endpoints via port-forward:

```bash
# api → {"status":"UP"}
kubectl port-forward -n boardhub svc/api 8080:8080 &
curl http://localhost:8080/api/actuator/health

# ai-services → health JSON
kubectl port-forward -n boardhub svc/ai-services 8081:8081 &
curl http://localhost:8081/v1/health

# opensearch → cluster health (green/yellow)
kubectl port-forward -n boardhub svc/opensearch 9200:9200 &
curl http://localhost:9200/_cluster/health

# UI in the browser
kubectl port-forward -n boardhub svc/ui 8082:80 &
# open http://localhost:8082
```

(Stop the forwards with `kill %1 %2 …` or `pkill -f port-forward`.)

---

## Exposing the UI

Default is `ClusterIP` (in-cluster only). Two portable ways to expose it — pick one:

**Option A — Ingress (recommended).** Requires an Ingress controller in the
cluster. Edit the host in `k8s/ingress.yaml`, set `ingressClassName` to your
controller, then:

```bash
kubectl apply -f k8s/ingress.yaml
```

All traffic targets the `ui` Service; nginx inside the ui image forwards `/api/`
to the api Service, so one backend covers both.

**Option B — LoadBalancer Service.** Change the `ui` Service in `k8s/ui.yaml`:

```yaml
spec:
  type: LoadBalancer   # was: ClusterIP
```

```bash
kubectl apply -f k8s/ui.yaml
kubectl get svc -n boardhub ui -w   # wait for EXTERNAL-IP
```

> The LoadBalancer **annotation differs per cloud** (internal-vs-internet, health
> checks, etc.). We deliberately do NOT hardcode one. Add the annotation your
> cloud needs under `metadata.annotations` of the `ui` Service.

---

## 5. Teardown

```bash
# Remove workloads but keep the namespace/secret:
kubectl delete -f k8s/

# Or nuke everything including PVCs (wipes DB/search/object data):
kubectl delete namespace boardhub
```

> Deleting the namespace deletes the PVCs and therefore all persisted data.
> To keep data, delete Deployments/StatefulSets but leave the PVCs.

---

## 6. Per-cloud notes

Only three things typically need per-cloud attention. **Not tested on live
clouds — validate on yours.**

| Cloud | Default StorageClass | LoadBalancer / Ingress | vm.max_map_count |
|---|---|---|---|
| **EKS** (AWS) | Install the EBS CSI driver; set `gp3`/`gp2` as default (older clusters have none). | `type: LoadBalancer` → NLB via AWS LB Controller (annotations e.g. `service.beta.kubernetes.io/aws-load-balancer-type: external`). Ingress: `ingressClassName: alb`. | Privileged initContainer usually works on managed node groups; else set via a launch-template/user-data or a node DaemonSet. |
| **GKE** | `standard-rwo` is default — nothing to do. | `type: LoadBalancer` gives a GCP L4 LB out of the box. Ingress: `ingressClassName: gce`. | Works on standard node pools. On **Autopilot**, privileged pods/host sysctls are restricted — prefer a node pool that allows it, or a bootstrap DaemonSet. |
| **Alibaba ACK** | `alicloud-disk-essd` (or `-available`); confirm one is default. | `type: LoadBalancer` provisions an SLB (annotations `service.beta.kubernetes.io/alibaba-cloud-loadbalancer-*`). Ingress: nginx or ALB Ingress. | Privileged initContainer generally allowed on ACK node pools. |
| **Oracle OKE** | `oci-bv` (block volume) — confirm default. | `type: LoadBalancer` provisions an OCI LB (annotations `oci.oraclecloud.com/load-balancer-*`, e.g. shape). Ingress: nginx. | Privileged initContainer works on standard OKE nodes. |

**Setting a StorageClass explicitly** (if you have no default, or want a specific
one): add `storageClassName: <name>` under each PVC's `spec` — that's the
`volumeClaimTemplates` in `postgres.yaml`/`redis.yaml`/`minio.yaml`/`opensearch.yaml`
and the standalone PVC in `ai-services.yaml`.

**If privileged pods / host sysctls are blocked** (some managed/hardened
clusters), remove the `initContainers` block from `k8s/opensearch.yaml` and set
`vm.max_map_count` at the node level instead — e.g. a privileged DaemonSet that
runs `sysctl -w vm.max_map_count=262144`, a node bootstrap script, or the node
image's kernel config. Without this OpenSearch fails its bootstrap memory check.

**Enabling `bootstrap.memory_lock`** (off here for portability): it needs an
unlimited `memlock` ulimit which Kubernetes can't grant portably. If your nodes
allow it, set the env back to `"true"` in `opensearch.yaml` and add
`securityContext.capabilities.add: ["IPC_LOCK"]` plus node-level `LimitMEMLOCK=infinity`.
Heap is pinned via `-Xms512m -Xmx512m`, so leaving it off is safe for correctness.

---

## Notes on values

- **DB name / usernames are `magales`**, not `boardhub` — these are load-bearing
  (JDBC URL, seeded data) and mirror the compose file. A rebrand is a separate pass.
- **Resource requests/limits are tunable starting points**, sized from the compose
  hints (OpenSearch 512m heap, JVM api, heavy faster-whisper). Adjust for your load.
- **ai-services does not connect to Postgres directly** — it reaches the DB
  through the api (`MAGALES_INTERNAL_BASE_URL`), matching the compose env block.
