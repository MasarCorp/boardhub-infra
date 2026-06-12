# Insights (Phase 5)

Computed governance analytics across meetings, decisions, tasks and voting — available on demand
and refreshed on a schedule into OpenSearch.

- ai-services: `GET /v1/insights` (fresh) / `GET /v1/insights?cached=true` (last scheduled snapshot);
  background `refresh_loop` persists per-tenant snapshots to the OpenSearch `insights` index.
- Backend proxy: `GET /api/ai/assist/insights`.
- Narrative surface: the **✦ AI insights** button on the Reports page (agent `get_insights`).

## 1. Structured analytics (fresh)

```bash
curl -sS "http://localhost:8080/api/ai/assist/insights" -H 'X-Tenant-Slug: acme' | python3 -m json.tool
```

**Expected:** JSON with `meetings`, `decisions` (`completion_rate`, `overdue`, `overdue_items`),
`tasks` (`overdue`, `high_critical`), `voting`, and a `risks` list. Numbers are computed (not
estimated) and match the records.

## 2. Cached (scheduled) snapshot

```bash
curl -sS "http://localhost:8080/api/ai/assist/insights?cached=true" -H 'X-Tenant-Slug: acme' | python3 -m json.tool
```

**Expected:** same shape, served from the last scheduled refresh. Confirm the snapshot exists:

```bash
curl -sS "http://localhost:9200/insights/_doc/acme" | python3 -m json.tool
```

The scheduler runs every `INSIGHTS_REFRESH_MINUTES` (default 30) for `INSIGHTS_TENANTS_CSV`
(default `acme,globex`). Check the worker log:

```bash
docker logs magales-ai-services 2>&1 | grep "insights refreshed"
```

## 3. Narrative insights (UI)

Reports page → **✦ AI insights** (or ask "how are we doing?" / "ما أبرز المخاطر؟" in the panel) →
headline numbers + a **Key Risks** section with clickable references.
