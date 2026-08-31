---
name: implement-spec
description: "Implement a specification in code."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

The goal is a PR which implements the entire spec on a single branch.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for **maximum concurrency**.

## Planning context preflight

When the specification or any ticket declares `## Planning context`, validate the complete graph before creating an integration branch, draft PR, or implementer worktree. If the specification and every ticket are markerless, continue the existing legacy workflow. A graph that mixes marked and markerless inputs fails closed because it has no single durable base.

1. Read the specification and every ticket, including every blocking edge and every ticket currently in the frontier.
2. Identify each input source. For a local artifact, validate it by path:

   ```bash
   python3 skills/engineering/planning-context/scripts/planning_context.py --repo . --json validate --context-file <spec-or-ticket> --phase final
   ```

   For a remote GitHub item, read its body successfully before invoking the validator:

   ```bash
   issue_body="$(gh issue view <number> --repo manoelcalixto/mattpocock-skills --json body --jq .body)" && \
   python3 skills/engineering/planning-context/scripts/planning_context.py --repo . --json validate --context-stdin --phase final <<<"$issue_body"
   ```

   Repeat the command for the specification and every ticket. A tracker read error stops this preflight before stdin transport. Never pass an empty body or reinterpret that read failure as `legacy`.
3. Continue only when every result reports `"status": "valid"`. Compare the returned `effort`, `ledger`, and full `checkpoint` SHA as exact values. They must be identical across the specification and all tickets, with the same effort, ledger, and checkpoint. Require `ancestry.is_ancestor: true`, matching `ancestry.checkpoint_sha`, and the current lineage for every result. The specification and ticket results must also expose the final specification and ticket coverage for their selected active decision IDs. Collect the union of their decision IDs and consequences for dispatch.
4. Record that exact validated checkpoint SHA as the common base. If a graph opts into Planning context but any input is missing, markerless, inconsistent, uncovered, unreachable, or resolved from a different effort, ledger, checkpoint, or lineage, report the failed invariant and stop before any branch, PR, worktree, TDD call, or code edit.

The preflight is a graph gate, not background reading. Do not create a branch or draft PR until the specification, every ticket, the ledger, the final coverage gate, and the ancestry check have all passed.

## Checkpoint and publication

After the graph gate passes, create the integration branch from the recorded checkpoint SHA, or from an integration head that already descends from it. Prove the ancestry before creating each worker branch or worktree. The checkpoint is local first. Push it only when a draft PR, a remote consumer, or a separate clone needs to resolve it, and make the draft PR after the preflight has passed. Keep the validated effort, ledger path, checkpoint SHA, decision IDs, and ticket references as context pointers for every downstream task. Do not copy canonical rationale into prompts or worktrees.

## Implementer evidence

Use the task graph, not a flat ticket list. Start implementers only for the current frontier, then recalculate the frontier after each merge. Each implementer works in its own branch and worktree descended from the common checkpoint lineage. Give it only pointers to the specification, its ticket, the effort ledger, the checkpoint SHA, and the relevant decision consequences.

An implementer owns its ticket or commit surface. It leaves the shared Decision ledger and its coverage unchanged. For a marked path, each implementation or fix commit carries one repeatable `Planning-Verification: DEC-NNN | <observable evidence>` trailer for each decision whose behavior that commit verifies or changes. A worker records only decisions relevant to its ticket; the union of the final history and validated ticket evidence must cover every applicable preflight decision before aggregation:

```text
Planning-Verification: DEC-001 | npm run test:planning-context
Planning-Verification: DEC-002 | rendered smoke test at /settings
```

When evidence was read from the implementer's own remote ticket instead, pass it to the coordinator only after the ticket read succeeded, using the deterministic form `DEC-NNN | origin | observable evidence`. The implementer never appends shared ledger coverage.

## Merge and review checkpoint

