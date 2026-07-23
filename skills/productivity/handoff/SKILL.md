---
name: handoff
description: Route a Codex conversation to compact, fork, side thread, resume, clean-thread handoff, or immediate delegated continuation.
---

# Handoff

Choose the smallest Codex-native transition that preserves the context the user actually needs. Infer the destination from the user's request and current conversation; ask only when two materially different routes remain plausible.

When that ambiguity becomes a **Decision prompt**, apply the [Codex-native user-input contract](../../../.agents/request-user-input.md).

## Routes

- **Same thread, less context** — tell the user to run `/compact`. Do not create a file.
- **Branch with full history** — tell the user to run `/fork`. Do not create a file.
- **Quick tangent** — tell the user to run `/side`. Do not create a file.
- **Resume a persisted thread** — tell the user to run `/resume`. Do not create a file.
- **Immediate continuation by another agent** — when `$delegate-handoff` is installed, tell the user to run it. This skill is human-only and cannot invoke another human-only skill itself. When it is unavailable, use the clean-thread artifact route instead.
- **Genuinely clean thread with curated context** — create the handoff artifact below, then tell the user to run `/new`.

Do not create a handoff document for routes that retain the required context natively.

## Clean-thread artifact

Resolve the operating system temporary directory (`$TMPDIR`, then `/tmp`; use the platform equivalent on Windows) and write a uniquely named Markdown file such as `codex-handoff-<timestamp>-<slug>.md`. Do not write it into the workspace.

Include:

- Goal and exact next action.
- Current state, decisions, constraints, and remaining unknowns.
- Suggested `$skills` for the next thread.
- References to existing specs, plans, ADRs, issues, commits, diffs, or files instead of duplicating them.
- Verification already run and any known failures.

Redact API keys, credentials, personal data, tokens, and unnecessary secrets. Treat any user argument as the intended focus of the next thread.

Return the absolute artifact path and these exact next steps:

1. Run `/new`.
2. Ask the new thread to read the handoff path.
3. Invoke the first suggested `$skill` when one is listed.
