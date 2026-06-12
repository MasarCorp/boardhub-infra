# Meeting Capture (Teams / recordings) + AI Streaming — Research & Plan

Research for: "if a governance meeting is held in MS Teams, how do we transcribe + record it
like Notion AI meeting notes?" and "is AI streaming in the panel present?".

This is a **plan**, not yet implemented (except where noted). It is shaped for a **governance**
product (formal, reviewed, approved minutes), not ephemeral live notes.

---

## 1. AI streaming in the panel — ALREADY PRESENT ✅

The AI Assist panel streams token-by-token over SSE:

- Frontend posts to `POST /api/ai/assist/agent/stream`; `consume()` reads the body stream,
  `handleFrame()` parses JSON SSE frames, and `delta` frames append to the message, which the
  bubble re-renders live (`[innerHTML]="md(m.content)"`).
- Backend `ai-services` `event_stream` emits `data: {"type":"delta","text":...}` per token
  (JSON-encoded so newlines can't corrupt frames), plus `tool` / `citations` / `done`.

No work needed here. (If we later want a visible "stop generating" button or a typing caret, those
are small UI additions on top of the existing stream.)

---

## 2. Teams meeting transcription/recording — IS IT DOABLE? Yes.

Three viable approaches. Notion's own approach is included for comparison, then the recommendation.

### How Notion AI Meeting Notes actually works (for comparison)
Notion's **desktop app captures the device mic + system audio in real time** and transcribes/
summarizes — it is **not** a Teams API integration; it works across Zoom/Meet/Teams because it
records whatever the device plays. It cannot ingest pre-recorded files (real-time only). System-
audio capture requires the **desktop app** (a browser SPA cannot reliably capture system audio).
➡️ **Not a clean fit for our web app** — we'd need a desktop/Electron client to mimic it.

### Option A — Microsoft Graph, post-meeting transcript/recording (RECOMMENDED)
After a Teams meeting with transcription on, fetch the transcript via Graph:

- `GET /me/onlineMeetings/{id}/transcripts` then download the **VTT** (speaker-labelled,
  timestamped — superior to re-transcribing audio), and `/recordings` for the MP4.
- `GET /users/{id}/onlineMeetings/getAllTranscripts?...` to pull a date range in one call (avoids
  indexing-delay misses).
- Permissions: `OnlineMeetingTranscript.Read.All` (+ `OnlineMeetingRecording.Read.All` for video).
  Application permissions require the tenant admin to grant an **application access policy**.
- Limitations: only **calendar-backed / scheduled** meetings (not ad-hoc Meet-Now); transcription
  must have been **turned on** during the meeting.

➡️ Best fit for governance: reliable, speaker-labelled, no per-user Copilot licence, and it feeds
our existing **transcript → AI Minutes draft → review → save** workflow.

### Option B — Microsoft Graph Meeting AI Insights (beta, Teams Premium + Copilot)
`GET /copilot/users/{userId}/onlineMeetings/{id}/aiInsights` returns Microsoft's own summary,
action items and mentions. Requires an **M365 Copilot licence per user** (cost). Useful as an
extra source, but our LLM still produces the governance-formatted minutes. Optional add-on.

### Option C — Real-time bot (Notion-live-like)
A Teams bot (Azure Bot + Graph **Communications calling** API, `Calls.AccessMedia.All`,
application-hosted media) that joins the call and consumes live media/captions. **Heavy infra**
(media servers, certs) and live notes aren't the governance need. ➡️ Out of scope unless live
captions become a hard requirement.

---

## 3. Recommended phased plan (for our business)

| Phase | What | Effort | Status |
| --- | --- | --- | --- |
| 0 | **Upload the Teams recording (mp4/wav) → Whisper `/v1/transcribe` → AI Minutes draft → save.** Or paste the VTT transcript. Works today; needs only the **audio→minutes UI wiring** in the panel/meeting page. | Small | Pipeline done (Whisper + minutes); UI wiring pending |
| A | **Teams Graph integration:** Azure AD app registration; link a Magales meeting to a Teams `onlineMeeting`; after the meeting, fetch the VTT via `getAllTranscripts` (or a change-notification subscription) → AI Minutes draft. Store per-tenant OAuth tokens in Magales `IntegrationConfig` (encrypted, like the Saynee pattern). | Medium | Plan |
| B | **Optional:** pull Teams AI Insights (Copilot) as an extra source for tenants that have it. | Small-Med | Optional |
| C | **Optional:** real-time bot for live captions. | Large | Likely out of scope |

### Why Option A over the Notion model
Notion records device audio locally (desktop app). Our product is a **web** governance app and the
deliverable is a **formal minutes document that is reviewed and approved** — so pulling the
authoritative **Teams transcript after the meeting** (speaker-labelled) and generating a
review-ready minutes draft is both lower-effort and a better governance fit than live capture.

---

## 4. What's needed for Phase A (Teams integration) — checklist
- Azure AD app (client id/secret or cert), admin-consented Graph permissions
  (`OnlineMeetingTranscript.Read.All`, optionally `OnlineMeetingRecording.Read.All`,
  `OnlineMeetings.Read.All`); application access policy for app-only.
- A `teams` integration config per tenant (encrypted tokens) in Magales.
- ai-services: a `graph` client to fetch `getAllTranscripts` / download VTT; a `/v1/minutes/from-teams`
  flow (meeting_id ↔ Teams onlineMeeting id) → parse VTT → draft → `save_minutes`.
- A "Link Teams meeting" field on the Magales meeting + a "Pull transcript & draft minutes" action.
- (Optional) Graph change-notification webhook → auto-draft when a transcript is ready.

## 5. Streaming — nothing left (already implemented).
