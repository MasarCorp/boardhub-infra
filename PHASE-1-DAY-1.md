# Phase 1 — Day 1: Containerized Local Stack

> **Status:** ✅ Complete
> **Goal:** Any developer runs **one command** and gets the full stack (DB, cache, object storage, API, UI) running locally.
> **Companion docs:** `Magales/MAGALES-MVP-PLAN.md` (overall plan, §6 Docker, §8 Day-by-day)

---

## 1. What changed in this phase

### 1.1 Backend (`Magales/`)
| Change | Why | Files |
|---|---|---|
| **Renamed Java package** `sa.gov.magales` → `tech.platform` | Decoupled the codebase from the Saudi-government namespace; product can now be rebranded without a refactor. 121 files moved + groupId updated. | every `*.java`, `pom.xml`, `application.yml`, `application-prod.yml` |
| **Dropped SQL Server profile** | One database = one schema-truth. Postgres + pgvector covers SaaS + self-hosted. SQL Server license cost + Postgres-only AI extensions made the dual-DB story untenable. | `application-sqlserver.yml` deleted; `mssql-jdbc` + `flyway-sqlserver` deps removed from `pom.xml` |
| **Demoted H2 to test scope** | H2 is a unit-test fixture, not a dev runtime. Devs use Docker Postgres for parity with prod. | `pom.xml` |
| **Postgres-compatible entity columns** | `columnDefinition = "NVARCHAR(N)"` was raw SQL Server DDL embedded in 24 entities — Postgres rejects it. Replaced with `length = N` and `columnDefinition = "TEXT"` for unbounded text. | 24 entity files under `src/main/java/tech/platform/**/entity/` |
| **New `Dockerfile`** | Multi-stage build: Maven 3.9 / JDK 21 → JRE 21 Alpine. Dedicated non-root user. Container-aware JVM flags. Built-in healthcheck on `/api/actuator/health`. | `Magales/Dockerfile`, `Magales/.dockerignore` |

### 1.2 Frontend (`Magales-ui/`)
| Change | Why | Files |
|---|---|---|
| **New `Dockerfile`** | Multi-stage: Node 20 build → nginx 1.27 Alpine. Healthcheck on `/`. | `Magales-ui/Dockerfile`, `Magales-ui/.dockerignore` |
| **New `nginx.conf`** | SPA fallback (`try_files /index.html`), long-cache for hashed assets, no-cache for `index.html`, security headers. | `Magales-ui/nginx.conf` |

### 1.3 New `magales-infra/` repo
| Change | Why | Files |
|---|---|---|
| **`docker-compose.dev.yml`** | One file orchestrates 5 services: postgres (with pgvector), redis, minio, api, ui. Healthchecks, dependency ordering, named volumes. Build contexts reference `../Magales` and `../Magales-ui`. | `magales-infra/docker-compose.dev.yml` |
| **`README.md`** | Quick-start + the three-repo model. | `magales-infra/README.md` |
| **`.gitignore`** | Pre-empts Terraform state, Helm chart packages, local env files. | `magales-infra/.gitignore` |

### 1.4 Things deliberately **not** done in Day 1 (deferred to later days per the plan)
- ❌ Multi-tenancy / `tenant_id` on entities → Day 2
- ❌ Replace `.anyRequest().permitAll()` in SecurityConfig → Day 3
- ❌ Move JWT secret to AWS Secrets Manager (env var only for now) → Day 3
- ❌ Move Nafath in-memory state to Redis → Day 3
- ❌ Refresh-token cookie hardening → Day 3
- ❌ Fix `AuthService:116-117` redundant call → Day 4
- ❌ Flyway baseline migration → Day 2 (Hibernate `ddl-auto: update` for now)
- ❌ Product rebrand (working name "Magales" stays — package is now `tech.platform`)

---

## 2. Prerequisites

You only need **Docker** on your machine. Nothing else.

| Tool | Min version | macOS | Linux | Windows |
|---|---|---|---|---|
| Docker Desktop / Docker Engine | 24+ | `brew install --cask docker` | `apt install docker.io docker-compose-plugin` | Docker Desktop installer |
| Docker Compose | v2 (built into Docker Desktop / `docker compose` plugin) | included | `apt install docker-compose-plugin` | included |

