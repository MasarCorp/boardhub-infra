# Magales — MVP Plan & Architecture (1-Week Release)

> Working name: **Magales** (placeholder, will be re-branded). Two repos under review:
> - `Magales/` — Spring Boot 3.3 / Java 21 backend
> - `Magales-ui/` — Angular 17 frontend
>
> Target offering: **SaaS** (AWS, multi-tenant) + **Enterprise self-hosted** (on-prem / private cloud), shipped as Docker images and deployed initially on **ECS Fargate**, later **EKS**. Multi-tenancy keyed by `tenant_id`. AI is a first-class capability (this is positioned as an "AI meeting system", not a static board portal).
> Reference business: **مجلس تك / majles.tech** — KSA digital governance platform for boards & general assemblies. Magales must match its feature surface and add an AI layer to differentiate.

---

## 1. Codebase Summary

### 1.1 Backend (`Magales/`)
| Area | Technology / Choice |
|---|---|
| Language / runtime | Java 21, Spring Boot 3.3.5, Maven |
| Persistence | Hibernate 6 / Spring Data JPA |
| DB profiles | `dev` (H2 in-memory), `sqlserver` (primary intended), `postgres`, `prod` (SQL Server + Flyway) |
| Auth | Spring Security + JWT (JJWT 0.12), Nafath stub, BCrypt |
| API docs | SpringDoc OpenAPI 2.6 (Swagger UI) |
| Mapping | MapStruct 1.6 (compile-time DTO mapping) |
| Misc | Lombok, Spring Actuator, Spring Validation |
| Package root | `sa.gov.magales.*` (KSA-government namespace — must change for global SaaS) |
| Domain modules | `identity`, `board`, `meeting`, `voting`, `minutes`, `signature`, `decision`, `document`, `audit`, `common` |
| Base entity | UUID PK, `created_at/by`, `updated_at/by`, `is_deleted`, `@Version` (optimistic locking) |
| i18n at data layer | Bilingual columns (`title_ar` / `title_en`) + `BilingualText` value object; Arabic stored as `NVARCHAR` (SQL Server-only syntax) |

### 1.2 Frontend (`Magales-ui/`)
| Area | Technology / Choice |
|---|---|
| Framework | Angular 17.3 standalone components, OnPush change detection |
| State | Signals (local) + RxJS for HTTP |
| i18n | ngx-translate 15 with `ar.json` / `en.json`, RTL/LTR auto-switch via CSS logical properties |
| Auth | `AuthService` w/ localStorage tokens, `authInterceptor` for Bearer + 401 refresh, mock + real backend wired |
| HTTP layer | Generic `ApiService` (paged GET/POST/PATCH/DELETE), per-domain services already scaffolded (`meeting`, `voting`, `minutes`, `decision`, `document`, `signature`, `board`, `user`) |
| Build | Angular Application builder, prod budget 2 MB |
| Pages | Login, Dashboard, Meetings, Meeting Detail, Voting, Minutes, Signature, Decisions, plus placeholders (Boards, Library, Chat, Reports, Settings, Users) |

