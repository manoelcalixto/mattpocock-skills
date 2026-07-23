Quickstart:

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Start a new Codex thread and type `$mattpocock-skills:handoff`.

[Source](https://github.com/manoelcalixto/mattpocock-skills/tree/main/skills/productivity/handoff)

## What it does

`handoff` routes a conversation to the Codex transition that preserves exactly the needed context. Most routes use native commands and create no artifact; only a genuinely blank thread receives a curated, redacted Markdown handoff.

It does not treat every context change as a document-writing problem.

## When to reach for it

You invoke this by typing `$mattpocock-skills:handoff` — the agent won't reach for it on its own.

Reach for it when you know the current thread should change shape but are unsure whether you need compaction, a full-history fork, a tangent, a resumed thread, a blank thread, or another agent. When two routes remain genuinely plausible, that bounded choice appears as a native Codex prompt when available.

## Transition map

- `/compact` stays in the same thread with a summarized past.
- `/fork` creates a branch with full conversation history.
- `/side` opens a quick tangent.
- `/resume` reopens persisted work.
- `$delegate-handoff`, when installed, transfers work immediately to a fresh subagent. When it is unavailable, use the clean-thread route.
- `/new` starts clean; this is the only route that receives a temporary handoff artifact.

## The clean-thread artifact

The artifact carries live decisions, constraints, remaining work, suggested `$skills`, verification, and references to existing sources. It lives in the operating system temporary directory and strips credentials, tokens, personal data, and duplicated content.

## It's working if

- `/compact`, `/fork`, `/side`, and `/resume` produce no file.
- A clean-thread handoff returns an absolute temporary path and exact `/new` instructions.
- Existing specs, issues, ADRs, commits, and diffs are referenced rather than copied.

## Where it fits

`handoff` is a reach-for-it-anytime session router. It complements [ask-matt](https://aihero.dev/skills-ask-matt), which routes between workflows, and [to-spec](https://aihero.dev/skills-to-spec), whose durable artifacts a handoff references instead of repeating.