Confirm:
```bash
docker --version          # Docker version 24.x or newer
docker compose version    # Docker Compose version v2.x
```

> You **do not need** local installs of Java, Maven, Node, or Postgres. The stack is fully containerized.

---

## 3. How to run locally

### 3.1 Clone (if you haven't already)
All **three** repos must be checked out as **siblings** under the same parent directory. The compose file uses `../Magales` and `../Magales-ui` as build contexts, so this layout is mandatory.

```bash
cd ~/Documents
mkdir -p masarcorprepos && cd masarcorprepos
git clone <git-url-of-Magales>       Magales
git clone <git-url-of-Magales-ui>    Magales-ui
git clone <git-url-of-magales-infra> magales-infra
```

Final layout:
```
masarcorprepos/
├── Magales/                    ← backend (Spring Boot)
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── pom.xml
│   ├── src/...
│   └── MAGALES-MVP-PLAN.md
├── Magales-ui/                 ← frontend (Angular 17)
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── nginx.conf
│   ├── package.json
│   └── src/...
└── magales-infra/              ← orchestration + IaC (this repo)
    ├── docker-compose.dev.yml  ← orchestrator
    ├── PHASE-1-DAY-1.md        ← this file
    ├── README.md
    └── (terraform/, helm/, .github/ — future phases)
```

### 3.2 Bring the stack up
**From inside `magales-infra/`:**

```bash
cd ~/Documents/masarcorprepos/magales-infra

# First time (or after code changes) — build images then start
docker compose -f docker-compose.dev.yml up --build

# Subsequent runs — start without rebuild
docker compose -f docker-compose.dev.yml up

# Run in the background
docker compose -f docker-compose.dev.yml up -d --build

# Tail logs (in another terminal, also from magales-infra/)
docker compose -f docker-compose.dev.yml logs -f api
```

First build takes ~3–5 minutes (Maven dependency download + Angular build). Subsequent builds are seconds thanks to layer caching.

### 3.3 Stop the stack
```bash
# from magales-infra/

# Stop containers, keep data
docker compose -f docker-compose.dev.yml down

# Stop AND wipe Postgres + MinIO data (full reset)
docker compose -f docker-compose.dev.yml down -v
```

---

## 4. Verify it's working

Once startup logs settle (look for `Started MagalesApplication in X seconds`), open these URLs in a browser:

| Service | URL | Expected |
|---|---|---|
| **UI (Angular)** | http://localhost:4200 | Login page (Arabic by default; toggle EN top-right) |
| **API root** | http://localhost:8080/api/meetings | JSON list of 3 seeded meetings |
| **Specific meeting** | http://localhost:8080/api/meetings/dddddddd-0001-0000-0000-000000000001 | Meeting `BOD-2026-012` details |
| **Swagger UI** | http://localhost:8080/api/swagger-ui.html | Interactive API docs |
| **Actuator health** | http://localhost:8080/api/actuator/health | `{"status":"UP"}` |
| **MinIO console** | http://localhost:9001 | Login `magales` / `magales-dev-secret` |
| **Postgres** | `localhost:5432` (psql client) | DB `magales`, user `magales`, password `magales-dev` |

