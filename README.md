# Matt Pocock Skills — Codex Fork

A Codex-native fork of [Matt Pocock's agent skills](https://github.com/mattpocock/skills), maintained by [Manoel Calixto](https://github.com/manoelcalixto).

The skills are small, composable workflows for real engineering: grilling, specs, tracer-bullet tickets, TDD, code review, domain modelling, architecture, research, session transitions, and adaptive multi-agent work.

## Install from this fork

Add the fork's marketplace and install its plugin:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

The full plugin identity is `mattpocock-skills@manoelcalixto`, so it can coexist with a plugin of the same name from another marketplace.

Start a new Codex thread, open the repository you want to configure, and run:

```text
$setup-matt-pocock-skills
```

The setup skill configures the issue tracker, triage labels when relevant, and domain-document layout in the repository's root `AGENTS.md` and `docs/agents/` files.

Codex loads plugin changes at a thread boundary. After installing or updating the plugin, use `/new` before testing a changed skill. Use `/skills` to browse available skills and `$skill-name` to invoke one explicitly.

### Editable-copy alternative

To copy selected skills into your own setup instead of subscribing to the managed plugin:

```bash
npx skills@latest add manoelcalixto/mattpocock-skills
```

Maintainers of this clone can link every non-deprecated skill directly into Codex with `scripts/link-skills.sh`.

## Core workflow

The default engineering chain is:

```text
$grill-with-docs → $to-spec → $to-tickets → /new → $implement
                                                       ├─ tdd
                                                       └─ code-review
```

- `$grill-with-docs` resolves the decision tree while maintaining project vocabulary and ADRs.
- `$to-spec` synthesizes the conversation without re-interviewing.
- `$to-tickets` splits larger work into independently executable tracer bullets.
- Each ticket starts in `/new` with `$implement <ticket>`.
- `implement` uses the model-invoked `tdd` and `code-review` disciplines.

Use `$ask-matt` when you are unsure which flow fits. For a huge effort whose route cannot fit one thread, use `$wayfinder`. For a hard bug, let `diagnosing-bugs` establish a tight feedback loop first.

## Codex-native behavior

- **Explicit skills:** `$skill-name`; `/...` is reserved for Codex commands.
- **Sessions:** `/compact` summarizes the same thread, `/fork` preserves full history in a branch, `/side` handles tangents, `/resume` reopens persisted work, and `$handoff` creates a curated artifact only for a genuinely clean `/new` thread.
- **Multi-agent:** `orchestrate-agents` adapts to Codex V1 or V2, defaults to isolated briefs, respects available slots, and protects the shared working directory.
- **Hooks:** trusted `PreToolUse` hooks are configured in `.codex/config.toml` or `~/.codex/config.toml`.
- **Repository instructions:** `AGENTS.md` is the only canonical agent-instructions file.

## Reference

Promoted skills are shipped by `mattpocock-skills@manoelcalixto`. User-invoked skills run only when you type `$skill-name`; model-invoked skills can also be selected automatically by Codex.

### Engineering

#### User-invoked

- **[ask-matt](./skills/engineering/ask-matt/SKILL.md)** — Route a situation to the right skill, workflow, or session transition.
- **[grill-with-docs](./skills/engineering/grill-with-docs/SKILL.md)** — Sharpen a design while maintaining `CONTEXT.md` and ADRs.
- **[triage](./skills/engineering/triage/SKILL.md)** — Move incoming requests through configured triage roles.
- **[improve-codebase-architecture](./skills/engineering/improve-codebase-architecture/SKILL.md)** — Find deepening opportunities and grill the selected refactor.
- **[setup-matt-pocock-skills](./skills/engineering/setup-matt-pocock-skills/SKILL.md)** — Configure issue tracking, domain docs, and agent instructions once per repository.
- **[to-spec](./skills/engineering/to-spec/SKILL.md)** — Synthesize the current conversation into a buildable spec.
- **[to-tickets](./skills/engineering/to-tickets/SKILL.md)** — Split work into tracer-bullet tickets with blocking edges.
- **[implement](./skills/engineering/implement/SKILL.md)** — Implement a spec or ticket with test-first seams and closing review.
- **[wayfinder](./skills/engineering/wayfinder/SKILL.md)** — Map a large, foggy effort as decision tickets until the route is clear.

#### Model-invoked

- **[prototype](./skills/engineering/prototype/SKILL.md)** — Build throwaway evidence for one design question.
- **[diagnosing-bugs](./skills/engineering/diagnosing-bugs/SKILL.md)** — Diagnose hard bugs and regressions through a tight feedback loop.
- **[research](./skills/engineering/research/SKILL.md)** — Produce a cited primary-source research report, delegated when available.
- **[tdd](./skills/engineering/tdd/SKILL.md)** — Run red-green-refactor one vertical slice at a time.
- **[domain-modeling](./skills/engineering/domain-modeling/SKILL.md)** — Sharpen domain terms, scenarios, glossary, and ADRs.
- **[codebase-design](./skills/engineering/codebase-design/SKILL.md)** — Design deep modules, interfaces, seams, and adapters.
- **[code-review](./skills/engineering/code-review/SKILL.md)** — Review Standards and Spec in isolated axes.
- **[resolving-merge-conflicts](./skills/engineering/resolving-merge-conflicts/SKILL.md)** — Resolve merge or rebase conflicts by intent.
- **[orchestrate-agents](./skills/engineering/orchestrate-agents/SKILL.md)** — Coordinate safe, bounded V1/V2 multi-agent work.

### Productivity

#### User-invoked

- **[grill-me](./skills/productivity/grill-me/SKILL.md)** — Relentlessly interview a plan or idea outside a codebase.
- **[handoff](./skills/productivity/handoff/SKILL.md)** — Route between Codex session transitions and clean-thread handoffs.
- **[teach](./skills/productivity/teach/SKILL.md)** — Build a stateful multi-session learning workspace.
- **[writing-great-skills](./skills/productivity/writing-great-skills/SKILL.md)** — Write predictable Codex skills with deliberate invocation and context load.

#### Model-invoked

- **[grilling](./skills/productivity/grilling/SKILL.md)** — Resolve a decision tree one question at a time.

## Attribution

The workflows and original skill set were created by Matt Pocock. This fork preserves that attribution while maintaining Codex-specific distribution and behavior under `manoelcalixto/mattpocock-skills`.
