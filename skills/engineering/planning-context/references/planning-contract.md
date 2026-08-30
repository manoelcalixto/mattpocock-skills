# Planning context contract

This is the maintained format reference for the `planning-context` skill and its deterministic helper. Callers can use the helper as an adapter, but the ledger remains the human-readable source of truth.

## Repository discovery

The repository configuration is `docs/agents/planning.md`. The default content is created by `planning_context.py init`:

```markdown
<!-- planning-context:v1 -->
# Planning context

- Format: v1
- Ledger directory: `docs/planning`
- Checkpoint trailer: `Planning-Checkpoint`
- Checkpoint phases: `intermediate`, `final`, `implementation`
- Legacy inputs: allowed when no Planning context marker is declared.
```

`init` is idempotent. A file that already carries the marker is preserved byte for byte. An existing file without the marker receives the default block appended to it, which is the lazy migration path. Setup should call the `planning-context` Skill tool to perform this initialization after the user confirms the other repository settings.

## Decision ledger

There is one ledger per effort. Its path is `<ledger directory>/<effort>/decision-ledger.md`; the effort is lowercase and path-safe. A ledger entry has this shape:

```markdown
## DEC-001
- Status: active
- Decision: Use the shared planning seam
- Context: Several sessions consume the same plan
- Rationale: A versioned contract prevents drift
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
```

`ADR` is optional and points to the canonical architectural record. `Obligations` may be `none` for an out-of-scope or process decision. The supported obligations are `specification`, `tickets`, and `verification`.

The helper allocates the next numeric ID within the selected effort. `decision add --supersedes DEC-001` changes only the old entry's validity fields and appends a new entry. The old decision and rationale stay byte-for-byte unchanged. A checkpointed ledger may receive coverage and evidence updates, but adding, removing, or changing a decision meaning requires a new checkpoint.

### Wayfinder resolution

A resolved Wayfinder Decision ticket uses the same ledger as every other producer. Inspect the active entries before recording the answer:

- If an active entry already represents the answer, run `decision reference --effort <effort> --decision DEC-NNN`. It returns that stable ID without appending another entry.
- If no active entry represents the answer, run `decision add` once and use the returned ID. One resolution creates at most one new entry.
- Carry exactly one active ID in the resolved Decision ticket's Planning context marker. The map remains an index that links to the ticket and gives a short gist; the ledger owns the decision and rationale.
- When the answer is ADR-worthy, make the ADR the canonical record and pass its path with `decision add --adr`. The ledger and ticket point to that ADR instead of copying its rationale.

After recording a new entry, create an intermediate checkpoint before publishing or handing off the resolution, then refresh the map and ticket markers to that checkpoint and active ID. The map marker must advance with each resolution checkpoint so its selected IDs remain coherent. The same specification, ticket, and final checkpoint coverage rules then apply to the Wayfinder map and its downstream consumers. A fresh build session is permitted only after the final checkpoint gate passes.

## Producer and consumer propagation

The ledger is the canonical source for decision meaning. A producer records one material choice through the owner and receives one stable ID. A specification or ticket may repeat that ID and the concise consequence needed to act, but it does not repeat the ledger's decision, context, rationale, or ADR prose.

| Consumer | Required account | Coverage evidence |
| --- | --- | --- |
| Specification | Every active entry that declares `specification`, with one actionable consequence per applicable ID | Published spec issue, URL, or local path |
| Ticket | Every active entry that declares `tickets`, mapped to one or more relevant tickets with criteria; entries without that obligation get a written non-ticket or not-applicable reason | Published child issue, URL, or local ticket path |
| Implementation | Applicable verification evidence after ticket work is integrated | Test command, observable result, or other verification artifact |

The marker's `Decisions` list is the consumer's selected set. It must contain only active IDs represented by that artifact. A final checkpoint fails until every active entry's declared specification and ticket obligations have complete, non-empty evidence. A non-ticket obligation is complete only when its justification is recorded as the corresponding coverage evidence.

## Phase gates

| Phase | Required coverage |
| --- | --- |
| `intermediate` | none |
| `final` | `specification` and `tickets`, when an entry declares them |
| `implementation` | `specification`, `tickets`, and `verification`, when declared |

The helper requires complete coverage and non-empty evidence for every active entry and applicable obligation. Superseded entries do not block a gate. This is a delivery gate, separate from entry validity.

## Checkpoint contract

`checkpoint` always includes `docs/agents/planning.md` and the effort ledger. Extra paths must be passed explicitly with `--path`. It stages those exact paths and commits them with:

```text
Planning-Checkpoint: <effort>
Planning-Phase: <intermediate|final|implementation>
Planning-Ledger: <relative ledger path>
```

The commit uses `git commit --only` with the owned path list, so unrelated staged or unstaged work is left outside the checkpoint. The returned full SHA is the pointer for a fresh consumer. Push it only when a remote consumer, pull request, or separate clone needs it.

## Consumer marker

Specifications and tickets that opt into the contract carry this block after a checkpoint exists:

```markdown
## Planning context

- Format: v1
- Repository: https://github.com/example/project
- Effort: demo
- Decision ledger: `docs/planning/demo/decision-ledger.md`
- Planning checkpoint: 0123456789abcdef0123456789abcdef01234567
- Decisions: DEC-001
```

`marker --output <path>` writes or replaces this block. `Repository` is informative. The validator resolves the ledger and checkpoint in the current clone, proves that the current branch descends from the checkpoint, and checks that checkpointed decision meaning is unchanged. Local artifacts may instead discover the checkpoint through the Git trailer when no external marker is needed.

For a remote tracker, the publishing skill must obtain the configured repository target from `docs/agents/issue-tracker.md` and pass it explicitly to every GitHub operation. A marker's `Repository` field is informative metadata; resolution still depends on the ledger, checkpoint, and ancestry in the consumer clone. After the final checkpoint, regenerate the marker so external children point to that exact final SHA.

## Validation and compatibility

`validate --context-file <path>` returns `legacy` when the file has no Planning context marker and no effort is supplied. A marker is fail-closed: its format, effort, ledger, checkpoint, decision IDs, trailer, ancestry, immutable meaning, and requested phase coverage must all resolve. A local artifact without a marker can pass `--effort <effort>` to resolve the latest matching checkpoint through its Git trailer. Use `--phase final` before a fresh implementation session and `--phase implementation` when aggregating completion evidence. Use repeated `--require` flags for a narrower explicit gate.

The public interface is the CLI:

```bash
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . init
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . ledger create --effort demo
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . decision add --effort demo --decision "..." --context "..." --rationale "..."
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . decision reference --effort demo --decision DEC-001
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . coverage add --effort demo --decision DEC-001 --obligation specification --evidence spec.md
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . checkpoint --effort demo --phase final
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . marker --effort demo --checkpoint <sha> --decisions DEC-001 --output spec.md
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . validate --context-file spec.md --phase final
python3 skills/engineering/planning-context/scripts/planning_context.py --repo . validate --context-file local-ticket.md --effort demo --phase final
```

The harness runs each scenario in a temporary Git repository and invokes only this interface. Future producers and consumers extend the same harness rather than adding a parallel planning state store.
