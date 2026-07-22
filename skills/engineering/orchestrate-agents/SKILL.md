---
name: orchestrate-agents
description: Coordinate bounded Codex MultiAgent V2 work with GPT-5.6 Sol, task-shaped reasoning effort, recursive workflow authorization, event-driven waiting, and shared-filesystem safety. Use when the user or an active skill explicitly asks for delegation, subagents, parallel agents, background research, or multiple independent review/design passes.
---

# Orchestrate Agents

Use only Codex MultiAgent V2: `spawn_agent`, `send_message`, `followup_task`, `interrupt_agent`, `list_agents`, and mailbox-style `wait_agent`. Never use or fall back to V1 tools.

Delegate only when the user or the active skill explicitly authorizes delegation or parallel agent work. Do not enable feature flags, edit Codex configuration, or invent unavailable tools. The root must already be running `gpt-5.6-sol`; otherwise ask the user to switch before orchestrating.

## Decide whether to delegate

Delegate a concrete, bounded subtask only when it can run independently alongside useful root-agent work. Keep dependent work on the root critical path. If the task is too small, tightly coupled, or likely to touch the same files, run it inline.

Treat the filesystem and working directory as shared:

- Give concurrent agents disjoint write sets, or make their tasks read-only.
- Give every agent a unique output path.
- Keep branch switching, rebases, commits, staging, and tracker/map index edits on the root agent.
- Never assume a separate worktree or branch exists.

## Isolate context

Write a self-contained brief containing the goal, allowed files and systems, constraints, expected output, completion criteria, recursive-delegation permission, and starting effort.

- Pass `fork_turns="none"` by default.
- Use a positive integer only when recent conversation turns are essential and duplicating them safely in the brief is impractical.
- Never omit `fork_turns` and never pass `"all"`; full-history forks cannot enforce the mandatory model and effort overrides.
- Use stable lower-case snake-case task names. Address later messages by the relative name or canonical path returned by `spawn_agent`.

## Fix the model and choose effort

Every `spawn_agent` call must set `model="gpt-5.6-sol"` and an explicit `reasoning_effort`. Never select Terra, Luna, or `ultra`.

Choose the smallest effort justified by task shape:

- `low` — deterministic or mechanical work: inventory, local lookup, test execution, formatting, exact docs synchronization, or a fully specified small edit.
- `medium` — bounded everyday judgment: ordinary implementation, focused primary-source research, verification, or synthesis of convergent evidence.
- `high` — complex multi-constraint reasoning: code review, diagnosis, architecture scanning, cross-file implementation, or research with several constraints.
- `xhigh` — competing designs, conflicting evidence, an ambiguous seam, or analysis with high consequences.
- `max` — exceptional quality-first work with high consequences and little tolerance for a weak result. Never make it a workflow-wide default.

Stable workflow starting points are `medium` for `research` and `wayfinder` research, and `high` for `code-review`, `architecture_scan`, and Design It Twice. Adjust from those points when the concrete task shape warrants it.

Treat the root's effort as guidance rather than a gate: use `medium` for routine orchestration, `high` for integrating several results, `xhigh` for conflicting designs, and `max` only for exceptional critical synthesis.

If output is weak because context or the brief was incomplete, correct it with `send_message` or `followup_task` at the existing effort. If reasoning depth is the actual failure, replace the worker at exactly one higher effort; do not run duplicate attempts concurrently. Reuse an agent only when continuity helps and the next activity needs the same effort. At `max`, narrow or integrate the task instead of escalating again.

## Schedule the tree

- Treat four active agents including the root as the normal capacity ceiling, while honoring the actual slots and spawn errors.
- Start no more than three direct children, and start fewer when an authorized child needs room for descendants.
- Recursive delegation is opt-in per task. The user or active workflow must authorize it, and the parent brief must state its conditions; having `spawn_agent` does not authorize recursion by itself.
- The child that spawns descendants owns their coordination and integrates their results before reporting upward.
- Capacity, not an artificial depth limit, bounds an authorized tree.
- Batch excess independent work. Do not retry spawns in a loop.

Start independent spawns together when the tool surface permits it, then continue meaningful non-overlapping root work.

## Coordinate without polling

- Use `send_message` to add context without triggering a new turn.
- Use `followup_task` for another bounded activity only when the same agent context and effort remain appropriate.
- Use `interrupt_agent` only when work must stop or change direction.
- Use `list_agents` for a necessary one-time tree or capacity snapshot, never for status polling.
- Call mailbox `wait_agent` only when the next root step is blocked. Use the longest permitted event-driven wait; it wakes for agent messages, final-status notifications, or steered user input. Read the delivered mailbox content, which arrives separately from the wait summary.
- Never use `sleep`, short-timeout wait loops, repeated `list_agents`, or any other polling pattern. After an exceptional timeout, resume useful work and re-enter a long wait only if still genuinely blocked.

Agents remain addressable after completion, but continuity alone does not justify reusing one at the wrong effort.

## Fall back without changing the contract

If MultiAgent V2 is unavailable or a spawn fails, run the work inline or sequentially when the required result can be preserved. Disclose lost isolation or parallelism, do not retry through V1, and do not switch away from Sol. If isolated agents are indispensable to the workflow's semantics, stop and explain the blocker.

## Integrate

Treat agent output as evidence, not authority. Verify claims against the repository or source material, reconcile conflicts explicitly, and let the root agent own final edits, tracker mutations, commits, and the user-facing answer unless the delegated write set was explicitly isolated.
