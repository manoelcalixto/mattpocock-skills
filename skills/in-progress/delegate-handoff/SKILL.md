---
name: delegate-handoff
description: Hand the current Codex conversation to a fresh subagent that continues immediately with curated, isolated context.
---

# Delegate Handoff

Hand the work to a fresh agent and stop doing duplicate work on the parent.

## Build the brief

Create a self-contained, redacted summary containing:

- Goal and exact next action.
- Current state, decisions, constraints, and remaining unknowns.
- Suggested `$skills`.
- References to existing specs, plans, ADRs, issues, commits, diffs, and files instead of copied content.
- Verification already run and known failures.

Treat any user argument as the next agent's focus. Remove credentials, tokens, personal data, and irrelevant sensitive information.

## Start the fresh agent

Use the `orchestrate-agents` skill and prefer an isolated context:

- V2: spawn a descriptive lower-case snake_case task with `fork_turns="none"` and the brief as the complete task.
- V1: spawn with `fork_context=false` and the brief as the complete task.

Do not override model or reasoning effort unless the user asked. Do not continue implementing the same task on the parent after a successful spawn.

Return the spawned task name or agent ID and tell the user that `/agent` switches to the active agent.

## Fallback

If no multi-agent tools are available, write the same sanitized brief to a uniquely named Markdown file in the operating system temporary directory. Return its absolute path and tell the user to run `/new`, ask the new thread to read the file, and invoke the first suggested `$skill`.
