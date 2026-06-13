# AI Meeting Notes — lifecycle-integrated design (Summary / Notes / Transcript)

Goal: mirror the Notion AI Meeting Notes UX **inside our meeting lifecycle** — when a meeting is
**started** it records, when it **ends** the system automatically produces the three artifacts
(**Summary · Notes · Transcript**) shown as tabs on that meeting. Reuse what exists; build only the gaps.

## We already have the skeleton — don't reinvent

| Notion piece | Our equivalent (exists) | Reuse |
| --- | --- | --- |
| "Start meeting" | `PATCH /api/meetings/{id}/start` → `IN_PROGRESS` (the existing **Start meeting** button) | start the recorder here |
| "Meeting is done" auto-trigger | `PATCH /api/meetings/{id}/end` → `COMPLETED` (the **End meeting** button) | run the AI pipeline on success |
| **Summary** tab | `Minutes.executiveSummary` | LLM fills it |
| **Notes** tab | `Minutes.contentAr` / `contentEn` (structured minutes) | existing AI-minutes draft + `save_minutes` |
| **Transcript** tab | Whisper `POST /v1/transcribe` output | generation exists; **storage is the gap** |
| Record audio (web) | — | Option D in-browser capture (`getUserMedia` + optional `getDisplayMedia`) |
| Minutes review/approve | `MinutesStatus` DRAFT→…, minutes comments/approval flow | existing |

Meeting states: `DRAFT → SCHEDULED → IN_PROGRESS → COMPLETED` (+ CANCELLED/POSTPONED).

## End-to-end flow (lifecycle-integrated)

1. **Start meeting** (`/start` → IN_PROGRESS): meeting page shows a **Recording** indicator and a
   consent notice; browser captures **mic** (`getUserMedia`) and, optionally, the **Teams/Zoom tab
   audio** (`getDisplayMedia({audio:true})`). (Recording lives in the browser; chunk-upload for long
   meetings, or one blob at the end.)
2. **End meeting** (`/end` → COMPLETED) — the auto-trigger:
   - stop recorder → upload audio → `POST /v1/transcribe` (Whisper) → **transcript**;
   - `POST /v1/minutes/generate {meeting_id, transcript}` → LLM returns **{executiveSummary,
     contentAr, contentEn, actionItems[]}** grounded in the agenda + transcript;
   - persist a `Minutes` **draft** carrying Notes (content) + Summary (executiveSummary) + the
     **transcript**, plus the audio stored as a linked Document (storage layer we built);
   - the meeting page reveals **Summary | Notes | Transcript** tabs (editable, review → approve).
3. **Action items**: from `actionItems[]`, offer one-click create via the existing `create_task` /
   `POST /api/tasks` (source=MINUTES) — already built.

## Build status

**Stage 1 — backend + AI generate: DONE 2026-06-13 (validated).**
- `MeetingNote` entity/repo/DTOs + owner-scoped service & controller `/api/meeting-notes`
  (create / list-mine / get / update / link / delete). **Each note is owned by its creator**
  (`ownerId`); only the owner can edit/link/delete. Validated: create 201; owner edit 200;
  **non-owner edit 403**; ownership isolation (other user sees 0); owner link→meeting 200.
- ai-services `POST /v1/meeting-notes/generate {transcript, meeting_id?}` →
  `{summary, notesAr, notesEn, actionItems[]}` (LLM, grounded in the agenda). Proxy
  `POST /api/ai/assist/meeting-notes/generate`. Validated: produced Arabic summary + bilingual
  notes + extracted action item.
- Decision model confirmed: per-user ownership (panel note → panel user; meeting note → meeting
  owner; other attendees keep their own note in their own space).

**Stage 2 — frontend: DONE 2026-06-13 (validated).**
- `MeetingNoteService` + `RecorderService` (mic + optional tab audio via `getDisplayMedia`).
- **My Meeting Notes** page (`/meeting-notes`, sidebar nav) + **3-tab** detail (Summary / Notes /
  Transcript), owner-edit + link-to-meeting. Note markdown rendered via `marked`.
- In-app **recorder** with a **consent gate** + a **paste-transcript** fallback; flow:
  transcribe → generate → create note → open it.
- Panel `+` **"🎙 AI Meeting Notes"** (ad-hoc, or scoped to the current meeting) + a meeting-page
  **"🎙 AI Meeting Notes"** button.
