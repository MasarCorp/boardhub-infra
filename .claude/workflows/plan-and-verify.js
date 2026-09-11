export const meta = {
  name: 'plan-and-verify',
  description: 'Design each work item against the real code, then have a skeptic try to refute the plan',
  whenToUse: 'Before building anything non-trivial in BoardHub. Pass one string per work item as args. Returns a grounded plan plus a skeptic verdict per item; read the verdicts before writing any code.',
  phases: [
    { title: 'Design', detail: 'one agent per item, reading the real code' },
    { title: 'Verify', detail: 'a skeptic greps for everything the plan named' },
  ],
}

/*
 * Why this exists.
 *
 * Run on 4 September against three roadmap items, this caught TWENTY things the plans named that
 * did not exist — `ApiService.get`, `AgendaItem.responsibleUserId`, `@Mock` on a static method,
 * repository finders assumed to filter soft-deletes that did not. Each would have become a bug
 * found later and more expensively.
 *
 * The failure it catches is not sloppiness, it is PLAUSIBILITY: every invented name was the name
 * the API should have had. That is the shape of most of this codebase's recorded findings —
 * raw Lucide glyphs where `app-icon` takes semantic names, `BusinessException` where the
 * convention was `ResponseStatusException`, a rule scoped to a text node where markdown puts a
 * `<strong>`. A reviewer who only reads the plan cannot see any of it; one who greps can.
 *
 * The design agents are read-only on purpose. Implementation stays sequential, because features
 * in this repo touch the same few files (the agent's tool list, the panel, the API) and parallel
 * writes just produce conflicts. What parallelises well is the expensive part: reading.
 */

const ROOT = '/Users/mohamedramadan/Documents/masarcorprepos'

/** The house rules. Every one of these was learned from a real finding. */
const CONTEXT = `
You are planning work on BoardHub, an Arabic-first board/committee governance platform.

Repos (siblings under ${ROOT}):
- boardhub              Spring Boot backend, package tech.platform.*, Postgres, Flyway
- boardhub-ui           Angular 22, standalone components, signals, i18n src/i18n/{ar,en}.json
- boardhub-ai-services  Python 3.12 FastAPI; the agent is app/agents/assist_agent.py
- boardhub-infra        docker-compose.dev.yml + runbooks/ai-features/07-ai-assist-test-plan.html

HOUSE RULES — each of these is a bug that already happened here:
1. REUSE, never duplicate. Search for an existing helper, endpoint or pattern first.
2. NEVER invent an endpoint, DTO field, enum value or method. Everything you name must be
   something you verified in the source; cite the file and line where you found it.
3. Soft deletes and status are not the same question. A resignation is MembershipStatus
   TERMINATED with the row KEPT — history has to survive and the person's work is delegated.
   So filtering isDeleted is not sufficient for "may this person see it"; check status too.
4. Owner-scoping follows tech.platform.reminder.ReminderService (requireOwner). Tenant scope
   alone is not a boundary for anything personal. ResponseStatusException for 401/403, never
   BusinessException.
5. The AI worker reaches data ONLY through the backend REST API, never the database.
6. Restraint: act only on evidence the run actually has (citations), never on "what exists".
7. Angular: [innerHTML] content is sanitized — every data-* attribute is STRIPPED, and
   component-scoped CSS cannot style it. Icons use SEMANTIC names from app-icon's registry, never
   raw Lucide names. i18n keys go in BOTH ar.json and en.json.
8. Scheduled jobs that SEND anything need @SchedulerLock, or every replica sends its own copy.
9. A test that cannot fail is worthless — several "passing" tests here asserted nothing.

Read the actual code before proposing anything. Do NOT modify any file; this is planning only.
`

