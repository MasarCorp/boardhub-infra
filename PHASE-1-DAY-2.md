# Phase 1 — Day 2: Multi-Tenancy Spine

> **Status:** ✅ Complete (this PR)
> **Goal:** Make every entity, query, and JWT carry tenant context. After this lands, single-tenant assumptions are physically impossible.
> **Companion docs:** [`MAGALES-MVP-PLAN.md`](./MAGALES-MVP-PLAN.md) §4 / §8 · [`Magales/tenant.md`](https://github.com/MasarCorp/Magales/blob/tenancy/tenant.md) (canonical design)

---

## 1. What changed

### 1.1 Backend (`Magales/`)
| Change | Why |
|---|---|
| New `tech.platform.tenant.*` package | Tenant entity, repository, services, controllers, context, AOP filter, identity & AI provider interfaces, email sender, integration test |
| `tenant_id UUID NOT NULL` on `BaseEntity` (auto-stamped via `@PrePersist`) | Mandatory column on every tenant-scoped table; missing context throws — never silent leak |
| Hibernate `@FilterDef` on `BaseEntity` enabled per-request via `TenantFilterAspect` | Every `findAll`/`findByX`/`@Query` is automatically tenant-scoped |
| `TenantContext` ThreadLocal + `TenantFilter` Servlet filter | Resolves tenant from sub-domain or `X-Tenant-Slug` header before any other filter runs |
| JWT now carries `tid` claim | Cross-tenant attack guard: stolen token from acme rejected on globex sub-domain |
| Unique constraints rescoped to `(tenant_id, …)` | Same email, meeting number, board code can co-exist across tenants |
| `POST /api/signup` (public) | Self-service tenant signup with consumer-email-domain blocklist |
| `POST /api/auth/verify-email` (public) | Consumes the email-verification token issued at signup |
| `POST /api/admin/tenants` (SUPER_ADMIN) | Direct enterprise provisioning, skips email verification |
| `GET /api/auth/tenant-context` (public) | UI fetches branding, locale, identity providers before login |
| `IdentityProvider` interface + `LocalIdentityProvider` | OIDC/SAML/Nafath adapters slot in cleanly later |
| `AiProvider` interface + `AiProviderKind` enum (`BEDROCK`/`OLLAMA`/`WATSONX`/`GROQ`/`NONE`) | Each tenant configures its own provider; impls land Day 4 |
| `EmailSender` interface + `ConsoleEmailSender` (logs to stdout) | SES adapter replaces it Day 5 |
| `@CrossTenant` annotation | Marks methods that legitimately bypass the filter (admin, signup) — every use justifiable in code review |
| `spring-boot-starter-aop` + `testcontainers-postgresql` deps | AOP for filter aspect; Testcontainers for the isolation integration test |
| Postgres-portable types (re-applied) | NVARCHAR → `length`/`TEXT` undone by an upstream revert PR; restored here |

### 1.2 Frontend (`Magales-ui/`)
| Change | Why |
|---|---|
| New `TenantService` | Resolves slug from sub-domain or env config; fetches tenant context on app boot; applies branding (`document.title`, CSS vars, `lang`/`dir`) |
| New `tenant.models.ts` interface module | Shared shape for `TenantContext` |
| HTTP interceptor injects `X-Tenant-Slug` for localhost | Backend resolves tenant when no real sub-domain is in play |
| `provideAppInitializer` calls `loadContext()` before router activates | Branding applied before first paint |
| `environment.defaultTenantSlug` (dev: `'acme'`, prod: empty) | Lets devs flip to globex for branding-swap demo |
| `index.html` `<title>Magales</title>` (was hardcoded `Ijtimaati · اجتماعاتي`) | Title now dynamic per-tenant |

### 1.3 Infra (`magales-infra/`)
Two env vars added to the `api` service in `docker-compose.dev.yml`:

```yaml
APP_TENANCY_ALLOW_DEFAULT_TENANT: "true"        # dev only — never true in prod
APP_TENANCY_DEFAULT_TENANT_SLUG: "acme"
APP_TENANCY_HOST_SUFFIXES: "magales.app,magales.local,magales.test"
APP_TENANCY_SIGNUP_DEV_HINT: "true"             # signup response includes verification URL for tester convenience
APP_TENANCY_VERIFICATION_BASE_URL: "http://localhost:4200/verify-email"
```

### 1.4 Deliberately deferred
- ❌ `BedrockAiProvider`, `OllamaAiProvider`, `WatsonxAiProvider`, `GroqAiProvider` impls → Day 4 (AI worker)
- ❌ `OidcIdentityProvider`, `SamlIdentityProvider`, `NafathIdentityProvider` impls → Day 3+
- ❌ SES email sending → Day 5 (still console-only)
- ❌ Stripe / Hyperpay billing → Phase 2
- ❌ Subscription-plan enforcement (rate limits, seat counts) → Phase 2
- ❌ Tenant suspension / hard-delete cleanup job → Phase 2
- ❌ Per-tenant schema option (Hibernate `MultiTenantConnectionProvider`) → Phase 3

---

## 2. How to run locally

Same as Day 1 — nothing new in the developer flow:

```bash
cd ~/Documents/masarcorprepos/magales-infra
docker compose -f docker-compose.dev.yml up --build
```

Two seeded tenants are available immediately:

| Tenant | slug | DB id | seeded users | AI provider |
|---|---|---|---|---|
| Acme Corporation | `acme` | `00000001-0000-0000-0000-000000000001` | 5 (admin / f.otaibi / m.otaibi / s.qahtani / n.mutairi) | Bedrock |
| Globex Industries | `globex` | `00000002-0000-0000-0000-000000000002` | 2 (admin / r.smith) | Ollama |

All passwords are `P@ssw0rd`.

---

## 3. Probing tenancy locally

### 3.1 Default tenant (acme) via fallback
```bash
curl http://localhost:8080/api/auth/tenant-context
# → {"slug":"acme","displayName":"Acme Corporation",...}
```
This works because `APP_TENANCY_ALLOW_DEFAULT_TENANT=true` in the dev compose.

### 3.2 Explicit slug
```bash
curl http://localhost:8080/api/auth/tenant-context?slug=globex
# → {"slug":"globex","displayName":"Globex Industries",...}
```

### 3.3 Header-based (what the UI uses on localhost)
```bash
curl -H 'X-Tenant-Slug: globex' http://localhost:8080/api/meetings
# → returns ONLY globex meetings (just the seeded GBX-2026-001)
```

### 3.4 Login with same email in different tenants

```bash
# acme/admin
curl -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-Slug: acme' \
  -d '{"identifier":"admin","password":"P@ssw0rd"}'
# → returns acme admin (د. خالد السديري)

# globex/admin (SAME identifier — different physical user)
curl -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-Slug: globex' \
  -d '{"identifier":"admin","password":"P@ssw0rd"}'
# → returns globex admin (Jane Globex)
```

The JWT returned in each case carries `tid` matching the resolved tenant; using one tenant's token against the other tenant's host returns 401 `TENANT_MISMATCH`.

### 3.5 Self-service signup
```bash
curl -X POST http://localhost:8080/api/signup \
  -H 'Content-Type: application/json' \
  -d '{
        "email":"founder@beta.example",
        "password":"P@ssw0rdLong!",
        "organizationName":"Beta LLC",
        "displayName":"Founder Person"
      }'
# → 201 { tenantSlug:"beta-llc", verificationRequired:true,
#         verificationDevHint:"http://localhost:4200/verify-email?token=…" }
#
# Watch the api logs:  docker compose -f docker-compose.dev.yml logs -f api
# The verification URL is also printed in the box-drawn email log.
```

### 3.6 Consumer-domain rejection
```bash
curl -X POST http://localhost:8080/api/signup \
  -H 'Content-Type: application/json' \
  -d '{ "email":"someone@gmail.com","password":"P@ssw0rdLong!",
        "organizationName":"Gmail User","displayName":"Some One" }'
# → 400 { "errorCode":"EMAIL_DOMAIN_NOT_BUSINESS",
#         "message":"Sign up with a business email. ..." }
```

### 3.7 UI tenant-swap demo

```bash
# 1. UI defaults to acme (env.defaultTenantSlug='acme'):
open http://localhost:4200
#    Title: "Acme Corporation"

# 2. Edit src/environments/environment.ts → defaultTenantSlug:'globex'
#    Then docker compose -f docker-compose.dev.yml up -d --build ui
open http://localhost:4200
#    Title: "Globex Industries"

# In production, the same swap happens via sub-domain:
#    acme.magales.app   → resolves slug=acme
#    globex.magales.app → resolves slug=globex
```

---

## 4. The contract

`Magales/src/test/java/tech/platform/tenant/CrossTenantIsolationIT.java` runs against a real Testcontainers Postgres and asserts:

- `findAll()` from acme context returns only acme rows (never globex)
- Same email allowed across tenants — different physical row each time
- `findById(other_tenant_row_id)` from acme returns empty
- `@PrePersist` throws if tenant context is missing on a new entity (cannot accidentally save a tenant-less row)

If this test ever fails, the multi-tenancy contract is broken and **no code merges to main**.

Run it:
```bash
cd ~/Documents/masarcorprepos/Magales
./mvnw test -Dtest=CrossTenantIsolationIT
# (Maven wrapper not yet committed; alternative: open in IntelliJ and Run)
```

---

## 5. Roadmap (this repo, post-Day 2)

| Phase | Adds |
|---|---|
| Phase 1 / Day 3 (next) | Identity adapters: OIDC + SAML scaffolding; `OidcIdentityProvider` for Entra ID + Okta |
| Phase 1 / Day 4 | AI worker service (Python) with Bedrock + Ollama provider impls |
| Phase 1 / Day 5 | SES email sender, S3 doc storage, billing scaffolding |
| Phase 1 / Week 1 close | Terraform: VPC, ECS, RDS, ElastiCache, S3, ECR, ALB, WAF, Route53, CloudFront, IAM, Secrets, CloudWatch |
| Phase 2 / Week 2 | Helm chart for self-hosted enterprise tier |

See [`MAGALES-MVP-PLAN.md`](./MAGALES-MVP-PLAN.md) §8 for the full week-1 sequence.
