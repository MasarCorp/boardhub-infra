# Update workflows

How code changes in the app repos make their way into the running stack.

## TL;DR

| Where the change is | What you do (from `magales-infra/`) |
|---|---|
| `Magales/` (backend) | `git -C ../Magales pull` → `docker compose -f docker-compose.dev.yml up -d --build api` |
| `Magales-ui/` (frontend) | `git -C ../Magales-ui pull` → `docker compose -f docker-compose.dev.yml up -d --build ui` |
| Both | pull both repos → `docker compose -f docker-compose.dev.yml up -d --build` |
| `docker-compose.dev.yml` itself | `git pull` here → `docker compose -f docker-compose.dev.yml up -d` |

---

## Why it works this way (today)

`docker-compose.dev.yml` references `../Magales` and `../Magales-ui` as **build contexts**, not registry images. So "deploy a new version" locally just means: pull the latest source and rebuild the affected service. No registry, no image tags to bump, no `pull`.

This is intentional for local dev. The registry-based path (build → tag → push → pull) lands with ECR in Phase 1 / Day 3 — see [Registry flow (future)](#registry-flow-future) below.

---

## Local flow (today, no registry)

### Backend changed (`Magales/`)

```bash
# 1. pull the new code
git -C ../Magales pull

# 2. rebuild + restart only the api service
docker compose -f docker-compose.dev.yml up -d --build api

# 3. (optional) watch it boot
docker compose -f docker-compose.dev.yml logs -f api
```

`--build` forces a rebuild from `../Magales` before bringing the container back up. Postgres, Redis, MinIO, and the UI are untouched.

### Frontend changed (`Magales-ui/`)

```bash
git -C ../Magales-ui pull
docker compose -f docker-compose.dev.yml up -d --build ui
```

### Both changed

```bash
git -C ../Magales pull
git -C ../Magales-ui pull
docker compose -f docker-compose.dev.yml up -d --build
```

### Compose file itself changed (this repo)

```bash
git pull
docker compose -f docker-compose.dev.yml up -d
# add --build only if a Dockerfile or build context also changed
```

### Schema-breaking backend change

If the backend change is incompatible with the existing Postgres data (entity rename, dropped column, etc.), wipe the volumes:

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

`-v` drops Postgres and MinIO data. Local-dev only — never run this against anything shared.

### Tail / inspect / shell

```bash
docker compose -f docker-compose.dev.yml ps
docker compose -f docker-compose.dev.yml logs -f api
docker compose -f docker-compose.dev.yml exec api sh
docker compose -f docker-compose.dev.yml exec postgres psql -U magales -d magales
```

---

## Registry flow (future)

Once ECR + CI land (Phase 1 / Day 3), the loop changes:

1. **App repo CI** runs on merge to `main`: build → trivy scan → tag → push to ECR. Tags: `<short-sha>` for traceability, `latest` for the tip of `main`.
2. **`docker-compose.dev.yml`** swaps `build:` for `image:`:
   ```yaml
   api:
     image: ${ECR_HOST}/magales-api:${API_TAG:-latest}
     # build: removed
   ui:
     image: ${ECR_HOST}/magales-ui:${UI_TAG:-latest}
   ```
3. **Rolling a new version** onto the running stack becomes:
   ```bash
   docker compose -f docker-compose.dev.yml pull api
   docker compose -f docker-compose.dev.yml up -d api
   ```

The build/tag/push commands themselves live in each app repo's README — keep them next to the code that produces the image.

---

## See also

- [`docs/CI-PIPELINE.md`](./docs/CI-PIPELINE.md) — reusable GHCR build/publish workflow blueprint
- [`../Magales/README.md`](../Magales/README.md) — backend image build & push
- [`../Magales-ui/README.md`](../Magales-ui/README.md) — UI image build & push
- [`PHASE-1-DAY-1.md`](./PHASE-1-DAY-1.md) — full Day-1 setup
- [`MAGALES-MVP-PLAN.md`](./MAGALES-MVP-PLAN.md) — overall plan, including Day-3 ECR + CI
