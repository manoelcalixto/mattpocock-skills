# Matt Pocock Skills

A fork of Matt Pocock's agent skills, maintained for the user's Codex workflow. Skills are organized into buckets and consumed by per-repo configuration emitted by `/setup-matt-pocock-skills`.

## Language

**Codex-native adaptation**:
A change maintained in this fork to improve the user's Codex workflow, even when it diverges from upstream's Claude Code-oriented conventions. It does not imply an upstream contribution.
_Avoid_: upstream-ready change, upstream contribution

**Planning context**:
The durable, versioned set of planning knowledge that a fresh implementation session must resolve: the Decision ledger, applicable domain glossary and ADRs, specification, issues, and Planning checkpoint.
_Avoid_: context window (session-local model input), handoff document (a portable summary)

**Planning checkpoint**:
The phase boundary before work continues in a fresh session. At this checkpoint, planning knowledge is made durable in a commit and the next session is given resolvable pointers to every required artifact.
_Avoid_: handoff (does not require durable repository state), save point (does not identify the planning boundary)

**Decision ledger**:
A versioned record of resolved planning decisions that must remain traceable through specifications, issues, implementation, and verification. It captures material decisions that need durable downstream coverage but do not warrant an ADR.
_Avoid_: ADR (reserved for architectural decisions), Decision ticket (an unresolved question tracked by `wayfinder`)

**Issue tracker**:
The tool that hosts a repo's issues: GitHub Issues, Linear, a local `.scratch/` markdown convention, or similar. Skills like `to-tickets`, `to-spec`, and `triage` read from and write to it.
_Avoid_: backlog manager, backlog backend, issue host

**Issue**:
A single tracked unit of work inside an **Issue tracker**: a bug, task, spec, or slice produced by `to-tickets`.
_Avoid_: ticket (use only when quoting external systems that call them tickets, or for a **Decision ticket**, see below)

**Decision ticket**:
A `wayfinder` unit: a child **Issue** of a `wayfinder:map` holding a *question* whose resolution is a decision, not a slice of a build to execute. The **decision** qualifier is what keeps it distinct from an implementation ticket; `wayfinder` introduces the term, then uses "ticket".

**Triage role**:
A canonical state-machine label applied to an **Issue** during triage (e.g. `needs-triage`, `ready-for-afk`). Each role maps to a real label string in the **Issue tracker** via `docs/agents/triage-labels.md`.

## Relationships

- An **Issue tracker** holds many **Issues**
- An **Issue** carries one **Triage role** at a time
- A **Decision ticket** is an **Issue** (a child of a `wayfinder:map`)
- A **Planning context** contains the durable pointers required by a fresh implementation session
- A **Planning checkpoint** makes a **Decision ledger** and the other required planning artifacts durable before a fresh session
- A **Decision ticket** may produce a resolved entry in the **Decision ledger**

## Flagged ambiguities

- "backlog" was previously used to mean both the *tool* hosting issues and the *body of work* inside it. Resolved: the tool is the **Issue tracker**; "backlog" is no longer used as a domain term.
- "backlog backend" / "backlog manager". Resolved: collapsed into **Issue tracker**.
