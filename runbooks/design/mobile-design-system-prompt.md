# BoardHub — design system prompt for the mobile app

Hand this to Claude Design as the brief. Every value below was read out of the running product on
9 September 2026, not invented — if something here contradicts the repos, the repos win and this
file is stale.

---

## 1. What BoardHub is

A **board governance platform** for Saudi and Gulf organisations: boards of directors, committees
and their secretariats. It runs meetings end to end — agenda, papers, attendance, quorum, voting,
minutes, decisions, follow-up tasks and e-signature — and it has an AI assistant that can read and
act on the whole governance record.

**Who holds the phone.** Assume a board member in their 50s–70s, on an iPhone or iPad, in a car or a
lobby, ten minutes before a meeting, reading Arabic. They are not power users and will not hunt.
The secretariat are the power users, and they mostly sit at a desk — so **the phone is for the
member, and the desktop is for the secretary.** When those two pull in different directions on
mobile, the member wins.

The three tasks that justify the app existing at all:
1. *"What am I walking into?"* — the pre-meeting brief.
2. *"Vote / confirm / sign."* — the things with a deadline.
3. *"Ask the assistant."* — a question answered from the real record, with sources.

Everything else is reachable, but it should not compete with those three.

---

## 2. Bilingual is the architecture, not a feature

The product is **fully bilingual Arabic ⇄ English, and Arabic is the primary language.** There are
**3,143 translation keys in each of `ar.json` and `en.json`** and they are kept exactly in step.

- **Every single string is translated.** Design nothing that hardcodes text into an image or icon.
- **RTL is a full mirror**, not a text-direction switch: navigation, back arrows, progress, sliders,
  drawers, swipe directions, chart axes, table column order and the chat bubble side all flip.
  Icons that encode direction (chevrons, arrows, send, reply, undo) mirror. Icons that do not
  (clock, calendar, search, user, checkmark, download) **must not** mirror.
- **Numbers, dates and times do not mirror.** A time stays `10:00`, a reference stays `BOD-2026-013`.
- Arabic text runs **10–20% longer** than English at the same font size and has taller ascenders and
  descenders. Every control must survive that without clipping or reflowing to two lines. Test the
  longest Arabic label, not the English one.
- **Both languages use the same typeface: `Noto Kufi Arabic`.** This is deliberate and unusual —
  Latin text is set in the Arabic family so the two languages sit at the same weight and colour on
  screen and a mixed sentence does not look spliced. Do not introduce a separate Latin font.
- Mixed-direction strings are everywhere ("قرار BOD-2026-013 معتمد"). Use proper bidi isolation so
  a Latin reference inside an Arabic sentence does not reorder the punctuation around it.
- The language switch is **instant and in-place** — no reload, no losing your position.

---

## 3. Design tokens — use these exact values

These are the live CSS custom properties. Do not invent hexes; every colour must map to a token.

**Brand**
```
--brand-navy   #0A1F44      --brand-blue   #1E3A8A     --brand-mid    #2E5597
--brand-accent #3B82F6      --brand-light  #EFF4FC     --brand-soft   #F6F9FE
```

**Neutral ramp**
```
--ink-900 #0F172A   --ink-700 #334155   --ink-500 #64748B   --ink-400 #94A3B8
--ink-300 #CBD5E1   --ink-200 #E2E8F0   --ink-100 #F1F5F9   --ink-50  #F8FAFC
```

**Semantic surfaces — everything flows through these so dark mode recolours the whole app**
```
--app-bg   #F0F2F5    page background        --surface   #FFFFFF   cards, sheets, popovers
--surface-2 #FAFBFC   raised areas           --border    #E2E8F0   hairlines
--hover    #F1F5F9    pressed / muted fill   --text      #0F172A   primary text
--muted    #64748B    secondary text
```

**Status** — each is a trio (line / fill / text), and status must never be colour alone:
```
success #10B981 / #D1FAE5 / #065F46      warning #F59E0B / #FEF3C7 / #92400E
danger  #EF4444 / #FEE2E2 / #991B1B      info    —       / #DBEAFE / #1E40AF
```