When an implementer completes, merge its branch through the merger into the integration branch, preserve its commit evidence, and then refresh the frontier. Ticket commits and merges remain inside one implementation batch, not separate review checkpoints. After every relevant ticket branch has merged, verify each worker tip is an ancestor of the integration head, then preserve the final integration head for the review checkpoint.

The review checkpoint is the integrated implementation batch's exact head. Do not aggregate verification or create the implementation checkpoint before the bounded `code-review` pass and its fix batches finish.

The integrated implementation batch is the workflow's only review checkpoint. Clean up all implementer worktrees only after the workflow reaches its terminal state.

## Planning implementation closeout

After the initial `code-review` pass, any eligible bounded follow-up, and the final fix-batch validation, close a declared Planning context through the owner. Use the final reviewed integration head as a supplied tip so evidence from implementation, merge, and review-fix commits is in the checkpoint-to-tip history:

```bash
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . coverage aggregate \
  --effort <effort> --checkpoint <final-checkpoint-sha> --head <final-reviewed-head-sha> \
  --decisions <comma-separated-applicable-IDs> --commit <worker-tip-one> --commit <worker-tip-two> \
  --commit <final-reviewed-head-sha> \
  --ticket-evidence "DEC-NNN | issue #<number> | observable ticket evidence"
```

The owner scans the supplied history for repeatable `Planning-Verification` trailers, accepts already-read ticket evidence with an explicit origin, rejects unmerged or wrong-lineage tips and worker ledger edits, and checks every applicable active decision in memory before writing. It must fail without modifying the ledger when any verification is absent. Every implementation and fix commit on the marked path must carry trailers only for decisions whose behavior it verifies or changes, and the union of the final history and validated ticket evidence must cover every applicable selected decision before aggregation. Only after aggregation succeeds, run the owner `checkpoint --phase implementation`; its exact commit is the final evidence boundary for the reviewed code. For an entirely markerless graph, preserve the legacy closeout and do not infer a ledger, coverage aggregation, or Planning checkpoint.

## Steps

1. Read the spec and every ticket, then complete the Planning context preflight before any branch, PR, or worktree.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Record the validated checkpoint SHA and current `HEAD` SHA as the fixed points for the implementation batch. Then create the integration branch and conditional draft PR. The PR should be marked as 'closing' the spec issue and tickets.

4. Use **implementer subagents** to implement each ticket. Each implementer subagent should work in its own worktree, on its own branch descended from the validated checkpoint, and receive context pointers plus its evidence contract.

5. Once an **implementer subagent** completes, merge its work to the PR branch with a **merger subagent**, preserving its ticket and commit evidence.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency. After all relevant branches are merged, preserve the final integration head for the review checkpoint. Do not aggregate verification or create the implementation checkpoint yet.

Ticket commits and merges are part of one implementation batch. They are not review checkpoints and do not trigger `code-review` from this workflow.

7. Once all tickets are complete and integrated, treat the PR branch as this workflow's only **review checkpoint** and pin its exact head for the initial pass. Call the Skill tool with "code-review" once on that checkpoint, using the SHA recorded in step 3 as its fixed point. Check every finding's citation, then use a single **implementer subagent** to apply the applicable findings in one **fix batch** and validate it. A fix batch may span one or more commits. Documented-standard violations and spec gaps can require a fix; baseline smells are judgement calls.

   Follow `code-review`'s bounded follow-up and terminal rule. If an eligible follow-up produces applicable findings, use one final **implementer subagent** for the final fix batch. Report rejected, deferred, or residual findings before stopping.

8. After the bounded review and all applicable fix batches are validated, ensure the union of final-history trailers and validated ticket evidence covers every decision ID returned by preflight. Then close a declared Planning context with `coverage aggregate` against the final reviewed head and those decision IDs, followed by `checkpoint --phase implementation`. Skip this closeout for an entirely markerless graph so its legacy path remains unchanged.

9. Mark the PR as ready for human review once validation passes and the review outcome, including any rejected, deferred, or residual findings, is recorded.

10. Clean up all **implementer subagent** worktrees.