const PLAN = {
  type: 'object',
  properties: {
    item: { type: 'string' },
    summary: { type: 'string' },
    reuse: {
      type: 'array',
      items: {
        type: 'object',
        properties: { what: { type: 'string' }, where: { type: 'string' } },
        required: ['what', 'where'],
      },
    },
    changes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          repo: { type: 'string' }, path: { type: 'string' },
          action: { type: 'string' }, change: { type: 'string' },
        },
        required: ['repo', 'path', 'action', 'change'],
      },
    },
    endpoints: { type: 'array', items: { type: 'string' } },
    migration: { type: 'string' },
    scoping: { type: 'string' },
    tests: {
      type: 'array',
      items: {
        type: 'object',
        properties: { name: { type: 'string' }, asserts: { type: 'string' } },
        required: ['name', 'asserts'],
      },
    },
    testPlanChecks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' }, name: { type: 'string' },
          expect: { type: 'string' }, failsIf: { type: 'string' },
        },
        required: ['id', 'name', 'expect', 'failsIf'],
      },
    },
    roadmapEntry: { type: 'string' },
    risks: { type: 'array', items: { type: 'string' } },
    openQuestions: { type: 'array', items: { type: 'string' } },
  },
  required: ['item', 'summary', 'reuse', 'changes', 'endpoints', 'migration', 'scoping',
             'tests', 'testPlanChecks', 'roadmapEntry', 'risks', 'openQuestions'],
}

const VERDICT = {
  type: 'object',
  properties: {
    item: { type: 'string' },
    verdict: { type: 'string', description: 'SOUND | NEEDS_WORK | UNSOUND' },
    inventedThings: { type: 'array', items: { type: 'string' } },
    duplication: { type: 'array', items: { type: 'string' } },
    scopingHoles: { type: 'array', items: { type: 'string' } },
    restraintHoles: { type: 'array', items: { type: 'string' } },
    weakTests: { type: 'array', items: { type: 'string' } },
    corrections: { type: 'array', items: { type: 'string' } },
  },
  required: ['item', 'verdict', 'inventedThings', 'duplication', 'scopingHoles',
             'restraintHoles', 'weakTests', 'corrections'],
}

const items = Array.isArray(args) ? args : (args ? [args] : [])
if (items.length === 0) {
  return { error: 'Pass the work items as args, e.g. args: ["roadmap item 4 — auto-linking"]' }
}
log(`planning ${items.length} item(s), each designed then refuted`)

phase('Design')

const results = await pipeline(
  items,
  (it, _orig, i) => agent(
    `${CONTEXT}

Design the implementation for: ${typeof it === 'string' ? it : JSON.stringify(it)}

Produce a plan precise enough that an engineer could implement it without re-deriving anything:
every file, every endpoint, every test. Ground every claim in code you actually read and cite
file:line. Where something already exists, reuse it and say where it is. Put only genuine product
decisions in openQuestions — decide anything an engineer would reasonably decide themselves.`,
    { label: `design:${i + 1}`, phase: 'Design', schema: PLAN },
  ),
  (plan, it, i) => {
    if (!plan) return null
    return agent(
      `${CONTEXT}

Review this implementation plan. Your job is to REFUTE it — assume it is wrong until the code
proves otherwise.

GREP FOR EVERY endpoint, DTO field, enum value, method and file path it names. The single most
common failure here is a plan naming something plausible that is not there. Then check: does it
duplicate something that exists? Does it confuse soft-delete with status? Does it respect tenant
and owner scoping? Does it act on more evidence than a run actually has? Could any proposed test
pass without exercising the behaviour?

Give concrete corrections, not opinions. Where the plan is right, say so in corrections so it is
not re-litigated.

THE PLAN:
${JSON.stringify(plan, null, 2)}`,
      { label: `verify:${i + 1}`, phase: 'Verify', schema: VERDICT, effort: 'high' },
    ).then((v) => ({ item: typeof it === 'string' ? it : `item ${i + 1}`, plan, verdict: v }))
  },
)

const out = results.filter(Boolean)
const needsWork = out.filter((r) => r.verdict && r.verdict.verdict !== 'SOUND').length
const invented = out.reduce((n, r) => n + ((r.verdict && r.verdict.inventedThings) || []).length, 0)
log(`${out.length} planned · ${needsWork} need work · ${invented} invented things caught`)
return out
