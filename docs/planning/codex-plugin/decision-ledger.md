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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
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
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-011
- Status: active
- Decision: Run the upstream synchronization automation weekly on Mondays at 09:00 America/Bahia, starting after the Codex plugin is functional.
- Context: The user approved the recommended cadence and activation gate.
- Rationale: A weekly run keeps upstream changes visible while avoiding runs against an incomplete plugin.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-012
- Status: active
- Decision: When upstream changes require work, the automation updates the upstream base and Codex plugin on a branch, validates them, and opens a non-draft PR; otherwise it records a no-change result.
- Context: The user approved the recommended automation deliverable.
- Rationale: A reviewable PR exposes the assessed adaptation and validation before integration.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-013
- Status: active
- Decision: Track upstream/main and record the incorporated upstream commit for each synchronization.
- Context: The user approved the recommended upstream reference.
- Rationale: The commit makes each evaluated update reproducible.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-014
- Status: active
- Decision: Preserve explicit-only invocation for skills marked user-invoked in the Codex plugin and make their Codex metadata consistent.
- Context: Current fork metadata removes allow_implicit_invocation: false from several user-invoked skills despite their frontmatter and repository policy.
- Rationale: The plugin should honor the declared invocation contract.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-015
- Status: active
- Decision: Keep existing skill documentation focused on upstream and Claude behavior, and document Codex plugin differences separately.
- Context: The user approved separate documentation for the adapted plugin.
- Rationale: Separate pages avoid presenting Codex-only behavior as upstream behavior.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-016
- Status: active
- Decision: Claim compatibility only for Codex versions verified by plugin tests.
- Context: The installed CLI and a newer source checkout expose different plugin contracts.
- Rationale: An untested minimum-version promise would be unreliable.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-017
- Status: active
- Decision: Port useful existing fork behavior from promoted skills into the Codex plugin, including Planning, bounded review, and command safety fixes, while adapting Claude-specific instructions to verified Codex behavior.
- Context: The fork currently changes shared skill instructions and Codex metadata relative to upstream; the user approved preserving useful behavior in the plugin.
- Rationale: The upstream reset should not discard established Codex workflows, and the plugin should use its host correctly.
- ADR: none
- Constraints: Keep beta skills outside the approved initial catalog and preserve explicit-only invocation where declared.
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-018
- Status: active
- Decision: Distribute a public plugin named mattpocock-skills-codex through a Codex marketplace in this same Git repository.
- Context: The user approved the proposed Git-backed marketplace rather than local-only installation.
- Rationale: A repository marketplace provides an installable and updatable native Codex distribution.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none

## DEC-019
- Status: active
- Decision: Keep the Codex plugin version synchronized with package.json and the Claude plugin version through the existing Changesets release flow.
- Context: The current release script synchronizes package.json and the Claude plugin; the user approved adding the Codex plugin to that shared version.
- Rationale: A single release version keeps the repository distribution coherent and minimizes new release machinery.
- ADR: none
- Obligations: specification, tickets, verification
- Coverage:
  - specification: complete
  - tickets: pending
  - verification: pending
- Evidence:
  - specification: https://github.com/manoelcalixto/mattpocock-skills/issues/18
  - tickets: none
  - verification: none
