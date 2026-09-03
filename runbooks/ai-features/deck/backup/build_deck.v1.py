# -*- coding: utf-8 -*-
"""Builds the BoardHub meeting deck in English and Arabic from one source.

Both decks share structure, motion and SVG assets; only copy, type and direction differ.
Written for a 15-minute discussion with a live demo, not a brochure read-through.
"""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)                      # runbooks/ai-features/
LOGO = io.open(os.path.join(HERE, "logo-light.b64")).read().strip()

# ── the real module list, taken from the running BoardHub sidebar ────────────
MODULES = [
    # (key, en, ar, cluster)
    ("dashboard",  "Dashboard",            "لوحة التحكم",        "govern"),
    ("boards",     "Boards & committees",  "المجالس واللجان",     "govern"),
    ("external",   "External committees",  "اللجان الخارجية",     "govern"),
    ("assess",     "Board assessments",    "تقييم المجالس",       "govern"),

    ("meetings",   "Meetings",             "الاجتماعات",          "meet"),
    ("agenda",     "Agenda items",         "بنود الأعمال",        "meet"),
    ("packs",      "Board packs",          "حزم المجلس",          "meet"),
    ("minutes",    "Minutes",              "المحاضر",             "meet"),

    ("voting",     "Voting & decisions",   "التصويت والقرارات",   "decide"),
    ("followup",   "Decision follow-up",   "متابعة القرارات",     "decide"),
    ("tasks",      "Task management",      "إدارة المهام",        "decide"),
    ("reports",    "Reports & KPIs",       "التقارير والمؤشرات",  "decide"),

    ("library",    "Document library",     "مكتبة المستندات",     "record"),
    ("esign",      "e-Signature",          "التوقيع الإلكتروني",  "record"),
    ("chat",       "Conversations",        "المحادثات",           "record"),
    ("settings",   "Roles & settings",     "إعدادات النظام",      "record"),
]
CLUSTERS = {
    "govern": ("Constitute",  "التكوين",   "Who governs, and how they are assessed."),
    "meet":   ("Convene",     "الانعقاد",  "Getting a valid meeting to happen."),
    "decide": ("Decide & do", "القرار والتنفيذ", "Turning discussion into tracked action."),
    "record": ("Evidence",    "الإثبات",   "The defensible record of what happened."),
}


# ════════════════════════════════════════════════════════════════════════════
# SVG assets
# ════════════════════════════════════════════════════════════════════════════

def svg_overwhelmed(t):
    """The board secretary buried in channels. Deliberately abstract — a literal
    stock figure would read as clip-art in a government room."""
    items = t["overwhelm_items"]
    badges = ""
    # orbiting interruption tokens
    ring = [(-250,-96,0),(-160,-150,.7),(-40,-168,1.4),(80,-150,2.1),
            (188,-104,2.8),(238,-16,3.5),(-286,-8,4.2),(206,66,4.9)]
    for i,(dx,dy,delay) in enumerate(ring):
        lbl = items[i % len(items)]
        w = 8 + len(lbl)*7.4
        badges += f'''
      <g class="tok" transform="translate({500+dx},{250+dy})">
        <g>
          <rect x="{-w/2}" y="-13" width="{w}" height="26" rx="13"
                fill="rgba(232,131,111,.14)" stroke="#E8836F" stroke-width="1"/>
          <text x="0" y="4.5" text-anchor="middle" class="tok-t">{lbl}</text>
          <animateTransform attributeName="transform" type="translate"
            values="0 0; 0 -7; 0 0" dur="{3.4+i*0.23}s" begin="{delay}s" repeatCount="indefinite"/>
        </g>
      </g>'''
    return f'''<svg viewBox="0 0 1000 470" role="img" aria-label="{t['overwhelm_alt']}">
  <defs>
    <radialGradient id="halo" cx="50%" cy="55%">
      <stop offset="0%" stop-color="#0D9488" stop-opacity=".30"/>
      <stop offset="100%" stop-color="#0D9488" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <ellipse cx="500" cy="268" rx="230" ry="180" fill="url(#halo)"/>
  <!-- desk -->
  <rect x="330" y="368" width="340" height="9" rx="4.5" fill="#0D9488" opacity=".45"/>
  <!-- figure: head, shoulders, a bowed posture -->
  <g class="fig">
    <circle cx="500" cy="238" r="42" fill="none" stroke="#2DD4BF" stroke-width="2.4"/>
    <path d="M424 368 q0-72 76-72 t76 72" fill="none" stroke="#2DD4BF" stroke-width="2.4"/>
    <!-- hands to head -->
    <path d="M462 262 q-26-10-30-38" fill="none" stroke="#2DD4BF" stroke-width="2" opacity=".8"/>
    <path d="M538 262 q26-10 30-38" fill="none" stroke="#2DD4BF" stroke-width="2" opacity=".8"/>
    <animateTransform attributeName="transform" type="translate"
      values="0 0; 0 4; 0 0" dur="5.5s" repeatCount="indefinite"/>
  </g>
  {badges}
</svg>'''


