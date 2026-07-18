---
name: ask-matt
description: Ask which Codex skill, session transition, or workflow fits your situation.
---

# Ask Matt

Route the user to the smallest workflow that fits. Recommend the next action explicitly, using `$mattpocock-skills:skill-name` for promoted plugin skills, standalone `$skill-name` for locally installed non-promoted skills, and `/command` only for Codex built-ins.

## Main engineering flow

1. Start with `$mattpocock-skills:grill-with-docs` when an idea belongs to a codebase. It uses `grilling` while `domain-modeling` maintains `CONTEXT.md` and ADRs. Without a codebase, use `$mattpocock-skills:grill-me`.
2. If a design question needs runnable evidence, use `prototype`, then return the result to the original flow. A prototype answers one question; it is not the production implementation.
3. When the decisions fit in one thread, run `$mattpocock-skills:to-spec`, then `$mattpocock-skills:to-tickets` when the work needs independent tracer-bullet slices. Keep the grilling/spec/ticket reasoning in one thread unless the smart zone is running out.
4. Start each ticket in `/new`, then run `$mattpocock-skills:implement <ticket>`. `implement` uses `tdd` for red-green slices and `code-review` for the closing Standards/Spec review.
5. Run `code-review` independently whenever a branch or PR needs review against a fixed point. Use `resolving-merge-conflicts` for an in-progress merge or rebase.

If the work is genuinely small, skip tickets and run `$mattpocock-skills:implement` in the current thread after the plan is clear.

## Other on-ramps

- **A hard bug or performance regression** — `diagnosing-bugs`: establish a tight failing loop, minimise, instrument, fix, and regression-test.
- **Incoming bugs, requests, or external PRs** — `$mattpocock-skills:triage`: move raw requests through the configured tracker states. Tickets created by `$mattpocock-skills:to-tickets` are already agent-ready and should not be triaged.
- **A huge effort whose route cannot fit one session** — `$mattpocock-skills:wayfinder`: chart decision tickets and resolve the frontier until the route is clear. Then return through `$mattpocock-skills:to-spec`; do not jump straight to implementation unless the effort collapsed into something small.
- **Architecture entropy** — `$mattpocock-skills:improve-codebase-architecture`: scan active hotspots for deepening opportunities and grill the chosen candidate. Use `codebase-design` for interface/seam vocabulary and alternative designs.
- **External facts or documentation** — `research`: produce a cited primary-source report while other work continues when agents are available.
- **Learning rather than building** — `$mattpocock-skills:teach`: use the directory as a multi-session teaching workspace.
- **Writing or editing a skill** — `$mattpocock-skills:writing-great-skills`: use the repo's predictability vocabulary and Codex skill contract.
- **Block destructive Git commands in Codex** — when the standalone `$codex-git-guardrails` skill is installed, use it to configure a trusted `PreToolUse` hook before risky repository work.

## Session transitions

- `/compact` — stay in the same thread with a summarized past.
- `/fork` — branch into a new thread with the full conversation history.
- `/side` — open a short tangent without disturbing the main line.
- `/resume` — reopen a persisted thread.
- `$mattpocock-skills:handoff` — cross into a genuinely blank `/new` thread with a curated, redacted Markdown artifact.
- `$delegate-handoff` — when that in-progress skill is installed, transfer the work immediately to a fresh subagent; use `/agent` to switch to it.

Use `$mattpocock-skills:handoff` only when native context-preserving transitions are insufficient. Do not create handoff files for `/compact`, `/fork`, `/side`, or `/resume`.

## Shared primitives

- `grilling` — one-question-at-a-time interview discipline behind both grill workflows.
- `domain-modeling` — active glossary and ADR maintenance.
- `tdd` — test-first red-green-refactor discipline.
- `codebase-design` — deep-module, interface, seam, leverage, and locality vocabulary.
- `orchestrate-agents` — adaptive V1/V2 delegation when the user or active skill authorizes agents.

## Prerequisite

Ask the user to run `$mattpocock-skills:setup-matt-pocock-skills` once per repository before an engineering flow needs issue-tracker, triage-label, or domain-doc configuration.
