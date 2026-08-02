# Matt Pocock's Skills for Codex

A Codex-focused distribution of [Matt Pocock's engineering and productivity skills](https://github.com/mattpocock/skills), maintained in the [`manoelcalixto` fork](https://github.com/manoelcalixto/mattpocock-skills).

The set turns recurring agent work into named workflows: grill an idea, capture a spec, split it into tracer-bullet tickets, implement test-first, review against both standards and intent, and preserve the domain language that keeps later tasks coherent.

## Install

Choose one installation model. Installing both gives Codex duplicate copies of the same skills.

### Native Codex plugin

Use the managed plugin when you want all 22 promoted skills to update together:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

The plugin is Codex-only and installs from the `manoelcalixto` marketplace.

### Editable skills

Use [`skills`](https://github.com/vercel-labs/skills) when you want local copies you can change:

```bash
npx skills add manoelcalixto/mattpocock-skills
```

Select Codex and the skills you want when prompted. The installer discovers the promoted `engineering` and `productivity` categories; material under `workbench/` is intentionally excluded.

After either installation, run `$setup-matt-pocock-skills` once in each engineering repository. It records the issue tracker, triage labels, and domain-document layout in `AGENTS.md` and `docs/agents/`.

## Use

Type `$ask-matt` when you know the situation but not the workflow. Every promoted skill can be invoked explicitly with Codex's `$skill-name` syntax or selected automatically when its trigger matches.

The main build flow is:

```text
$grill-with-docs → $to-spec → $to-tickets → $implement → $code-review
```

Use `$grill-me` for a stateless interview outside a repository, `$triage` for incoming work you did not author, and `$wayfinder` when the route is too large or foggy for one Codex task.

## Engineering skills

### Workflow entry points

- [ask-matt](docs/engineering/ask-matt.md) — route a situation to the right skill or flow.
- [grill-with-docs](docs/engineering/grill-with-docs.md) — stress-test an idea while updating `CONTEXT.md` and ADRs.
- [implement](docs/engineering/implement.md) — build a spec or ticket set through `$tdd`, then run `$code-review` and commit.
- [improve-codebase-architecture](docs/engineering/improve-codebase-architecture.md) — find deepening opportunities and explore one with the user.
- [setup-matt-pocock-skills](docs/engineering/setup-matt-pocock-skills.md) — configure the repository conventions used by the engineering workflows.
- [to-spec](docs/engineering/to-spec.md) — synthesize the current conversation into a spec.
- [to-tickets](docs/engineering/to-tickets.md) — split a plan into tracer-bullet tickets with blocking edges.
- [triage](docs/engineering/triage.md) — classify and verify incoming issues or external pull requests.
- [wayfinder](docs/engineering/wayfinder.md) — map a large, foggy effort as decision tickets.

### Reusable disciplines

- [code-review](docs/engineering/code-review.md) — review a diff independently against repository standards and its originating spec.
- [codebase-design](docs/engineering/codebase-design.md) — design deep modules with small interfaces and clean seams.
- [diagnosing-bugs](docs/engineering/diagnosing-bugs.md) — reproduce, minimize, hypothesize, instrument, fix, and regression-test.
- [domain-modeling](docs/engineering/domain-modeling.md) — sharpen domain language and record durable decisions.
- [prototype](docs/engineering/prototype.md) — build a throwaway artifact that answers a design question.
- [research](docs/engineering/research.md) — investigate primary sources and save cited findings.
- [resolving-merge-conflicts](docs/engineering/resolving-merge-conflicts.md) — resolve merge or rebase conflicts by tracing intent.
- [tdd](docs/engineering/tdd.md) — build one vertical slice at a time through red-green-refactor.

## Productivity skills

### Workflow entry points

- [grill-me](docs/productivity/grill-me.md) — stress-test any plan one decision at a time.
- [handoff](docs/productivity/handoff.md) — capture a conversation for a fresh Codex task.
- [teach](docs/productivity/teach.md) — teach through a stateful learning workspace.
- [writing-great-skills](docs/productivity/writing-great-skills.md) — design predictable, concise Agent Skills.

### Reusable discipline

- [grilling](docs/productivity/grilling.md) — the relentless one-question-at-a-time interview loop used by the grilling workflows.

## Repository scope

Only `skills/engineering/` and `skills/productivity/` ship through the plugin and editable installer. Deprecated, experimental, miscellaneous, and personal material is preserved under [`workbench/`](workbench/README.md), outside recursive product discovery.

The repository root is the Codex plugin. See [AGENTS.md](AGENTS.md) for the authoring contract and [ADR-0003](docs/adr/0003-ship-codex-focused-fork-as-a-root-plugin.md) for the migration decision.

## Attribution

The workflows and Matt Pocock brand originate with [Matt Pocock](https://www.aihero.dev). This fork packages and maintains them for Codex under the original MIT license; fork-specific installation and source links point to [`manoelcalixto/mattpocock-skills`](https://github.com/manoelcalixto/mattpocock-skills).
