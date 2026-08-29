# Runbook — Local stack URLs + smoke test scenarios

> **Audience:** anyone running the full Magales stack locally for the
> first time, or returning to it after a break and wanting a quick
> "is everything healthy + tenancy still works" check.
> **Maintained on:** `develop` (this repo). Update when ports change,
> when new tenancy features ship, or when default credentials change.

---

## 1. Launch the stack

From this repo:

```bash
cd ~/Documents/masarcorprepos/magales-infra
docker compose -f docker-compose.dev.yml up -d --build
```

First boot takes ~3-4 minutes (Maven dependency download + Angular
build). Subsequent boots are seconds.

**Sibling layout is mandatory** — the compose builds `api` from
`../Magales` and `ui` from `../Magales-ui`, so the three repos must
live next to each other on disk.

Check everything is healthy:

```bash
docker compose -f docker-compose.dev.yml ps
# expect all five services Up + (healthy)
```

---

## 2. URLs reference

| Surface | URL | What it is |
|---|---|---|
| **Web UI** | <http://localhost:4200> | Angular app (defaults to `acme` tenant) |
| **API** | <http://localhost:8080/api> | Spring Boot backend |
| **Swagger / OpenAPI** | <http://localhost:8080/api/swagger-ui.html> | API reference + try-it |
| **Actuator health** | <http://localhost:8080/api/actuator/health> | `{"status":"UP"}` |
| **MinIO console** | <http://localhost:9001> | S3 mock (login `magales` / `magales-dev-secret`) — not wired yet |

Internal-only ports (no need to open):

| Service | Port | Use |
|---|---|---|
| postgres | 5432 | DB |
| redis | 6379 | cache + future rate-limit state |
| minio S3 API | 9000 | future object storage |

## 3. Default credentials

Seeded by `Magales/src/main/resources/data-postgres.sql`.

| Tenant | Slug | Login | Password | Notes |
|---|---|---|---|---|
| Acme Corporation | `acme` | `admin` | `P@ssw0rd` | Has SUPER_ADMIN + TENANT_ADMIN in dev so platform-admin endpoints are testable |
| Globex Industries | `globex` | `admin` | `P@ssw0rd` | Different physical user from acme's `admin` — same identifier, different tenant |

All other seed users (acme: `f.otaibi`, `m.otaibi`, `s.qahtani`,
`n.mutairi`) also use `P@ssw0rd`.

---

## 4. Test scenarios

### 4.1 Login as the seeded acme admin (smoke)

1. Open <http://localhost:4200>.
2. Login: `admin` / `P@ssw0rd`.
3. Expect: dashboard for Acme Corporation, Arabic branding (RTL),
   browser title `"Acme Corporation"`.
4. You should see meetings, boards, decisions, signatures
   already populated.

### 4.2 Switch tenant branding to globex (proves multi-tenancy)

1. Logout.
2. Confirm globex is reachable via header-scoped call:

   ```bash
   curl -H 'X-Tenant-Slug: globex' \
        http://localhost:8080/api/auth/tenant-context?slug=globex
   ```

3. The UI uses `defaultTenantSlug='acme'` from `environment.ts`. To
   force globex temporarily, edit
   `Magales-ui/src/environments/environment.ts` →
   `defaultTenantSlug: 'globex'`, then from this directory:

   ```bash
   docker compose -f docker-compose.dev.yml up -d --build ui
   ```

   Reload <http://localhost:4200>. Title should now read
   "Globex Industries". Revert when done.

### 4.3 Self-service signup (the Day-2 UI page)

1. From login screen click **"Create a workspace"**, or open
   <http://localhost:4200/signup> directly.
2. Fill:
   - **Organisation:** `Beta Corp`
   - **Full name:** `Founder One`
   - **Email:** `founder@beta.example` (business domain — `@gmail.com` is rejected)
   - **Password:** ≥ 12 chars + upper + lower + digit + symbol
     (e.g. `Founder2026!Strong`). Watch the live checklist tick green.
3. Submit. You'll land on **"Check your inbox"** with the email echoed.
4. Because `APP_TENANCY_SIGNUP_DEV_HINT=true` in compose, the
   verification URL is shown inline on that page. Click it.
   Alternatively pull from API logs:

   ```bash
   docker logs boardhub-api | grep -i "verification"
   ```

5. Verify-email page shows "Email verified", counts down 3 seconds,
   redirects to login. You can now log in with
   `founder@beta.example` / `Founder2026!Strong`.

### 4.4 Consumer-email rejection (proves the blocklist)

1. Open <http://localhost:4200/signup>.
2. Use `someone@gmail.com` as the email; fill the rest legitimately.
3. Submit. Expect a red error: *"Consumer email providers (e.g. gmail.com)
   are not allowed. Use a business email."*

### 4.5 Verify-email error states

- **Invalid token:** <http://localhost:4200/verify-email?token=nonsense>
  → red "Invalid verification link" + restart-signup button.
- **Missing token:** <http://localhost:4200/verify-email>
  → "No verification token" state.
- **Already used:** click the same link from §4.3 twice → second
  click shows "Already verified".
- **Expired:** harder to demo without DB tweaking — skip in normal smoke.

