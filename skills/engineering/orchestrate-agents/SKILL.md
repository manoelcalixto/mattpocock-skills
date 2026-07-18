---
name: orchestrate-agents
description: Coordinate bounded multi-agent work across Codex V1 and V2 while protecting shared files and context isolation. Use when the user or an active skill explicitly asks for delegation, subagents, parallel agents, background research, or multiple independent review/design passes.
---

# Orchestrate Agents

Delegate only when the user or the active skill explicitly authorizes delegation or parallel agent work. Do not enable feature flags, edit Codex configuration, or invent unavailable tools. Adapt to the multi-agent contract exposed in the current session.

## Decide whether to delegate

Delegate a concrete, bounded subtask only when it can run independently alongside useful root-agent work. Keep dependent work on the root critical path. If the task is too small, tightly coupled, or likely to touch the same files, run it inline.

Treat the filesystem and working directory as shared:

- Give concurrent agents disjoint write sets, or make their tasks read-only.
- Give every agent a unique output path.
- Keep branch switching, rebases, commits, staging, and tracker/map index edits on the root agent.
- Tell children not to spawn more agents unless the user explicitly authorized recursive delegation.
- Never assume a separate worktree or branch exists.

## Detect the contract

Use **V2** when `spawn_agent` exposes `task_name` or `fork_turns`, together with flat collaboration tools such as `send_message`, `followup_task`, `interrupt_agent`, `list_agents`, and mailbox-style `wait_agent`.

Use **V1** when `spawn_agent` exposes `fork_context`, together with `send_input`, targeted `wait_agent`, `resume_agent`, and `close_agent`.

If no multi-agent tools are available or a spawn fails, run the work inline or sequentially and disclose the fallback when it changes isolation or latency.

## Isolate context by default

Write a self-contained brief containing the goal, allowed files/systems, constraints, expected output, and completion criteria.

- V2: default to `fork_turns="none"`. Use full history only when the subtask cannot be briefed safely without it.
- V1: default to `fork_context=false`. Enable inherited context only for the same exceptional case.
- Do not override model or reasoning effort unless the user explicitly requests it.

Use stable V2 task names in lower-case snake_case. Address later messages by that task name or the canonical path returned by `spawn_agent`.

## Schedule within capacity

- V2 normally allows four active agents including the root: start no more than three children at once.
- V1 normally allows up to six children.
- Treat these as ceilings, not guarantees. Honor the actual available slots and spawn errors.
- Batch excess work and reuse an idle agent with follow-up work instead of growing an unbounded tree.

Start independent calls together when the tool surface permits it. Continue useful root work while children run. Wait only when the root is blocked on their results.

## Coordinate V2

1. Spawn each isolated subtask with a descriptive `task_name` and the smallest useful `fork_turns` value.
2. Use `send_message` for context that does not require a new turn.
3. Use `followup_task` to give a completed or idle agent another bounded task.
4. Use `list_agents` to inspect the live tree and `interrupt_agent` only when work must stop or change direction.
5. Use mailbox `wait_agent` only when blocked. Read the delivered agent messages/final results, then integrate them on the root.

V2 agents remain addressable after completion; reuse them when continuity helps.

## Coordinate V1

1. Spawn each task with `fork_context=false` unless inheritance is essential.
2. Use `send_input` for follow-up guidance.
3. Wait on the specific agent IDs whose results block the root.
4. Resume a stopped agent only when more work belongs to the same brief.
5. Close completed agents after collecting their output so slots are released.

## Integrate

Treat agent output as evidence, not authority. Verify claims against the repository or source material, reconcile conflicts explicitly, and let the root agent own final edits, tracker mutations, commits, and the user-facing answer unless the delegated write set was explicitly isolated.
