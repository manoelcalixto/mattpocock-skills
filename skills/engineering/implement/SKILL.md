---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

## Planning preflight

Before calling `tdd`, editing code, or committing, identify the input source. A local spec or ticket artifact uses `--context-file`; a remote tracker item uses its already-obtained body through `--context-stdin`. For a plan that exists only in the conversation, there is no Planning context marker and the legacy path remains available.

```bash
# Local artifact, relative to the repository root
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . --json validate --context-file <spec-or-ticket> --phase final

# Remote GitHub body, read successfully before invoking the validator
issue_body="$(gh issue view <number> --repo owner/repository --json body --jq .body)" && \
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . --json validate --context-stdin --phase final <<<"$issue_body"
```

Replace `owner/repository` with the explicit target from the repository's issue-tracker configuration. The assignment and `&&` are intentional: a nonzero tracker read stops before the validator, and the here-string preserves the validator's own exit status. Surface that read error as a preflight failure, never pass empty input to the validator, and never interpret a tracker read failure as `legacy`. Continue a declared Planning context only when the JSON result reports `"status": "valid"`. Carry its resolved effort, ledger, checkpoint SHA, decision IDs, coverage, and branch ancestry into the implementation context. The `final` phase proves the selected active decisions have specification and ticket coverage; verification belongs to implementation closeout. A valid stdin result identifies `source: stdin` and `context: <stdin>`; a local marker identifies its repository-relative context file.

A result of `"status": "legacy"` is valid only when the artifact has no `## Planning context` marker. Continue the existing implementation path unchanged and do not infer a Planning context. A declared marker with missing, inconsistent, uncovered, or unreachable state, or any other validator error, fails closed. Surface the exact failed invariant and its remediation, then stop before TDD, code edits, or commits. A declared marker never falls back to the legacy path.

If an active decision cannot be honored, stop the implementation at that conflict and report the decision ID and consequence. Call the Skill tool with `planning-context` to return to planning for user resolution. Resume only after a superseding decision, a new Planning checkpoint, a refreshed marker, and a passing preflight. Keep the conflict explicit instead of recording a silent deviation in code, tests, commits, or the ledger.

Record the current `HEAD` SHA before implementation. It is the fixed point for this invocation.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Commit the completed implementation to the current branch. This exact commit is the **review checkpoint** for the invocation. When the preflight returned a valid Planning context, add repeatable `Planning-Verification: DEC-NNN | <observable evidence>` trailers to the implementation commit, one for each applicable decision returned by preflight.

Call the Skill tool with "code-review" once, using the starting SHA as its fixed point. Check each finding's citation, then apply the applicable findings in one **fix batch**. Documented-standard violations and spec gaps can require a fix; baseline smells are judgement calls. For a marked path, put one observable `Planning-Verification: DEC-NNN | <evidence>` trailer on an implementation or fix commit for each decision whose behavior that commit verifies or changes. Re-run the relevant validation and commit the fix batch if it changed the code.

Follow `code-review`'s bounded follow-up and terminal rule. Report rejected, deferred, or residual findings before stopping.

## Planning implementation closeout

Only for a declared Planning context that passed preflight, after the bounded `code-review` pass, any eligible follow-up, and the final fix-batch validation, inspect the final history and validated ticket evidence to ensure the union of the final history and validated ticket evidence covers every applicable preflight decision and represents the final reviewed code. Then call the `planning-context` owner with the final planning checkpoint, final reviewed `HEAD`, and that final tip:

For `/implement`, the initial implementation commit covers every applicable decision returned by preflight. A fix commit adds trailers only for decisions whose behavior it verifies or changes. If the final union is missing a required decision, add the corresponding trailer to the implementation or fix commit that verifies or changes it, then rerun final validation before aggregation.

```bash
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . coverage aggregate \
  --effort <effort> --checkpoint <final-planning-checkpoint-sha> --head <final-reviewed-head-sha> \
  --decisions <comma-separated-preflight-decision-IDs> --commit <final-reviewed-head-sha>
```

The owner must pass its merged-tip, lineage, and complete verification gates before writing the ledger. Only after aggregation succeeds, run `checkpoint --phase implementation`. If this invocation owns only a subset of the applicable preflight decisions, pass those IDs with `--decisions <comma-separated-preflight-decision-IDs>`; omitting the option keeps the default fail-closed gate over every active applicable decision. The final planning phase does not accept a subset. This checkpoint records the final reviewed code's Planning verification. If preflight returned "status": "legacy", keep the existing implementation, review, fix, and terminal sequence byte-for-byte behaviorally unchanged: skip this closeout and never infer a ledger, checkpoint, or coverage aggregation.
