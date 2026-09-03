# AI Features — Test Guides

Step-by-step validation for the AI features built on top of the BoardHub stack
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
4. [AI Assist acceptance suite](07-ai-assist-test-plan.html) — **the source of truth for AI Assist.** 113 checks: the agent's business logic in Arabic, the SSE/AG-UI streaming protocol, the panel's UI and navigation, and cross-service integration. Open the file in a browser; it tracks your progress locally.
5. [AI capability register — English](10-ai-capabilities-en.html) and [Arabic](11-ai-capabilities-ar.html) —
   what every AI feature does **in business terms**, as a numbered list, plus a glossary of the terms
   (knowledgebase, precedent, guardrail, reminder vs notification…). Written for board members and
   buyers rather than engineers; pair it with the deck for a customer conversation.
6. [Client deck — English](08-boardhub-deck-en.html) and [Arabic](09-boardhub-deck-ar.html) — the 15-minute
   customer presentation ending in a live demo. **Generated**: edit [`deck/build_deck.py`](deck/), never
   the HTML, or the two languages drift apart.

Each guide lists the command, the expected result, and how to confirm.
