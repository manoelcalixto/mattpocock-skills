Quickstart:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Start a new Codex thread and type `$mattpocock-skills:orchestrate-agents`.

[Source](https://github.com/manoelcalixto/mattpocock-skills/tree/main/skills/engineering/orchestrate-agents)

## What it does

`orchestrate-agents` coordinates bounded Codex MultiAgent V2 work on GPT-5.6 Sol. It gives every worker an isolated brief, an explicit task-shaped reasoning effort, and a safe place in the shared filesystem and agent tree.

Delegation must already be authorized by the user or active workflow. The skill never enables feature flags, restores the legacy agent contract, selects a cheaper model tier, or turns an ordinary request into an agent tree by itself.

## When to reach for it

Type `$mattpocock-skills:orchestrate-agents`, or the agent reaches for it automatically when an authorized workflow needs parallel reviews, alternative designs, background research, or another independent subtask.

Reach for it when the work can be divided into bounded pieces that make progress alongside the root agent. Keep tightly coupled work inline.

## Prerequisites

The root must already run `gpt-5.6-sol`, and Codex must expose the flat MultiAgent V2 tools. If V2 is unavailable, eligible workflows fall back inline or sequentially and disclose lost isolation or parallelism; they never retry through V1.

## Why one model and one contract

V2-only coordination removes a compatibility branch that otherwise makes isolation, messaging, waiting, and lifecycle behavior differ between workers. Pinning every worker to GPT-5.6 Sol provides one capability baseline; varying reasoning effort by task shape preserves a deliberate quality, latency, and cost trade-off without changing models. `ultra` stays outside spawned workers because it would add automatic delegation on top of the workflow-controlled tree.

This follows OpenAI's guidance to begin with lower effort and raise it only when the workload benefits, reserving max for the hardest quality-first work. OpenAI also describes ultra as multi-agent coordination rather than a simple reasoning increment. See the [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6), the [GPT-5.6 launch](https://openai.com/index/gpt-5-6/), and Codex's [Sol model preset](https://github.com/openai/codex/blob/main/codex-rs/models-manager/models.json).

## Isolation and control

The leading idea is **isolation**: each worker receives only the context and authority its task needs, so parallel work does not inherit an unrelated transcript or silently expand its scope. The filesystem remains shared, which is why concurrent work needs disjoint write ownership and why the root owns shared integration points.

Recursive delegation is a workflow decision, not a capability that activates itself. When a workflow authorizes a tree, finite shared capacity shapes that tree and each child remains responsible for integrating its own descendants. Coordination is event-driven, so the root can continue useful work until a message or result actually becomes blocking rather than monitoring agents for progress.

## It's working if

- Every worker uses Sol and an intentional task-shaped effort.
- The root keeps doing useful work and waits only when a result becomes blocking.
- No two agents modify the same file, branch, commit, or tracker index concurrently.
- Missing V2 tools change latency, not the required output, unless isolation is indispensable to the workflow's semantics.

## Where it fits

`orchestrate-agents` is the V2-only shared primitive used by [code-review](https://aihero.dev/skills-code-review), [codebase-design](https://aihero.dev/skills-codebase-design), [research](https://aihero.dev/skills-research), [wayfinder](https://aihero.dev/skills-wayfinder), and architecture maintenance. [ask-matt](https://aihero.dev/skills-ask-matt) maps the wider workflow set.
