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