def svg_system_map(t):
    """Every module, grouped by the business function it serves, with the
    dependencies between groups drawn — the 'capabilities are not defined' fix."""
    cols = [("govern",90),("meet",325),("decide",560),("record",795)]
    out = []
    for key, x in cols:
        en, ar, _ = CLUSTERS[key]
        label = ar if t["rtl"] else en
        out.append(f'''
    <g class="cl">
      <rect x="{x}" y="66" width="190" height="300" rx="14"/>
      <text x="{x+95}" y="96" text-anchor="middle" class="cl-t">{label}</text>''')
        mods = [m for m in MODULES if m[3] == key]
        for i, (_, men, mar, _) in enumerate(mods):
            y = 122 + i*58
            name = mar if t["rtl"] else men
            out.append(f'''
      <g class="mod">
        <rect x="{x+14}" y="{y}" width="162" height="44" rx="9"/>
        <text x="{x+95}" y="{y+27}" text-anchor="middle" class="mod-t">{name}</text>
      </g>''')
        out.append("    </g>")
    # dependency arrows between clusters
    arrows = ""
    for x1, x2 in [(280,325),(515,560),(750,795)]:
        arrows += f'''
    <path class="dep" marker-end="url(#dep)" d="M{x1} 216 H{x2-4}"/>'''
    # feedback loop: evidence informs constitution
    arrows += '''
    <path class="dep dashed" marker-end="url(#dep)" d="M890 372 V412 H185 V372"/>'''
    return f'''<svg viewBox="0 0 1000 448" role="img" aria-label="{t['map_alt']}">
  <defs><marker id="dep" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto">
    <path d="M0 .5 L8 4.5 L0 8.5 z" fill="#0D9488"/></marker></defs>
  {''.join(out)}
  {arrows}
  <text x="537" y="432" text-anchor="middle" class="loop-t">{t['map_loop']}</text>
</svg>'''


