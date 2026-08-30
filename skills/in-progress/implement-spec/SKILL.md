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

## Steps

1. Read the spec and tickets. Read enough to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Record the current `HEAD` SHA as the fixed point for the whole implementation batch. Then create a branch and a draft PR. The PR should be marked as 'closing' the spec issue and tickets.

4. Use **implementer subagents** to implement each ticket. Each implementer subagent should work in its own worktree, on its own branch.

5. Once an **implementer subagent** completes, merge its work to the PR branch with a **merger subagent**.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

Ticket commits and merges are part of one implementation batch. They are not review checkpoints and do not trigger `code-review` from this workflow.

7. Once all tickets are complete and integrated, treat the PR branch as this workflow's only **review checkpoint** and pin its exact head for the initial pass. Call the Skill tool with "code-review" once on that checkpoint, using the SHA recorded in step 3 as its fixed point. Check every finding's citation, then use a single **implementer subagent** to apply the applicable findings in one **fix batch** and validate it. A fix batch may span one or more commits. Documented-standard violations and spec gaps can require a fix; baseline smells are judgement calls.

   Follow `code-review`'s bounded follow-up and terminal rule. If an eligible follow-up produces applicable findings, use one final **implementer subagent** for the final fix batch. Report rejected, deferred, or residual findings before stopping.

8. Mark the PR as ready for human review once validation passes and the review outcome, including any rejected, deferred, or residual findings, is recorded.

9. Clean up all **implementer subagent** worktrees.
