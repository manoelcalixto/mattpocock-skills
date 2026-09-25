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

## DEC-006
- Status: active
- Decision: Include upstream-promoted skills and Codex-specific workflow skills, beginning with planning-context, in the native Codex plugin.
- Context: The user accepted the proposed catalog after choosing to restore skills/ to upstream.
- Rationale: The promoted set is the public baseline, while plugin-only skills preserve the fork workflow without changing upstream files.
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

## DEC-007
- Status: active
- Decision: Use a recurring Codex automation to evaluate upstream changes and adapt the Codex plugin copies.
- Context: The user requested an automation because upstream changes require Codex judgment rather than a blind file copy.
- Rationale: A normal agent run can inspect upstream changes, reconcile customized skills, and validate the result.
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

## DEC-008
- Status: active
- Decision: Keep the Claude plugin tied to the upstream skill set without this fork’s Codex-specific workflow adaptations.
- Context: Restoring skills/ to upstream removes the fork-specific planning-context skill and customized shared skill text from the Claude plugin source.
- Rationale: The Claude distribution continues to follow upstream while Codex customizations live in the native plugin.
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

## DEC-009
- Status: active
- Decision: Stop creating local Codex skill links from skills/; use the native plugin for Codex development.
- Context: The existing link-skills.sh links skills/ into ~/.agents/skills, which would expose upstream variants alongside plugin variants.
- Rationale: One active Codex distribution avoids duplicate skill names and accidental use of upstream text.
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

## DEC-010
- Status: active
- Decision: Limit the first native Codex plugin to adapted skills and their required scripts, references, and metadata.
- Context: The user selected this scope instead of adding MCP servers or other plugin components in the first version.
- Rationale: This includes the resources needed for working skills without speculative integrations.
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
