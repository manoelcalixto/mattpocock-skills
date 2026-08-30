---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Record the current `HEAD` SHA before implementation. It is the fixed point for this invocation.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Commit the completed implementation to the current branch. This exact commit is the **review checkpoint** for the invocation.

Call the Skill tool with "code-review" once, using the starting SHA as its fixed point. Check each finding's citation, then apply the applicable findings in one **fix batch**. Documented-standard violations and spec gaps can require a fix; baseline smells are judgement calls. Re-run the relevant validation and commit the fix batch if it changed the code.

Follow `code-review`'s bounded follow-up and terminal rule. Report rejected, deferred, or residual findings before stopping.