### 1.3 Reference business (MajlesTech / مجلس تك, built by Sure Global Tech)
Source: official MajlesTech company profile (PDF, AR) + reference site. Vendor is **Sure Global Tech** (`sure.com.sa`), a Tadawul-listed Saudi enterprise software firm — *not* a startup competitor. Self-positioning: *"نظام الحوكمة الرقمية الأول بالمملكة"* (the Kingdom's first digital governance system); explicit Vision 2030 anchor.

**Authoritative feature list (12 features, exact names from the profile):**

| # | Feature (AR) | Feature (EN) | In our code today? |
|---|---|---|---|
| 1 | جدولة الاجتماعات | Meeting scheduling + invitations + attendance confirmation | ✅ entity + service |
| 2 | إدارة المجالس واللجان | Boards & committees mgmt incl. executive bylaw (لائحة تنفيذية) | ✅ entity, no bylaw doc |
| 3 | التصويت الإلكتروني | E-voting with instant tally | ✅ |
| 4 | الاجتماع عبر الفيديو | **Native video meetings (mobile + web)** | ❌ URL field only |
| 5 | مراجعة واعتماد محضر الاجتماع | Minutes review + approval + member feedback | 🟡 entity, no approval workflow |
| 6 | التوقيع الإلكتروني | E-signature via **Saen / صاين** (CST-licensed) | 🟡 stubbed; brand spelled `SAYNEE` (wrong — should be `SAEN`) |
| 7 | المحادثات | In-system chat (1:1 + per-board/committee groups) | ❌ placeholder page |
| 8 | متابعة القرارات | Decision tracking & assignment | ✅ |
| 9 | القرارات بالتمرير | Circular resolutions (vote without convening) | ✅ flag on VotingSession |
| 10 | **التقييم والاستبيانات** | **Surveys & evaluations** of committee work or members | ❌ not modelled |
| 11 | مكتبة المستندات | Document library | ✅ |
| 12 | **اللجان الداخلية والخارجية** | **Internal AND external committees** (members spanning orgs) | 🟡 single-org assumption in our `Board` |

**Two business model tells from the profile:**
- They market **General Assemblies (الجمعيات العمومية)** as a first-class motion — the website headline says *"إدارة اجتماعات مجالس الإدارة والجمعيات العمومية"*. GA voting differs structurally from board voting: quorum is % of issued share capital, ballots are weighted by shareholding, proxies are common. Our backend has `Board`/`Committee` but **no GA flow**. This is a real gap for listed-company / JSC governance.
- **No AI mentioned anywhere** in the company profile. Their "محضر آلي" (automatic minutes) is rule-based templating, not LLM-generated. **AI is our defensible differentiator.**

**Customer base shown in the profile (proves the market is real and enterprise-grade):**
- Government (~22 logos): Ministry of Culture, Ministry of Municipal & Rural Affairs, **CST (Communications, Space & Technology Commission)**, **Digital Government Authority**, Saudi Awqaf (الهيئة العامة للأوقاف), **SOCPA**, Saudi Contractors Authority, State Properties General Authority, National Center for Environmental Compliance, Saudi Exports, Eastern Health Cluster, National Water Efficiency Center, EXPRO, Makkah Province Development Authority, Hail Region Development Authority, **Council of Health Insurance (ضمان)**, Saudi Red Crescent, Saudi Center for Organ Transplantation, Riyadh Municipality, Saudi Energy Efficiency Center.
- Private (~22 logos): Al Akaria, Annasban Holding, Aldyar Alarabiya, DHS Arabia, **Dr. Abdul Rahman Al Mishari Hospital**, Al Rajhi Real Estate Union, Aseel Finance, **SATEC**, **Al Zamil**, **Dallah Hospitals**, Arabian Drilling, **Vision Bank**, Al Amjad, Uptown Jeddah, Clean Life, **Derayah**, **SALIC**, Mina Real Estate Co., GCC pilgrim-hosting companies.

### 1.4 Competitive positioning (where Magales wins)
SGT/MajlesTech is entrenched in KSA government. We do not beat them at their own game — we change the game.

| Axis | SGT / MajlesTech | Magales (target) |
|---|---|---|
| AI / automation | None in profile; rule-based minutes | **AI-native**: transcription, auto-minutes, action-item extraction, semantic search |
| Geography | KSA-first, Arabic-first | **GCC + global**: KSA, UAE, Bahrain, Oman, Egypt, EU/US — multi-region from day 1 |
| Go-to-market | Enterprise sales, demo-on-request, multi-month onboarding | **Self-serve SaaS** + free trial + Stripe/Hyperpay; enterprise tier optional |
| Identity | Nafath-centric | Pluggable: Nafath, UAE PASS (future), OIDC/SAML, password+MFA |
| E-signature | Saen only | **Pluggable**: Saen, DocuSign, Adobe Sign, eIDAS QES |
| Deployment | Cloud (KSA-hosted) | **SaaS (AWS) + Enterprise self-hosted** (Helm chart, MinIO, Ollama) |
| Pricing | Enterprise contracts | Per-seat + per-tenant tiers; mid-market priced |
| Mobile | Native video app exists | Web-first MVP; React Native / Capacitor mobile in Phase 2 |

**Initial target segments where SGT is weakest:**
1. **Mid-market private sector** (50–500 employees) — SGT pursues large enterprise.
2. **GCC outside KSA** — UAE, Bahrain, Oman, Qatar.
3. **Verticals SGT under-serves**: universities & academic boards, NGOs/non-profits, family offices, listed-company investor relations teams (general assemblies), VC/PE funds (LP advisory boards).
4. **Industries asking for AI**: legal, consulting, tech.

**Gaps vs. reference (must close, with priority):**
- 🔴 MVP: Multi-tenancy + AI minutes + chat (basic) + minutes approval workflow.
- 🟡 Phase 2: Surveys & evaluations, native video conferencing, executive bylaw doc model, external committees, General Assembly module.
- 🟢 Phase 3: Mobile apps, agenda screen sync, advanced surveys/360 board evaluations.

---

## 2. Bug & Risk Scan

### 2.1 Critical (must fix before any non-local deploy)
- **`SecurityConfig.java:42` — `.anyRequest().permitAll()`**: every API endpoint is open. Fix: explicit role-based rules + `.anyRequest().authenticated()`.
- **`application.yml:34` — default JWT secret in source** (`change-me-in-production…`). Fix: fail-fast on startup if env var unset; rotate via AWS Secrets Manager / SSM.
- **Zero multi-tenancy.** No `tenant_id` on `BaseEntity`; every repository query (`findByEmail`, `findByStatus`, `findAll`) leaks across tenants. SaaS shared instance is unsafe today. (See §4.)
- **`NafathService` keeps transactions in `ConcurrentHashMap` (in-memory)**: breaks the moment we run >1 replica behind an ALB. Move to Redis with TTL.
- **`AuthService:116-117`** — `expiresIn` computed by calling `generateAccessToken` again, just to check if non-null. Replace with `accessExpiration.toSeconds()` from `JwtService`.
- **NVARCHAR / NVARCHAR(MAX) on entities (61 occurrences)** — SQL Server-specific DDL embedded in JPA columns. Postgres `ddl-auto: update` will silently misinterpret. Fix: drop `columnDefinition`, let dialect choose `text`/`varchar`; rely on `Arabic_CI_AS` collation at DB level for SQL Server.

### 2.2 High
- **No Dockerfile, no health probes** for ALB/ECS. `/actuator/health` is permitted but no liveness/readiness split, no DB/Redis/cache indicators.
- **`Asia/Riyadh` hardcoded** in `application.yml:8`, `application-postgres.yml:24`, etc. Move to env var; SaaS must serve multiple TZs.
- **CORS allowed origins hardcoded twice** (`application.yml:38` and `SecurityConfig:57`). Single source of truth, env-driven.
- **Refresh token storage**: SHA-256 hex of token without salt — improves on plaintext but still rainbow-able. Fix: HMAC with server secret, or bcrypt the token hash.
- **Eager `Set<UserRole>` collection** on `User` (`fetch = EAGER`, line 85) — load amplification on every user fetch. Switch to `LAZY` + DTO projection.
- **N+1 risk** on `Meeting.agendaItems` + `attendees`, `Minutes.revisions` + `comments`, `VotingSession.ballots`, `Board.memberships`, `SignatureRequest.records`. No `@EntityGraph` / `JOIN FETCH` anywhere. Will catch fire as soon as a real tenant has 1000+ meetings.
- **`Document.filePath` exposed in DTO** — leaks storage topology. Serve via signed URL.
- **No rate limiting** on `/auth/login`, `/auth/nafath/request`, `/auth/refresh`. Trivially brute-forceable.
- **Soft-delete index missing**: no index on `is_deleted`; queries scan deleted rows.
- **Pagination missing** on several `findBy…` repository methods that return `List<…>` (e.g. `BoardRepository.findByParentBoardIsNull`).

### 2.3 Medium / cosmetic
- `localStorage` for access + refresh tokens (UI) — XSS-stealable. Move refresh to HttpOnly Secure cookie; access can stay if CSP is tight.
- `User.preferredLanguage` defaults to `"ar"` — SaaS default should be `"en"` (region-aware).
- `BoardService` doesn't validate parent-board self-reference (cycle).
- `Minutes.contentAr/En` allow null at `PUBLISHED` status.
- `JwtAuthenticationFilter` swallows JWT errors silently — emit metric / 401 on the protected path.
- Frontend has no environment switching for staging vs prod (`environment.ts` only points to `localhost:8080/api`).

### 2.4 Saudi-government coupling that blocks global SaaS
| Coupling | Where | Action |
|---|---|---|
| Package `sa.gov.magales.*` | every Java file | Rename root package to `tech.<brand>.platform.*` post-rebrand. |
| Nafath as primary auth | `AuthController`, `NafathService`, `NafathRequest*` DTOs | Refactor as **pluggable IdP adapter** (`IdentityProvider` interface): Nafath, OIDC, SAML, password-only — picked per tenant config. |
| Saynee (sic) as default e-sign provider | `SignatureRequest` | **Brand is Saen / صاين**, not Saynee — rename enum/string `SAYNEE` → `SAEN` in code & DB. Refactor as `SignatureProvider` interface with adapters: Saen, DocuSign, Adobe Sign, internal PKCS#7, eIDAS QES. |
| `nationalId` on `User` indexed/unique | `User.java:45`, `UserRepository:14` | Make optional + tenant-scoped; not all tenants are KSA. |
| Default RTL / Arabic-first | UI + entities | Tenant config flag `defaultLocale` + `defaultDirection`. |

---

## 3. Target Architecture (AWS, MVP → Scale)

### 3.1 Logical microservices (post-refactor)
For a 1-week MVP we **don't split the backend yet** — we ship the existing modular monolith as **one container**. The package boundaries (`identity`, `meeting`, `voting`, …) are already module-shaped, so a future split is mechanical. Net microservices target:

```
┌────────────────────────┐  ┌────────────────────────┐
│ magales-api (monolith) │  │ magales-ai-worker      │  ← async, NEW
│ Java 21 / Spring Boot  │  │ Python (FastAPI)       │
└────────────────────────┘  └────────────────────────┘
┌────────────────────────┐  ┌────────────────────────┐
│ magales-ui (Angular)   │  │ magales-realtime        │  ← Phase 2
│ static, served by CF   │  │ Node/Spring + WebSocket │
└────────────────────────┘  └────────────────────────┘
```

`magales-ai-worker` is a **new** small service that consumes a queue and runs: transcription pull, summarization, action-item extraction, embedding indexing. It is **separate** because (a) it runs on Python where the AI ecosystem lives, (b) its scaling profile (bursty, GPU-friendly) is different from the API.

### 3.2 AWS reference architecture (SaaS — shared instance, MVP)
```
              Route 53
                 │
            CloudFront ── S3 (static UI, signed URLs for docs)
                 │
                AWS WAF
                 │
           ALB (HTTPS only)
            │            │
   ECS Fargate svc     ECS Fargate svc
   magales-api         magales-ai-worker
            │            │
   ┌────────┼────────────┼─────────┐
   │        │            │         │
   ▼        ▼            ▼         ▼
 RDS Pg  ElastiCache  S3 docs   SQS jobs
 (15+    Redis 7      bucket    transcription
 pgvector tenant      versioned + summarize
 ext)    cache,                  queue
         sessions,
         nafath txns
                                   │
                                   ▼
                            Bedrock (Claude)
                            + Transcribe
                            (or Deepgram)

Cross-cutting: Secrets Manager, SSM Param Store, CloudWatch Logs+Metrics,
X-Ray tracing, ECR (images), GuardDuty, Config, KMS-CMK for at-rest enc.
SES for email, SNS for SMS (or Unifonic in KSA region).
```

### 3.3 Why these choices
| Choice | Rationale |
|---|---|
| **Postgres (RDS) over SQL Server** | (a) SQL Server license cost on AWS is ~5–10× Postgres on the same hardware; (b) `pgvector` extension gives us AI embeddings in the same DB instead of paying for OpenSearch/Pinecone in the MVP; (c) Aurora Postgres path exists when we outgrow RDS; (d) on-prem enterprise tier — Postgres runs anywhere. **Drop the `sqlserver` profile from MVP.** Keep Flyway migrations Postgres-only. |
| **ElastiCache Redis** | Required for Nafath transient state, JWT denylist, rate limiting, distributed cache (per-tenant boards/users), and pub/sub for the future real-time agenda sync. |
| **S3 for documents, recordings, signed PDFs, minutes content** | The blob fields (`Minutes.contentAr/En`, `Document` files, `SignatureRecord.signatureData`, audit `oldValue/newValue`) belong in object storage, not Postgres. Keep references (S3 key + version) in DB. |
| **ECS Fargate for MVP, EKS later** | Fargate gives us "Docker on AWS" with zero node management for two services. EKS becomes worth it when (a) we have ≥4 services, (b) we need Karpenter for GPU bursts, (c) enterprise customers ask for Helm charts (which we'll already have for self-hosted — see §6). |
| **Bedrock + Transcribe** | Bedrock = Anthropic Claude on AWS (data residency + IAM auth, no separate vendor contract). Transcribe = native Arabic + English STT. Alternative: Deepgram if we need diarization quality. |
| **Cognito vs Keycloak** | MVP: roll our own JWT (already done) + Cognito as a **federation broker** for SSO (SAML/OIDC). Enterprise on-prem: ship Keycloak in the Helm chart. Nafath stays as a custom IdP adapter. |
| **CloudFront + WAF** | Required for KSA & EU/US edge latency; WAF gives us managed OWASP rules + rate-limit on `/auth/*`. |

### 3.4 Enterprise self-hosted topology
```
docker-compose / Helm chart shipping:
  - magales-api      (image)
  - magales-ai-worker(image, optional — can be disabled)
  - magales-ui-nginx (image)
  - postgres 15 + pgvector
  - redis 7
  - minio            (S3-compatible local object store)
  - keycloak         (optional IdP, replaces Cognito federation)
  - ollama           (optional local LLM, replaces Bedrock for air-gapped)
```
Same images, different orchestrator, configured purely via env vars. **No code branches between SaaS and Enterprise** — that's the entire point of the refactor.

---

## 4. Multi-Tenancy Refactor (Mandatory, Phase 1)

### 4.1 Strategy: shared DB / shared schema with `tenant_id` discriminator
This is the cheapest and matches "one shared instance" goal. Phase 3 we add the option of per-tenant schema for enterprise-on-shared-SaaS (compliance escape hatch).

### 4.2 Required code changes

**a. Add `tenantId` to `BaseEntity`** (every entity inherits it):
```java
@Column(name = "tenant_id", nullable = false, updatable = false)
private UUID tenantId;
```
- Make it `@NotNull` at the DB level.
- Migration: add column NOT NULL with default = bootstrap tenant for existing rows, then drop default.

**b. New `Tenant` entity + `tenants` table**:
```
tenants(id, slug, display_name, plan, status, locale, timezone,
        identity_provider, signature_provider, branding_json,
        created_at, ...)
```

**c. `TenantContext` (ThreadLocal)** populated from JWT claim:
```java
public final class TenantContext {
  private static final ThreadLocal<UUID> CURRENT = new ThreadLocal<>();
  public static void set(UUID id) { CURRENT.set(id); }
  public static UUID require() { /* throw if null */ }
  public static void clear() { CURRENT.remove(); }
}
```
- JWT must carry `tid` claim (issued at login from `User.tenantId`).
- `JwtAuthenticationFilter` calls `TenantContext.set(claims.get("tid"))` and clears in a `finally`.
- For SaaS sign-up, tenant is resolved from sub-domain (`acme.magales.app`) before login.

**d. Hibernate `@Filter` on `BaseEntity`**:
```java
@FilterDef(name = "tenantFilter",
           parameters = @ParamDef(name = "tenantId", type = UUID.class))
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
```
Enable in a JPA `@PrePersist` / `@PostLoad` hook or via a Hibernate `Interceptor` that pulls from `TenantContext`.

**e. `@PrePersist` to auto-set `tenantId`** — devs never write `entity.setTenantId(...)`; the listener does it.

**f. Repository safety**:
- Audit every `@Query` for missing `tenant_id =` clause.
- Add a custom test (`@SpringBootTest`) that creates two tenants and asserts no cross-leak on `findAll`, `findByX`, etc.

**g. Composite indexes** (`tenant_id` first, then frequent columns):
```
idx_meetings_tenant_status (tenant_id, status, start_time)
idx_decisions_tenant_status (tenant_id, status, due_date)
idx_users_tenant_email (tenant_id, email)  -- replaces global unique on email
idx_documents_tenant_category (tenant_id, category_id, created_at)
```

**h. Unique constraints scoped to tenant**:
- `users.email` must be unique **per tenant**, not globally.
- `meetings.meeting_number` must be unique per tenant.
- Update `User`, `Meeting`, `Board` `@UniqueConstraint`.

**i. UI tenant resolution**:
- Sub-domain-based: `acme.magales.app` → `tenantSlug = acme` resolved by API at `/auth/tenant-context` before login.
- Branding (logo, colors, app name) returned from `/auth/tenant-context` and applied via CSS variable injection.

### 4.3 Migration plan for existing data
- Existing data is dev/seed only. Drop schema, re-create with `tenant_id` everywhere, seed one demo tenant.
- Production-bound Flyway: `V1__init_with_tenant.sql` written from scratch from current Hibernate auto-DDL output, **regenerated against Postgres**.

---

## 5. Data Layer Plan

### 5.1 Primary DB
- **Postgres 15** on RDS (single-AZ for MVP, Multi-AZ from week 2). Aurora Postgres is the upgrade path.
- `pgvector` extension enabled from day 1 (used by AI module — §7).
- `pg_trgm` extension for Arabic / English fuzzy search on titles.
- Connection pool: HikariCP, sized 20/replica.
- All schema changes via **Flyway** (`db/migration/V*.sql`). Drop the `ddl-auto: update` habit; production = `validate`.

### 5.2 Caching (ElastiCache Redis 7)
| Cache | Purpose | TTL |
|---|---|---|
| `tenant:{slug}` | Tenant resolution from sub-domain | 5 min |
| `user:{id}` | Hot user lookup (JWT validation, audit author) | 60 s |
| `board:{tenantId}:{boardId}` | Board details (rarely change) | 5 min |
| `dashboard:{tenantId}:{userId}` | Dashboard KPIs | 30 s |
| `nafath:tx:{transId}` | **Replaces in-memory `ConcurrentHashMap`** in `NafathService` | 3 min |
| `ratelimit:{ip}:{endpoint}` | Login / Nafath rate limit | 60 s window |
| `jwt:denylist:{jti}` | Logout / forced-revoke | until `exp` |
| `pubsub: meeting:{id}` | Real-time agenda sync (Phase 2) | n/a |

Spring abstraction: `@Cacheable` with Spring Cache → Redis. No Redis dependency for unit tests (in-memory Caffeine fallback).

### 5.3 Object storage
- **S3 buckets** (KMS-encrypted, versioned):
  - `magales-{env}-documents/{tenantId}/...`
  - `magales-{env}-recordings/{tenantId}/...` (videos for transcription)
  - `magales-{env}-minutes/{tenantId}/...` (final PDF/DOCX)
  - `magales-{env}-signatures/{tenantId}/...` (signed evidence packages)
- DB stores only the S3 key + version + content-hash + `tenantId`. **`Minutes.contentAr/En` migrate from `NVARCHAR(MAX)` to S3 reference.**
- API serves docs only via short-lived (5 min) **pre-signed URLs**.
- Self-hosted: same code, MinIO instead of S3 (drop-in API).

### 5.4 Search
MVP: Postgres `pg_trgm` + `tsvector` over `title_ar/en`, `description`, `tags`. Not OpenSearch yet — we don't need it for the volume the MVP will have.

### 5.5 Soft-delete & audit
- Add index on `is_deleted` (partial: `WHERE is_deleted = false`).
- Audit log → S3 (cold) + Postgres (hot, last 90d). Long-term audit is large and write-heavy — split it.

---

## 6. Docker / Container Refactor

### 6.1 Repos to add per service
```
Magales/                       Magales-ui/
├── Dockerfile                 ├── Dockerfile (multi-stage, nginx)
├── .dockerignore              ├── .dockerignore
├── docker-compose.yml  ◄── joint compose at parent dir, see below
└── ...
```

### 6.2 Backend Dockerfile (multi-stage)
```dockerfile
# Stage 1: build
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
COPY pom.xml .
COPY .mvn .mvn
COPY mvnw .
RUN ./mvnw -B dependency:go-offline
COPY src ./src
RUN ./mvnw -B -DskipTests package

# Stage 2: runtime
FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD wget -qO- http://localhost:8080/api/actuator/health/liveness || exit 1
ENTRYPOINT ["java","-XX:+UseContainerSupport","-XX:MaxRAMPercentage=75","-jar","/app/app.jar"]
```

### 6.3 Frontend Dockerfile
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build:prod

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/ijtimaati-ui /usr/share/nginx/html
HEALTHCHECK --interval=30s CMD wget -qO- http://localhost:80/ || exit 1
EXPOSE 80
```
`nginx.conf` includes the SPA fallback (`try_files $uri /index.html`) and a `/config.js` runtime config injection so we don't rebuild the image per environment.

### 6.4 Joint dev compose (`masarcorprepos/docker-compose.dev.yml`)
```yaml
services:
  postgres:
    image: postgres:15
    environment: { POSTGRES_DB: magales, POSTGRES_USER: magales, POSTGRES_PASSWORD: dev }
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000","9001:9001"]
    environment: { MINIO_ROOT_USER: magales, MINIO_ROOT_PASSWORD: magales-dev }
  api:
    build: ./Magales
    environment:
      SPRING_PROFILES_ACTIVE: postgres
      DB_HOST: postgres
      DB_USER: magales
      DB_PASSWORD: dev
      DB_NAME: magales
      REDIS_HOST: redis
      S3_ENDPOINT: http://minio:9000
      JWT_SECRET: dev-secret-32chars-minimum-please-rotate
    ports: ["8080:8080"]
    depends_on: [postgres, redis, minio]
  ui:
    build: ./Magales-ui
    ports: ["4200:80"]
    depends_on: [api]
volumes:
  pgdata:
```
**One command for any developer, on any machine: `docker compose up`.** No more "install Maven, Lombok plugin, JDK 21, npm 20, copy SQL Server collation script…".

### 6.5 Externalize all config
- Strip hardcoded `Asia/Riyadh`, `localhost:4200`, JWT default, default profile from YAML.
- Drive 100 % of config from env vars with `${ENV_VAR:default}` only for safe defaults (i.e. **not** for secrets).
- A single config layer, two consumers (SaaS Helm `values.yaml` vs. on-prem `.env` file).

### 6.6 Image registry & supply chain
- Push to **ECR** for SaaS (`magales-api`, `magales-ui`, `magales-ai-worker`).
- Push to **public read-only registry** (or licensed registry per customer) for enterprise on-prem.
- Sign images with **cosign**; SBOMs with `syft`; scan with `trivy` in CI.

---

## 7. AI Module (Day-One Differentiator)

### 7.1 Capabilities to ship in MVP
| Capability | What it does | Provider (SaaS / Enterprise) |
|---|---|---|
| **Speech-to-text (AR + EN)** | Transcribe meeting recording (uploaded or video link) | AWS Transcribe / Deepgram ▸ Whisper local |
| **Speaker diarization** | Tag each transcript segment with speaker | Deepgram or Transcribe Speaker Identification |
| **Auto-minutes** | Generate structured `Minutes` from transcript | Bedrock Claude 4.x ▸ local Llama / Ollama |
| **Action item extraction** | Pull "who, what, by when" → `Decision` + `DecisionAssignment` rows | Bedrock Claude tool use |
| **Decision summarization** | One-paragraph executive summary per decision | Bedrock Claude |
| **Semantic search** | "Find decisions about budget Q3" across minutes/decisions | pgvector embeddings (`bge-m3` or Cohere multilingual) |
| **Smart agenda assistant** | Suggest agenda from past meetings + uploaded brief | Bedrock Claude |

### 7.2 New service: `magales-ai-worker`
- Python 3.12 + FastAPI (admin endpoints) + RQ/Celery (jobs).
- Triggered by SQS messages produced by the Java backend after a meeting is marked `COMPLETED` or a recording is uploaded.
- Pipeline:
  ```
  recording.uploaded → transcribe → diarize → llm.summarize
    ├─→ minutes.draft (S3 + DB row, status=DRAFT_AI)
    ├─→ decisions.extracted[]
    ├─→ embeddings.indexed (pgvector)
    └─→ event: ai.minutes.ready (SQS → Java backend → notify users)
  ```
- Deployed as separate ECS task. **Stateless**, scales independently.

### 7.3 Backend hooks needed
- New tables: `transcription_job`, `ai_artifact`, `embedding` (with `vector(1024)` column).
- New fields on `Minutes`: `aiGenerated`, `aiConfidence`, `aiModelVersion`.
- New fields on `Meeting`: `recordingS3Key`, `transcriptionStatus`.
- New endpoint `POST /api/meetings/{id}/recording` (presigned upload + job enqueue).
- New endpoint `GET /api/search?q=...` → semantic search on minutes + decisions for the calling tenant.

### 7.4 Tenant-aware AI
- All AI calls carry `tenant_id`; embeddings are per-tenant (no cross-tenant query in `pgvector`).
- Per-tenant token budget tracking (Bedrock metering → CloudWatch custom metric).
- Per-tenant **opt-out** flag (enterprise customers may disable AI entirely).

### 7.5 SaaS vs Enterprise AI
- SaaS: Bedrock + Transcribe (no extra ops).
- Enterprise air-gapped: Ollama (Llama 3.x) + Whisper (faster-whisper) packaged in the Helm chart. Same Python service, swap provider via env var.

---

## 8. One-Week MVP — Phased Plan

> Assumption: 2–3 engineers, parallel tracks. Each phase = roughly 1 day; days 6–7 = harden + demo.

### Day 1 — Foundation (Infra + Repo)
| Track | Tasks |
|---|---|
| **Infra** | AWS account baseline (IAM, KMS, VPC, 2 AZs, ECR, S3 buckets, RDS Postgres, ElastiCache Redis, SSM/Secrets, CloudWatch). Terraform module skeleton (`infra/terraform/`). |
| **App** | Add Dockerfiles (api, ui). Joint `docker-compose.dev.yml`. Drop SQL Server profile from MVP. Default profile → `postgres`. Add `application-prod.yml` driven entirely by env vars. |
| **Automation** | New monorepo or sibling `magales-infra/` with Terraform + GitHub Actions: build → trivy → push to ECR → register ECS task definition → deploy. |
| **AI** | Decide provider (Bedrock vs Deepgram). Provision Bedrock model access. Scaffold `magales-ai-worker` Python repo. |

### Day 2 — Multi-tenancy Spine
| Track | Tasks |
|---|---|
| App | Add `Tenant` entity + table. Add `tenantId` to `BaseEntity`. Hibernate filter. `TenantContext` ThreadLocal. JWT `tid` claim. `@PrePersist` listener. Update unique constraints to `(tenant_id, …)`. Cross-tenant isolation integration test. Sub-domain → tenant resolver. |
| UI | `/auth/tenant-context` call before login. Inject branding (logo, colors, name) at runtime. Replace hardcoded "Ijtimaati" / "Magales". |
| Automation | Flyway baseline `V1__init.sql` for Postgres with tenant columns. CI runs migration test. |

### Day 3 — Security & Identity
| Track | Tasks |
|---|---|
| App | Replace `.anyRequest().permitAll()` with proper rules. Move JWT secret to AWS Secrets Manager / SSM. Add fail-fast on missing secret. Refactor refresh-token hash to HMAC-SHA-256 with server pepper. Move Nafath transient state to Redis. Add `IdentityProvider` interface; Nafath becomes one adapter; password+OIDC are the others. Cognito federation set up. |
| UI | Move refresh token to HttpOnly cookie; access token stays in memory (signal). Implement strict CSP + Subresource Integrity. |
| Automation | Add OWASP ZAP baseline scan + `trivy` to CI. Pre-commit secrets scan (`gitleaks`). |
| AI | Skeleton AI worker + SQS consumer. End-to-end smoke: upload sample WAV → S3 → SQS → transcribe → Bedrock summary → DB. |

### Day 4 — Core domain hardening
| Track | Tasks |
|---|---|
| App | Pagination on every `findBy…` returning `List`. `@EntityGraph` on hot queries. NVARCHAR cleanup → portable types. Indexes: `tenant_id` composites. Soft-delete partial indexes. Health: split `liveness` / `readiness` indicators (DB, Redis, S3). Structured JSON logging + correlation ID filter. |
| UI | Wire all stub services to real endpoints. Replace mock data on Dashboard, Meetings, Voting, Minutes, Decisions, Signature pages. Loading + error states. |
| Automation | Postman / Insomnia OpenAPI collection auto-generated; published artifact. |
| AI | Real meeting → minutes pipeline: action-item extraction with Claude tool use. Embeddings into pgvector. `/api/search` endpoint. |

### Day 5 — Operational features
| Track | Tasks |
|---|---|
| App | S3 doc storage + presigned URLs. Move `Minutes.contentAr/En` to S3. Audit log dual-write (DB hot, S3 cold). Rate limiting (Bucket4j on Redis) on `/auth/*`. Email + SMS via SES + SNS. |
| UI | Document upload with progress. Search box (semantic) on Dashboard + Meetings. AI-generated minutes preview + accept/reject UX. |
| Automation | Blue-green ECS deploy via GitHub Actions. Rollback on health-check failure. CloudWatch dashboard provisioned via Terraform. |
| AI | Per-tenant token-budget metering. Admin endpoint `/api/admin/ai/usage`. |

### Day 6 — Hardening & QA
| Track | Tasks |
|---|---|
| All | Load test (k6) for 500 concurrent meeting attendees. Security review checklist. PII scrubbing in logs. RTO/RPO doc. KSA data-residency note (deploy region = `me-south-1` Bahrain or future `me-central-1` UAE — confirm with KSA customers; on-prem option = Saudi cloud Sahab). |
| UI | Cross-browser pass (Safari iPad — board members use those). RTL/LTR regression sweep. Print-to-PDF for minutes. |
| Automation | Helm chart for enterprise tier (parity with ECS task defs). |

### Day 7 — Demo & cut
| Track | Tasks |
|---|---|
| All | Seed demo tenant (e.g. `acme.magales.app`) with realistic data. Walk-through script. Cut `v0.1.0` tag. Run final security scan. Publish images to ECR. Internal demo. |

### Definition of Done for MVP
- [ ] One Postgres-backed shared instance, behind ALB, with WAF.
- [ ] Two ECS Fargate services (`api`, `ai-worker`); UI on S3+CloudFront.
- [ ] One demo tenant + one staging tenant fully isolated.
- [ ] Login (password + Nafath stub + OIDC), meeting CRUD, agenda, voting, decisions, minutes (with AI draft), signature stub, document upload to S3.
- [ ] AI: upload recording → get auto-minutes + extracted actions in <5 min for a 30-min meeting.
- [ ] Helm chart in `magales-infra/helm/` builds and runs locally on `kind`.
- [ ] CI/CD green on `main`; image scan passing; OpenAPI published.

---

## 9. Future Improvements (Post-MVP, Prioritized)

### Near-term (weeks 2–6) — close the SGT feature gap
1. **In-app secure chat** (المحادثات) — WebSocket service (`magales-realtime`); per-meeting + per-board + DM channels; messages encrypted at rest with tenant CMK. *Blocker for SGT parity.*
2. **Surveys & Evaluations** (التقييم والاستبيانات) — new module: `Survey`, `Question`, `Response`; templates for board self-evaluation, member 360, post-meeting feedback. *SGT has this, we don't.*
3. **Native video conferencing** (الاجتماع عبر الفيديو) — embed LiveKit / 100ms / Daily.co SDK. Replace `Meeting.videoLink` URL field with first-party in-app video that pipes audio directly into the AI worker for real-time transcription. *Blocker for SGT parity AND a wedge — they don't have AI on top.*
4. **Minutes approval workflow** (مراجعة واعتماد محضر الاجتماع) — review → comment → approve states with member sign-off log; today the entity exists but no workflow.
5. **Executive bylaw doc** (لائحة تنفيذية) on Board/Committee — versioned bylaw document attached per board; SGT lists this explicitly.
6. **External committees** (اللجان الخارجية) — members spanning multiple tenants. Requires `User` to be linked to multiple `tenant_id`s via a `tenant_membership` join table; revisit auth claims to carry active tenant + role list.
7. **Real-time agenda sync** — same WebSocket service; synchronized agenda screens across attendee devices.
8. **Per-tenant branding** — full theming, custom domain (`*.customer-domain.com`) via ACM + CloudFront.
9. **OIDC + SAML** SSO adapters wired for Microsoft Entra, Okta, Google Workspace.
10. **Aurora Postgres + read replicas** when single RDS hits ceiling.

### Mid-term (months 2–4)
11. **General Assembly module** (الجمعيات العمومية) — first-class flow distinct from board meetings:
    - `Shareholder` entity with capital share (% or shares-held)
    - Capital-weighted ballots (1 share = 1 vote)
    - Quorum = % of issued capital, not headcount
    - Proxy delegation (`Proxy` entity: shareholder → delegate, with limits)
    - Pre-GA ballot mailing, in-meeting voting, post-GA registrar export
    - GA-specific minutes template
    - This is the JSC / listed-company motion SGT advertises in its tagline; entering this segment requires this module.
12. **Mobile app** — iOS / Android (Capacitor on top of Angular shell) for attendance + voting + push notifications.
13. **Per-tenant schema option** for compliance-heavy tenants (Hibernate `MultiTenantConnectionProvider`).
14. **Advanced AI**: live in-meeting copilot (real-time transcription + suggested decisions); meeting brief generator from past minutes.
15. **Saen + DocuSign + Adobe Sign + eIDAS QES** adapters all live.
16. **EKS migration** when ≥4 services or GPU AI workloads.
17. **Audit & compliance pack**: PDPL (KSA), GDPR (EU), SOC 2 Type I evidence collection.
18. **OpenSearch** for full-text + audit search at scale.
19. **Marketplace integrations**: Microsoft Teams, Google Calendar, Outlook, Slack, Webex.

### Mid-term (months 2–4)
8. **Per-tenant schema option** for compliance-heavy tenants (Hibernate `MultiTenantConnectionProvider`).
9. **Advanced AI**: live in-meeting copilot (real-time transcription + suggested decisions); multilingual semantic search across all tenants' public knowledge bases (with consent).
10. **Saynee + DocuSign + Adobe Sign** adapters all live.
11. **Audit & compliance pack**: PDPL (KSA), GDPR (EU), SOC 2 Type I evidence collection.
12. **OpenSearch** for full-text + audit search at scale.
13. **Marketplace integrations**: Microsoft Teams, Google Calendar, Outlook, Slack, Webex.

### Long-term (months 4+)
20. **EKS + Karpenter** + GPU node pool for self-hosted AI in enterprise tier.
21. **Multi-region active-active** (KSA + EU + US) for global enterprise customers.
22. **AI agent layer**: autonomous "board secretary" that drafts agendas, prepares briefs from past minutes, and follows up on unfinished decisions.
23. **Investor relations portal** — bolted onto General Assembly module; shareholders self-serve view of past resolutions, dividend votes, AGM materials.

---

## 10. Action Items — Right Now

1. ✅ Adopt Postgres + pgvector as the single DB; **delete** SQL Server profile from `pom.xml` & `application-*.yml`.
2. ✅ Add `tenant_id` to `BaseEntity` + `TenantContext` + Hibernate filter (~1 day for a senior Spring dev).
3. ✅ Add Dockerfiles + `docker-compose.dev.yml` at the parent dir (`masarcorprepos/`).
4. ✅ Replace `.anyRequest().permitAll()`; pull JWT secret from env; fail-fast.
5. ✅ Move `NafathService` transient state from `ConcurrentHashMap` → Redis.
6. ✅ Bootstrap `magales-ai-worker` repo (Python + FastAPI + Celery + Bedrock client).
7. ✅ Bootstrap `magales-infra` repo (Terraform: VPC, ECS, RDS, ElastiCache, S3, ECR, ALB, WAF, Route53, CloudFront, IAM, Secrets, CloudWatch).
8. ✅ Rebrand decision: pick the new product name **before** the package rename (one Maven `groupId` change, one search-replace in 121 files).
9. ✅ Decide AWS region(s): **`me-south-1` (Bahrain)** for KSA tenants in MVP; add `eu-west-1` once we have a non-KSA design partner.

---

## 11. Business Feature Lifecycle

### 11.1 Release cadence (the timeline every feature is mapped to)
| Release | Window | Theme | Audience |
|---|---|---|---|
| **R0** | Week 1 (MVP) | Core governance loop end-to-end + AI minutes; one shared SaaS instance | Internal demo + 1 design-partner tenant |
| **R1** | Weeks 2–4 | SGT feature parity (chat, surveys, native video, minutes approval, real-time agenda); per-tenant branding | 3–5 design partners (private mid-market) |
| **R2** | Weeks 5–8 | GCC-ready: UAE PASS, multi-region, eIDAS QES, Stripe self-serve billing | Public beta — open signup |
| **R3** | Months 3–4 | General Assembly module + mobile + advanced AI copilot | GA / public launch — JSC + listed cos |
| **R4+** | Months 4+ | Multi-region active-active, EKS, AI agent layer, IR portal | Enterprise on-prem GA |

### 11.2 Lifecycle stages (each feature passes through these)
| Stage | Symbol | Definition |
|---|---|---|
| Stub | 🌱 | Schema/skeleton exists in code; not user-visible |
| MVP | 🌿 | End-to-end functional, single tenant, happy path only, behind feature flag |
| Beta | 🪴 | Multi-tenant safe, error states, telemetry, audit; opt-in for design partners |
| GA | 🌳 | SLA-backed, documented, in pricing tier, self-serve onboarding |
| AI-Enhanced | 🤖 | LLM/embedding capability layered on top (not a replacement) |
| Mature | 🏆 | Hardened, optimized, compliance-certified (SOC 2 / PDPL evidence) |
| Sunset | 💀 | Scheduled for removal; replacement live |

### 11.3 Per-feature lifecycle map

**Core governance loop** (table reads left→right as time progresses):

| Feature | R0 (Week 1) | R1 (Weeks 2–4) | R2 (Weeks 5–8) | R3 (Months 3–4) | R4+ |
|---|---|---|---|---|---|
| **Meeting scheduling** (جدولة الاجتماعات) | 🌿 CRUD + email invitations | 🪴 SMS + ICS calendar feed + recurrence | 🌳 Outlook/Google sync | 🤖 Smart-scheduling assistant (free-slot finder, conflict resolution) | 🏆 |
| **Boards & committees mgmt** (إدارة المجالس واللجان) | 🌿 Board/Committee CRUD + memberships + roles | 🪴 + executive bylaw doc (لائحة تنفيذية) versioned | 🌳 + external committees (cross-tenant members) | 🤖 Suggested members from past meeting attendance | 🏆 |
| **E-voting** (التصويت الإلكتروني) | 🌿 Open/close vote, cast ballot, instant tally | 🪴 + secret ballot, abstention rules, comment per ballot | 🌳 + custom thresholds, tie-break rules | 🤖 Outcome predictor for circular resolutions; sentiment from comments | 🏆 |
| **Minutes** (محضر الاجتماع) | 🌿 Manual draft + 🤖 AI auto-draft from recording | 🪴 Approval workflow (review→comment→sign-off log) | 🌳 PDF/DOCX export, watermark, redaction | 🤖 Live in-meeting minutes (real-time transcription) | 🏆 |
| **Decision tracking** (متابعة القرارات) | 🌿 Decision CRUD + assignment + status | 🪴 SLA timers, due-date reminders, evidence attach | 🌳 Cross-board portfolio view | 🤖 Auto-extract decisions+actions from minutes; risk scoring on overdue items | 🏆 |
| **Document library** (مكتبة المستندات) | 🌿 Upload to S3, presigned URL, categories, permissions | 🪴 Versioning, watermark, expiring shares | 🌳 + DLP scan, virus scan, bulk download | 🤖 Semantic search (pgvector) + auto-tagging + summary on hover | 🏆 |
| **E-signature** (التوقيع الإلكتروني) | 🌱 Schema only (rename `SAYNEE` → `SAEN`) | 🌿 Saen adapter live + sequential flow | 🪴 + DocuSign + Adobe Sign + eIDAS QES adapters | 🌳 Bulk sign, in-app draw signature | 🏆 |
| **Circular resolutions** (القرارات بالتمرير) | 🌿 Flag on VotingSession + async voting | 🪴 + reminders, auto-close on quorum reached | 🌳 + bundle multiple decisions in one circular | 🤖 Suggested wording + risk flags on draft circulars | 🏆 |
| **Conversations / chat** (المحادثات) | 🌱 placeholder UI | 🌿 1:1 + per-board channels (REST polling) | 🪴 WebSocket push, typing indicators, read receipts | 🌳 E2E encryption with tenant CMK; mentions/notifications | 🤖 Thread summarizer; "what was decided?" Q&A over channel history |
| **Video meetings** (الاجتماع عبر الفيديو) | 🌱 URL field only | 🌿 LiveKit/100ms embed + audio-tap to AI worker | 🪴 Recording auto-stored to S3 + auto-transcribed | 🌳 Native mobile video, screen share, breakouts | 🤖 Live captions, live action-item extraction, speaker analytics |
| **Surveys & evaluations** (التقييم والاستبيانات) | — | 🌱 Schema (Survey, Question, Response) | 🌿 Templates: post-meeting feedback, board self-eval | 🪴 360 board-member evaluation, anonymous mode | 🤖 Theme extraction across responses; insight reports |
| **General Assembly** (الجمعيات العمومية) | — | — | 🌱 Shareholder + Proxy entities | 🌿 Capital-weighted voting, % issued-capital quorum, AGM minutes template | 🪴 Pre-GA ballot mailing, registrar export, IR portal hooks |
| **Real-time agenda sync** | — | 🌱 WebSocket service skeleton | 🌿 Push agenda updates to attendee screens | 🪴 Multi-device cursor + presence | 🌳 |
| **Mobile apps** | — | — | 🌱 Capacitor wrapper PoC | 🌿 iOS + Android (attendance, voting, push) | 🪴 Offline-first cache + biometric auth |

### 11.4 Cross-cutting capabilities (on the same timeline)

| Capability | R0 | R1 | R2 | R3 | R4+ |
|---|---|---|---|---|---|
| **Multi-tenancy** | 🌿 Shared schema + `tenant_id` filter + JWT `tid` claim | 🪴 Sub-domain routing, per-tenant branding | 🌳 Per-tenant rate limits, quotas, audit | 🪴 Per-tenant schema option (compliance escape hatch) | 🌳 Per-tenant region pinning |
| **Identity** | 🌿 Password + JWT + Nafath (KSA) | 🪴 OIDC + SAML adapters (Entra, Okta, Google) | 🌳 + UAE PASS + MFA (TOTP, WebAuthn) | 🏆 SCIM provisioning | 🏆 |
| **Audit & compliance** | 🌿 AuditLog table | 🪴 Immutable audit (S3 cold + Postgres hot) | 🌳 PDPL data-export + delete flows | 🪴 SOC 2 Type I evidence collection | 🏆 SOC 2 Type II + ISO 27001 |
| **Billing** | — | 🌱 Plan/seat schema | 🌿 Stripe + Hyperpay (KSA) integration | 🪴 Usage metering (AI tokens, storage) | 🌳 Self-serve plan changes |
| **Observability** | 🌱 CloudWatch logs + actuator | 🌿 Structured JSON logs, X-Ray traces, RED metrics | 🪴 Per-tenant dashboards, SLO alerts | 🌳 Tenant-cost attribution | 🏆 |
| **Security posture** | 🌿 WAF + ALB + KMS + Secrets Mgr | 🪴 Pen-test #1, ZAP in CI, gitleaks | 🌳 Pen-test #2 + bug bounty (HackerOne) | 🪴 SOC 2 prep | 🏆 |
| **Self-hosted (enterprise)** | — | 🌱 Helm chart skeleton | 🌿 docker-compose + Helm parity | 🪴 Air-gapped install (Ollama + MinIO + Keycloak) | 🌳 Customer support runbooks |
| **Mobile** | — | — | 🌱 PoC | 🌿 iOS + Android beta | 🪴 GA |

### 11.5 AI capability lifecycle (the differentiator track)

| AI Capability | R0 | R1 | R2 | R3 | R4+ |
|---|---|---|---|---|---|
| Speech-to-text (AR + EN) | 🌿 Transcribe / Deepgram async | 🪴 Speaker diarization | 🌳 Real-time streaming (in-meeting) | 🏆 | 🏆 |
| Auto-minutes from transcript | 🌿 Bedrock Claude draft | 🪴 Editable AI-suggestions inline | 🌳 Multi-language output (AR/EN/FR) | 🤖 Live minutes during meeting | 🏆 |
| Action item extraction | 🌿 Claude tool-use → Decision rows | 🪴 Owner inference from speaker diarization | 🌳 Auto-assign + reminders | 🤖 Cross-meeting action rollup | 🏆 |
| Semantic search (pgvector) | 🌿 Embeddings on minutes + decisions | 🪴 + documents + chat | 🌳 + filters (board, date, status) | 🤖 RAG-powered Q&A ("what did we decide about X?") | 🏆 |
| Smart agenda assistant | — | 🌱 Templates from past meetings | 🌿 Suggest agenda from brief | 🤖 Pre-meeting brief generator | 🏆 |
| AI board secretary (agent) | — | — | 🌱 Skeleton agent loop | 🌿 Drafts agenda + chases overdue decisions | 🪴 Autonomous follow-up (with HITL approval) |
| Per-tenant token budget | 🌿 CloudWatch metric | 🪴 Per-feature breakdown | 🌳 Customer-facing usage page | 🏆 | 🏆 |
| AI opt-out (enterprise) | 🌿 Tenant config flag | 🪴 Self-hosted Ollama path | 🌳 Air-gapped LLM in Helm chart | 🏆 | 🏆 |

### 11.6 Sunset / deprecation track (things we kill, with target releases)

| Item | Replace with | Killed in |
|---|---|---|
| 💀 SQL Server profile (`application-sqlserver.yml`, mssql-jdbc dep) | Postgres + pgvector | R0 |
| 💀 H2 dev profile in-memory mode | docker-compose Postgres for all devs | R0 |
| 💀 In-memory `ConcurrentHashMap` Nafath transactions | Redis (ElastiCache) | R0 |
| 💀 `.anyRequest().permitAll()` in `SecurityConfig` | Explicit role rules + `.authenticated()` | R0 |
| 💀 Default JWT secret in `application.yml` | Fail-fast on missing env var; AWS Secrets Manager | R0 |
| 💀 `NVARCHAR(MAX)` columnDefinitions | Portable types (let dialect choose) | R0 |
| 💀 `Asia/Riyadh` hardcoded timezone | Per-tenant `timezone` field; UTC at DB layer | R0 |
| 💀 `localStorage` refresh token | HttpOnly Secure cookie | R0 |
| 💀 `SAYNEE` provider name (typo) | `SAEN` (correct brand) | R0 |
| 💀 `Minutes.contentAr/En` as `NVARCHAR(MAX)` in DB | S3 references + content-hash | R1 |
| 💀 `User.nationalId` as required | Optional + tenant-scoped | R1 |
| 💀 `EAGER` `User.roles` collection | LAZY + DTO projection | R1 |
| 💀 `sa.gov.magales.*` package namespace | `tech.<brand>.platform.*` (post-rebrand) | R1 (after new name picked) |
| 💀 ECS Fargate (when ≥4 services or GPU AI) | EKS + Karpenter | R4+ |

### 11.7 Lifecycle gates (Definition of Done per stage, applied uniformly)

A feature **only advances** when it passes the gate for the next stage:

| Gate | Criteria |
|---|---|
| **🌱 → 🌿 (MVP)** | Schema migrated, happy-path tested, behind feature flag, OpenAPI documented, can be demoed end-to-end on the dev tenant |
| **🌿 → 🪴 (Beta)** | Multi-tenant integration test (no leak), error states + i18n, audit log entries, telemetry (RED metrics), opt-in flag for design-partner tenants |
| **🪴 → 🌳 (GA)** | Load test ≥1000 concurrent users, runbook, on-call alert thresholds, customer-facing docs, billing tier assigned, support team trained |
| **🌳 → 🤖 (AI-Enhanced)** | LLM/embedding integration with per-tenant token budget, opt-out flag for enterprise, evals (precision/recall on benchmark set), prompt versioning |
| **🤖 → 🏆 (Mature)** | SLA met for ≥1 quarter, compliance evidence (SOC 2 / PDPL), pen-tested, optimized (p95 < target), security review signed-off |
| **→ 💀 (Sunset)** | Replacement at 🌳+ for ≥1 release, customer-comms sent, migration tool runs clean on staging, DB columns dropped in next migration window |

### 11.8 Lifecycle ownership

| Track | DRI | Cadence review |
|---|---|---|
| Core governance features | Backend tech lead | Weekly during R0–R1, biweekly after |
| AI track | AI/ML lead (new role) | Weekly |
| Multi-tenancy + identity | Platform/security lead | Weekly |
| Self-hosted / Helm | DevOps lead | Biweekly |
| Mobile | Mobile lead (R3) | Monthly until R3, weekly after |
| Compliance & audit | Security lead | Monthly; every release for evidence |

---

## Appendix A — Bug Fix Quick-List (file:line, severity)

| # | File | Line | Severity | Issue |
|---|---|---|---|---|
| 1 | `common/config/SecurityConfig.java` | 42 | **Critical** | `.anyRequest().permitAll()` |
| 2 | `application.yml` | 34 | **Critical** | Default JWT secret in source |
| 3 | `common/entity/BaseEntity.java` | (whole) | **Critical** | No `tenant_id` |
| 4 | `identity/service/NafathService.java` | 39 | **Critical** | In-memory tx map breaks on >1 replica |
| 5 | `identity/service/AuthService.java` | 116-117 | High | Redundant `generateAccessToken()` for `expiresIn` |
| 6 | `identity/service/AuthService.java` | 133-141 | High | Unsalted SHA-256 token hash |
| 7 | `identity/entity/User.java` | 85 | High | `EAGER` collection — load amplification |
| 8 | `meeting/entity/Meeting.java` | 28-50 | High | `NVARCHAR(MAX)` — not Postgres-compatible |
| 9 | `application.yml` | 8 | High | `Asia/Riyadh` hardcoded |
| 10 | `common/config/SecurityConfig.java` | 57 | High | Hardcoded CORS origins |
| 11 | `meeting/entity/Meeting.java` | 77, 82 | High | Lazy collections + no `@EntityGraph` → N+1 |
| 12 | `document/entity/Document.java` | (DTO) | Medium | `filePath` exposed in response |
| 13 | `identity/controller/AuthController.java` | (whole) | High | No rate limit on `/auth/*` |
| 14 | `Magales-ui/.../auth.service.ts` | 18-21 | Medium | Refresh token in `localStorage` |
| 15 | `board/service/BoardService.java` | (parent ref) | Medium | No cycle check on `parentBoardId` |
| 16 | `minutes/entity/Minutes.java` | 27-31 | Medium | Nullable `contentAr/En` at `PUBLISHED` |
| 17 | (everywhere) | — | Medium | Soft-delete index missing |
| 18 | (multiple repos) | — | Medium | Unpaginated `List` returns |

---

*End of plan. Companion artifacts to produce next: `infra/terraform/`, `Magales/Dockerfile`, `Magales-ui/Dockerfile`, `docker-compose.dev.yml`, `magales-ai-worker/` repo skeleton, Flyway `V1__init.sql`.*
