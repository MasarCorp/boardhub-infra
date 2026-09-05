---
description: Design work against the real BoardHub code, then have a skeptic try to refute the plan
---

Run the `plan-and-verify` workflow for the work described in `$ARGUMENTS`, then act on what it
returns.

```
Workflow({ name: "plan-and-verify", args: [ ...one string per work item... ] })
```

Split `$ARGUMENTS` into one entry per item of work. One item is fine; several run concurrently,
each designed and then refuted independently.

**When it returns, read the verdicts before writing any code.**

- `inventedThings` — endpoints, fields, enums or methods the plan named that do not exist. Correct
  the plan; never implement one of these on the assumption the skeptic is wrong. If you disagree,
  grep for it yourself and settle it from the source.
- `duplication` — something already exists. Use it.
- `scopingHoles` / `restraintHoles` — tenant, owner or evidence boundaries. Treat these as
  blocking: they are the ones that become privacy incidents rather than bug reports.
- `weakTests` — a proposed test that could pass without exercising the behaviour. Rewrite it or
  drop it; a test that cannot fail is worse than no test, because it reads as coverage.
- `openQuestions` — bring genuine product forks to the user rather than deciding them. Decide
  anything an engineer would reasonably decide.

Then implement **sequentially**, one item per commit. Features here touch the same few files —
the agent's tool list, the assist panel, the API — so parallel edits conflict.

Each item finishes the same way, and none of these is optional:

1. build and run the unit tests
2. verify against the running stack — in the browser where the change is user-visible, because
   several bugs here were invisible in the source and obvious in the DOM
3. a release entry in `boardhub-ai-services/docs/AI-ROADMAP.md`
4. checks added to `boardhub-infra/runbooks/ai-features/07-ai-assist-test-plan.html`, with the
   count verified against the file rather than restated

Report what the skeptics caught. That is usually the most useful part of the run.
