Quickstart:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Start a new Codex thread and type `$orchestrate-agents`.

[Source](https://github.com/manoelcalixto/mattpocock-skills/tree/main/skills/engineering/orchestrate-agents)

## What it does

`orchestrate-agents` coordinates bounded delegated work across the two Codex multi-agent contracts. It detects the tools the current session exposes, chooses V1 or V2 semantics, isolates the child's context, and falls back to inline or sequential work when agents are unavailable.

Delegation must already be authorized by the user or active workflow. The skill never enables feature flags or turns an ordinary request into an agent tree by itself.

## When to reach for it

Type `$orchestrate-agents`, or the agent reaches for it automatically when an authorized workflow needs parallel reviews, alternative designs, background research, or another independent subtask.

Reach for it when the work can be divided into bounded pieces that make progress alongside the root agent. Keep tightly coupled work inline.

## Isolated briefs

The leading idea is **isolation**. V2 agents default to `fork_turns="none"`; V1 agents default to `fork_context=false`. Each worker receives a self-contained goal, constraints, allowed files, output contract, and completion criteria rather than an inherited transcript.

The working directory is still shared. Concurrent agents receive disjoint write sets or read-only tasks, while the root owns branches, commits, tracker mutations, and shared indexes.

## Adaptive capacity

V2 normally leaves room for three children beside the root; V1 can expose more. These are ceilings rather than promises: the workflow honors real slots, batches overflow, reuses workers, and degrades sequentially after a spawn failure.

## It's working if

- V1 and V2 receive equivalent self-contained briefs through their native parameters.
- The root keeps doing useful work and waits only when a result becomes blocking.
- No two agents modify the same file, branch, commit, or tracker index concurrently.
- Missing tools change latency, not the required output.

## Where it fits

`orchestrate-agents` is a model-invoked shared primitive used by [code-review](https://aihero.dev/skills-code-review), [codebase-design](https://aihero.dev/skills-codebase-design), [research](https://aihero.dev/skills-research), [wayfinder](https://aihero.dev/skills-wayfinder), and architecture maintenance. [ask-matt](https://aihero.dev/skills-ask-matt) maps the wider workflow set.
