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

---

## Planning: `/plan` — design, then refute

Before building anything non-trivial, run the work through `plan-and-verify`:

```
/plan roadmap item 4 — auto-linking on upload
```

or directly, for several items at once:

```
Workflow({ name: "plan-and-verify",
           args: ["roadmap item 3 — obligation drift", "fix the Library upload"] })
```

Each item gets a design agent that reads the real code and returns a plan citing file:line, and
then a **skeptic whose job is to refute that plan** — grepping for every endpoint, field, enum and
method it named.

**Why it is worth the run.** On 4 September this was run against three roadmap items. All three
plans came back `NEEDS_WORK`, with **twenty things named that do not exist**: `ApiService.get`,
`AgendaItem.responsibleUserId`, `@Mock` on a static method, repository finders assumed to filter
soft-deletes that do not. Roughly 19 minutes of machine time, no engineer waiting, and every one of
them would otherwise have been found later and more expensively.

The failure it catches is **plausibility, not sloppiness**. Every invented name was the name the
API should have had — which is exactly why reading the plan cannot catch it and grepping can. It is
the same shape as most of the findings in `AI-ROADMAP.md`: raw Lucide glyphs where `app-icon` takes
semantic names, `BusinessException` where the convention was `ResponseStatusException`, a fix
scoped to a text node where markdown puts a `<strong>`.

**Read the verdicts before writing code.** Treat `scopingHoles` and `restraintHoles` as blocking —
those are the ones that become privacy incidents rather than bug reports. `weakTests` names a
proposed test that could pass without exercising anything, which reads as coverage and is worse
than no test.

Design agents are read-only, and implementation stays **sequential** — features here touch the same
few files (the agent's tool list, the assist panel, the API), so parallel edits only conflict. What
parallelises well is the expensive part: reading the code.
