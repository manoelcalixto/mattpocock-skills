---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

When the destination is a fresh session and the current work has an active Planning context, call the Skill tool with `planning-context` first and create the checkpoint that matches the next phase. Use an intermediate checkpoint while planning continues, a final checkpoint before implementation, and an implementation checkpoint after verification.

For an active Planning context, make the handoff a pointer bridge. Include the exact full checkpoint SHA, effort, ledger path, current branch, and the resolvable paths or URLs for the map, specification, and tickets that the next session needs. Verify that each local target is present in or resolvable from that checkpoint commit. A fresh implementation session must receive the final checkpoint and its marker validation path. Reference these versioned artifacts; do not copy their ledger, specification, ticket, ADR, or decision content into the handoff.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