**Radius** `--radius-sm 6px` · `--radius 10px` · `--radius-lg 14px` · `--radius-xl 20px`
Cards use `lg`, controls use `10px`, sheets use `xl`. Nothing else.

**Elevation** — four steps, and restraint is the house style:
```
--shadow-sm  0 1px 3px rgba(15,23,42,.06), 0 1px 2px rgba(15,23,42,.04)
--shadow     0 4px 12px rgba(15,23,42,.08), 0 1px 3px rgba(15,23,42,.04)
--shadow-lg  0 10px 30px rgba(15,23,42,.12)
--shadow-xl  0 25px 50px -12px rgba(15,23,42,.25)
```
On mobile, `--shadow-sm` for cards, `--shadow-lg`/`xl` only for sheets and the assistant panel.
**Prefer a background-tone change over a visible 1px box.** No gradients.

**Spacing** — a strict 4px scale. No arbitrary values.

**Dark theme is required, not optional.** It is a real inverted ramp under `[data-theme="dark"]`
(`--ink-900` becomes the *lightest* value). Design every screen in both, and never let a colour
exist only in one theme.

---

## 4. Component and icon rules

These are enforced in the codebase and the mobile app must match, or the two products will drift.

- **Icons: Lucide only** (`@ng-icons/lucide`). No emoji anywhere in the UI — this has been actively
  removed twice. No custom glyphs without adding them to the set properly.
- **Components come from the shared `spartan/ui` helm set** — buttons, inputs, dialogs, selects,
  tabs, tooltips. Do not design a one-off control where one exists.
- Touch targets **44×44pt minimum**; 48 for anything a 70-year-old taps in a moving car.
- Every interactive element needs **five states**: default, pressed, disabled, loading, error.
- Every list needs **four states**: loading (skeleton, not a spinner), empty (with the action that
  fills it), error (with retry), and populated.

---

## 5. The surface area you are designing for

**85 routes exist on desktop.** Do not port them. The navigation groups are:

> Dashboard · Control panel · **Meetings** · Agenda items · Minutes · **Voting** · Decisions ·
> **Signature** · Boards · External committees · Assessments · Surveys · Board packs · Library ·
> Transactions · Reminders · Chat · Reports · **Tasks** (inbox, sent, drafts, transactions,
> reports) · Appointments (daily agenda, annual agenda) · My preferences (signatures, committees,
> delegations, security) · System settings (users, roles & permissions, delegations, notification
> settings, task settings)

**Proposed mobile shape** — a 5-tab bar, everything else behind "More":

| Tab | Holds |
|---|---|
| **Home** | Today: next meeting with its brief, what needs my vote, what needs my signature, overdue tasks |
| **Meetings** | List → detail (agenda, papers, attendees, quorum, live mode), calendar |
| **Actions** | Voting · Signature · Tasks · Approvals — everything with a deadline, in one queue |
| **Assistant** | The AI panel as a first-class destination, not a floating button |
| **More** | Boards, committees, library, minutes, decisions, reports, settings, profile |

Deep-link every entity: a notification about `BOD-2026-013` opens *that decision*, not a list.

---

## 6. The AI assistant — the part that needs the most design care

This is the product's differentiator and it is genuinely rich. It has **31 tools over the live API**
and can read *and act*. Design for all of it:

- **Streams token by token** (SSE). Never a blocking spinner for the answer.
- **Says what it is doing in the board's own language** while it works — *reviewing the record*,
  *drafting*, *checking the minutes* — with a matching icon. Never raw tool names like
  `list_meetings`. The Arabic is phrased as a governance professional would say it, not translated
  word for word. Design this progress chip carefully; it is on screen for most of every run.
- **Every record it names is an inline link.** A meeting, decision, minute, document or earlier
  conversation is tappable *where it is mentioned in the sentence*, the way a Notion mention is —
  with a preview on long-press and the record opening **beside** the conversation, never
  underneath it. The old footnote-style "Sources" list at the bottom has been removed precisely
  because the reader should not have to match `[7]` to a line of text.
