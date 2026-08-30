---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, recording domain docs and confirmed Planning decisions as it goes.
disable-model-invocation: true
---

# Grill with docs

Call the Skill tool once with `planning-context` to initialize the repository's Planning discovery and resolve the effort ledger. Then call the Skill tool once with `grilling`. Then call the Skill tool once with `domain-modeling`. Each call is separate because each named skill owns a different part of the flow.

## During the interview

`grilling` owns the rounds, frontier, recommendations, and wait for the user's answers. `domain-modeling` owns vocabulary, `CONTEXT.md`, and ADRs. Use `planning-context` as the sole owner of the per-effort Decision ledger.

After each user answer, classify the resolved choice before advancing the frontier:

- A choice that changes behavior, constraints, scope, a contract, a test seam, or architecture is material. Record it once through `planning-context` with its concise context, rationale, and applicable obligations.
- A routine local implementation choice is not ledger material. Keep it in the conversation for `to-spec` or implementation to use when relevant.
- A domain term still goes through `domain-modeling`; an ADR-worthy architectural choice still goes through `domain-modeling`. The ledger points to those artifacts when they own the rationale and does not replace or copy them.

The user's answer is the confirmation for a material decision. Do not ask for a second confirmation solely to record it. Use the ID returned by `planning-context` in the round summary, for example `Recorded decisions: DEC-004, DEC-005`, so the next round and downstream synthesis can refer to stable identities.

## Completion

The grilling session is complete only when `grilling` reports an empty frontier, every material choice has one ledger ID, and the round summary exposes every ID recorded in that round. If the work will cross into a fresh session, call `planning-context` to create an intermediate checkpoint before handing the plan to another session. Leave final specification and ticket gates to the downstream planning flow.
