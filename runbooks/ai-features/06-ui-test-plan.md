# AI Features — UI Test Plan

Manual, browser-driven test plan for the AI features delivered in the 2026-06-13 testing round
(AI Meeting Notes, two-button recorder, live meeting recorder, in-panel board/committee picker,
smart `create_meeting`/`create_decision`, meeting-link dropdown, Arabic ASR). Run top-to-bottom.

> ASR note: these steps assume the current `WHISPER_MODEL=medium` (CPU, in Docker). An engine
> decision is still open (MLX host-GPU / Groq cloud / CPU large-v3) — see runbook 05 + 02.

---

## 0. Preconditions / setup
| # | Check | Expected |
|---|---|---|
| 0.1 | Stack up: `docker compose -f docker-compose.dev.yml ps` | api, ai-services, ui all **healthy** |
| 0.2 | Open `http://localhost:4200`, log in (tenant **acme**) | Dashboard loads |
| 0.3 | Use **Chrome/Edge desktop** | Recorder needs `MediaRecorder` + tab-audio (Chromium) |
| 0.4 | Grant the site **microphone** permission when first prompted | Mic allowed |
| 0.5 | Test both languages: toggle **EN ⇄ AR** (top bar) | UI flips LTR ⇄ RTL |

**Test data:** seeded boards = *لجنة المراجعة والتدقيق / Audit & Review Committee* and
*مجلس الإدارة الرئيسي / Board of Directors*.

---

## A. Recorder screen-share fix
Core complaint: mic recording must **never** ask to share a screen.

| # | Step | Expected |
|---|---|---|
| A.1 | **Meeting Notes** (sidebar) → **✦ New** | Modal: title prefilled, consent checkbox, **two** buttons **🎙 Record (microphone)** and **🖥 Record + meeting audio**, plus a hint line |
| A.2 | Tick consent | Both record buttons enable |
| A.3 | Click **🎙 Record (microphone)** | Recording starts **immediately — NO "Choose what to share" dialog**. Red dot + timer |
| A.4 | Speak a few sentences → **⏹ Stop & generate** | Orb → "Transcribing…" → "Generating…" |
| A.5 | Re-open modal, consent, **🖥 Record + meeting audio** | *Now* the browser tab/share picker appears (only path for tab audio) |
| A.6 | Cancel the share picker | Recording continues **mic-only** (graceful), not an error |
| A.7 | Read the hint line in AR and EN | Explains mic-only never prompts; +meeting-audio shares a tab |

✅ **Pass if:** A.3 produces zero screen-share prompt.

---

## B. Arabic transcription accuracy
| # | Step | Expected |
|---|---|---|
| B.1 | UI → **AR**. Meeting Notes → New → consent → **🎙 Record (microphone)** | Records |
| B.2 | Speak ~30–60s of clear **formal Arabic** (mock board discussion) | — |
| B.3 | Stop & generate | First run slower (medium warm-up). Transcript **markedly more accurate** than the old garbled output |
| B.4 | Open note → **النص (Transcript)** tab | Readable Arabic |
| B.5 | **الملخص (Summary)** tab | Summary + بنود العمل **in Arabic**, relevant to what was said (not invented) |

✅ **Pass if:** transcript is intelligible and the summary reflects the audio.
> If accuracy is still insufficient → that's the open `large-v3` / GPU decision.

---

## C. Paste-transcript path (no audio)
| # | Step | Expected |
|---|---|---|
| C.1 | Meeting Notes → New → paste Arabic text into **"or paste a transcript"** | — |
| C.2 | **Generate notes** | Skips transcription → Summary/Notes/Actions from pasted text |

---

## D. 3-tab note detail + edit + ownership
| # | Step | Expected |
|---|---|---|
| D.1 | Open a note from the list | Header + 3 tabs: **Summary / Notes / Transcript** |
| D.2 | Click each tab | Summary = summary + action items; Notes = AR/EN body per UI lang; Transcript = raw text |
| D.3 | As **owner**: Edit → change summary → **Save** | Saved, view updates |
| D.4 | Open same note as a **different user** | **Edit/Link/Delete hidden** (owner-only); viewing still works |

---

## E. Link-to-meeting dropdown
| # | Step | Expected |
|---|---|---|
| E.1 | Note detail (as owner) → **Link to meeting** | Panel with a **dropdown** (not a "meeting id" text box) |
| E.2 | Open dropdown | Lists meetings as **`MTG-number — title`** |
| E.3 | Pick one → **Link** | Note links; header shows **Open meeting**; Link disabled until a meeting is chosen |
| E.4 | **Open meeting** | Navigates to that meeting |