- **Citations still exist underneath the surface** — answers are grounded in real records and the
  design must always make it possible to reach the evidence. On a phone, that is the inline
  mention plus a "sources" affordance in the message's overflow menu.
- **Per-answer affordances**: copy, insert, a helpful / not-helpful signal, and a **+** that files
  the answer into a governance record.
- **Contextual follow-ups** after each answer, about *the record just shown* — "summarise
  BOD-2026-013", "show its agenda" — not generic prompts.
- **The assistant can navigate**: "open the page for this meeting" actually opens it.
- **It can ask you a question mid-run** and wait for the answer, then continue.
- **Co-edited drafts**: it writes a decision or minute while you correct a field in the same
  document, live. Design the two-cursor state — who changed what, and what happens when both touch
  the same field.
- **Arabic OCR and per-document Q&A**: point it at a scanned board paper and ask.
- **Meeting recording → transcript → minutes.** Mic plus (on desktop) shared call audio. On mobile
  this needs: a always-visible recording indicator, elapsed time, the fact that **the recording
  lives only in the app until it uploads** (design an explicit "saving…" state and a failure state
  that does not lose the audio), and a paste-transcript fallback.
- **Reminders** the assistant sets for you, which interrupt politely.
- **Insights**: computed governance analytics — overdue decisions, attendance, voting patterns.
- **Voice input is a natural fit on mobile** and the speech pipeline already exists.

**Tone constraint:** the assistant must never read as a verdict-giver. It proposes, cites and
drafts. A human approves. That distinction should be visible in the design — drafts look like
drafts, suggestions look like suggestions.

---

## 7. Governance constraints that are design constraints

Get these wrong and the product is unusable in its market:

- **Confidentiality is the proposition.** A document marked confidential must look and behave
  differently. Never show a document's contents in a notification or a preview.
- **Secret ballots are secret.** The UI may show *whether* someone voted, never *what* they voted.
- **A brief is personal.** One member's pre-meeting brief must never show another member's tasks,
  obligations or ballot. Attendance readiness is shown as **counts only** — "3 of 5 confirmed" —
  never as a list of names.
- **Nothing is deleted, things change status.** A resigned director's row stays for the historical
  record. Design "no longer active" states, not disappearances.
- **Quorum is a legal threshold**, not a progress bar. Show it as a definite state — quorate or
  not — with what is missing.
- Arabic-first labels for governance concepts: محضر (minutes), نصاب (quorum), قرار (decision),
  بند أعمال (agenda item), مكافآت (remuneration), إنابة/بديل (proxy/substitute).

---

## 8. Mobile-specific asks

- **Offline reading** for board papers and agendas — members read on planes. Show clearly what is
  cached and what is stale.
- **Biometric unlock** (Face ID / Touch ID) — this is a confidential product on a personal device.
- **Push notifications** with deep links, and a clear per-category preference screen.
- **Large text support.** The audience is older; the app must survive a system text size two steps
  up without breaking layout.
- **iPad is a first-class target**, not a stretched phone — split view for papers beside the agenda
  is the natural reading posture for a board member.
- Design **light and dark, Arabic and English** for every key screen. That is four variants of the
  hero flows, and the Arabic dark variant is the one that finds the bugs.

---

## 9. What to deliver

1. The 5 tabs, each in Arabic **and** English, light **and** dark.
2. The pre-meeting brief — the single highest-value screen.
3. The meeting detail: agenda, papers, attendees, quorum, and the live-meeting state.
4. The assistant: idle, working (with the activity chip), streamed answer with inline mentions,
   the record opening beside the conversation, a mid-run question, and an error.
5. The actions queue: vote, sign, confirm attendance, nominate a substitute.
6. The recording flow, including the failure state.
7. A component sheet: buttons, inputs, cards, list rows, status chips, empty states, sheets,
   and the tab bar — with the RTL mirror of each.
