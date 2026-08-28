# AI Features — Test Guides

Step-by-step validation for the AI features built on top of the Magales stack
(`api` = backend, `ai-services` = Python AI worker). Bring the stack up with:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Local URLs:

| Service | URL |
| --- | --- |
| Backend API | http://localhost:8080/api |
| ai-services | http://localhost:8081 |
| MinIO console | http://localhost:9001 (magales / magales-dev-secret) |
| OpenSearch | http://localhost:9200 |
| UI | http://localhost:4200 |

All tenant-scoped calls use the header `X-Tenant-Slug: acme` (dev tenant).

## Guides

1. [Storage + document vectorization](01-storage-and-documents.md) — upload/download document files (MinIO) and index their content into RAG.
2. [Audio → minutes (Whisper)](02-audio-minutes.md) — transcribe a recording and draft/save minutes.
3. [Insights](03-insights.md) — structured governance analytics endpoint + scheduled persistence.
4. [AI Assist acceptance suite](07-ai-assist-test-plan.html) — **the source of truth for AI Assist.** 45 checks: the agent's business logic in Arabic, the SSE/AG-UI streaming protocol, the panel's UI and navigation, and cross-service integration. Open the file in a browser; it tracks your progress locally.

Each guide lists the command, the expected result, and how to confirm.
