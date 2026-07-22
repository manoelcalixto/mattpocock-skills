Quickstart:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Start a new Codex thread and type `$mattpocock-skills:ask-matt`.

[Source](https://github.com/manoelcalixto/mattpocock-skills/tree/main/skills/engineering/ask-matt)

## What it does

`ask-matt` routes your situation to the smallest suitable Codex skill, workflow, or session transition. It explains which step comes next and how adjacent skills connect.

It does no engineering work itself: it is the map, not a hidden mega-workflow.

## When to reach for it

Type `$mattpocock-skills:ask-matt`, or the agent reaches for it automatically when a task fits.

Reach for it when you have an idea, bug, incoming request, architecture problem, large foggy effort, research question, or context-boundary problem and cannot tell which tool should lead.

## The main flow

```text
$mattpocock-skills:grill-with-docs → $mattpocock-skills:to-spec → $mattpocock-skills:to-tickets → /new → $mattpocock-skills:implement
```

`implement` uses the model-invoked `tdd` and `code-review` disciplines. A small change can skip tickets; a huge effort starts in `$mattpocock-skills:wayfinder` and returns through `$mattpocock-skills:to-spec` once the route becomes clear.

For repository safety outside the promoted plugin set, the standalone `$codex-git-guardrails` skill is the route when you want Codex to block destructive Git commands before execution.

## Session map

`/compact` stays in one summarized thread, `/fork` branches with full history, `/side` handles a tangent, `/resume` reopens persisted work, and `$mattpocock-skills:handoff` creates a curated artifact only when crossing into a genuinely clean `/new` thread. When the optional in-progress `$delegate-handoff` is installed, it hands work to another active agent and `/agent` switches to it.

## Agent work

When a routed workflow explicitly needs parallel or delegated work, [orchestrate-agents](https://aihero.dev/skills-orchestrate-agents) supplies the GPT-5.6 Sol-only MultiAgent V2 contract, task-shaped effort, isolated briefs, workflow-authorized recursion, and event-driven waiting. It is a shared primitive, not a reason to create agents for an otherwise local task.

## Where it fits

`ask-matt` is the router over the whole set. It commonly leads to [grill-with-docs](https://aihero.dev/skills-grill-with-docs), [diagnosing-bugs](https://aihero.dev/skills-diagnosing-bugs), [triage](https://aihero.dev/skills-triage), or [wayfinder](https://aihero.dev/skills-wayfinder); every other page points back here when the next route is unclear.