def svg_octopus(t):
    """The agent drawn as one body with many reaching arms — the point being that a
    single assistant touches every module, rather than eight disconnected features."""
    caps = t["octo_caps"]
    # (angle-ish target x,y, curve control x,y)
    targets = [
        (150,110,300,150),(500,60,500,150),(850,110,700,150),
        (930,270,760,255),(850,430,700,360),(500,478,500,370),
        (150,430,300,360),(70,270,240,255),
    ]
    arms, nodes = "", ""
    for i,(tx,ty,cx,cy) in enumerate(targets):
        arms += f'''
    <path id="arm{i}" class="arm" d="M500 268 Q{cx} {cy} {tx} {ty}"/>
    <circle r="4.5" class="pulse-dot">
      <animateMotion dur="{2.6+i*0.17}s" begin="{i*0.28}s" repeatCount="indefinite">
        <mpath href="#arm{i}"/></animateMotion>
    </circle>'''
        label = caps[i]
        w = 22 + len(label)*7.1
        anchor_x = max(w/2+6, min(1000-w/2-6, tx))
        nodes += f'''
    <g class="cap">
      <rect x="{anchor_x-w/2}" y="{ty-17}" width="{w}" height="34" rx="17"/>
      <text x="{anchor_x}" y="{ty+5}" text-anchor="middle" class="cap-t">{label}</text>
    </g>'''
    return f'''<svg viewBox="0 0 1000 540" role="img" aria-label="{t['octo_alt']}">
  <defs>
    <radialGradient id="body" cx="50%" cy="42%">
      <stop offset="0%" stop-color="#2DD4BF" stop-opacity=".38"/>
      <stop offset="100%" stop-color="#0D9488" stop-opacity=".05"/>
    </radialGradient>
  </defs>
  {arms}
  <!-- body -->
  <g class="octo">
    <ellipse cx="500" cy="262" rx="86" ry="76" fill="url(#body)" stroke="#2DD4BF" stroke-width="2"/>
    <circle cx="474" cy="248" r="7.5" fill="#2DD4BF"/>
    <circle cx="526" cy="248" r="7.5" fill="#2DD4BF"/>
    <path d="M478 288 q22 16 44 0" fill="none" stroke="#2DD4BF" stroke-width="2.4" stroke-linecap="round"/>
    <animateTransform attributeName="transform" type="translate"
      values="0 0; 0 -9; 0 0" dur="6s" repeatCount="indefinite"/>
  </g>
  {nodes}
</svg>'''


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
  client="Human Resources Development Fund", client_sub="هدف",
  prepared="Prepared for", by="MasarCorp", foot="MASARCORP",
  nav=["Opening","The problem","What it costs","The platform","Convene",
       "Decide","Evidence","The assistant","AI value","Live demo","Why us","Roadmap","Close"],

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
  s9_rows=[("Tool use","It answers from the live system, not last night's export. \"How many meetings next month\" queries the record as you ask."),
           ("Knowledge base","Upload a policy, a circular or a scanned resolution. It is indexed and becomes answerable — with the source cited."),
           ("OCR, Arabic","A scanned or stamped page is read, not skipped. Photographed minutes become searchable text."),
           ("Retrieval & citations","Every claim carries a numbered link to the record it came from. Nothing is asserted without provenance."),
           ("Memory","It holds the thread. Establish a committee or a month once, then keep asking in plain language."),
           ("Reasoning","\"What is overdue, and what should the next agenda cover?\" is several lookups and a judgement — handled in one ask."),
           ("Document generation","It drafts the memo, you approve it, and it files it against the meeting as a real Word document in Arabic."),
           ("Guardrails","It will not invent a number, and writes nothing without explicit confirmation.")],

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
  s12_cards=[("Correspondence systems","Link official incoming and outgoing correspondence to the decision or meeting it belongs to, closing the loop between a transaction and its resolution."),
             ("AI Work Council","A standing advisory layer over the record, surfacing risk, drift and follow-up before the meeting rather than after."),
             ("Microsoft Teams & Webex","Schedule and join from the meeting record, and bring the recording back for minutes."),
             ("ServiceNow","Two-way sync so a board task and its operational ticket remain a single truth.")],

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
  fonts="family=Tajawal:wght@400;500;700;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500",
  f_display='"Tajawal","IBM Plex Sans Arabic",system-ui,sans-serif',
  f_body='"IBM Plex Sans Arabic","Tajawal",system-ui,sans-serif',
  client="صندوق تنمية الموارد البشرية", client_sub="هدف",
  prepared="أُعدّ لـ", by="مسار كورب", foot="مسار كورب",
  nav=["الافتتاح","التحدي","الكلفة","المنصة","الانعقاد","القرار",
       "الإثبات","المساعد","قيمة الذكاء","العرض الحي","لماذا نحن","خارطة الطريق","الختام"],

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
  s9_rows=[("استخدام الأدوات","يجيب من النظام الحيّ لا من تصدير الأمس. «كم اجتماعاً الشهر القادم؟» يستعلم من السجل لحظة سؤالك."),
           ("قاعدة المعرفة","ارفع سياسة أو تعميماً أو قراراً ممسوحاً ضوئياً، فيُفهرَس ويصبح قابلاً للسؤال — مع ذكر مصدره."),
           ("المسح الضوئي بالعربية","الصفحة الممسوحة أو المختومة تُقرأ ولا تُتجاهَل. المحاضر المصوَّرة تتحول إلى نص قابل للبحث."),
           ("الاسترجاع والمصادر","كل معلومة تحمل رابطاً مرقّماً إلى السجل الذي جاءت منه. لا يُقال شيء بلا سند."),
           ("الذاكرة","يحتفظ بخيط الحوار. حدّد اللجنة أو الشهر مرة واحدة ثم تابع أسئلتك بلغة طبيعية."),
           ("الاستدلال","«ما المتأخر؟ وبماذا ينبغي أن يهتم جدول الأعمال القادم؟» عدة استعلامات وحكم مهني، في سؤال واحد."),
           ("توليد المستندات","يصوغ المذكرة، وتعتمدها أنت، فيحفظها على الاجتماع كمستند Word عربي حقيقي."),
           ("الضوابط","لا يختلق رقماً، ولا يكتب شيئاً دون تأكيد صريح منك.")],

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
  s12_cards=[("أنظمة المعاملات والمراسلات","ربط الوارد والصادر الرسمي بالقرار أو الاجتماع الذي يخصّه، فتُغلق الدائرة بين المعاملة وقرارها."),
             ("مجلس العمل الذكي","طبقة استشارية دائمة فوق السجل، تُظهر المخاطر والانحراف والمتابعات قبل الاجتماع لا بعده."),
             ("التكامل مع Microsoft Teams و Webex","الجدولة والانضمام من سجل الاجتماع، وإعادة التسجيل لصياغة المحضر."),
             ("التكامل مع ServiceNow","مزامنة ثنائية الاتجاه تجعل مهمة المجلس وتذكرتها التشغيلية مصدراً واحداً للحقيقة.")],

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
      rows=[("مذكرة سياسة السفر","مُولَّدة · مرتبطة بـ BOD-2026-013","Word","ok"),
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
h3{font-family:var(--f-display);font-weight:600;font-size:17px;margin:0 0 6px;color:var(--ink)}
.slide.dark h1,.slide.dark h2,.slide.navy h1,.slide.navy h2{color:#F2F8FC}
.slide.dark h3,.slide.navy h3{color:#EAF3F9}
.lede{font-size:clamp(15.5px,1.5vw,19px);max-width:64ch;color:var(--muted);margin:0}
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
.card p{margin:0;font-size:14px;color:var(--muted);line-height:%(lh)s}
.slide.dark .card p,.slide.navy .card p{color:#93AEC4}
.pts{list-style:none;margin:24px 0 0;padding:0;display:flex;flex-direction:column;gap:13px}
.pts li{position:relative;padding-inline-start:26px;font-size:15px;color:var(--muted);line-height:%(lh)s}
.slide.dark .pts li{color:#9BB4C8}
.pts li::before{content:"";position:absolute;inset-inline-start:0;top:9px;width:8px;height:8px;
  border-radius:2px;background:var(--teal-bright)}
/* illustration + diagram shells */
.art{margin-top:8px}.art svg{width:100%%;height:auto;display:block}
.wide{margin-top:26px;overflow-x:auto}.wide svg{min-width:900px;width:100%%;height:auto;display:block}
.tok-t{font-family:var(--f-body);font-size:12px;fill:var(--coral)}
.cl rect{fill:rgba(255,255,255,.04);stroke:rgba(255,255,255,.12)}
.cl-t{font-family:var(--f-display);font-weight:700;font-size:14px;fill:var(--teal-bright);
  letter-spacing:.04em;text-transform:uppercase}
.mod rect{fill:rgba(13,148,136,.13);stroke:rgba(45,212,191,.4)}
.mod-t{font-family:var(--f-body);font-size:12.5px;fill:#DCE9F4}
.dep{stroke:var(--teal-bright);stroke-width:1.7;fill:none;opacity:.75}
.dep.dashed{stroke-dasharray:5 6;opacity:.45;animation:march 1.2s linear infinite}
@keyframes march{to{stroke-dashoffset:-11}}
.loop-t{font-family:var(--f-mono);font-size:10.5px;fill:#7E97AD;letter-spacing:.08em}
.arm{stroke:var(--teal);stroke-width:2.2;fill:none;opacity:.5;stroke-linecap:round}
.pulse-dot{fill:var(--teal-bright)}
.cap rect{fill:rgba(13,148,136,.18);stroke:var(--teal-bright);stroke-width:1.2}
.cap-t{font-family:var(--f-body);font-size:12.5px;fill:#EAF3F9}
/* value table */
.tr{margin-top:26px;display:flex;flex-direction:column;gap:9px}
.tr-row{display:grid;gap:16px;align-items:center;grid-template-columns:190px 1fr;
  background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.11);
  border-radius:12px;padding:14px 18px}
@media(max-width:760px){.tr-row{grid-template-columns:1fr;gap:5px}}
.tr-k{font-family:var(--f-mono);font-size:12px;color:var(--teal-bright);letter-spacing:.02em}
.tr-v{font-size:14.5px;color:#D5E4F0;line-height:%(lh)s}
/* comparison */
.cmp{margin-top:28px;display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.cmp-col{border-radius:14px;padding:22px;border:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.04)}
.cmp-col.ours{border-color:var(--teal);background:rgba(13,148,136,.10)}
.cmp ul{margin:12px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:10px}
.cmp li{font-size:14px;padding-inline-start:22px;position:relative;color:#9BB4C8;line-height:%(lh)s}
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
.demo{display:flex;flex-direction:column;gap:12px;margin-top:28px}
.demo div{display:flex;gap:14px;align-items:center;background:rgba(255,255,255,.05);
  border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:15px 18px;
  font-size:15px;color:#D5E4F0}
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
.logo{display:block;width:auto;height:44px}
.contact .logo{height:32px}
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

    logo = f'<img class="logo" src="{LOGO}" alt="{t["by"]}">'

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
      <div class="art reveal">{svg_overwhelmed(t)}</div>''',"01:00")

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
      <div class="wide reveal">{svg_octopus(t)}</div>''',"10:30")

    # 9 ─ AI value
    rows = ''.join(f'<div class="tr-row reveal"><span class="tr-k">{k}</span>'
                   f'<span class="tr-v">{v}</span></div>' for k,v in t['s9_rows'])
    slide(8,"navy",f'''
      <p class="eyebrow reveal">{t['s9_eyebrow']}</p>
      <h2 class="reveal">{t['s9_h']}</h2>
      <div class="tr">{rows}</div>''',"11:30")

    # 10 ─ demo
    items = ''.join(f'<div class="reveal"><b>{i+1:02d}</b><span>{x}</span></div>'
                    for i,x in enumerate(t['s10_items']))
    slide(9,"dark",f'''
      <p class="eyebrow reveal">{t['s10_eyebrow']}</p>
      <h1 class="reveal">{t['s10_h']}</h1>
      <p class="lede reveal">{t['s10_l']}</p>
      <div class="demo">{items}</div>''',"13:00")

    # 11 ─ differentiation
    them = ''.join(f'<li>{x}</li>' for x in t['s11_them'])
    us   = ''.join(f'<li>{x}</li>' for x in t['s11_us'])
    slide(10,"dark",f'''
      <p class="eyebrow reveal">{t['s11_eyebrow']}</p>
      <h2 class="reveal">{t['s11_h']}</h2>
      <p class="lede reveal">{t['s11_l']}</p>
      <div class="cmp">
        <div class="cmp-col reveal"><h3>{t['s11_them_h']}</h3><ul>{them}</ul></div>
        <div class="cmp-col ours reveal"><h3>{t['s11_us_h']}</h3><ul>{us}</ul></div>
      </div>''',"14:00")

    # 12 ─ roadmap
    rm = ''.join(f'<div class="rm-card reveal"><span class="rm-badge">{t["s12_badge"]}</span>'
                 f'<h3>{a}</h3><p>{b}</p></div>' for a,b in t['s12_cards'])
    slide(11,"",f'''
      <p class="eyebrow reveal">{t['s12_eyebrow']}</p>
      <h2 class="reveal">{t['s12_h']}</h2>
      <p class="lede reveal">{t['s12_l']}</p>
      <div class="rm">{rm}</div>''',"14:30")

    # 13 ─ close
    slide(12,"dark",f'''
      <p class="eyebrow">{t['by']}</p>
      <h1>{t['s13_h']}</h1><p class="lede">{t['s13_l']}</p>
      <div class="contact">{logo}
        <a class="ltr" href="https://masarrcorp.com">masarrcorp.com</a></div>''',"15:00")

    css = CSS % dict(f_display=t['f_display'], f_body=t['f_body'], dir=t['dir'],
                     lh="1.8" if t['rtl'] else "1.6",
                     h_lh="1.16" if t['rtl'] else "1.05",
                     ls="0" if t['rtl'] else "-.028em")
    return (f'<title>{t["title"]}</title>\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{t["fonts"]}&display=swap">\n'
            f'<style>{css}</style>\n'
            f'<div class="rail" id="rail" aria-label="Slides"></div>\n'
            f'<div class="pager"><span id="pgnow">01</span> / <span id="pgall">13</span></div>\n'
            f'<div class="foot">{t["foot"]}</div>\n'
            + "\n".join(S) + f'\n<script>{JS}</script>\n')


for t, fn in ((EN, "08-boardhub-deck-en.html"), (AR, "09-boardhub-deck-ar.html")):
    html = build(t)
    path = os.path.join(OUT, fn)
    io.open(path, "w", encoding="utf-8").write(html)
    print(f"  {fn}: {round(len(html)/1024,1)} KB, slides={html.count('class=\"slide')}")
