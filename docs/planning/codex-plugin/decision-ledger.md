# Decision ledger

- Format: v1
- Effort: codex-plugin

Decision meanings are immutable after a Planning checkpoint. Coverage advances from pending to complete, and evidence may be appended without replacing prior values.

## DEC-001
- Status: active
- Decision: Create a native Codex plugin that contains physical copies of the selected skills.
- Context: The repository currently ships a curated Claude plugin, while the user requested a Codex plugin patterned after copied Salesforce plugin skills.
- Rationale: Physical copies give the Codex plugin a self-contained skill tree and avoid the symlink installation failure recorded in ADR 0002.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: pending
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: none
  - tickets: none
  - verification: none