### 4.6 Cross-tenant isolation (proves no leak)

Same identifier exists in two tenants as different physical users:

```bash
# acme/admin
curl -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' -H 'X-Tenant-Slug: acme' \
  -d '{"identifier":"admin","password":"P@ssw0rd"}'

# globex/admin
curl -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' -H 'X-Tenant-Slug: globex' \
  -d '{"identifier":"admin","password":"P@ssw0rd"}'
```

Pick the `accessToken` from the acme response. Send it with the
globex slug:

```bash
curl -H "Authorization: Bearer <acme-token>" \
     -H "X-Tenant-Slug: globex" \
     http://localhost:8080/api/meetings
# expect 401 TENANT_MISMATCH
```

### 4.7 Click through the existing modules

Each path below loads tenant-scoped data behind the scenes — logged
in as acme you will never see globex rows.

- **Boards** — list & detail (`/boards`)
- **Meetings** — list, create, detail (`/meetings`, `/meetings/create`, `/meetings/:id`)
- **Agenda items** — standalone library (`/agenda-items`)
- **Decisions** — list & detail (`/decisions`)
- **Minutes** — list & detail (`/minutes`)
- **Signature** — list & detail (`/signature`)
- **Meeting invitations** — `/meetings/:id/invitations`

### 4.8 Saynee webhook routing (curl only — no UI)

```bash
# Valid path, valid tenant — expect 200
curl -i -X POST http://localhost:8080/api/webhooks/saynee/acme \
  -H 'Content-Type: application/json' \
  -d '{"event":"signature.completed","request_id":"ext-fake-123"}'

# Unknown tenant — expect 401
curl -i -X POST http://localhost:8080/api/webhooks/saynee/nope \
  -H 'Content-Type: application/json' \
  -d '{"event":"signature.completed","request_id":"x"}'

# Suspended / DELETING tenant would also return 401 (no slug-existence leak)
```

### 4.9 Tenant-context endpoint

```bash
curl http://localhost:8080/api/auth/tenant-context?slug=acme    # 200
curl http://localhost:8080/api/auth/tenant-context?slug=globex  # 200
curl http://localhost:8080/api/auth/tenant-context?slug=ghost   # 404
```

---

## 5. Day-to-day commands

```bash
# Tail API logs
docker compose -f docker-compose.dev.yml logs -f api

# Tail UI nginx logs
docker compose -f docker-compose.dev.yml logs -f ui

# Restart just the API after a backend code change
docker compose -f docker-compose.dev.yml up -d --build api

# Restart just the UI after a frontend code change
docker compose -f docker-compose.dev.yml up -d --build ui

# Stop everything (keeps Postgres volume so seed data survives)
docker compose -f docker-compose.dev.yml down

# Stop AND wipe DB volume (full reset → re-runs data-postgres.sql on next up)
docker compose -f docker-compose.dev.yml down -v
```

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `POST /signup` returns 500 with `Connection refused` | DB not ready | Wait ~10 s after `up` and retry; check `docker compose ps` |
| UI shows "Magales" instead of "Acme Corporation" | `tenant-context` call failed at boot | Open DevTools network tab; verify `/api/auth/tenant-context` returns 200 |
| Verification email never arrives | Local dev uses `ConsoleEmailSender` | Look at API logs; the URL is logged AND echoed in the `verificationUrl` response field |
| `signup` rejects all emails as consumer | Blocklist matches your test domain too eagerly | Use a unique fake business domain like `beta.example` |
| Login returns 401 right after signup | Email not verified yet | Click the verification link first |
| `TENANT_MISMATCH` on a freshly issued JWT | Logged in via one slug, sending requests with another | Match `X-Tenant-Slug` (or the host sub-domain) to the tenant the JWT was issued for |

---

## 7. Going beyond the local stack

- **Branch-only smoke** (no compose): `Magales/scripts/ci/smoke-local.sh`
  builds the API image alone and stands it up against a throwaway
  pgvector sidecar. Cleans up on exit.
- **Cross-tenant isolation contract test:**

  ```bash
  cd ~/Documents/masarcorprepos/Magales
  ./mvnw test -Dtest=CrossTenantIsolationIT
  ```

  (Or run from IntelliJ.) Uses Testcontainers — Docker must be running.

- **Bootstrap a fresh SUPER_ADMIN** (only useful when wiping the DB):

  ```bash
  docker compose -f docker-compose.dev.yml down -v
  BOOTSTRAP_SUPER_ADMIN_EMAIL=ops@magales.app \
  BOOTSTRAP_SUPER_ADMIN_PASSWORD='S0meStrongOpsP@ss!' \
    docker compose -f docker-compose.dev.yml up -d --build api
  ```

  Then check `docker logs boardhub-api | grep BOOTSTRAP` for the
  confirmation lines.

---

## 8. What this runbook deliberately does NOT cover

- AWS / staging / prod deploys → `terraform/` (pending Phase 1, Week 1 close).
- On-prem Helm install → `helm/` (pending Day 5).
- AI features → Phase 2, separate doc.
- CI pipeline mechanics → see `WORKFLOWS.md` and `docs/CI-PIPELINE.md`.

When those land, link them here.
