---
name: planning-context
description: "Own a versioned Planning context for multi-session work. Use when a plan needs a per-effort Decision ledger, a Git Planning checkpoint, phase-aware coverage, consumer validation, or setup and lazy migration across sessions."
---

# Planning context

Use this skill as the single owner of the Planning context contract. It keeps material decisions, their downstream coverage, and the Git commit that makes them durable together. A Planning context is active when a specification or ticket carries the `## Planning context` marker; an input without that marker follows its legacy workflow.

## Start with the context

1. Read `docs/agents/planning.md` when it exists. If this is the first use in a repository, initialize the default configuration and preserve any existing file content.
2. Resolve the per-effort Decision ledger at `docs/planning/<effort>/decision-ledger.md`. Read the ledger before proposing an entry or changing coverage.
3. Read `CONTEXT.md` and applicable ADRs for vocabulary and canonical architectural decisions. The ledger points to an ADR when an ADR owns the rationale; it does not replace either document.

## Own the ledger

Record a decision when changing it would alter behavior, constraints, scope, a contract, a test seam, or architecture. Keep routine implementation choices out. Give each entry the next `DEC-001` style ID within that effort, concise decision, context, and rationale fields, a validity status, and only the coverage obligations that apply. Coverage and verification evidence can be appended.

After a Planning checkpoint, keep decision and rationale meaning immutable. If a choice changes, append a new entry that supersedes the old one and create a new checkpoint. If implementation cannot honor an active entry, stop and return to planning for that supersession instead of recording a silent deviation.

## Cross the Git seam

Create an intermediate checkpoint while future specification or ticket coverage is still pending. Create a final checkpoint only after every active applicable entry is covered by the specification and tickets. Implementation completion also requires applicable verification evidence. Stage the configuration, ledger, and explicitly owned planning artifacts only; the checkpoint writes a machine-readable `Planning-Checkpoint` trailer and leaves unrelated worktree changes alone.

Before a fresh implementation session, validate the declared ledger, checkpoint trailer, branch ancestry, active decision IDs, and requested coverage. A valid consumer descends from the exact checkpoint commit. A declared but unresolved context fails with the failed invariant and its repair. A legacy input without a marker remains allowed.

## Deterministic seam

Use `scripts/planning_context.py` for the file and Git operations when a deterministic result matters. Read [the planning contract](references/planning-contract.md) before changing the format or adding a caller. Run `npm run test:planning-context` to exercise the public conformance harness in disposable Git repositories.