✅ **Pass if:** no raw UUID ever shown/entered.

---

## F. AI Assist — in-panel board/committee picker
| # | Step | Expected |
|---|---|---|
| F.1 | Open **AI Assist** panel. Switch to AR | Panel open |
| F.2 | Send: **"أريد إنشاء قرار جديد"** | Assistant renders **clickable buttons** for each board/committee — not a typed list |
| F.3 | Hover a choice | Fills with accent color |
| F.4 | Click **لجنة المراجعة والتدقيق** | Button **locks/highlights**; assistant proceeds with the choice |

---

## G. Agent — smart `create_meeting`
| # | Step | Expected |
|---|---|---|
| G.1 | AI panel (AR): **"جهّز اجتماعاً جديداً"** | Asks which board via the **picker** |
| G.2 | Pick board, then provide title / date+time / type / quorum (or all at once) | Summarizes for **confirmation** before creating |
| G.3 | Confirm | **"Created meeting MTG-… [n]"** with a clickable **[n]** reference |
| G.4 | Click the reference | Opens the new meeting (status **DRAFT**) |

---

## H. Agent — smart `create_decision`
| # | Step | Expected |
|---|---|---|
| H.1 | AI panel (AR): **"أنشئ قراراً"** | Asks board via **picker**, then decision number, title, issue date, **category** |
| H.2 | Provide fields (category may be inferred from title) | Summarizes, asks to confirm |
| H.3 | Confirm | **"تم إنشاء القرار … [n]"** with clickable reference — **no 500** (backend `progressPercent` fix) |
| H.4 | Open the reference | Decision detail loads |
| H.5 | Negative: give an unknown board name | Agent offers the picker / lists available boards; no crash |

---

## I. Agent — action items in Arabic (regression)
| # | Step | Expected |
|---|---|---|
| I.1 | Completed meeting with minutes; AI panel (AR): **"استخرج بنود العمل من محضر هذا الاجتماع"** | Action items **in Arabic** (title/owner/due), not English |

---

## J. Live recorder on the meeting page
| # | Step | Expected |
|---|---|---|
| J.1 | Open a meeting → **Start meeting** (→ IN_PROGRESS) | **"Record this meeting"** card appears below the status flow |
| J.2 | Check DRAFT/SCHEDULED/COMPLETED meetings | Card visible **only** while IN_PROGRESS |
| J.3 | Consent → **🎙 Record (microphone)** | Records (no screen prompt); red dot + timer |
| J.4 | **⏹ Stop & generate** | Orb → Transcribing → Generating |
| J.5 | On finish | Card shows **✅ ready** + **Open notes** |
| J.6 | **Open notes** | MeetingNote **linked to this meeting** (source = MEETING) |
| J.7 | Confirm linkage | Note header shows **Open meeting** back to J.1 |

---

## K. RTL / i18n sweep
| # | Step | Expected |
|---|---|---|
| K.1 | In **AR**: Meeting Notes modal, note detail, meeting recorder card, AI picker | Labels translated, layout **RTL**, buttons mirrored |
| K.2 | Switch to **EN** | English labels, **LTR** |
| K.3 | Note with AR + EN body | Notes tab shows the side matching UI language |

---

## L. Negative / robustness
| # | Step | Expected |
|---|---|---|
| L.1 | Start recording with consent **unticked** | Record buttons disabled |
| L.2 | Stop with near-silence | Graceful: empty/short transcript, no crash |
| L.3 | Kill network mid-generate | Error message shown (spinner not stuck) |
| L.4 | Very long recording (5+ min) | Completes (slower on medium/CPU) — record the time for the ASR decision |

---

## Triage
- Recorder issues → DevTools console + `getUserMedia` permission.
- Transcription/summary → `docker compose -f docker-compose.dev.yml logs ai-services`.
- Decision/meeting create errors → `docker compose -f docker-compose.dev.yml logs api`.

## Coverage map (feature → commit area)
- Two-button recorder, board picker, meeting-link dropdown, live recorder → **Magales-ui** `develop`.
- `present_board_choices`, `create_decision`, `event: choices`, Whisper medium → **ai-services** `feat/ai`.
- `Decision.progressPercent` `@Builder.Default` fix → **Magales** `develop`.
- `WHISPER_MODEL=medium` + this plan → **magales-infra** `main`.
