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

Record a decision when changing it would alter behavior, constraints, scope, a contract, a test seam, or architecture. Keep routine implementation choices out. Give each entry the next `DEC-001` style ID within that effort, concise decision, context, and rationale fields, a validity status, and only the coverage obligations that apply. Coverage advances monotonically from pending to complete, and checkpointed evidence can remain unchanged or be extended without replacing prior values.

After a Planning checkpoint, keep decision and rationale meaning immutable. If a choice changes, append a new entry that supersedes the old one and create a new checkpoint. If implementation cannot honor an active entry, stop and return to planning for that supersession instead of recording a silent deviation.

Decision producers call this owner rather than writing a second ledger. `grill-with-docs` records each confirmed material choice once and reports the returned ID in its round summary. `wayfinder` records a resolved Decision ticket by referencing one active ID or creating exactly one new entry, then carries that ID in the ticket marker. `to-spec` accounts for every active applicable entry with an actionable consequence, and `to-tickets` maps every entry with a ticket obligation to one or more focused tickets. Neither downstream artifact copies the ledger's canonical rationale. Entries whose obligation is `none` or excludes a phase receive a recorded applicability or non-ticket justification instead of an artificial consequence or ticket.

For a Wayfinder resolution, inspect the effort ledger before writing. Run `decision reference` when the answer already has an active entry, or `decision add` once when it does not. If the answer is ADR-worthy, keep the rationale in the ADR and pass its path with `--adr`; the ledger and Decision ticket point to it. After a new entry's intermediate checkpoint, refresh both the map and resolved ticket markers to that SHA and active ID before handing off. The map remains an index with a linked ticket and short gist, not another rationale store.

## Cross the Git seam

Create an intermediate checkpoint while future specification or ticket coverage is still pending. Create a final checkpoint only after every active applicable entry is covered by the specification and tickets. Implementation completion also requires applicable verification evidence. Stage the configuration, ledger, and explicitly owned planning artifacts only; the checkpoint writes a machine-readable `Planning-Checkpoint` trailer and leaves unrelated worktree changes alone.

Before an active Planning context crosses into a fresh session, create the checkpoint for the next phase. This gate applies before `/compact`, `/handoff`, or `/clear`: use `intermediate` while planning continues, `final` before implementation, and `implementation` after verification. A markerless small task and work that stays in the current session remain on the lightweight path.

Before a fresh implementation session, validate the declared ledger, checkpoint trailer, branch ancestry, active decision IDs, and requested coverage. A valid consumer descends from the exact checkpoint commit. A declared but unresolved context fails with the failed invariant and its repair. A legacy input without a marker remains allowed.

Wayfinder may hand off to the build flow only after the final Planning checkpoint passes its applicable specification and ticket coverage gate. The intermediate checkpoint makes a resolved ticket durable; `to-spec` and `to-tickets` carry its ID through their shared contract before the final checkpoint authorizes a fresh build session.

The public validator accepts exactly one context input. Use `--context-file <path>` for a local specification or ticket, relative to the repository root. Use `--context-stdin` for the body already obtained from a configured remote tracker, such as a GitHub issue fetched with an explicit `--repo owner/repository`. The stdin path is read-only transport and does not materialize a tracker body or Planning artifact in the consumer repository.

Read the remote tracker body successfully before invoking the validator. A tracker read error fails the preflight before stdin transport, and it must never be converted into empty input or the `legacy` result.

When a specification or ticket is published to GitHub, generate its marker after the relevant checkpoint and use the configured repository target from `docs/agents/issue-tracker.md` for every external operation. An external marker must carry an exact 40-character hexadecimal checkpoint SHA, which is checked before any Git revision resolution. The `marker` command may accept a resolvable revision as input, but always emits the full SHA. The marker's ledger path and full checkpoint SHA must remain resolvable from a clone containing that checkpoint. Refresh external markers after the final checkpoint so consumers point at the final planning state.

For a completed ticket graph, the coordinator uses this owner to aggregate worker evidence. Workers write repeatable `Planning-Verification: DEC-NNN | <observable evidence>` trailers on their own commits and leave the shared ledger untouched. Evidence read from a ticket uses `--ticket-evidence "DEC-NNN | origin | observable evidence"`. After every relevant worker tip is merged and any required bounded review or fix batches are complete, run `coverage aggregate` with the validated final checkpoint, current integration head, applicable decision IDs, and each merged or final reviewed tip. The command proves checkpoint ancestry, proves every supplied tip is merged, rejects commits that edit the ledger, and validates the complete verification set in memory before one ledger write. A missing record fails without changing the ledger; a successful aggregation stores a deterministic JSON evidence array and can then be followed by an `implementation` checkpoint.

## Deterministic seam

Use `scripts/planning_context.py` for the file, stdin, and Git operations when a deterministic result matters. Its JSON `validate` result identifies the context source and, for a valid marker, returns the selected decisions with each declared obligation's `status` and `evidence`, plus proven `ancestry` containing the resolved `checkpoint_sha`, current `head_sha`, and `is_ancestor: true`. Read [the planning contract](references/planning-contract.md) before changing the format or adding a caller. Run `npm run test:planning-context` to exercise the public conformance harness in disposable Git repositories.
