---
name: to-tickets
description: Break a plan, spec, or the current conversation into tracer-bullet tickets with Planning decision coverage, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
disable-model-invocation: true
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

When the source conversation or specification has an active Planning context, call the Skill tool with `planning-context` before drafting. It is the sole owner of the ledger, checkpoint, coverage, and marker contract. A source without a Planning context marker follows the legacy ticket path.

A cleared Wayfinder map is consumed through this same path. Resolve its marker and ledger, preserve each active Decision ticket ID, and map its actionable consequence to implementation tickets. Read the map and Decision tickets as pointers; their prose does not replace the ledger's canonical rationale.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

For an active Planning context, validate the declared marker against the exact checkpoint and current branch, then read every active ledger entry. Build a coverage table before drafting: each entry with a `tickets` obligation must map to one or more tickets, while an entry without that obligation must have a written non-ticket or not-applicable justification. Keep the ledger's rationale in the ledger. Tickets receive only the relevant decision IDs, actionable consequences, and acceptance criteria.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

For an active Planning context, each proposed ticket also declares its decision coverage:

- `Decisions: DEC-NNN, DEC-NNN` names only the active entries that affect that ticket.
- `Consequences:` gives one concise, actionable consequence for each named ID. Do not copy canonical rationale, context, or ADR text.
- Acceptance criteria make the consequence observable. A decision covered by several tickets may appear in each one when each ticket owns a different part of the consequence.

Every active decision with a `tickets` obligation must appear in at least one ticket. A process, out-of-scope, or otherwise non-ticket decision is recorded as a justified non-ticket obligation in the planning coverage instead of receiving an artificial implementation ticket.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Publish the tickets to the configured tracker

Publish the approved tickets. **How** depends on the tracker `/setup-matt-pocock-skills` configured; the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's "Blocked by" lists the numbers/titles it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. Apply the `ready-for-agent` triage label unless instructed otherwise; the tickets are agent-grabbable by construction.

When Planning context is active, include a marker from `planning-context` in every published ticket. The marker's decision list and the ticket's decision coverage must match exactly. After each publication, record ticket coverage through `planning-context` using the published issue number, URL, or local ticket path as evidence. This is append-only coverage, not a second decision record.

Read `docs/agents/issue-tracker.md` before any tracker operation. For GitHub, copy its configured `owner/repository` into every command's explicit `--repo owner/repository` option, including issue creation, reads, edits, labels, comments, and relationship wiring. Use the same fully qualified target for any `gh api repos/owner/repository/...` call. Never infer the target from the checkout, a remote, or the current `gh` context. If the target is absent or ambiguous, stop before publication and ask for setup repair.

A GitHub child publication therefore looks like `gh issue create --repo owner/repository --title "..." --body "..."`; relationship calls use `gh api repos/owner/repository/...` with no inferred repository. Before publishing or refreshing a remote marker, resolve the configured Git remote and branch, run `git push <configured-remote> HEAD:<configured-branch>`, and verify that the checkpoint is reachable there. After the final checkpoint, update a child body with `gh issue edit <child> --repo owner/repository --body "<body with the regenerated marker>"`.

After all approved tickets and justified non-ticket obligations have coverage evidence, call `planning-context` for the final Planning checkpoint with phase `final`. Let its gate fail while any required specification or ticket coverage is pending. Only after the checkpoint returns its full SHA, resolve the configured Git remote and branch, run `git push <configured-remote> HEAD:<configured-branch>`, and verify that the checkpoint is reachable there. Then regenerate the marker for the parent specification and every child ticket with that SHA and update the external bodies through the configured tracker target. Do not invent `origin`, a branch, or a fallback target. The final checkpoint stages only planning-owned configuration, ledger, and explicitly owned artifacts; it does not absorb unrelated worktree changes.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Planning context

- Format: v1
- Repository: <configured owner/repository>
- Effort: <effort>
- Decision ledger: `<ledger path>`
- Planning checkpoint: <checkpoint SHA>
- Decisions: <relevant decision IDs only>

### Decision consequences

- `DEC-NNN`: <actionable consequence for this ticket>

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)".

</issue-template>

In either form, avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.
