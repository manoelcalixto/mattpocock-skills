## What it does

`implement` builds work that has already been decided. You point it at a [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket), a [spec](https://www.aihero.dev/ai-coding-dictionary/spec), or the plan you just agreed in the conversation. Before TDD or code edits, a declared Planning context goes through the public validator, which resolves its ledger, checkpoint SHA, decision IDs, coverage, and branch ancestry.

An artifact without a Planning context marker keeps the legacy path unchanged. A declared marker that cannot be resolved fails closed before mutation with the failed invariant and its remediation. Once the preflight passes, `implement` writes the code, drives [tdd](https://aihero.dev/skills-tdd) at the seams, typechecks as it goes, commits a stable review checkpoint, and for a marked input records observable `Planning-Verification` trailers. It then runs [code-review](https://aihero.dev/skills-code-review) once and batches the applicable fixes. Only after the bounded review and final fix validation does the marked path aggregate verification against the final reviewed head and create the implementation checkpoint. If an active decision conflicts with implementation, the work returns to planning for an explicit supersession and new checkpoint instead of silently diverging.

## When to reach for it

You invoke this by typing `/implement` yourself: the agent won't reach for it on its own. It ships with `disable-model-invocation: true`, so no other skill can call it either. Wherever [ask-matt](https://aihero.dev/skills-ask-matt) or [to-tickets](https://aihero.dev/skills-to-tickets) says "then `/implement` per ticket", that is an instruction to you, not something the agent will do unprompted.

Where the work currently lives decides whether this is the right skill:

| The work is… | Reach for |
| --- | --- |
| A ticket on the tracker | `/implement #42`, one ticket per [session](https://www.aihero.dev/ai-coding-dictionary/session), [clearing](https://www.aihero.dev/ai-coding-dictionary/clearing) context between tickets |
| A spec, not yet split up, and the build spans sessions | [to-tickets](https://aihero.dev/skills-to-tickets) first, then `/implement` per ticket |
| A spec, and the build is small | `/implement` directly against the spec |
| Only in the conversation you just had, and it's still small | `/implement` right there, in the same window |
| Not written down anywhere yet | [grill-with-docs](https://aihero.dev/skills-grill-with-docs), or [grill-me](https://aihero.dev/skills-grill-me) if there's no codebase |
| One concrete behaviour you want test-first, with no spec | [tdd](https://aihero.dev/skills-tdd) directly |
| Already built, and you want it checked | [code-review](https://aihero.dev/skills-code-review) directly |

The same-session case is worth naming because the skill's own first line doesn't cover it. `SKILL.md` says "the spec or tickets", which nudges the [model](https://www.aihero.dev/ai-coding-dictionary/model) to go hunting for a file that doesn't exist. If the plan lives only in the thread, say so when you invoke it.

## Prerequisites

`implement` commits to the branch you are on. It does not create one, and it does not ask. Check you are on the branch you want the work on before you start. A declared Planning context also requires the configuration, ledger, and checkpoint to be present and reachable from that branch. An input without a marker needs no Planning setup.

If the tickets came from [to-tickets](https://aihero.dev/skills-to-tickets), the tracker they live on was configured by [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills). `code-review` reads the same configuration to find the originating spec at close-out.

## Planning preflight

The marker is an admission gate, not background context. The validator checks the exact checkpoint lineage and selected active decisions before the implementation loop starts.

| Input state | Result |
| --- | --- |
| Declared marker resolves | Continue with the returned ledger, checkpoint, decision IDs, coverage, and ancestry. |
| No marker | Continue the legacy implementation path without a Planning checkpoint. |
| Marker is missing, inconsistent, uncovered, or unreachable | Stop before TDD or edits, report the failed invariant, and repair the Planning context. |
| Active decision conflicts with the implementation | Return to planning, resolve or supersede the decision, create a new checkpoint, refresh the marker, and rerun the preflight. |

## What one run does

A run is eight beats, in order:

1. Resolve the input and run the Planning preflight when a marker is declared.
2. Read the ticket or spec and work out the seams.
3. Drive [tdd](https://aihero.dev/skills-tdd) at the pre-agreed seams, one red-green slice at a time.
4. Typecheck often, run single test files as it goes.
5. Run the full test suite once, at the end.
6. Commit the implementation to the current branch, pinning the exact review checkpoint. For a valid Planning context, include one repeatable `Planning-Verification: DEC-NNN | <observable evidence>` trailer per applicable preflight decision that declares `verification`. Decisions without that obligation stay trailer-free, and the closeout aggregator filters them out while rejecting evidence that names them.
7. Run [code-review](https://aihero.dev/skills-code-review) once against the starting SHA, check each citation, apply applicable findings in one fix batch, rerun validation, and commit that batch if needed. For a marked path, put one observable verification trailer on an implementation or fix commit for each decision whose behavior that commit verifies or changes. Follow the bounded follow-up rule below.
8. For a valid Planning context only, ensure the union of final-history trailers and validated ticket evidence covers every applicable preflight decision that declares `verification`, pass the final reviewed `HEAD` and decision IDs to `coverage aggregate`, then run `checkpoint --phase implementation`. If this invocation owns only a subset of the applicable preflight decisions, pass those IDs to the implementation checkpoint with `--decisions <comma-separated-preflight-decision-IDs>`; omit it for the default fail-closed gate over every active applicable decision. The final planning checkpoint does not accept a subset. For `/implement`, the initial commit carries trailers only for applicable preflight decisions that declare `verification`, and a fix adds trailers only for decisions whose behavior it verifies or changes. The aggregator keeps ticket-only mode, filters selected IDs without `verification`, and fails closed when selected verification evidence is missing. Use the final reviewed tip as the supplied `--commit` so review-fix evidence is included. A markerless input skips this closeout and keeps the legacy sequence without inferring Planning state.

The marked closeout uses the final planning checkpoint and the final reviewed tip. It aggregates only decisions whose declared obligations include verification.

```bash
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . coverage aggregate \
  --effort <effort> --checkpoint <final-planning-checkpoint-sha> --head <final-reviewed-head-sha> \
  --decisions <comma-separated-preflight-decision-IDs> --commit <final-reviewed-head-sha>
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . checkpoint \
  --effort <effort> --phase implementation --decisions <comma-separated-preflight-decision-IDs>
```

One run covers one ticket. The tickets [to-tickets](https://aihero.dev/skills-to-tickets) produces are tracer-bullet vertical slices sized to fit a single fresh [context window](https://www.aihero.dev/ai-coding-dictionary/context-window), so the intended rhythm is: clear context, implement one ticket, commit, clear again. Each ticket is self-contained, which is what makes the previous ticket's context disposable.

## The bounded review checkpoint

One invocation is one logical **review checkpoint**, regardless of how many implementation or fix commits it contains. Each pass pins the exact head SHA it reviews. A commit records the state; it does not ask for another review.

The initial Standards and Spec passes happen once. Applicable findings land in one logical **fix batch**, which may span one or more commits. The bounded follow-up rule belongs to `code-review`: only an axis whose own inputs or conclusions changed materially, or whose reviewer explicitly requested it, can run once more. That pass keeps the original fixed point and pins the new head. Its findings can produce one final validated fix batch, then the marked path aggregates verification and creates the implementation checkpoint, while the run stops and reports anything rejected, deferred, or residual.

## Pre-agreed seams

The idea the skill runs on is the **seam**: the public boundary you observe behaviour at, without reaching inside. Tests live at seams. Working at a seam agreed before any code is written is what keeps the tests durable, because the implementation underneath can be rewritten without the tests moving.

The word "pre-agreed" is doing real work, and it is also the skill's weakest joint. Nothing inside `implement` agrees the seams. `tdd` is the skill that asks, and it refuses to write a test at an unconfirmed seam. So in practice the agreement happens either upstream in the spec, or in the first exchange of the run. If it happens nowhere, the precondition never fires and the run quietly becomes "just write the code". Naming the seams in the spec is what stops that.

## Common questions

**What happens when my ticket has no Planning context marker?**

It follows the legacy path. No ledger, checkpoint, or coverage is inferred, and the existing TDD, validation, review, and commit sequence remains the same.

**When is the implementation checkpoint created for a marked ticket?**

After the bounded review, any eligible follow-up, and the final fix-batch validation. The owner aggregates the applicable preflight decision IDs that declare `verification` from the final reviewed history, then `checkpoint --phase implementation` records that verification boundary. The review checkpoint remains the stable commit reviewed by `code-review`.

**Why did implementation stop before TDD?**

A declared marker could not prove one of its required invariants, such as a missing ledger, a mismatched checkpoint, incomplete coverage, or a branch outside the checkpoint ancestry. The exact validator error names the repair. Fix the Planning context and rerun the preflight instead of removing the marker.

**What if an active decision cannot be implemented as written?**

Stop at the conflict and surface the decision ID and consequence. Return to planning for user resolution, a superseding ledger entry, a new checkpoint, and a refreshed marker. Implementation resumes only after that marker passes validation.

**It finished, but my ticket is still open and the acceptance criteria are still unchecked.**

Correct, and expected. `implement` ends after its review and fix batches but never touches the work item, confirmed on GitHub Issues and on the local markdown tracker, so it is not a tracker integration problem. It does not tick the `- [ ]` boxes on the originating issue. Close the ticket and reconcile the criteria yourself. This bites hardest on a dependency chain, because `to-tickets` defines the frontier as tickets whose blockers are all closed. If nothing gets closed, nothing ever becomes visibly unblocked.

**Can I point it at all my tickets at once, or run several in parallel?**

No. One invocation, one ticket. Batch dispatch across a ticket queue and [subagent](https://www.aihero.dev/ai-coding-dictionary/subagent) fan-out are both requested repeatedly, and neither exists. Running several `/implement` sessions side by side in one checkout is worse than unsupported: one field report describes a `git commit --amend` in one session landing on another session's commit, a stash vanishing from `refs/stash`, and commits landing on the wrong branch, all in a single afternoon across three issues. The sessions share one working directory, one index, and one HEAD. Git worktrees are the community workaround, and note that `refs/stash` is shared across worktrees too, so worktrees alone do not fix the stash case. If you want parallelism today, you are assembling it yourself.

**Can it open a pull request instead of committing?**

Not built in. It commits straight to the current branch, which several people find too eager: the code lands before they have had a chance to verify it works. There is no configuration flag and no PR mode. People override it in the invocation ("commit to a branch and open a PR") or by editing their local copy of the skill.

**`code-review` says it cannot see my changes.**

This was caused by older versions running `code-review` before committing even though its three-dot diff excludes staged and working-tree changes. `implement` now records the starting SHA, commits the implementation, and reviews that exact checkpoint against the start, so the diff is visible and stable.

Separately, some people deliberately do not want the review inside the run at all, because an agent reviewing the code it just wrote is biased toward its own solution. Running [code-review](https://aihero.dev/skills-code-review) in a fresh session against a fixed point is a legitimate alternative, and is the same reason that skill runs its two axes in separate sub-agents.

**One ticket burned 150k tokens. Am I using it wrong?**

Probably the ticket is too big rather than the skill being misused. A run does codebase exploration, a red-green loop per seam, a full suite, and a review, so a non-trivial ticket exceeding 100k [tokens](https://www.aihero.dev/ai-coding-dictionary/token) is normal rather than a sign something broke. The lever is upstream: right-size the tickets in [to-tickets](https://aihero.dev/skills-to-tickets) so each fits one fresh window. If a single ticket keeps blowing out, split it rather than raising the [effort](https://www.aihero.dev/ai-coding-dictionary/effort) level.

**`/implement #2` in a fresh session worked on something completely unrelated.**

`#2` is resolved against whatever numbered list the agent can see, which in a fresh session may be a todo file, a checklist, or another work list rather than the configured tracker. The resolution is confident rather than fail-closed, so the mistake is not obvious until it has started. Pass the full reference, the issue URL or `owner/repo#2`, and ask it to confirm the title back before it begins.

## It's working if

- A marked ticket or spec is validated before the first TDD invocation or code edit, and the output names the effort, ledger, checkpoint, decisions, coverage, and ancestry.
- A marker-less ticket follows the same legacy path without being forced to create planning artifacts.
- A broken marker stops the run with the exact invariant and a repair path, before the implementation worktree changes.
- An active decision conflict produces a return to planning and a new checkpoint rather than an undocumented exception.
- The session opens by reading the ticket or spec and restating what it will build, rather than asking you what to build.
- You can see an actual `/tdd` invocation in the trace, not just tests appearing in the diff.
- Typechecks and single test files run repeatedly during the run, and the full suite runs once near the end.
- The implementation reaches a stable commit before review, so the reviewer sees the exact diff.
- Applicable findings land in one validated fix batch rather than one review request per commit.
- The run stops after its bounded follow-up rule and reports residual findings instead of chasing a clean review.
- A marked run aggregates the final-history and ticket-evidence union for every applicable preflight decision that declares `verification` only after review fixes, then creates the implementation checkpoint from the final reviewed head.
- A markerless run never creates or infers Planning ledger, coverage, or checkpoint state.
- The diff is one ticket's worth of change: a vertical slice through every layer, not several tickets swept together.

## Where it fits

`implement` is the build step of the main chain, second from the end:

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review
```

Its neighbours are [to-tickets](https://aihero.dev/skills-to-tickets), which produces the tickets it consumes and declares the blocking edges that decide their order; [planning-context](https://aihero.dev/skills-planning-context), which owns the declared marker, coverage aggregation, and checkpoint validation; [tdd](https://aihero.dev/skills-tdd), which it drives internally at each seam; and [code-review](https://aihero.dev/skills-code-review), which it runs once after committing the stable review checkpoint. It validates the Planning seam before trusting a marked artifact, while the implementation shape and acceptance criteria remain the responsibility of the upstream planning flow.

That boundary is why [wayfinder](https://aihero.dev/skills-wayfinder) merges onto the chain at [to-spec](https://aihero.dev/skills-to-spec) rather than looping its map straight into `implement`. Go straight to `implement` from a map only when the effort turned out genuinely small.

[ask-matt](https://aihero.dev/skills-ask-matt) is the router over the whole set when you are not sure which flow you are in.
