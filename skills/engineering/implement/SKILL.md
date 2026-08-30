---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

## Planning preflight

Before calling `tdd`, editing code, or committing, resolve a file or tracker ticket to one repository-relative spec or ticket artifact. For a plan that exists only in the conversation, there is no Planning context marker and the legacy path remains available. For an artifact, run the public validator without an effort override:

```bash
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . --json validate --context-file <spec-or-ticket> --phase final
```

Continue a declared Planning context only when the JSON result reports `"status": "valid"`. Carry its resolved effort, ledger, checkpoint SHA, decision IDs, coverage, and branch ancestry into the implementation context. The `final` phase proves the selected active decisions have specification and ticket coverage; verification belongs to implementation closeout.

A result of `"status": "legacy"` is valid only when the artifact has no `## Planning context` marker. Continue the existing implementation path unchanged and do not infer a Planning context. A declared marker with missing, inconsistent, uncovered, or unreachable state, or any other validator error, fails closed. Surface the exact failed invariant and its remediation, then stop before TDD, code edits, or commits. A declared marker never falls back to the legacy path.

If an active decision cannot be honored, stop the implementation at that conflict and report the decision ID and consequence. Call the Skill tool with `planning-context` to return to planning for user resolution. Resume only after a superseding decision, a new Planning checkpoint, a refreshed marker, and a passing preflight. Keep the conflict explicit instead of recording a silent deviation in code, tests, commits, or the ledger.

Record the current `HEAD` SHA before implementation. It is the fixed point for this invocation.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Commit the completed implementation to the current branch. This exact commit is the **review checkpoint** for the invocation.

Call the Skill tool with "code-review" once, using the starting SHA as its fixed point. Check each finding's citation, then apply the applicable findings in one **fix batch**. Documented-standard violations and spec gaps can require a fix; baseline smells are judgement calls. Re-run the relevant validation and commit the fix batch if it changed the code.

Follow `code-review`'s bounded follow-up and terminal rule. Report rejected, deferred, or residual findings before stopping.
