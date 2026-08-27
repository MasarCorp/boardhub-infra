# boardhub-infra

Infrastructure + local dev orchestration for the platform. This repo owns the
`docker-compose.dev.yml` that boots the whole stack, the CI workflows, and the
ops runbooks. **App code lives in sibling repos** — this repo builds them.

## Required layout (siblings)

All repos must sit next to each other under one parent directory. The compose
file builds from `../boardhub`, `../boardhub-ui`, and `../boardhub-ai-services`,
so this is not optional:

```
boardhub/                    ← parent directory
├── boardhub/                ← Spring Boot backend  (built as `api`)
├── boardhub-ui/             ← Angular frontend      (built as `ui`)
├── boardhub-ai-services/    ← Python AI services    (built as `ai-services`)
└── boardhub-infra/          ← you are here
    └── docker-compose.dev.yml
```

Clone them together:

```bash
git clone git@github.com:MasarCorp/boardhub.git
git clone git@github.com:MasarCorp/boardhub-ui.git
git clone git@github.com:MasarCorp/boardhub-ai-services.git
git clone git@github.com:MasarCorp/boardhub-infra.git
```

## 1. Prerequisites

Install one thing per OS, then run one setup command.

| OS | Install | Then run / note |
|---|---|---|
| **macOS** | Docker Desktop | In Docker Desktop → Settings → Resources, give it **≥ 8 GB RAM** (OpenSearch needs headroom). |
| **Windows** | WSL2 (`wsl --install`) + Docker Desktop with the **WSL2 backend** enabled | Clone all repos **inside the WSL2 Linux filesystem** (e.g. `~/masarcorprepos`, **not** `/mnt/c`), and run every command from the **WSL2 shell**. |
| **Linux** | Docker Engine + the compose plugin | `sudo sysctl -w vm.max_map_count=262144` (required by OpenSearch), and `sudo usermod -aG docker $USER` then re-login. |

## 2. Start (one command)

```bash
docker compose -f docker-compose.dev.yml up --build
# ...or detached:
docker compose -f docker-compose.dev.yml up -d --build
```

First boot takes a few minutes (Maven + Angular build + model pulls). Then open:

- **http://localhost:4200** — log in with **`admin`** / **`P@ssw0rd`**
  (seeded `acme` tenant admin; see the runbook for the full user list).

## 3. Verify

```bash
# All 7 services should be Up (and healthy where a healthcheck is defined):
docker compose -f docker-compose.dev.yml ps

# Health probes:
curl http://localhost:8080/api/actuator/health   # api → {"status":"UP"}
curl http://localhost:9200/_cluster/health        # opensearch → {"status":"green"|"yellow"}
curl -I http://localhost:4200                      # ui → HTTP 200
```

Teardown (stop and wipe volumes for a clean DB/search reset):

```bash
docker compose -f docker-compose.dev.yml down -v
```

## 4. What's running

| Service | Port(s) | Purpose |
|---|---|---|
| **postgres** (pgvector) | 5432 | Primary DB; `pgvector` for embeddings |
| **redis** | 6379 | Cache + shared state |
| **minio** | 9000 (S3 API), 9001 (console) | S3-compatible object storage |
| **opensearch** | 9200 | Full-text + vector search |
| **api** (Spring Boot) | 8080 | REST API at `/api/*` |
| **ai-services** (Python) | 8081 | AI: transcription, insights, RAG |
| **ui** (Angular + nginx) | 4200 → 80 | SPA |

## 5. Optional: `.env` for live AI

`.env` is **optional** — every variable has a working default, so the stack
boots without one. You only need it to enable **live AI** calls, by supplying
the provider keys you want:

```bash
# .env (all optional)
OPENROUTER_API_KEY=...
ANTHROPIC_API_KEY=...
GROQ_API_KEY=...
# Self-hosted models via Ollama on the host:
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## 6. Run from pre-built GHCR images (no local build)

CI publishes each app image to **GitHub Container Registry** on every push to
`develop`/`main`:

| Image | Tags |
|---|---|
| `ghcr.io/masarcorp/boardhub-api` | `develop`, `main`, `sha-<short>`, `latest` (on `main`) |
| `ghcr.io/masarcorp/boardhub-ui` | `develop`, `main`, `sha-<short>`, `latest` |
| `ghcr.io/masarcorp/boardhub-ai-services` | `develop`, `main`, `sha-<short>`, `latest` |

These packages are **private**, so authenticate first with a GitHub token that
has the **`read:packages`** scope (classic PAT from GitHub → Settings →
Developer settings, or `gh auth token`):

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u <your-github-username> --password-stdin
```

Pull the images:

```bash
docker pull ghcr.io/masarcorp/boardhub-api:develop
docker pull ghcr.io/masarcorp/boardhub-ui:develop
docker pull ghcr.io/masarcorp/boardhub-ai-services:develop
```

**Run the whole stack from the registry** (skips the source build) by layering
an override that points the app services at the published images. Create
`docker-compose.ghcr.yml` next to the dev compose:

```yaml
# docker-compose.ghcr.yml — run app services from GHCR instead of building
services:
  api:
    image: ghcr.io/masarcorp/boardhub-api:develop
  ui:
    image: ghcr.io/masarcorp/boardhub-ui:develop
  ai-services:
    image: ghcr.io/masarcorp/boardhub-ai-services:develop
```

Then start with both files and skip building:

```bash
docker compose -f docker-compose.dev.yml -f docker-compose.ghcr.yml up -d --no-build
```

The infra services (postgres/redis/minio/opensearch) still come from their own
public images. Verify with the same probes as §3, and tear down with
`docker compose -f docker-compose.dev.yml -f docker-compose.ghcr.yml down -v`.

> Run a **single** image directly? The `api` needs a Postgres sidecar (and
> `-e MANAGEMENT_HEALTH_MAIL_ENABLED=false` to report healthy without a mailer),
> and the `ui` expects an `api` host to be resolvable (it proxies `/api`). The
> images are designed to run **together** — prefer the compose command above.

## Per-OS reminders

- **Windows:** always work from the **WSL2** shell with repos on the Linux
  filesystem — it then behaves exactly like Linux. Building on `/mnt/c` is slow
  and breaks file watching.
- **Linux:** set `vm.max_map_count=262144` (above) or OpenSearch won't start.

## More

- Local URLs, credentials, smoke tests, troubleshooting →
  [`runbooks/local-stack-and-smoke-tests.md`](./runbooks/local-stack-and-smoke-tests.md)
- Code-change → rebuild flow → [`WORKFLOWS.md`](./WORKFLOWS.md)
- Full plan → [`MAGALES-MVP-PLAN.md`](./MAGALES-MVP-PLAN.md)

> **Rebrand note:** some *internal* identifiers still carry the old `magales`
> name (compose container names, the `magales_db` database, seed usernames, and
> the Java package `tech.platform`). Those are load-bearing (volumes, JDBC URLs,
> seeded data) and are being renamed in a separate, dedicated pass — changing
> them here would break existing local volumes and data.