- Backend `POST /api/ai/assist/transcribe` multipart proxy → Whisper.
- Validated end-to-end via API: audio→transcript→summary/notes→MeetingNote (201, owner-scoped).
- **Follow-up:** true *live capture during the meeting* (recorder hosted on the meeting page across
  Start→End with auto-generate on End) — current entry point is a button that opens the recorder
  scoped to the meeting.

## Gaps to build (next steps, in order)

1. **Store the transcript** (backend): add `transcript` (text/LOB) to `Minutes` + `MinutesCreateRequest`/
   `MinutesResponse`. Store the **audio** as a `Document` (via the new MinIO layer) linked to the meeting
   for audit/replay. *Small.*
2. **Generate endpoint** (ai-services): `POST /v1/minutes/generate {meeting_id, transcript}` → structured
   `{executiveSummary, contentAr, contentEn, actionItems[]}` (LLM, JSON). *Small.* Reuses agenda fetch.
3. **In-app recorder** (frontend, Option D): mic + optional tab audio → `MediaRecorder`; tied to
   Start/End; visible recording state + **consent notice**. *Medium.*
4. **Auto-pipeline on End** (frontend orchestrates, since audio is in the browser): on `/end` success →
   transcribe → generate → save Minutes → show tabs. *Medium.*
5. **3-tab UI** on the (completed) meeting page: **Summary / Notes / Transcript**, editable, with
   "regenerate", "save", "approve", and "create tasks from actions". *Medium.*
6. **Robustness/governance**: chunked upload + progressive transcription for long meetings; **recording
   consent + retention policy** (board meetings — compliance); per-tenant on/off. *Medium.*

## How the two capture sources converge
- **Option D (in-app recorder)** → audio → Whisper → transcript → the same `generate` + tabs.
- **Option A (Teams Graph)** → authoritative VTT → straight into `generate` + tabs (no Whisper).
Both fill the **same** Summary/Notes/Transcript on the meeting — pick the source per meeting.

## Reuse summary (already shipped)
Whisper transcribe · AI minutes draft + `save_minutes` · `create_task` (actions) · MinIO storage ·
`Minutes` (content + executiveSummary) · meeting start/end lifecycle · streaming panel.
**New build = transcript storage + `/v1/minutes/generate` + recorder + 3-tab UI + End auto-trigger.**

---

## Session update — 2026-06-13 (testing feedback round)

Shipped in response to live test feedback. All validated against the running dev stack.

