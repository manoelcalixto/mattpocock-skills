## What it does

`planning-context` gives multi-session work a durable source for material decisions. It keeps one per-effort Decision ledger, the coverage those decisions need, and the Git checkpoint that makes the plan safe for a fresh [session](https://www.aihero.dev/ai-coding-dictionary/session).

The ledger is concise and append-oriented: routine implementation choices stay out, while changed decisions become new entries that supersede old ones. Coverage advances from pending to complete, and checkpointed evidence can only stay unchanged or be extended while preserving its prior values. A declared context is validated against its ledger, checkpoint trailer, branch ancestry, active decision IDs, and phase gate before a consumer proceeds. The public validator accepts a local artifact through `--context-file` or an already-obtained remote tracker body through `--context-stdin`, so remote content does not need to become a repository file.

For a valid marker, JSON output names the input source and exposes the selected decisions' declared coverage as `status` and `evidence`. It also proves ancestry with the resolved checkpoint SHA, current `HEAD` SHA, and `is_ancestor: true`. A local marker reports its repository-relative context and `source: marker`; stdin reports `context: <stdin>` and `source: stdin`.

It is the single owner used by `grill-with-docs`, `wayfinder`, `to-spec`, and `to-tickets`: producers receive stable IDs, specifications attach actionable consequences to every applicable active ID, and tickets carry only the IDs and consequences relevant to their own criteria. Canonical rationale stays in the ledger or its ADR pointer.

## When to reach for it

Type `/planning-context`, or the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) reaches for it automatically when a task needs a Planning context, a Decision ledger, a Git Planning checkpoint, setup migration, or consumer validation.

