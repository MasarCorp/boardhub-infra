# -*- coding: utf-8 -*-
"""Builds the BoardHub meeting deck in English and Arabic from one source.

Both decks share structure, motion and SVG assets; only copy, type and direction differ.
Written for a 15-minute discussion with a live demo, not a brochure read-through.
"""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)                      # runbooks/ai-features/
# The supplied artwork is dark navy ink. Reversing it for the dark slides left halo artefacts
# around the letterforms, so the brand is set as type instead — it scales cleanly and sits in the
# same type system as the headings. logo-light.b64 is kept in case a light-on-dark asset arrives.
HERO = io.open(os.path.join(HERE, "challenge-hero.b64")).read().strip()
AGENT = io.open(os.path.join(HERE, "agent-hero.b64")).read().strip()

# ── the real module list, taken from the running BoardHub sidebar ────────────
MODULES = [
    # (key, en, ar, cluster) — mirrors the product's sidebar; keep in step with app.routes.ts
    ("boards",     "Boards & committees",  "المجالس واللجان",     "govern"),
    ("org",        "Org committees",       "لجان المنظمة",        "govern"),
    ("external",   "External committees",  "اللجان الخارجية",     "govern"),
    ("assess",     "Board assessments",    "تقييم المجالس",       "govern"),
    ("roles",      "Roles & permissions",  "الصلاحيات والإعدادات", "govern"),

    ("meetings",   "Meetings",             "الاجتماعات",          "meet"),
    ("calendar",   "Meeting calendar",     "تقويم الاجتماعات",    "meet"),
    ("agenda",     "Agenda items",         "بنود الأعمال",        "meet"),
    ("packs",      "Board packs",          "حزم المجلس",          "meet"),
    ("notes",      "AI meeting notes",     "محاضر بالذكاء",       "meet"),
    ("minutes",    "Minutes",              "المحاضر",             "meet"),

    ("voting",     "Voting",               "التصويت",             "decide"),
    ("decisions",  "Decisions",            "القرارات",            "decide"),
    ("followup",   "Decision follow-up",   "متابعة القرارات",     "decide"),
    ("tasks",      "Task management",      "إدارة المهام",        "decide"),
    ("control",    "Control panel",        "لوحة التحكم",         "decide"),
    ("reports",    "Reports & KPIs",       "التقارير والمؤشرات",  "decide"),

    ("library",    "Document library",     "مكتبة المستندات",     "record"),
    ("esign",      "e-Signature",          "التوقيع الإلكتروني",  "record"),
    ("deleg",      "Sign delegations",     "تفويض التوقيع",       "record"),
    ("trans",      "Transactions",         "المعاملات",           "record"),
    ("chat",       "Conversations",        "المحادثات",           "record"),
    ("notif",      "Notifications",        "الإشعارات",           "record"),
]
CLUSTERS = {
    "govern": ("Constitute",  "التكوين",   "Who governs, and how they are assessed."),
    "meet":   ("Convene",     "الانعقاد",  "Getting a valid meeting to happen."),
    "decide": ("Decide & do", "القرار والتنفيذ", "Turning discussion into tracked action."),
    "record": ("Evidence",    "الإثبات",   "The defensible record of what happened."),
}



# ── Vendor / platform glyphs ────────────────────────────────────────────────
# A single monoline set, drawn to one grid and one stroke weight. Official brand marks are
# deliberately not used: they cannot be fetched into the sandbox (external images are blocked),
# and redrawing trademarks by hand tends to look subtly wrong next to the real thing. To use the
# real assets instead, drop SVGs into deck/vendor/ and swap ICONS[key] for the file contents.
ICONS = {
 # layered strata — a foundation you build on
 "bedrock": '<path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 12l9 4 9-4"/><path d="M3 17l9 4 9-4"/>',
 # a nucleus with an orbit — the agent runtime
 "core": '<circle cx="12" cy="12" r="3.2"/><ellipse cx="12" cy="12" rx="9" ry="4.4"/>'
         '<ellipse cx="12" cy="12" rx="4.4" ry="9"/>',
 # concentric reasoning rings
 "watson": '<circle cx="12" cy="12" r="8.4"/><circle cx="12" cy="12" r="4.8"/><circle cx="12" cy="12" r="1.4"/>',
 # cloud with a spark
 "cloudai": '<path d="M6.5 18h11a3.5 3.5 0 0 0 .3-7 5.2 5.2 0 0 0-10-1.4A3.9 3.9 0 0 0 6.5 18z"/>'
            '<path d="M12 9.6l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>',
 # a router / switch — many models, one route
 "route": '<circle cx="5" cy="12" r="2.1"/><circle cx="19" cy="6.4" r="2.1"/>'
          '<circle cx="19" cy="17.6" r="2.1"/><path d="M7 11.2l10-4.2M7 12.8l10 4.2"/>',
 # offline — a machine with no signal
 "offline": '<rect x="3" y="5" width="18" height="12" rx="2"/><path d="M2 20h20"/><path d="M9 9l6 6M15 9l-6 6"/>',
 # stacked containers
 "docker": '<rect x="3" y="12" width="4" height="4"/><rect x="8" y="12" width="4" height="4"/>'
           '<rect x="13" y="12" width="4" height="4"/><rect x="8" y="7" width="4" height="4"/>'
           '<path d="M2 16.5c3.5 3 12 3.4 16.5-1.5 2.2.6 3.5-.6 3.5-.6"/>',
 # the seven-spoke helm — Kubernetes is geometric enough to draw honestly
 "k8s": '<path d="M12 2.6l8.1 3.9 2 8.8-5.6 7H7.5l-5.6-7 2-8.8z"/><circle cx="12" cy="12" r="3.1"/>'
        '<path d="M12 4.6v4.3M12 15.1v4.3M5.2 8.3l3.9 2M14.9 13.7l3.9 2M5.2 15.7l3.9-2M14.9 10.3l3.9-2"/>',
 # any cloud, in and out
 "anycloud": '<path d="M6.5 17h11a3.5 3.5 0 0 0 .3-7 5.2 5.2 0 0 0-10-1.4A3.9 3.9 0 0 0 6.5 17z"/>'
             '<path d="M12 21v-5M9.6 18.4L12 16l2.4 2.4"/>',
 # shared tenancy
 "saas": '<path d="M4 20V9l8-5 8 5v11"/><path d="M4 20h16"/><path d="M9.5 20v-5h5v5"/>',
 # official correspondence moving in and out
 "corr": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 8l9.5 6 9.5-6"/>'
         '<path d="M7 19l2-2M17 19l-2-2"/>',
 # a standing council with an intelligence spark
 "council": '<circle cx="8" cy="9" r="2.4"/><circle cx="16" cy="9" r="2.4"/>'
            '<path d="M3.5 19a4.5 4.5 0 0 1 9 0M11.5 19a4.5 4.5 0 0 1 9 0"/>'
            '<path d="M12 2l.7 1.8L14.5 4.5l-1.8.7L12 7l-.7-1.8L9.5 4.5l1.8-.7z"/>',
 # a meeting on screen
 "video": '<rect x="2.5" y="6" width="13" height="12" rx="2"/><path d="M15.5 10.5l6-3.5v10l-6-3.5z"/>',
 # a workflow ticket moving through states
 "flow": '<rect x="2.5" y="4" width="8" height="6" rx="1.6"/><rect x="13.5" y="14" width="8" height="6" rx="1.6"/>'
         '<path d="M6.5 10v4.5a2.5 2.5 0 0 0 2.5 2.5h4.5"/>',
 # a storefront listing
 "market": '<path d="M3 9l1.4-4.2A1.5 1.5 0 0 1 5.8 4h12.4a1.5 1.5 0 0 1 1.4 1.1L21 9"/>'
           '<path d="M3 9h18v2a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0z"/><path d="M5 14v6h14v-6"/>',
}


