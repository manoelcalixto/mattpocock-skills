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

## DEC-002
- Status: active
- Decision: Keep the skills/ tree aligned with the upstream repository, and maintain Codex-specific skill adaptations in the native plugin.
- Context: The user wants to reset the fork skill directory to upstream and receive upstream skill updates while preserving Codex customization.
- Rationale: See the repository decision on separating the upstream base from the Codex distribution.
- ADR: .agents/adr/0004-separate-upstream-skills-from-codex-plugin.md
- Obligations: specification, tickets, verification
- Coverage:
  - specification: pending
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: none
  - tickets: none
  - verification: none

## DEC-003
- Status: active
- Decision: Ship one native Codex plugin for this repository.
- Context: The user chose one plugin rather than thematic plugin groups.
- Rationale: A single installation surface matches the desired Codex workflow.
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

## DEC-004
- Status: active
- Decision: Document the native plugin as the recommended Codex installation route.
- Context: The user wants Codex consumers to use the adapted plugin, while skills/ retains upstream originals.
- Rationale: Direct installation from skills/ would miss the Codex-specific adaptations.
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

## DEC-005
- Status: active
- Decision: Document an upstream update workflow in AGENTS.md that reconciles changed upstream skills with the plugin adaptations.
- Context: The user expects future upstream updates to be brought into the plugin after reviewing changes in the original skills.
- Rationale: Without an explicit maintenance rule, the plugin can drift from updated upstream behavior.
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