### 4.1 Test login (API)

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"identifier":"admin","password":"P@ssw0rd"}'
```

Expected: JSON with `accessToken`, `refreshToken`, and `user` object.

### 4.2 Test login (UI)
1. Open http://localhost:4200
2. Form is pre-filled — click **"تسجيل الدخول الآمن" / "Secure Sign In"**
3. You should land on the dashboard with seeded meetings

### 4.3 Seeded users (all share password `P@ssw0rd`)
| Username | Role | Name |
|---|---|---|
| `admin` | `BOARD_MEMBER` | د. خالد السديري |
| `f.otaibi` | `BOARD_MEMBER` | أ. فهد العتيبي |
| `m.otaibi` | `BOARD_SECRETARY` + `SYSTEM_ADMIN` | أ. محمد العتيبي |
| `s.qahtani` | `BOARD_MEMBER` | د. سعد القحطاني |
| `n.mutairi` | `BOARD_MEMBER` | د. نورة المطيري |

---

## 5. Common operations

### 5.1 Connect to Postgres from the host
```bash
psql 'postgresql://magales:magales-dev@localhost:5432/magales'
```

Or with a GUI (DBeaver, TablePlus, pgAdmin): host `localhost`, port `5432`, db `magales`, user `magales`, password `magales-dev`.

### 5.2 Tail individual service logs
```bash
docker compose -f docker-compose.dev.yml logs -f api
docker compose -f docker-compose.dev.yml logs -f ui
docker compose -f docker-compose.dev.yml logs -f postgres
```

### 5.3 Rebuild only one service (e.g. after a backend change)
```bash
docker compose -f docker-compose.dev.yml up -d --build api
```

### 5.4 Shell into a running container
```bash
docker compose -f docker-compose.dev.yml exec api sh
docker compose -f docker-compose.dev.yml exec postgres psql -U magales magales
```

### 5.5 Reset the database (drop schema, lose data)
```bash
docker compose -f docker-compose.dev.yml down -v      # wipe volumes
docker compose -f docker-compose.dev.yml up --build   # bring back fresh
```

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | Something else on host port 8080 (or 4200, 5432, 6379, 9000, 9001) | `lsof -nP -iTCP:8080 \| grep LISTEN`, then kill or change port mapping in `docker-compose.dev.yml` |
| `api` container restarts repeatedly with `Connection refused` to postgres | DB not yet ready — but `depends_on: condition: service_healthy` should handle it | Wait 30s; if persistent, check `docker compose logs postgres` |
| `400 Bad Request` calling `/api/auth/login` | Wrong payload shape — must be `{"identifier":"...","password":"..."}` not `{"email","password"}` | Use the exact body shown in §4.1 |
| UI loads but API calls fail with CORS error | UI loaded from a port other than 4200 | Visit http://localhost:4200 (not e.g. `127.0.0.1`); CORS allowlist is exactly `localhost:4200` and `localhost:3000` |
| `Caused by: org.hibernate.exception.SQLGrammarException` on first startup | Old Postgres volume from before the NVARCHAR fix | `docker compose down -v` then `up --build` |
| `Maven build` step hangs in Dockerfile | First-time dependency download | Wait ~3 min; subsequent builds use layer cache |
| Frontend container won't start | Build output path mismatch with Angular 17 application builder | Verify `dist/ijtimaati-ui/browser/` exists in build stage; the Dockerfile copies from there |
| `JWT_SECRET` errors | The default in `docker-compose.dev.yml` is 53 chars; if you override it, keep ≥ 32 chars | Don't override unless you must; Day 3 introduces real secret management |

### 6.1 Nuke everything and start over
```bash
docker compose -f docker-compose.dev.yml down -v --rmi all --remove-orphans
docker system prune -f
docker compose -f docker-compose.dev.yml up --build
```

---

## 7. What runs where (port reference)

| Service | Container name | Host port | Purpose |
|---|---|---|---|
| postgres | `magales-postgres` | 5432 | Primary database (with pgvector — used in AI phase) |
| redis | `magales-redis` | 6379 | Cache + Nafath state (wired in Day 2/3) |
| minio | `magales-minio` | 9000 (S3 API), 9001 (console) | Object storage (wired in Day 5) |
| api | `magales-api` | 8080 | Spring Boot REST API; context-path `/api` |
| ui | `magales-ui` | 4200 → 80 | Angular SPA served by nginx |

---

## 8. What's next (Day 2)

Per `Magales/MAGALES-MVP-PLAN.md` §8:

1. **Multi-tenancy spine** — `tenant_id` on `BaseEntity`, `Tenant` table, `TenantContext` ThreadLocal, JWT `tid` claim, Hibernate filter, `@PrePersist` listener, sub-domain → tenant resolver, **cross-tenant isolation integration test** (the contract).
2. **Flyway baseline** — generate `V1__init.sql` from current Hibernate auto-DDL; switch prod profile to `validate`.
3. **UI tenant-context endpoint** — `/auth/tenant-context` called before login; runtime branding injection (logo, colors, app name).
4. **Replace hardcoded "Ijtimaati" / "Magales"** strings in UI with tenant-driven config.

When you're ready to start Day 2, say the word and I'll execute it the same way: incremental commits, this doc updated to a `PHASE-1-DAY-2.md`, and a verifiable end state.
