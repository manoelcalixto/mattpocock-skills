## What it does

`planning-context` gives multi-session work a durable source for material decisions. It keeps one per-effort Decision ledger, the coverage those decisions need, and the Git checkpoint that makes the plan safe for a fresh [session](https://www.aihero.dev/ai-coding-dictionary/session).

The ledger is concise and append-oriented: routine implementation choices stay out, while changed decisions become new entries that supersede old ones. A declared context is validated against its ledger, checkpoint trailer, branch ancestry, active decision IDs, and phase gate before a consumer proceeds.

It is the single owner used by `grill-with-docs`, `wayfinder`, `to-spec`, and `to-tickets`: producers receive stable IDs, specifications attach actionable consequences to every applicable active ID, and tickets carry only the IDs and consequences relevant to their own criteria. Canonical rationale stays in the ledger or its ADR pointer.

## When to reach for it

Type `/planning-context`, or the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) reaches for it automatically when a task needs a Planning context, a Decision ledger, a Git Planning checkpoint, setup migration, or consumer validation.

Reach for it when work crosses a session boundary or when a [spec](https://www.aihero.dev/ai-coding-dictionary/spec) or [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket) declares the `## Planning context` marker. Small work without that marker stays on its lightweight path.

| Situation | Use |
| --- | --- |
| Material choice must survive a fresh session | `planning-context` |
| The domain term or architectural rationale itself needs work | [domain-modeling](https://aihero.dev/skills-domain-modeling) |
| A complete specification or ticket already needs implementation | [implement](https://aihero.dev/skills-implement) |

## The ledger and checkpoint

The leading word is **checkpoint**. An intermediate checkpoint can leave future coverage pending. A final checkpoint requires applicable specification and ticket coverage, while implementation completion also requires verification evidence. The commit stages only named planning artifacts, writes a machine-readable trailer, and leaves unrelated worktree changes in place.

Coverage is separate from validity. A decision can be active while its specification or verification evidence is still pending. Once checkpointed, its decision and rationale keep their meaning; a changed choice receives a new ID and a new checkpoint, while coverage and evidence can be appended.

For a remote tracker, the `Repository` value in a marker is metadata for the reader, not a target-selection mechanism. Publishing skills read `docs/agents/issue-tracker.md` and pass its fully qualified `owner/repository` to every GitHub command. The final checkpoint is created only after the specification and all ticket or justified non-ticket coverage is recorded, then the parent and children receive fresh markers with its exact SHA.

## Prerequisites

The skill writes planning discovery and ledger files in the repository:

| It writes | Where |
| --- | --- |
| Planning discovery | `docs/agents/planning.md` |
| Decision ledger | `docs/planning/<effort>/decision-ledger.md` |
| Planning context marker | the selected specification or ticket, when requested |

## Common questions

**Does this replace `CONTEXT.md` or an ADR?**

No. `CONTEXT.md` remains the domain glossary, and an ADR remains canonical for an architectural decision. The ledger carries the downstream consequences and points back to an ADR when one owns the rationale.

**Will it reject older specifications and tickets?**

No. A file without a Planning context marker returns the legacy result. Fail-closed validation applies only after a specification or ticket opts into the marker.

**Can I update evidence after a checkpoint?**

Yes. Coverage and verification evidence are appendable. Editing a checkpointed decision meaning requires a superseding entry and a new checkpoint.

**How does Wayfinder reuse a decision that is already in the ledger?**

The resolver inspects active entries and calls `decision reference` for an existing answer, or `decision add` once for a new one. The resolved Decision ticket carries exactly one active ID. Its map entry stays a short pointer, while the ledger or its ADR keeps the canonical rationale. After a new entry's intermediate checkpoint, regenerate the map and ticket markers so they point to the same checkpoint and active ID.

**How does the grill-to-tickets path avoid losing decisions?**

`grill-with-docs` records each confirmed material choice once and exposes its ID in the round summary. `to-spec` accounts for every applicable active ID with a consequence, then `to-tickets` maps ticket obligations to one or more children or records a non-ticket justification. The final phase gate reports any pending coverage before implementation can begin.

**Why do external markers need a final refresh?**

The intermediate checkpoint makes the ledger resolvable while the spec and tickets are drafted. The final checkpoint adds their coverage evidence, so each external child is updated afterward with the final SHA and remains resolvable from a clone descended from that commit.

**What prevents a GitHub command from reaching upstream?**

The issue-tracker configuration supplies one explicit `owner/repository` target. Every `gh issue`, `gh pr`, and `gh api repos/...` operation must use it, including `gh issue edit <child> --repo owner/repository --body "<body with the regenerated marker>"`, regardless of the checkout's remotes or `gh` defaults.

## It's working if

- A first use creates `docs/agents/planning.md`, while rerunning it preserves an initialized file byte for byte.
- A ledger allocates `DEC-001`, `DEC-002`, and later IDs within one effort without sharing an allocator across efforts.
- A final checkpoint fails with a named missing obligation, then succeeds after the evidence is recorded.
- A resolved Wayfinder Decision ticket references or creates exactly one active ID, and that ID remains traceable through its spec, implementation ticket, and final checkpoint coverage.
- A Wayfinder map marker is refreshed after each resolution checkpoint and after the final coverage checkpoint.
- `git show -s --format=%B <checkpoint>` contains `Planning-Checkpoint`, and an unrelated worktree change remains outside that commit.
- A valid marker passes only on a branch descended from the exact checkpoint, a local artifact can resolve that checkpoint from its trailer, and a legacy file still returns `legacy`.
- The public [harness](https://www.aihero.dev/ai-coding-dictionary/harness) reports all scenarios passed from `npm run test:planning-context`.

## Where it fits

`planning-context` is the model-invoked contract beneath the planning and implementation flows. [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) initializes its discovery, [grill-with-docs](https://aihero.dev/skills-grill-with-docs) and [wayfinder](https://aihero.dev/skills-wayfinder) produce decisions for it, and [implement](https://aihero.dev/skills-implement) consumes its checkpoint. [ask-matt](https://aihero.dev/skills-ask-matt) routes the whole set and explains when this cross-session seam is needed.
