---
name: to-spec
description: "Turn the current conversation into a spec with Planning decision coverage and publish it to the configured issue tracker: no interview, just synthesis of what you've already discussed."
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user; just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

When the source conversation has an active Planning context, call the Skill tool with `planning-context` before drafting. It is the owner of the ledger, checkpoint, coverage, and marker contract. A source without a Planning context marker follows the legacy path and does not need a ledger.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Read `CONTEXT.md`, applicable ADRs, and the Planning context when it is active. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

   When Planning context is active, enumerate every active ledger entry and its declared obligations before writing. The specification obligation is the set that needs an actionable consequence in this spec. An active entry without a specification obligation still needs an explicit applicability note in the coverage check, with the reason it has no specification consequence. Do not silently omit an active entry.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Write the spec using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

   For an active Planning context, create or resolve an intermediate checkpoint through `planning-context` before generating the marker. Include that marker in the published spec. In the implementation-decisions section, add one concise line per applicable active decision in the form `DEC-NNN: consequence`. Keep the consequence actionable and do not copy the ledger's canonical rationale, context, or ADR prose. The marker's decision list must contain only the IDs represented by the spec.

   After publication, call `planning-context` with `coverage add --obligation specification` to mark the specification obligation complete with evidence naming the published spec. This is coverage bookkeeping, not a new decision.

   Read `docs/agents/issue-tracker.md` before any tracker operation. For GitHub, use the configured `owner/repository` from that file in every command's explicit `--repo owner/repository` option. Never infer the target from the checkout, a remote, or the current `gh` context. If the configured target is missing or ambiguous, stop before publication and ask for setup repair.

   A GitHub publication therefore looks like `gh issue create --repo owner/repository --title "..." --body "..."`, with the configured target substituted literally. If the marker must be refreshed in a published body, use `gh issue edit <spec> --repo owner/repository --body "<body with the marker>"`.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>