def icon(key: str) -> str:
    return (f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{ICONS.get(key, "")}</svg>')


# ════════════════════════════════════════════════════════════════════════════
# SVG assets
# ════════════════════════════════════════════════════════════════════════════

def hero_challenge(t):
    """The challenge slide. A photographic hero reads truer to a Saudi government room than
    an abstract figure would; the counters are part of the artwork, so the motion here is a
    slow float plus a ring of live counters layered over it rather than redrawn chips."""
    return f'''<div class="hero">
      <img class="hero-img" src="{HERO}" alt="{t['overwhelm_alt']}">
    </div>'''


def svg_system_map(t):
    """Every module, grouped by the business function it serves, with the
    dependencies between groups drawn — the 'capabilities are not defined' fix."""
    cols = [("govern",90),("meet",325),("decide",560),("record",795)]
    out = []
    tallest = max(len([m for m in MODULES if m[3] == k]) for k, _ in cols)
    for key, x in cols:
        rows = tallest
        en, ar, _ = CLUSTERS[key]
        label = ar if t["rtl"] else en
        out.append(f'''
    <g class="cl">
      <rect x="{x}" y="66" width="190" height="{28 + rows*46}" rx="14"/>
      <text x="{x+95}" y="96" text-anchor="middle" class="cl-t">{label}</text>''')
        mods = [m for m in MODULES if m[3] == key]
        for i, (_, men, mar, _) in enumerate(mods):
            y = 112 + i*46
            name = mar if t["rtl"] else men
            out.append(f'''
      <g class="mod">
        <rect x="{x+14}" y="{y}" width="162" height="36" rx="8"/>
        <text x="{x+95}" y="{y+23}" text-anchor="middle" class="mod-t">{name}</text>
      </g>''')
        out.append("    </g>")
    # dependency arrows between clusters
    arrows = ""
    for x1, x2 in [(280,325),(515,560),(750,795)]:
        arrows += f'''
    <path class="dep" marker-end="url(#dep)" d="M{x1} 210 H{x2-4}"/>'''
    # feedback loop: evidence informs constitution
    arrows += '''
    <path class="dep dashed" marker-end="url(#dep)" d="M890 356 V394 H185 V356"/>'''
    return f'''<svg viewBox="0 0 1000 428" role="img" aria-label="{t['map_alt']}">
  <defs><marker id="dep" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto">
    <path d="M0 .5 L8 4.5 L0 8.5 z" fill="#0D9488"/></marker></defs>
  {''.join(out)}
  {arrows}
  <text x="537" y="414" text-anchor="middle" class="loop-t">{t['map_loop']}</text>
</svg>'''


def agent_hero(t):
    """The assistant slide.

    The artwork already draws the connectors between the capability chips and the agent, so the
    motion is layered on top rather than redrawn: a transparent SVG in the image's own coordinate
    space (1168x904) sends pulses along those same lines. Signals travel inward from the chips and
    back out again, which is the actual round trip — the agent is asked, then answers.
    """
    hub = (790, 330)
    chips = [   # (x, y, direction) anchors taken from the artwork's own connector endpoints
        (348, 100, "in"), (660, 100, "in"), (855, 100, "out"),
        (240, 252, "in"), (215, 448, "out"),
        (955, 250, "out"), (960, 448, "in"),
    ]
    paths, dots = "", ""
    for i, (cx, cy, direction) in enumerate(chips):
        mx, my = (cx + hub[0]) / 2, (cy + hub[1]) / 2 - 26
        d = (f"M{cx} {cy} Q{mx:.0f} {my:.0f} {hub[0]} {hub[1]}" if direction == "in"
             else f"M{hub[0]} {hub[1]} Q{mx:.0f} {my:.0f} {cx} {cy}")
        paths += f'\n      <path id="ln{i}" d="{d}" fill="none" stroke="none"/>'
        dots += (f'\n      <circle r="5" class="sig">'
                 f'<animateMotion dur="{2.9 + i * 0.21:.2f}s" begin="{i * 0.42:.2f}s" '
                 f'repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" calcMode="linear">'
                 f'<mpath href="#ln{i}"/></animateMotion></circle>')
    return f'''<div class="hero agent-hero">
      <img class="hero-img" src="{AGENT}" alt="{t['octo_alt']}">
      <svg class="hero-fx" viewBox="0 0 1168 904" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
        <defs><radialGradient id="sigg"><stop offset="0%" stop-color="#5EEAD4" stop-opacity=".95"/>
          <stop offset="100%" stop-color="#2DD4BF" stop-opacity="0"/></radialGradient></defs>{paths}
        <circle cx="{hub[0]}" cy="{hub[1]}" r="52" fill="url(#sigg)" opacity=".28">
          <animate attributeName="r" values="46;62;46" dur="4.2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values=".16;.34;.16" dur="4.2s" repeatCount="indefinite"/>
        </circle>{dots}
      </svg>
    </div>'''


def ui_mock(t, screen):
    """A stylised BoardHub screen. Uses the product's real navigation labels so the
    room recognises the system they are about to see demonstrated."""
    nav = [(m[2] if t["rtl"] else m[1], m[0]) for m in MODULES[:9]]
    items = "".join(
        f'<li class="{"on" if k==screen["active"] else ""}">{n}</li>' for n, k in nav)
    rows = "".join(
        f'''<div class="mk-row"><span class="mk-c1">{r[0]}</span>
        <span class="mk-c2">{r[1]}</span>
        <span class="mk-pill {r[3]}">{r[2]}</span></div>''' for r in screen["rows"])
    kpis = "".join(
        f'<div class="mk-kpi"><b>{k[0]}</b><span>{k[1]}</span></div>' for k in screen["kpis"])
    return f'''<div class="mock" aria-hidden="true">
  <div class="mk-side"><div class="mk-brand">{t['mock_brand']}</div><ul>{items}</ul></div>
  <div class="mk-main">
    <div class="mk-top"><span class="mk-title">{screen['title']}</span><span class="mk-dot"></span></div>
    <div class="mk-kpis">{kpis}</div>
    <div class="mk-table">{rows}</div>
  </div>
</div>'''


# ════════════════════════════════════════════════════════════════════════════
# Copy
# ════════════════════════════════════════════════════════════════════════════
EN = dict(
  rtl=False, lang="en", dir="ltr",
  title="BoardHub for Hadaf",
  fonts="family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Arabic:wght@400;600&family=IBM+Plex+Mono:wght@400;500",
  f_display='"Bricolage Grotesque","IBM Plex Sans",system-ui,sans-serif',
  f_body='"IBM Plex Sans",system-ui,-apple-system,sans-serif',
  wordmark="Masar<em>Corp</em>",
  client="Human Resources Development Fund", client_sub="هدف",
  prepared="Prepared for", by="MasarCorp", foot="MASARCORP",
  nav=["Opening","The problem","What it costs","The platform","Convene","Decide","Evidence",
       "The assistant","AI value","Models & cloud","Live demo","Why us","Roadmap","Close"],

  s1_eyebrow="Board & committee governance · 15 minutes",
  s1_h="Governance that<br>thinks with you.",
  s1_l="A working session, not a brochure. We will walk the platform, then open it live and answer from your own record.",
  s1_meta=["Arabic & English · RTL native","Deployable in your environment","Live demo at the end"],

  s2_eyebrow="The problem",
  s2_h="The decision takes an hour.<br>Chasing it takes a month.",
  s2_l="The board secretariat is not short of systems. It is short of one thread connecting what was discussed, what was decided, and what actually happened.",
  overwhelm_items=["Email","WhatsApp","Call","Attachment v7","Reminder","Where is it?","Signature","Follow-up"],
  overwhelm_alt="A board secretary surrounded by competing interruptions: email, calls, messages, attachment versions and reminders",

  s3_eyebrow="What it costs",
  s3_h="Three costs a board actually feels",
  s3_cards=[("Decisions that quietly expire","An overdue decision stops being anybody's job. By the next meeting the context is gone and it is re-discussed from scratch."),
            ("A record you cannot defend","When the regulator or the auditor asks how a decision was reached, the answer lives across inboxes and drives."),
            ("Arabic as a translation layer","Papers drafted in Arabic, reported in English. Two versions of the truth, and neither is authoritative.")],

  s4_eyebrow="The platform",
  s4_h="Sixteen modules, four business functions",
  s4_l="Not a feature list. Each group answers a different governance question, and each feeds the next — which is why nothing is re-keyed between them.",
  map_alt="The platform's modules grouped into four business functions — constitute, convene, decide and do, evidence — with dependencies flowing left to right and evidence feeding back into constitution",
  map_loop="Evidence feeds the next cycle: assessments, quorum history and follow-up rates",

  s5_eyebrow="Convene",
  s5_h="Getting a valid meeting to happen",
  s5_l="Quorum, agenda, papers and attendance are one object, not four spreadsheets. The pack assembles itself from the agenda.",
  s5_points=["Physical, virtual or hybrid, with quorum enforced before the meeting opens",
             "Agenda items carry type, duration, owner and papers — and unresolved ones roll forward automatically",
             "Board packs build from the agenda, so the papers can never drift from what is being discussed"],

  s6_eyebrow="Decide and do",
  s6_h="Where discussion becomes accountability",
  s6_l="A decision is not a paragraph in a minute. It is a numbered, owned, dated object that escalates itself when it slips.",
  s6_points=["Digital voting with quorum rules and a complete audit trail",
             "Decisions are numbered, categorised and tracked to completion",
             "Overdue decisions escalate on a schedule and can be carried onto the next agenda"],

  s7_eyebrow="Evidence",
  s7_h="The record that has to hold up",
  s7_l="Every artefact is stored, versioned, signed where required, and reachable from the decision it belongs to.",
  s7_points=["Document library with categories, versions and retention",
             "e-Signature requests bound to the documents that need them",
             "Every AI answer cites the exact minute, decision or task it came from"],

  s8_eyebrow="The assistant",
  s8_h="One assistant, many reaches",
  s8_l="Not eight disconnected AI features. One agent that plans, then calls the same governed APIs your staff use — with their permissions, every time.",
  octo_caps=["Reads live records","Knowledge base","Documents & OCR","Drafts minutes",
             "Creates decisions & tasks","Generates documents","Insights & risk","Remembers context"],
  octo_alt="The AI assistant drawn as a single body with eight reaching arms, each connecting to a capability: live records, knowledge base, documents and OCR, drafting minutes, creating decisions and tasks, generating documents, insights, and memory",

  s9_eyebrow="AI, in business terms",
  s9_h="What the intelligence is worth",
  s9_rows=[("Tool use","Answers from the live system, not last night's export — it queries the record as you ask."),
           ("Knowledge base","Upload a policy, circular or resolution. It is indexed and becomes answerable, with the source cited."),
           ("Arabic OCR","Scanned and stamped pages are read, not skipped. Photographed minutes become searchable text."),
           ("Retrieval & citations","Every claim carries a numbered link to the record it came from."),
           ("Chat with a document","Ask about one specific uploaded file and get answers from that file alone."),
           ("Memory","Holds the thread across a session — establish a committee or a month once, then keep asking."),
           ("Reasoning","Multi-step questions resolve in one ask: several lookups plus a judgement."),
           ("Page awareness","\"This meeting\" means the one on screen. No ids, no re-explaining."),
           ("Document generation","Drafts the memo in Arabic, you approve, and it files it against the meeting as real Word."),
           ("AI meeting notes","Record an Arabic meeting; get a transcript and a structured minutes draft to review."),
           ("Insights & risk","Computed KPIs and by-month charts rendered inline, never hand-counted."),
           ("Summarise & translate","Any attachment condensed, or moved between Arabic and English."),
           ("Suggested next steps","Page-aware starter prompts, so staff discover what it can actually do."),
           ("Visible working","You see which tools ran, and can stop a long answer without losing it."),
           ("Guardrails","It will not invent a number, and writes nothing without explicit confirmation."),
           ("Tenant isolation","Every call carries the signed-in user's permissions and their organisation's scope.")],
  s10_eyebrow="Over to the system",
  s10_h="Live demo",
  s10_l="We will open the platform on real data and take your questions against it — including anything raised in this room.",
  s10_items=["Ask it something in Arabic and watch which tools it calls",
             "Upload a scanned document and question it",
             "Draft a memo, approve it, and see it filed against a meeting"],

  s11_eyebrow="Positioning",
  s11_h="Most board AI writes documents.<br>Ours reads your record.",
  s11_l="Compared against the established global portal, using only what each vendor publishes.",
  s11_them_h="Typical global portal",
  s11_them=["AI generates artefacts — agenda, board book, minutes, insights",
            "The AI suite is commonly a paid add-on above the base tier",
            "Localisation is not stated on the platform overview",
            "Certified to SOC 2 / ISO 27001 / GDPR, with no published data-residency commitment"],
  s11_us_h="BoardHub",
  s11_us=["The agent queries and acts on live records, and creates meetings, decisions and tasks on your confirmation",
          "AI is part of the platform, not a separately priced tier",
          "Arabic-first and genuinely bilingual: real RTL, Arabic answers, Arabic documents",
          "Deployable in your environment, so data residency is your decision",
          "Built to Saudi governance practice and DGA expectations"],

  s12_eyebrow="What comes next",
  s12_h="On the roadmap",
  s12_l="Committed direction, not yet shipped — kept visually separate so nothing here is mistaken for what is live today.",
  s12_badge="Planned",
  s12_cards=[("corr","Correspondence systems","Link official incoming and outgoing correspondence to the decision or meeting it belongs to, closing the loop between a transaction and its resolution."),
             ("council","AI Work Council","A standing advisory layer over the record, surfacing risk, drift and follow-up before the meeting rather than after."),
             ("video","Microsoft Teams & Webex","Schedule and join from the meeting record, and bring the recording back for minutes."),
             ("flow","ServiceNow","Two-way sync so a board task and its operational ticket remain a single truth."),
             ("market","AWS Marketplace","Listing BoardHub for procurement through your existing AWS agreement and committed spend.")],

  s14_eyebrow="Models and deployment",
  s14_h="Your models. Your cloud.<br>Your data boundary.",
  s14_l="The platform is model-agnostic by design: every provider routes through one abstraction, so the model is an administrative choice rather than an architectural commitment.",
  s14_models_h="Foundation models",
  s14_models=[("bedrock","AWS Bedrock","Primary. Chat, streaming, tool-calling and embeddings, inside your AWS account."),
              ("core","AWS Bedrock AgentCore","The agent is built on AWS's open-source Strands framework, the same runtime AgentCore hosts."),
              ("watson","IBM watsonx","Supported for chat and embeddings; tool-calling varies by model and is validated per model."),
              ("cloudai","Alibaba Cloud (Qwen)","Already in production here — Arabic retrieval runs on Qwen3 embeddings today."),
              ("route","Anthropic, Groq, OpenRouter","Direct or routed access when a specific model is preferred."),
              ("offline","Ollama — fully offline","Open-weight models on your own hardware, with no outbound call at all.")],
  s14_deploy_h="Where it runs",
  s14_deploy=[("docker","Docker","Every service ships as a container."),
              ("k8s","Kubernetes","Cloud-agnostic manifests, already written and in the repository."),
              ("anycloud","Any cloud, self-hosted","AWS, Google Cloud, Oracle, or your own datacentre."),
              ("saas","SaaS","Multi-tenant from the database up, if you would rather we ran it.")],

  s13_h="Thank you.",
  s13_l="We would be glad to run this on your own governance record and answer with your data, not our slides.",

  mock_brand="BoardHub",
  mock=dict(
    meet=dict(active="meetings", title="Meetings",
      kpis=[("8","Total"),("3","September"),("1","Draft")],
      rows=[("BOD-2026-013","10 Sep 2026","Scheduled","ok"),
            ("AUD-2026-004","2 Sep 2026","Scheduled","ok"),
            ("BOD-2026-007","5 Sep 2026","Draft","warn")]),
    decide=dict(active="voting", title="Decisions",
      kpis=[("6","Decisions"),("1","Overdue"),("5","Open tasks")],
      rows=[("D-2026-005","Remuneration policy","Overdue","bad"),
            ("D-2026-003","Internal control","In progress","warn"),
            ("D-2026-001","H2 budget","Completed","ok")]),
    record=dict(active="library", title="Document library",
      kpis=[("4","Documents"),("2","Signatures"),("3","Minutes")],
      rows=[("Travel policy memo","Generated · linked to BOD-2026-013","Word","ok"),
            ("Audit committee minutes","Scanned · read by OCR","Indexed","ok"),
            ("Annual report 2025","Board · signed","Signed","ok")]),
  ),
)


AR = dict(
  rtl=True, lang="ar", dir="rtl",
  title="بوردهَب — عرض لصندوق تنمية الموارد البشرية",
  fonts="family=Cairo:wght@400;500;600;700;900&family=IBM+Plex+Mono:wght@400;500",
  f_display='"Cairo","Noto Kufi Arabic",system-ui,sans-serif',
  f_body='"Cairo","Noto Kufi Arabic",system-ui,sans-serif',
  wordmark="مسار<em>كورب</em>",
  client="صندوق تنمية الموارد البشرية", client_sub="هدف",
  prepared="أُعدّ لـ", by="مسار كورب", foot="مسار كورب",
  nav=["الافتتاح","التحدي","الكلفة","المنصة","الانعقاد","القرار","الإثبات","المساعد",
       "قيمة الذكاء","النماذج والسحابة","العرض الحي","لماذا نحن","خارطة الطريق","الختام"],

  s1_eyebrow="حوكمة المجالس واللجان · ١٥ دقيقة",
  s1_h="حوكمة<br>تفكّر معك.",
  s1_l="جلسة عمل لا عرضاً تسويقياً. سنستعرض المنصة، ثم نفتحها أمامكم مباشرةً ونجيب من سجلكم أنتم.",
  s1_meta=["عربي وإنجليزي · دعم أصيل لليمين‑لليسار","قابلة للتشغيل داخل بيئتكم","عرض حيّ في الختام"],

  s2_eyebrow="التحدي",
  s2_h="القرار يستغرق ساعة.<br>وتتبّعه يستغرق شهراً.",
  s2_l="أمانة المجلس لا تنقصها الأنظمة، بل ينقصها خيط واحد يربط ما نوقش بما تقرر بما نُفّذ فعلاً.",
  overwhelm_items=["بريد","واتساب","اتصال","مرفق نسخة ٧","تذكير","وين الملف؟","توقيع","متابعة"],
  overwhelm_alt="أمين سر مجلس تحاصره المقاطعات: بريد واتصالات ورسائل ونسخ مرفقات وتذكيرات",

  s3_eyebrow="الكلفة",
  s3_h="ثلاث كلف يشعر بها المجلس فعلاً",
  s3_cards=[("قرارات تنتهي بهدوء","القرار المتأخر يتوقف عن كونه مسؤولية أحد، وبحلول الاجتماع التالي يكون السياق قد ضاع فيُعاد نقاشه من الصفر."),
            ("سجل لا يمكن الدفاع عنه","حين يسأل المدقق أو الجهة الرقابية كيف اتُّخذ القرار، تكون الإجابة موزعة بين البريد والأقراص المشتركة."),
            ("العربية كطبقة ترجمة","أوراق تُحرَّر بالعربية وتُرفع تقاريرها بالإنجليزية. نسختان للحقيقة، وليست إحداهما معتمدة.")],

  s4_eyebrow="المنصة",
  s4_h="ستة عشر وحدة، أربع وظائف عمل",
  s4_l="ليست قائمة مزايا. كل مجموعة تجيب عن سؤال حوكمي مختلف، وتغذّي التي تليها — ولهذا لا يُعاد إدخال أي بيانات بينها.",
  map_alt="وحدات المنصة مجمّعة في أربع وظائف عمل: التكوين والانعقاد والقرار والتنفيذ والإثبات، مع تدفق الاعتماديات بينها وعودة الإثبات ليغذي التكوين",
  map_loop="الإثبات يغذّي الدورة التالية: التقييمات وسجل النصاب ومعدلات المتابعة",

  s5_eyebrow="الانعقاد",
  s5_h="أن ينعقد الاجتماع صحيحاً",
  s5_l="النصاب وجدول الأعمال والأوراق والحضور كيان واحد، لا أربعة جداول منفصلة. وحزمة المجلس تتكوّن من جدول الأعمال نفسه.",
  s5_points=["حضورياً أو افتراضياً أو مدمجاً، مع التحقق من النصاب قبل افتتاح الجلسة",
             "بنود الأعمال تحمل نوعها ومدتها ومسؤولها وأوراقها، وغير المنجز منها يُرحَّل تلقائياً",
             "حزم المجلس تُبنى من جدول الأعمال، فلا تفترق الأوراق عمّا يُناقَش"],

  s6_eyebrow="القرار والتنفيذ",
  s6_h="حيث يتحول النقاش إلى مساءلة",
  s6_l="القرار ليس فقرة في محضر، بل كيان مرقّم له مالك وتاريخ، ويُصعِّد نفسه إذا تأخر.",
  s6_points=["تصويت رقمي بقواعد نصاب وسجل تدقيق كامل",
             "القرارات مرقّمة ومصنّفة ومتابَعة حتى الإنجاز",
             "القرارات المتأخرة تُصعَّد وفق جدول، ويمكن ترحيلها إلى جدول الأعمال التالي"],

  s7_eyebrow="الإثبات",
  s7_h="السجل الذي يجب أن يصمد",
  s7_l="كل مخرج محفوظ ومُصدَّر ومُوقَّع عند اللزوم، ويمكن الوصول إليه من القرار الذي يخصّه.",
  s7_points=["مكتبة مستندات بتصنيفات وإصدارات ومدد احتفاظ",
             "طلبات توقيع إلكتروني مرتبطة بالمستندات التي تتطلبها",
             "كل إجابة من المساعد تستشهد بالمحضر أو القرار أو المهمة التي جاءت منها"],

  s8_eyebrow="المساعد",
  s8_h="مساعد واحد بأذرع متعددة",
  s8_l="ليست ثماني مزايا منفصلة، بل مساعد واحد يخطط ثم يستدعي الواجهات المحوكمة نفسها التي يستخدمها موظفوكم — وبصلاحياتهم في كل مرة.",
  octo_caps=["يقرأ السجل الحيّ","قاعدة المعرفة","المستندات والمسح","يصوغ المحاضر",
             "ينشئ القرارات والمهام","يولّد المستندات","المؤشرات والمخاطر","يتذكّر السياق"],
  octo_alt="المساعد الذكي مرسوماً بجسد واحد وثماني أذرع، كل ذراع تصل إلى قدرة: السجل الحيّ، وقاعدة المعرفة، والمستندات والمسح الضوئي، وصياغة المحاضر، وإنشاء القرارات والمهام، وتوليد المستندات، والمؤشرات، والذاكرة",

  s9_eyebrow="الذكاء الاصطناعي بلغة العمل",
  s9_h="ما قيمة الذكاء فعلياً",
  s9_rows=[("استخدام الأدوات","يجيب من النظام الحيّ لا من تصدير الأمس — يستعلم من السجل لحظة سؤالك."),
           ("قاعدة المعرفة","ارفع سياسة أو تعميماً أو قراراً، فيُفهرَس ويصبح قابلاً للسؤال مع ذكر مصدره."),
           ("المسح الضوئي بالعربية","الصفحات الممسوحة والمختومة تُقرأ ولا تُتجاهَل، فتصبح المحاضر المصوَّرة نصاً قابلاً للبحث."),
           ("الاسترجاع والمصادر","كل معلومة تحمل رابطاً مرقّماً إلى السجل الذي جاءت منه."),
           ("محادثة مستند بعينه","اسأل عن ملف واحد رفعته، فتأتي الإجابة من ذلك الملف وحده."),
           ("الذاكرة","يحتفظ بخيط الجلسة — حدّد اللجنة أو الشهر مرة واحدة ثم تابع أسئلتك."),
           ("الاستدلال","الأسئلة المركّبة تُحسم في طلب واحد: عدة استعلامات وحكم مهني."),
           ("إدراك الصفحة","«هذا الاجتماع» يعني المعروض أمامك، دون معرّفات ودون إعادة شرح."),
           ("توليد المستندات","يصوغ المذكرة بالعربية، وتعتمدها أنت، فتُحفظ على الاجتماع كملف <span class='ltr'>Word</span> حقيقي."),
           ("محاضر بالذكاء الاصطناعي","سجّل اجتماعاً بالعربية، واحصل على تفريغ ومسودة محضر منظّمة للمراجعة."),
           ("المؤشرات والمخاطر","مؤشرات محسوبة ورسوم شهرية تظهر داخل المحادثة، دون عدّ يدوي."),
           ("التلخيص والترجمة","اختصار أي مرفق أو نقله بين العربية والإنجليزية."),
           ("اقتراح الخطوة التالية","مقترحات بادئة حسب الصفحة، فيكتشف الموظفون ما يستطيع فعله حقاً."),
           ("عمل مرئي","ترى أي أدوات استُدعيت، ويمكنك إيقاف إجابة طويلة دون فقدان ما ظهر."),
           ("الضوابط","لا يختلق رقماً، ولا يكتب شيئاً دون تأكيد صريح."),
           ("عزل الجهات","كل طلب يحمل صلاحيات المستخدم المسجَّل ونطاق جهته.")],
  s10_eyebrow="ننتقل إلى النظام",
  s10_h="العرض الحيّ",
  s10_l="سنفتح المنصة على بيانات حقيقية ونستقبل أسئلتكم عليها مباشرة — بما في ذلك ما يُطرح في هذه القاعة.",
  s10_items=["اسأله بالعربية وشاهد أي أدوات يستدعي",
             "ارفع مستنداً ممسوحاً ضوئياً واسأله عنه",
             "اطلب صياغة مذكرة، اعتمدها، وشاهدها تُحفظ على الاجتماع"],

  s11_eyebrow="التموضع",
  s11_h="أغلب أنظمة الذكاء تكتب مستندات.<br>نظامنا يقرأ سجلّك.",
  s11_l="مقارنة مع المنصة العالمية الرائدة، مبنية على ما ينشره كل مزوّد عن نفسه فقط.",
  s11_them_h="المنصة العالمية النموذجية",
  s11_them=["الذكاء الاصطناعي يولّد مخرجات: جدول أعمال وكتيّب مجلس ومحاضر ومؤشرات",
            "حزمة الذكاء الاصطناعي غالباً إضافة مدفوعة فوق الباقة الأساسية",
            "لا يرد ذكر التعريب في صفحة استعراض المنصة",
            "حاصلة على SOC 2 و ISO 27001 و GDPR، دون التزام معلن بموقع استضافة البيانات"],
  s11_us_h="بوردهَب",
  s11_us=["المساعد يستعلم من السجل الحيّ ويتصرف فيه، وينشئ اجتماعات وقرارات ومهام بعد تأكيدك",
          "الذكاء الاصطناعي جزء من المنصة لا باقة تُسعَّر على حدة",
          "العربية أولاً وثنائية حقيقية: دعم أصيل لليمين‑لليسار، وإجابات ومستندات بالعربية",
          "قابلة للتشغيل داخل بيئتكم، فموقع البيانات قراركم",
          "مبنية وفق ممارسات الحوكمة السعودية ومتطلبات هيئة الحكومة الرقمية"],

  s12_eyebrow="ما هو قادم",
  s12_h="خارطة الطريق",
  s12_l="توجّه معتمد لم يُطلَق بعد — نعرضه منفصلاً بصرياً حتى لا يلتبس شيء منه بما هو متاح اليوم.",
  s12_badge="مخطط له",
  s12_cards=[("corr","أنظمة المعاملات والمراسلات","ربط الوارد والصادر الرسمي بالقرار أو الاجتماع الذي يخصّه، فتُغلق الدائرة بين المعاملة وقرارها."),
             ("council","مجلس العمل الذكي","طبقة استشارية دائمة فوق السجل، تُظهر المخاطر والانحراف والمتابعات قبل الاجتماع لا بعده."),
             ("video","التكامل مع <span class='ltr'>Microsoft Teams</span> و<span class='ltr'>Webex</span>","الجدولة والانضمام من سجل الاجتماع، وإعادة التسجيل لصياغة المحضر."),
             ("flow","التكامل مع <span class='ltr'>ServiceNow</span>","مزامنة ثنائية الاتجاه تجعل مهمة المجلس وتذكرتها التشغيلية مصدراً واحداً للحقيقة."),
             ("market","متجر <span class='ltr'>AWS Marketplace</span>","إدراج بوردهَب للشراء عبر اتفاقيتكم القائمة مع <span class='ltr'>AWS</span> والإنفاق الملتزم به.")],

  s14_eyebrow="النماذج والاستضافة",
  s14_h="نماذجكم. سحابتكم.<br>وحدود بياناتكم.",
  s14_l="المنصة محايدة تجاه النماذج بالتصميم: كل مزوّد يمرّ عبر طبقة تجريد واحدة، فيصبح اختيار النموذج قراراً إدارياً لا التزاماً معمارياً.",
  s14_models_h="النماذج الأساسية",
  s14_models=[("bedrock","<span class='ltr'>AWS Bedrock</span>","الأساس. محادثة وبث واستدعاء أدوات وتضمينات، داخل حسابكم على <span class='ltr'>AWS</span>."),
              ("core","<span class='ltr'>AWS Bedrock AgentCore</span>","المساعد مبني على إطار <span class='ltr'>Strands</span> مفتوح المصدر من <span class='ltr'>AWS</span>، وهو نفسه ما تستضيفه <span class='ltr'>AgentCore</span>."),
              ("watson","<span class='ltr'>IBM watsonx</span>","مدعوم للمحادثة والتضمينات؛ واستدعاء الأدوات يختلف حسب النموذج ويُتحقق منه لكل نموذج."),
              ("cloudai","سحابة علي بابا (<span class='ltr'>Qwen</span>)","يعمل لدينا فعلاً — الاسترجاع العربي يقوم اليوم على تضمينات <span class='ltr'>Qwen3</span>."),
              ("route","<span class='ltr'>Anthropic</span> و<span class='ltr'>Groq</span> و<span class='ltr'>OpenRouter</span>","وصول مباشر أو موجَّه حين يُفضَّل نموذج بعينه."),
              ("offline","<span class='ltr'>Ollama</span> — دون اتصال","نماذج مفتوحة الأوزان على أجهزتكم، دون أي اتصال خارجي إطلاقاً.")],
  s14_deploy_h="أين تعمل",
  s14_deploy=[("docker","<span class='ltr'>Docker</span>","كل خدمة تُشحن كحاوية."),
              ("k8s","<span class='ltr'>Kubernetes</span>","ملفات نشر محايدة تجاه السحابة، مكتوبة وجاهزة في المستودع."),
              ("anycloud","أي سحابة، استضافة ذاتية","<span class='ltr'>AWS</span> أو <span class='ltr'>Google Cloud</span> أو <span class='ltr'>Oracle</span> أو مركز بياناتكم."),
              ("saas","<span class='ltr'>SaaS</span>","متعددة الجهات من قاعدة البيانات صعوداً، إن فضّلتم أن نشغّلها نحن.")],

  s13_h="شكراً لكم.",
  s13_l="يسعدنا تشغيل المنصة على سجل الحوكمة الخاص بكم، والإجابة ببياناتكم لا بشرائحنا.",

  mock_brand="بوردهَب",
  mock=dict(
    meet=dict(active="meetings", title="الاجتماعات",
      kpis=[("٨","الإجمالي"),("٣","سبتمبر"),("١","مسودة")],
      rows=[("BOD-2026-013","١٠ سبتمبر ٢٠٢٦","مجدول","ok"),
            ("AUD-2026-004","٢ سبتمبر ٢٠٢٦","مجدول","ok"),
            ("BOD-2026-007","٥ سبتمبر ٢٠٢٦","مسودة","warn")]),
    decide=dict(active="voting", title="القرارات",
      kpis=[("٦","قرارات"),("١","متأخر"),("٥","مهام مفتوحة")],
      rows=[("D-2026-005","سياسة المكافآت","متأخر","bad"),
            ("D-2026-003","الرقابة الداخلية","قيد التنفيذ","warn"),
            ("D-2026-001","ميزانية النصف الثاني","مكتمل","ok")]),
    record=dict(active="library", title="مكتبة المستندات",
      kpis=[("٤","مستندات"),("٢","توقيعات"),("٣","محاضر")],
      rows=[("مذكرة سياسة السفر","مُولَّدة · مرتبطة بـ BOD-2026-013","<span class='ltr'>Word</span>","ok"),
            ("محضر لجنة المراجعة","ممسوح · قُرئ ضوئياً","مفهرس","ok"),
            ("التقرير السنوي ٢٠٢٥","المجلس · موقّع","موقّع","ok")]),
  ),
)


CSS = """
:root{
  --navy:#0B2545;--navy-deep:#05070D;--teal:#0D9488;--teal-bright:#2DD4BF;--coral:#E8836F;
  --ground:#F7FAFC;--paper:#FFFFFF;--paper-2:#EEF3F7;
  --ink:#0B2545;--ink-2:#33465F;--muted:#64798F;--line:#D9E3EC;
  --f-display:%(f_display)s;--f-body:%(f_body)s;
  --f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#070B14;--paper:#0E1626;--paper-2:#141F33;
  --ink:#EAF1F8;--ink-2:#C0CEDC;--muted:#8497AC;--line:#243349;}}
:root[data-theme="dark"]{--ground:#070B14;--paper:#0E1626;--paper-2:#141F33;
  --ink:#EAF1F8;--ink-2:#C0CEDC;--muted:#8497AC;--line:#243349;}
*{box-sizing:border-box}
html{scroll-behavior:smooth;direction:%(dir)s}
body{margin:0;background:var(--ground);color:var(--ink-2);font-family:var(--f-body);
  font-size:16px;line-height:%(lh)s;-webkit-font-smoothing:antialiased;
  scroll-snap-type:y mandatory;overflow-y:scroll;height:100vh}
.slide{min-height:100vh;scroll-snap-align:start;display:flex;flex-direction:column;
  justify-content:center;padding:74px 40px 64px;position:relative;overflow:hidden}
.inner{width:100%%;max-width:1180px;margin:0 auto;position:relative;z-index:1}
.slide.dark{background:var(--navy-deep);color:#C6D6E4}
.slide.navy{background:var(--navy);color:#CBDCEA}
.glow{position:absolute;inset:0;pointer-events:none;z-index:0;background:
  radial-gradient(60%% 50%% at 76%% 12%%,rgba(45,212,191,.17),transparent 70%%),
  radial-gradient(50%% 45%% at 8%% 92%%,rgba(13,148,136,.13),transparent 70%%)}
.eyebrow{font-family:var(--f-mono);font-size:11px;font-weight:500;letter-spacing:.2em;
  text-transform:uppercase;color:var(--teal);margin:0 0 14px}
.slide.dark .eyebrow,.slide.navy .eyebrow{color:var(--teal-bright)}
h1{font-family:var(--f-display);font-weight:800;font-size:clamp(34px,5.2vw,70px);
  line-height:%(h_lh)s;letter-spacing:%(ls)s;margin:0 0 18px;color:var(--ink);text-wrap:balance}
h2{font-family:var(--f-display);font-weight:700;font-size:clamp(25px,3.4vw,43px);
  line-height:%(h_lh)s;letter-spacing:%(ls)s;margin:0 0 12px;color:var(--ink);text-wrap:balance}
h3{font-family:var(--f-display);font-weight:600;font-size:%(fs_h3)s;margin:0 0 6px;color:var(--ink)}
.slide.dark h1,.slide.dark h2,.slide.navy h1,.slide.navy h2{color:#F2F8FC}
.slide.dark h3,.slide.navy h3{color:#EAF3F9}
.lede{font-size:clamp(%(fs_lede)s);max-width:64ch;color:var(--muted);margin:0}
.slide.dark .lede,.slide.navy .lede{color:#93AEC4}
.ltr{direction:ltr;unicode-bidi:isolate;display:inline-block}
.stamp{position:absolute;top:24px;inset-inline-end:40px;font-family:var(--f-mono);
  font-size:10px;letter-spacing:.14em;color:var(--muted);opacity:.65;z-index:2}
.two{display:grid;gap:36px;grid-template-columns:1fr;align-items:center;margin-top:26px}
@media(min-width:900px){.two{grid-template-columns:.85fr 1.15fr}}
.grid{display:grid;gap:14px;margin-top:30px}
.g3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.card{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:20px}
.slide.dark .card,.slide.navy .card{background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.12)}
.card p{margin:0;font-size:%(fs_card)s;color:var(--muted);line-height:%(lh)s}
.slide.dark .card p,.slide.navy .card p{color:#93AEC4}
.pts{list-style:none;margin:24px 0 0;padding:0;display:flex;flex-direction:column;gap:13px}
.pts li{position:relative;padding-inline-start:26px;font-size:%(fs_li)s;color:var(--muted);line-height:%(lh)s}
.slide.dark .pts li{color:#9BB4C8}
.pts li::before{content:"";position:absolute;inset-inline-start:0;top:9px;width:8px;height:8px;
  border-radius:2px;background:var(--teal-bright)}
/* illustration + diagram shells */
.art{margin-top:4px}.art svg{width:100%%;height:auto;display:block}
.hero{position:relative;display:flex;justify-content:center}
.hero-img{width:100%%;max-width:860px;height:auto;display:block;
  filter:drop-shadow(0 30px 60px rgba(0,0,0,.45));animation:float 7s ease-in-out infinite}
.agent-hero{max-width:980px;margin-inline:auto}
.agent-hero .hero-img{max-width:980px;animation:float 9s ease-in-out infinite;border-radius:16px}
.hero-fx{position:absolute;inset:0;width:100%%;height:100%%;pointer-events:none}
.sig{fill:#5EEAD4;filter:drop-shadow(0 0 7px rgba(94,234,212,.95))}
@keyframes float{0%%,100%%{transform:translateY(0)}50%%{transform:translateY(-12px)}}
.wide{margin-top:26px;overflow-x:auto}.wide svg{min-width:940px;width:100%%;height:auto;display:block}
.tok-t{font-family:var(--f-body);font-size:12px;fill:var(--coral)}
.cl rect{fill:rgba(255,255,255,.04);stroke:rgba(255,255,255,.12)}
.cl-t{font-family:var(--f-display);font-weight:700;font-size:14px;fill:var(--teal-bright);
  letter-spacing:.04em;text-transform:uppercase}
.mod rect{fill:rgba(13,148,136,.13);stroke:rgba(45,212,191,.4)}
.mod-t{font-family:var(--f-body);font-size:%(fs_mod)s;fill:#DCE9F4}
.dep{stroke:var(--teal-bright);stroke-width:1.7;fill:none;opacity:.75}
.dep.dashed{stroke-dasharray:5 6;opacity:.45;animation:march 1.2s linear infinite}
@keyframes march{to{stroke-dashoffset:-11}}
.loop-t{font-family:var(--f-mono);font-size:10.5px;fill:#7E97AD;letter-spacing:.08em}
.arm{stroke:var(--teal);stroke-width:2.2;fill:none;opacity:.5;stroke-linecap:round}
.pulse-dot{fill:var(--teal-bright)}
.cap rect{fill:rgba(13,148,136,.18);stroke:var(--teal-bright);stroke-width:1.2}
.cap-t{font-family:var(--f-body);font-size:12.5px;fill:#EAF3F9}
/* value table */
.tr{margin-top:22px;display:grid;gap:8px;grid-template-columns:1fr}
@media(min-width:960px){.tr{grid-template-columns:1fr 1fr}}
.tr-row{display:flex;flex-direction:column;gap:2px;
  background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.11);
  border-radius:10px;padding:10px 14px}
@media(max-width:760px){.tr-row{grid-template-columns:1fr;gap:5px}}
.tr-k{font-family:var(--f-display);font-weight:600;font-size:%(fs_tr_k)s;color:var(--teal-bright);letter-spacing:.02em}
.tr-v{font-size:%(fs_tr_v)s;color:#B9CADB;line-height:1.55}
/* comparison */
.cmp{margin-top:28px;display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.cmp-col{border-radius:14px;padding:22px;border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.04)}
.cmp-col.ours{border-color:var(--teal);background:rgba(13,148,136,.10)}
.cmp ul{margin:12px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:10px}
.cmp li{font-size:%(fs_cmp)s;padding-inline-start:22px;position:relative;color:#9BB4C8;line-height:%(lh)s}
.cmp li::before{content:"";position:absolute;inset-inline-start:0;top:8px;width:7px;height:7px;
  border-radius:50%%;background:#64798F}
.cmp-col.ours li::before{background:var(--teal-bright)}
/* roadmap — badge sits in flow so it can never collide with the heading */
.rm{margin-top:28px;display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}
.rm-card{background:var(--paper);border:1px dashed var(--line);border-radius:14px;padding:20px;
  display:flex;flex-direction:column;gap:9px;align-items:flex-start}
.slide.dark .rm-card{background:rgba(255,255,255,.035);border-color:rgba(255,255,255,.18)}
.rm-badge{font-family:var(--f-mono);font-size:9px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--teal);border:1px solid currentColor;border-radius:20px;padding:3px 9px;flex:none}
.rm-card h3{margin:0}
.rm-top{display:flex;align-items:center;justify-content:space-between;width:100%%;gap:10px}
.rm-card .ico{color:var(--teal);width:28px;height:28px;margin:0}
/* UI mock */
.mock{display:grid;grid-template-columns:186px 1fr;border-radius:14px;overflow:hidden;
  border:1px solid rgba(255,255,255,.14);background:#0E1626;
  box-shadow:0 24px 60px rgba(0,0,0,.34);font-size:12px}
.mk-side{background:#123C7A;padding:14px 0}
.mk-brand{font-family:var(--f-display);font-weight:700;color:#fff;font-size:13.5px;
  padding:0 16px 12px;border-bottom:1px solid rgba(255,255,255,.16);margin-bottom:8px}
.mk-side ul{list-style:none;margin:0;padding:0}
.mk-side li{color:#C6D8F2;padding:8px 16px;font-size:11.5px}
.mk-side li.on{background:#fff;color:#123C7A;font-weight:600;
  border-radius:8px;margin:0 8px}
.mk-main{padding:16px 18px;background:#0E1626}
.mk-top{display:flex;align-items:center;justify-content:space-between;
  padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,.1)}
.mk-title{font-family:var(--f-display);font-weight:700;color:#EAF3F9;font-size:15px}
.mk-dot{width:26px;height:26px;border-radius:50%%;background:rgba(45,212,191,.25);
  border:1px solid var(--teal-bright)}
.mk-kpis{display:flex;gap:10px;margin:14px 0}
.mk-kpi{flex:1;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);
  border-radius:9px;padding:9px 11px}
.mk-kpi b{display:block;font-family:var(--f-mono);font-size:19px;color:#EAF3F9;line-height:1.1}
.mk-kpi span{font-size:10.5px;color:#8497AC}
.mk-table{display:flex;flex-direction:column;gap:6px}
.mk-row{display:grid;grid-template-columns:1.1fr 1.5fr auto;gap:10px;align-items:center;
  background:rgba(255,255,255,.035);border-radius:8px;padding:9px 11px}
.mk-c1{font-family:var(--f-mono);font-size:11px;color:var(--teal-bright)}
.mk-c2{font-size:11.5px;color:#B9CADB}
.mk-pill{font-size:10px;padding:3px 9px;border-radius:20px;white-space:nowrap}
.mk-pill.ok{background:rgba(45,212,191,.16);color:#5EEAD4}
.mk-pill.warn{background:rgba(232,199,154,.16);color:#E8C79A}
.mk-pill.bad{background:rgba(232,131,111,.18);color:#F0A091}
/* demo slide */
.sub{font-family:var(--f-mono);font-size:%(fs_sub)s;letter-spacing:.16em;text-transform:uppercase;
  color:var(--teal-bright);margin:0 0 12px}
.fm-wrap{display:grid;gap:30px;margin-top:26px;grid-template-columns:1fr}
@media(min-width:940px){.fm-wrap{grid-template-columns:1.45fr 1fr}}
.fm-list{display:flex;flex-direction:column;gap:9px}
.fm,.dep-card{display:flex;flex-direction:column;gap:2px;background:rgba(255,255,255,.05);
  border:1px solid rgba(255,255,255,.11);border-radius:11px;padding:12px 15px}
.fm{flex-direction:row;align-items:flex-start;gap:12px}
.fm>div{display:flex;flex-direction:column;gap:2px;min-width:0}
.ico{width:26px;height:26px;flex:none;color:var(--teal-bright);margin-top:2px}
.fm b,.dep-card b{font-family:var(--f-display);font-weight:600;font-size:%(fs_fm_b)s;color:#EAF3F9}
.fm span,.dep-card span{font-size:%(fs_fm_s)s;color:#93AEC4;line-height:1.6}
.fm:first-child{border-color:var(--teal);background:rgba(13,148,136,.14)}
.demo{display:flex;flex-direction:column;gap:12px;margin-top:28px}
.demo div{display:flex;gap:14px;align-items:center;background:rgba(255,255,255,.05);
  border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:15px 18px;
  font-size:%(fs_demo)s;color:#D5E4F0}
.demo b{font-family:var(--f-mono);font-size:12px;color:var(--teal-bright);flex:none}
.reveal{opacity:0;transform:translateY(15px);
  transition:opacity .55s cubic-bezier(.2,.7,.3,1),transform .55s cubic-bezier(.2,.7,.3,1)}
.reveal.in{opacity:1;transform:none}
.rail{position:fixed;inset-inline-end:18px;top:50%%;transform:translateY(-50%%);z-index:40;
  display:flex;flex-direction:column;gap:8px}
.rail button{width:7px;height:7px;padding:0;border-radius:50%%;border:none;cursor:pointer;
  background:var(--muted);opacity:.3;transition:opacity .2s,transform .2s}
.rail button:hover{opacity:.7}
.rail button[aria-current="true"]{opacity:1;background:var(--teal);transform:scale(1.6)}
.rail button:focus-visible{outline:2px solid var(--teal);outline-offset:3px}
.pager{position:fixed;inset-inline-start:22px;bottom:18px;z-index:40;font-family:var(--f-mono);
  font-size:10.5px;color:var(--muted);letter-spacing:.1em}
.foot{position:fixed;inset-inline-end:22px;bottom:18px;z-index:40;font-family:var(--f-mono);
  font-size:10px;color:var(--muted);letter-spacing:.08em;opacity:.7}
.brandbar{display:flex;align-items:center;gap:18px;margin-bottom:40px;flex-wrap:wrap}
.wordmark{font-family:var(--f-display);font-weight:800;font-size:27px;line-height:1;
  color:#F2F8FC;white-space:nowrap;letter-spacing:%(wm_ls)s}
.wordmark em{font-style:normal;color:var(--teal-bright)}
.brandbar .wordmark::after{content:"";display:block;height:2px;margin-top:8px;
  background:linear-gradient(90deg,var(--teal-bright),transparent)}
.contact .wordmark{font-size:22px}
.bsep{width:1px;height:30px;background:rgba(255,255,255,.2)}
.prepared{font-family:var(--f-mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:#6E8BA3;display:block;margin-bottom:4px}
.client-name{font-family:var(--f-display);font-weight:600;font-size:19px;color:#EAF3F9}
.client-sub{font-size:14px;color:#93AEC4;margin-inline-start:8px}
.title-meta{margin-top:44px;display:flex;gap:30px;flex-wrap:wrap;font-family:var(--f-mono);
  font-size:11.5px;color:#6E8BA3}
.contact{margin-top:38px;display:flex;gap:30px;flex-wrap:wrap;align-items:center}
.contact a{color:var(--teal-bright);text-decoration:none;font-family:var(--f-mono);font-size:13.5px;
  border-bottom:1px solid currentColor;padding-bottom:2px}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .reveal{opacity:1;transform:none;transition:none}
  .dep.dashed{animation:none}
  animateMotion,animateTransform{display:none}}
@media (max-width:680px){.slide{padding:58px 18px 54px}.rail{display:none}
  .mock{grid-template-columns:1fr}.mk-side{display:none}}
"""


JS = """
(function(){
  var slides=[].slice.call(document.querySelectorAll('.slide'));
  var rail=document.getElementById('rail'),pg=document.getElementById('pgnow');
  document.getElementById('pgall').textContent=String(slides.length).padStart(2,'0');
  slides.forEach(function(s,i){
    var b=document.createElement('button');b.type='button';
    b.setAttribute('aria-label',s.dataset.name||('Slide '+(i+1)));
    b.addEventListener('click',function(){s.scrollIntoView({behavior:'smooth'});});
    rail.appendChild(b);
  });
  var dots=[].slice.call(rail.children);
  new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting)return;var i=slides.indexOf(e.target);
    dots.forEach(function(d,j){d.setAttribute('aria-current',String(j===i));});
    pg.textContent=String(i+1).padStart(2,'0');
  });},{threshold:.55}).observe&&slides.forEach(function(s){
    // one observer instance, attached below
  });
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting)return;var i=slides.indexOf(e.target);
    dots.forEach(function(d,j){d.setAttribute('aria-current',String(j===i));});
    pg.textContent=String(i+1).padStart(2,'0');
  });},{threshold:.55});
  slides.forEach(function(s){io.observe(s);});
  var ro=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add('in');ro.unobserve(e.target);}
  });},{threshold:.16});
  document.querySelectorAll('.reveal').forEach(function(n,i){
    n.style.transitionDelay=(Math.min(i%10,7)*55)+'ms';ro.observe(n);});
  document.addEventListener('keydown',function(e){
    var cur=0,best=1e9;
    slides.forEach(function(s,i){var d=Math.abs(s.getBoundingClientRect().top);
      if(d<best){best=d;cur=i;}});
    if(e.key==='ArrowDown'||e.key==='PageDown'||e.key===' '){
      if(slides[cur+1]){e.preventDefault();slides[cur+1].scrollIntoView({behavior:'smooth'});}}
    else if(e.key==='ArrowUp'||e.key==='PageUp'){
      if(slides[cur-1]){e.preventDefault();slides[cur-1].scrollIntoView({behavior:'smooth'});}}
  });
}());
"""


def build(t):
    n = t["nav"]
    S = []
    def slide(i, cls, body, stamp):
        S.append(f'<section class="slide {cls}" data-name="{n[i]}">'
                 f'<div class="glow"></div><span class="stamp">{stamp}</span>'
                 f'<div class="inner">{body}</div></section>')

    logo = f'<span class="wordmark">{t["wordmark"]}</span>'

    # 1 ─ title
    slide(0,"dark",f'''
      <div class="brandbar">{logo}<span class="bsep"></span>
        <span><span class="prepared">{t['prepared']}</span>
        <span class="client-name">{t['client']}</span><span class="client-sub">{t['client_sub']}</span></span></div>
      <p class="eyebrow">{t['s1_eyebrow']}</p>
      <h1>{t['s1_h']}</h1><p class="lede">{t['s1_l']}</p>
      <div class="title-meta">{''.join(f"<span>{m}</span>" for m in t['s1_meta'])}</div>''',"00:00")

    # 2 ─ problem
    slide(1,"dark",f'''
      <p class="eyebrow reveal">{t['s2_eyebrow']}</p>
      <h2 class="reveal">{t['s2_h']}</h2>
      <p class="lede reveal">{t['s2_l']}</p>
      <div class="art reveal">{hero_challenge(t)}</div>''',"01:00")

    # 3 ─ cost
    cards = ''.join(f'<div class="card reveal"><h3>{a}</h3><p>{b}</p></div>' for a,b in t['s3_cards'])
    slide(2,"",f'''
      <p class="eyebrow reveal">{t['s3_eyebrow']}</p>
      <h2 class="reveal">{t['s3_h']}</h2>
      <div class="grid g3">{cards}</div>''',"03:00")

    # 4 ─ system map
    slide(3,"dark",f'''
      <p class="eyebrow reveal">{t['s4_eyebrow']}</p>
      <h2 class="reveal">{t['s4_h']}</h2>
      <p class="lede reveal">{t['s4_l']}</p>
      <div class="wide reveal">{svg_system_map(t)}</div>''',"04:30")

    # 5,6,7 ─ business functions with a screen each
    for idx,(key,mk,stamp) in enumerate([("s5","meet","06:00"),("s6","decide","07:30"),("s7","record","09:00")]):
        pts = ''.join(f'<li>{p}</li>' for p in t[f'{key}_points'])
        slide(4+idx,"navy" if idx%2 else "",f'''
      <p class="eyebrow reveal">{t[f'{key}_eyebrow']}</p>
      <h2 class="reveal">{t[f'{key}_h']}</h2>
      <div class="two">
        <div><p class="lede reveal">{t[f'{key}_l']}</p><ul class="pts reveal">{pts}</ul></div>
        <div class="reveal">{ui_mock(t, t['mock'][mk])}</div>
      </div>''',stamp)

    # 8 ─ the agent
    slide(7,"dark",f'''
      <p class="eyebrow reveal">{t['s8_eyebrow']}</p>
      <h2 class="reveal">{t['s8_h']}</h2>
      <p class="lede reveal">{t['s8_l']}</p>
      <div class="art reveal">{agent_hero(t)}</div>''',"10:30")

    # 9 ─ AI value
    rows = ''.join(f'<div class="tr-row reveal"><span class="tr-k">{k}</span>'
                   f'<span class="tr-v">{v}</span></div>' for k,v in t['s9_rows'])
    slide(8,"navy",f'''
      <p class="eyebrow reveal">{t['s9_eyebrow']}</p>
      <h2 class="reveal">{t['s9_h']}</h2>
      <div class="tr">{rows}</div>''',"11:30")

    # 10 ─ foundation models + where it runs
    models = ''.join(
        f'<div class="fm reveal">{icon(k)}<div><b>{a}</b><span>{b}</span></div></div>'
        for k,a,b in t['s14_models'])
    deploy = ''.join(
        f'<div class="fm reveal">{icon(k)}<div><b>{a}</b><span>{b}</span></div></div>'
        for k,a,b in t['s14_deploy'])
    slide(9,"dark",f'''
      <p class="eyebrow reveal">{t['s14_eyebrow']}</p>
      <h2 class="reveal">{t['s14_h']}</h2>
      <p class="lede reveal">{t['s14_l']}</p>
      <div class="fm-wrap">
        <div><p class="sub reveal">{t['s14_models_h']}</p><div class="fm-list">{models}</div></div>
        <div><p class="sub reveal">{t['s14_deploy_h']}</p><div class="fm-list">{deploy}</div></div>
      </div>''',"11:30")

    # 11 ─ demo
    items = ''.join(f'<div class="reveal"><b>{i+1:02d}</b><span>{x}</span></div>'
                    for i,x in enumerate(t['s10_items']))
    slide(10,"dark",f'''
      <p class="eyebrow reveal">{t['s10_eyebrow']}</p>
      <h1 class="reveal">{t['s10_h']}</h1>
      <p class="lede reveal">{t['s10_l']}</p>
      <div class="demo">{items}</div>''',"12:30")

    # 12 ─ differentiation
    them = ''.join(f'<li>{x}</li>' for x in t['s11_them'])
    us   = ''.join(f'<li>{x}</li>' for x in t['s11_us'])
    slide(11,"dark",f'''
      <p class="eyebrow reveal">{t['s11_eyebrow']}</p>
      <h2 class="reveal">{t['s11_h']}</h2>
      <p class="lede reveal">{t['s11_l']}</p>
      <div class="cmp">
        <div class="cmp-col reveal"><h3>{t['s11_them_h']}</h3><ul>{them}</ul></div>
        <div class="cmp-col ours reveal"><h3>{t['s11_us_h']}</h3><ul>{us}</ul></div>
      </div>''',"13:30")

    # 13 ─ roadmap
    rm = ''.join(f'<div class="rm-card reveal">'
                 f'<div class="rm-top">{icon(k)}<span class="rm-badge">{t["s12_badge"]}</span></div>'
                 f'<h3>{a}</h3><p>{b}</p></div>' for k,a,b in t['s12_cards'])
    slide(12,"",f'''
      <p class="eyebrow reveal">{t['s12_eyebrow']}</p>
      <h2 class="reveal">{t['s12_h']}</h2>
      <p class="lede reveal">{t['s12_l']}</p>
      <div class="rm">{rm}</div>''',"14:15")

    # 14 ─ close
    slide(13,"dark",f'''
      <p class="eyebrow">{t['by']}</p>
      <h1>{t['s13_h']}</h1><p class="lede">{t['s13_l']}</p>
      <div class="contact">{logo}
        <a class="ltr" href="https://masarrcorp.com">masarrcorp.com</a></div>''',"15:00")

    ar = t['rtl']
    css = CSS % dict(f_display=t['f_display'], f_body=t['f_body'], dir=t['dir'],
                     lh="1.85" if ar else "1.6",
                     h_lh="1.2" if ar else "1.05",
                     ls="0" if ar else "-.028em",
                     # Arabic script sits smaller on the em than Latin, so the same px reads
                     # roughly a step down. Every body-copy size is scaled through these.
                     fs_lede="18.5px, 1.75vw, 22px" if ar else "15.5px, 1.5vw, 19px",
                     fs_card="15.5px" if ar else "14px",
                     fs_li="16.5px" if ar else "15px",
                     fs_cmp="15.5px" if ar else "14px",
                     fs_tr_k="15px" if ar else "13.5px",
                     fs_tr_v="14.5px" if ar else "12.8px",
                     fs_fm_b="16px" if ar else "14.5px",
                     fs_fm_s="14.5px" if ar else "13px",
                     fs_h3="19px" if ar else "17px",
                     fs_demo="17px" if ar else "15px",
                     fs_mod="14px" if ar else "12.5px",
                     fs_sub="12.5px" if ar else "11px",
                     wm_ls="0" if ar else "-.035em")
    return ('<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{t["title"]}</title>\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{t["fonts"]}&display=swap">\n'
            f'<style>{css}</style>\n'
            f'<div class="rail" id="rail" aria-label="Slides"></div>\n'
            f'<div class="pager"><span id="pgnow">01</span> / <span id="pgall">14</span></div>\n'
            f'<div class="foot">{t["foot"]}</div>\n'
            + "\n".join(S) + f'\n<script>{JS}</script>\n')


for t, fn in ((EN, "08-boardhub-deck-en.html"), (AR, "09-boardhub-deck-ar.html")):
    html = build(t)
    path = os.path.join(OUT, fn)
    io.open(path, "w", encoding="utf-8").write(html)
    print(f"  {fn}: {round(len(html)/1024,1)} KB, slides={html.count('class=\"slide')}")