Reach for it when work crosses a session boundary or when a [spec](https://www.aihero.dev/ai-coding-dictionary/spec) or [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket) declares the `## Planning context` marker. Small work without that marker stays on its lightweight path.

| Situation | Use |
| --- | --- |
| Material choice must survive a fresh session | `planning-context` |
| The domain term or architectural rationale itself needs work | [domain-modeling](https://aihero.dev/skills-domain-modeling) |
| A complete specification or ticket already needs implementation | [implement](https://aihero.dev/skills-implement) |

## Prerequisites

The skill writes planning discovery and ledger files in the repository:

| It writes | Where |
| --- | --- |
| Planning discovery | `docs/agents/planning.md` |
| Decision ledger | `docs/planning/<effort>/decision-ledger.md` |
| Planning context marker | the selected specification or ticket, when requested |

## The ledger and checkpoint

The leading word is **checkpoint**. An intermediate checkpoint can leave future coverage pending. A final checkpoint requires applicable specification and ticket coverage, while implementation completion also requires verification evidence when declared. A decision with `Obligations: none` must carry complete, non-empty `applicability` evidence explaining `non-ticket: ...` or `not-applicable: ...`. The checkpoint command rejects an in-progress merge or repository-wide unresolved index conflicts before mutation, handles staged extra deletions and renames, rejects duplicate or unidentifiable extra paths even when listed extras are unchanged, and rejects extra-only owned diffs before staging. It validates that the committed configuration resolves the declared ledger, writes machine-readable trailers including the exact `Planning-Paths` ownership list, and leaves unrelated worktree changes in place.

Before `/compact`, `/handoff`, or `/clear`, a `Subagent`, or any other fresh context crosses an active Planning context, create the checkpoint for the next phase. Parallel subagents may reuse the same exact checkpoint when Planning artifacts are unchanged. If a subagent changes those artifacts before another fresh context, checkpoint again. The lightweight path remains available for markerless small work and for work that stays in the current session.

Coverage is separate from validity. A decision can be active while its specification or verification evidence is still pending. Once checkpointed, its decision and rationale keep their meaning, complete coverage cannot regress, and existing evidence cannot be removed or replaced. A changed choice receives a new ID and a new checkpoint, while pending coverage may complete and evidence may be appended in order. An `Obligations: none` entry accepts applicability evidence only when it starts with `non-ticket:` or `not-applicable:`; the parser applies this rule when it reads the ledger as well as when coverage is added.

`coverage add` treats the `none` sentinel case-insensitively. Before writing, it validates the complete proposed ledger, including the updated coverage and evidence lines. A validation failure leaves the ledger, configuration, Git index, and history unchanged.

For a whole ticket graph, verification aggregation has two modes while the shared ledger remains unchanged. In commit mode, implementers put observable evidence on their own commits with repeatable `Planning-Verification: DEC-NNN | <observable evidence>` trailers, and the coordinator supplies each merged worker or final reviewed tip. In ticket-evidence mode, the coordinator passes an already-read `--ticket-evidence "DEC-NNN | origin | observable evidence"` record and omits `--commit`. Both modes require at least one non-empty record when the selected set contains a decision that declares verification, and validate the final checkpoint, current integration head, applicable decision IDs, and complete verification set before one ledger write. Aggregation also rejects staged changes to the planning configuration or declared ledger before reading or writing worktree evidence. Selected decisions without a verification obligation are filtered from that set and do not require a record; any verification record naming one is rejected. Ticket-only mode remains valid, while the runtime gate fails closed when a selected verification decision has no evidence. Supplied commit tips additionally prove the common checkpoint ancestry and merged state, reject commits that edit the ledger, and are read only from the final Git trailer block. Empty JSON arrays or blank list values are rejected. Evidence is retained in a compact JSON array, so repeated aggregation stays idempotent even when an observation contains `; `. Missing applicable evidence leaves the ledger untouched, so the implementation checkpoint cannot pass early. An implementation checkpoint may pass `--decisions DEC-001,DEC-002` for an explicit subset; omitting that option keeps the default all-active applicable gate.

For a remote tracker, the `Repository` value in a marker is metadata for the reader, not a target-selection mechanism. Publishing skills read `docs/agents/issue-tracker.md` and pass its fully qualified `owner/repository` to every GitHub command. Before publishing or refreshing a remote marker, they resolve the configured Git remote and branch, run `git push <configured-remote> HEAD:<configured-branch>`, and verify that the checkpoint is reachable there before writing to the tracker. If the remote or branch is absent, ambiguous, or cannot be verified, they stop and repair the configuration. They do not invent `origin`, a branch, or a fallback target. The final checkpoint is created only after the specification and all ticket or justified non-ticket coverage is recorded, then the parent and children receive fresh markers with its exact SHA.

## Common questions

**Does this replace `CONTEXT.md` or an ADR?**

No. `CONTEXT.md` remains the domain glossary, and an ADR remains canonical for an architectural decision. The ledger carries the downstream consequences and points back to an ADR when one owns the rationale.

**Will it reject older specifications and tickets?**

No. A file without a Planning context marker returns the legacy result. Fail-closed validation applies only after a specification or ticket opts into the marker.

**How do I validate a remote ticket without creating a file?**

Obtain its body from the configured tracker with an explicit target, and invoke the validator only after that read succeeds. For GitHub, replace `owner/repository` with the target in `docs/agents/issue-tracker.md`:

```bash
issue_body="$(gh issue view <number> --repo owner/repository --json body --jq .body)" && \
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . --json validate --context-stdin --phase final <<<"$issue_body"
```

If the tracker read returns an error, `&&` prevents the helper from running. The here-string also preserves the helper's exit status. Report that read failure as a preflight failure, never as `legacy`. The helper reads successful stdin without creating a ticket or Planning artifact in the repository.

**What evidence does valid JSON expose?**

`coverage` contains one entry for each selected decision and each declared obligation, with its `status` and `evidence`. For `Obligations: none`, it includes the synthetic `applicability` pair. `ancestry` contains `checkpoint_sha`, `head_sha`, and `is_ancestor`, which is true only after the branch relationship was proven.

**Can I update evidence after a checkpoint?**

Yes, only monotonically. Pending coverage may become complete, and existing evidence may stay unchanged or gain appended values that preserve the previous order. Removing or replacing checkpointed evidence, or regressing complete coverage, fails validation. Editing a checkpointed decision meaning requires a superseding entry and a new checkpoint.

**How do I record a decision with no delivery obligation?**

Create it with `--obligations none`, then call `coverage add --obligation applicability --evidence "non-ticket: ..."` or use a `not-applicable: ...` explanation. The final and implementation gates reject the entry until that evidence is complete and non-empty.

**Can an implementation checkpoint cover only this ticket's decisions?**

Yes. Pass `--decisions DEC-NNN,DEC-NNN` to `checkpoint --phase implementation` for the explicit active subset owned by this invocation. The final planning phase rejects selection and still requires every active applicable decision. Omit selection at implementation closeout when the coordinator owns the whole graph.

**What proves that a checkpoint did not include unrelated files?**

The checkpoint records its exact config, ledger, and explicitly passed extra paths in `Planning-Paths`. Validation rejects changed paths outside that list, rejects extras that are not recognizable as a Planning context artifact, rejects an ownership trailer with an empty diff, and rejects a trailer whose changed diff contains only extras without the config or declared ledger. Older checkpoints remain readable only when their non-empty diff changes both config and ledger with no extra path.

**How does a parallel implementation avoid ledger conflicts?**

Each worker branch starts from the same validated checkpoint and records evidence on its own ticket or commit surface. The coordinator waits for every relevant branch to merge and any required bounded review or fix batches to finish, then runs `coverage aggregate` with the final checkpoint, integration head, merged or final reviewed tips, and applicable decision IDs. The owner rejects an unmerged tip or a worker ledger edit and fails atomically if any selected verification is absent.

**Can verification evidence live only in a remote ticket?**

Yes. After a successful ticket read, pass a repeatable `--ticket-evidence "DEC-NNN | origin | observable evidence"` value to `coverage aggregate`. The origin is required, and the coordinator still validates the complete set before recording it.

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
- A valid marker passes only on a branch descended from the exact checkpoint, a local artifact can resolve that checkpoint from its trailer, a remote marker passes through stdin without creating a file, and a legacy file still returns `legacy`.
- Valid JSON names the input source, selected decision coverage, and proven checkpoint ancestry.
- The public [harness](https://www.aihero.dev/ai-coding-dictionary/harness) reports all scenarios passed from `npm run test:planning-context`.

## Where it fits

`planning-context` is the model-invoked contract beneath the planning and implementation flows. [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) initializes its discovery, [grill-with-docs](https://aihero.dev/skills-grill-with-docs) and [wayfinder](https://aihero.dev/skills-wayfinder) produce decisions for it, and [implement](https://aihero.dev/skills-implement) consumes its checkpoint. [ask-matt](https://aihero.dev/skills-ask-matt) routes the whole set and explains when this cross-session seam is needed.