### 1. Live recorder ON the meeting page (was a gap above — now closed)
- `MeetingDetailComponent` shows a **"Record this meeting"** card while the meeting is `IN_PROGRESS`.
- Consent checkbox + two buttons (see #4). On **Stop & generate** it runs
  `transcribe → /meeting-notes/generate → create MeetingNote (source=MEETING, linkedMeetingId)`
  and surfaces an **Open notes** link. No raw ids touched by the user.
- The older entry point (button → `/meeting-notes?record=1&meetingId=`) still works for ad-hoc capture.

### 2. Smart `create_decision` agent action (parity with `create_meeting`)
- New Strands tool in `assist_agent.py`. Resolves **board** by name/code/UUID and an **optional
  meeting** by number/title/UUID — the user never types an id.
- Required by the backend and gathered/confirmed by the agent: `decisionNumber`, `titleAr`,
  `issuedDate`, **`category`** (`STRATEGIC|FINANCIAL|OPERATIONAL|LEGAL|HR|IT|OTHER`). Posts to
  `POST /api/decisions`. Validated: created `2026-502` with a clickable `[n]` reference.
- **Backend bug fixed along the way:** `Decision.progressPercent` (NOT NULL) lacked `@Builder.Default`,
  so every decision insert failed with a 500 (null `progress_percent`). Added `@Builder.Default` —
  the same class of bug previously fixed for `Document.currentVersion`.

### 3. In-panel board/committee picker (interactive choices, not a typed name)
- `present_board_choices` tool sets `state.choices = {kind, prompt, options[]}`.
- `agent.py` emits an SSE `event: choices` frame (and a `choices` field on the non-stream response).
- The Angular panel parses it (`AiAssistService.handleFrame` → `AssistMessage.choices`) and renders
  the options as buttons; clicking one calls `pick()` → sends the chosen value as the next turn and
  locks the picker. Used before `create_meeting`/`create_decision`.

### 4. Recorder screen-share UX (fix: mic-only must never prompt)
- Replaced the single "Start recording" + tab-audio checkbox with **two explicit buttons**:
  **🎙 Record (microphone)** — mic only, never calls `getDisplayMedia`, so **no screen/tab prompt**;
  **🖥 Record + meeting audio** — also captures a meeting tab's sound, which the browser can *only* do
  via the tab-share picker (there is no other web API). A hint line explains the difference.
- Applied to both the `/meeting-notes` recorder modal and the in-meeting recorder card.

### 5. Link-to-meeting uses a dropdown, not a raw id
- `MeetingNoteDetailComponent` "Link to meeting" now loads `MeetingService.list()` into a `<select>`
  (label `meetingNumber — title`) instead of a free-text "meeting id" field.

### 6. Arabic ASR accuracy → `WHISPER_MODEL=medium`
- Garbled Arabic transcripts (and the wrong summaries downstream) were caused by `small`.
- Default bumped to **`medium`** (compose + `config.py`); set `WHISPER_MODEL=large-v3` for best Arabic
  at the cost of a heavier download and slower CPU inference.

### 7. Pluggable transcription engine + repetition/language fixes (follow-up round)
Two further bugs showed up in testing: Whisper **looped** ("كيف حالكم؟ ×10", "How are you? I'm fine ×N")
and the UI was **forcing `language=en`** so Arabic speech got transcribed/translated into English.
- **`app/transcription.py`** (new) — pluggable STT with two backends, selectable via
  `TRANSCRIBE_PROVIDER` env or a per-request `?provider=`:
  - **`openrouter`** (default): an audio-INPUT multimodal LLM (default `google/gemini-2.5-flash`) via
    OpenRouter chat completions with an `input_audio` part. Strong Arabic; transcribes verbatim in the
    original spoken language. Audio is decoded webm/opus→16 kHz mono WAV in-memory with **PyAV** (no
    ffmpeg CLI in the image). Uses `OPENROUTER_API_KEY`. Falls back to local Whisper on any error.
  - **`whisper`**: local faster-whisper, now with temperature-fallback + `compression_ratio_threshold`/
    `log_prob_threshold` + `repetition_penalty=1.15` + `no_repeat_ngram_size=3` to kill the loop, and
    **auto language detection** (no longer forces the UI language).
  > Note: OpenRouter's `output_modalities=audio` models are *text-to-speech*; transcription uses
  > *audio-input* chat models instead. OpenRouter has no dedicated `/audio/transcriptions` endpoint.
- **Frontend**: recorder modal gains a **Spoken language** selector (Auto/AR/EN, default Auto — never
  the UI language) and a **Transcription engine** selector (Cloud AI / On-device Whisper). The summary
  is generated in the *spoken/detected* language, falling back to the UI language. The meeting-page
  live recorder auto-detects + uses the server-default engine.
- **Proxy**: `AiAssistController#transcribe` forwards `provider` alongside `language`.
- Validated end-to-end with the real OpenRouter key on Arabic + English audio: both engines return the
  correct spoken-language transcript with no repetition.

### 8. "Create a decision/task from THIS meeting note" (context + non-blocking draft)
On a meeting-note page the AI panel said *"I can't see the page you're browsing"* and fell back to
`list_meetings`, because `/meeting-notes/:id` was never mapped and the note is **owner-scoped** (the
agent can't fetch it over the internal HMAC path).
- **Frontend pushes the facts it already has.** `AiAssistService.setEntity({type, id, label, facts})`
  (cleared on navigation); `MeetingNoteDetailComponent` registers the note's title/linkedMeetingId/
  summary/notes/actionItems/transcript (clipped). `ask()` sends `scope_kind/scope_id/scope_facts`.
- **Backend** `AgentRequest.scope_facts`: when present, used directly as the scope context (skips
  `fetch_scope_context`) — so the agent acts on "this note".
- **Decision needs a board, not a meeting.** Prompt clarified: a decision always needs a
  board/committee (via `present_board_choices`); a meeting link is OPTIONAL. New tool
  **`present_meeting_choices`** offers a clickable meeting picker for linking (frontend renders any
  `state.choices` kind generically).
- **Never a blocker.** If the user won't assign a board / link a meeting, the agent does NOT refuse —
  it DRAFTS the full decision inline (number, titleAr+titleEn, category, body, action items) for
  copy-paste, and offers to file it for real once they pick a board. Validated both paths.
