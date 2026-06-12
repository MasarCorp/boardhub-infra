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
Notion runs **both web and desktop**, but with different capture power:
- **Web (browser):** works, but **mic-only** — it transcribes your microphone. It does **not**
  capture system/conferencing audio digitally; with headphones, other participants are missed
  (without headphones the mic may pick them up acoustically). Notion nudges you to the desktop app.
- **Desktop app:** captures **mic + system audio** in real time (OS screen-recording permission),
  so it gets all participants even with headphones. It's **not** a Teams API integration — it
  records whatever the device plays (works across Zoom/Meet/Teams/in-person). Real-time only
  (no file upload).

➡️ Takeaway: a **web** app *can* do mic capture (like Notion web), and can do **better** than
Notion web by also using the browser tab/screen-audio API (`getDisplayMedia`) — see Option D.

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

### Option D — In-browser capture in OUR web app (Notion-web-like, but stronger) ⭐
Record the meeting **inside the Magales web app** and send the audio to our Whisper pipeline — no
Azure/Teams app, works for Teams/Zoom/Meet/in-person:
- **Mic** via `getUserMedia({audio:true})` — always available (covers in-person board meetings and
  your own voice). Same capability as Notion web.
- **Meeting audio** via `getDisplayMedia({audio:true})` — the user shares the **Teams/Zoom tab**
  (or screen) **with audio**, capturing all participants digitally even with headphones. This is
  what Notion web does NOT do.
- Mix mic + tab streams → `MediaRecorder` (webm/opus) → upload to `POST /v1/transcribe` (Whisper)
  → AI Minutes draft → review → save. Can chunk every N seconds for near-real-time, or record the
  whole meeting and transcribe at the end.

Caveats: `getDisplayMedia` audio is best on **Chromium desktop** (Chrome/Edge) — tab audio works
well; full system audio is Windows-only; macOS shares tab audio, not full system audio. Safari/
Firefox are limited. Mic always works. Requires the user to click "share tab + share audio".

➡️ **Best web-native fit**: closest to Notion without a desktop app, no Microsoft licensing/Azure,
and it reuses everything we already built (Whisper → minutes). Recommended alongside Option A
(Option A = authoritative transcript when the meeting is in Teams with transcription on; Option D =
universal in-app recorder when it isn't).

### Option C — Real-time bot (Notion-live-like)
A Teams bot (Azure Bot + Graph **Communications calling** API, `Calls.AccessMedia.All`,
application-hosted media) that joins the call and consumes live media/captions. **Heavy infra**
(media servers, certs) and live notes aren't the governance need. ➡️ Out of scope unless live
captions become a hard requirement.

---

## 3. Recommended phased plan (for our business)

| Phase | What | Effort | Status |
| --- | --- | --- | --- |
| 0 | **Upload a recording (mp4/wav) or paste a VTT** → Whisper `/v1/transcribe` → AI Minutes draft → save. Works today; needs only the **audio→minutes UI wiring**. | Small | Pipeline done; UI wiring pending |
| **D** ⭐ | **In-app recorder (web):** mic (`getUserMedia`) + optional tab/screen audio (`getDisplayMedia`) → `MediaRecorder` → `/v1/transcribe` → minutes. Notion-web-like, universal (Teams/Zoom/Meet/in-person), no Azure. | Medium | Plan (recommended near-term) |
| A | **Teams Graph integration:** Azure AD app; link a Magales meeting to a Teams `onlineMeeting`; fetch the authoritative VTT via `getAllTranscripts`/subscription → minutes. Tokens in Magales `IntegrationConfig` (encrypted). | Medium | Plan (when meeting is in Teams w/ transcription) |
| B | **Optional:** pull Teams AI Insights (Copilot) as an extra source. | Small-Med | Optional |
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
