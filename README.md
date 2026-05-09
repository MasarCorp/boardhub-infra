# magales-infra

Operations & infrastructure for the **Magales** platform (working name).

This repo owns everything that is *not* application code:

- **Local dev orchestration** — `docker-compose.dev.yml`
- **AWS infrastructure as code** — `terraform/` (added in week-1, Day 1 per the plan)
- **Self-hosted enterprise deployment** — `helm/` (added in Day 5)
- **CI/CD pipelines** — `.github/workflows/` (added in Day 1)
- **Runbooks & ops docs** — `PHASE-*.md`, `runbooks/`

App code lives in two sibling repos:

| Repo | What it is |
|---|---|
| `Magales/` | Spring Boot 3.3 / Java 21 backend |
| `Magales-ui/` | Angular 17 frontend |
| `magales-infra/` (this repo) | Orchestration + AWS IaC + Helm + CI/CD |

---

## Required directory layout

All three repos must be cloned as **siblings** under the same parent directory:

```
~/Documents/masarcorprepos/   ← (or wherever you keep code)
├── Magales/
├── Magales-ui/
└── magales-infra/             ← you are here
```

The compose file references `../Magales` and `../Magales-ui` as build contexts, so this layout is not optional.

---

## Quick start (local dev)

```bash
# 1. Clone all three repos as siblings (one-time)
cd ~/Documents/masarcorprepos
git clone <git-url-Magales>      Magales
git clone <git-url-Magales-ui>   Magales-ui
git clone <git-url-magales-infra> magales-infra

# 2. Start the full stack
cd magales-infra
docker compose -f docker-compose.dev.yml up --build

# 3. Open the UI
open http://localhost:4200
```

Login with seeded user `admin` / `P@ssw0rd`.

For the complete how-to (verification, troubleshooting, port reference, default credentials), see [`PHASE-1-DAY-1.md`](./PHASE-1-DAY-1.md).

For **what to do when code changes** in either app repo (the rebuild loop, and the future registry-based flow), see [`WORKFLOWS.md`](./WORKFLOWS.md).

---

## Common commands

```bash
# Detached
docker compose -f docker-compose.dev.yml up -d --build

# Tail one service
docker compose -f docker-compose.dev.yml logs -f api

# Stop, keep data
docker compose -f docker-compose.dev.yml down

# Stop and wipe volumes (full DB reset)
docker compose -f docker-compose.dev.yml down -v

# Rebuild only the backend after code change
docker compose -f docker-compose.dev.yml up -d --build api
```

---

## What's running

| Service | Port | Purpose |
|---|---|---|
| postgres (pgvector) | 5432 | Primary DB |
| redis | 6379 | Cache + Nafath state (wired in Day 2/3) |
| minio | 9000 (S3 API), 9001 (console) | Object storage (wired in Day 5) |
| api (Spring Boot) | 8080 | REST API at `/api/*` |
| ui (Angular + nginx) | 4200 → 80 | SPA |

---

## Roadmap (this repo)

| Phase | Adds | Status |
|---|---|---|
| Phase 1 / Day 1 | `docker-compose.dev.yml`, `PHASE-1-DAY-1.md` | ✅ done |
| Phase 1 / Day 2 | Flyway baseline migration | next |
| Phase 1 / Day 3 | `.github/workflows/` (CI: build → trivy → push to ECR) | next |
| Phase 1 / Week 1 | `terraform/` (VPC, ECS, RDS, ElastiCache, S3, ECR, ALB, WAF, Route53, CloudFront, IAM, Secrets, CloudWatch) | week 1 |
| Phase 1 / Day 5 | `helm/` chart for self-hosted enterprise tier | week 1 |

See [`MAGALES-MVP-PLAN.md`](./MAGALES-MVP-PLAN.md) for the full plan and rationale.
