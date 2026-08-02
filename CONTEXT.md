# Matt Pocock Skills

A collection of skills and workflow entry points for Codex. Promoted skills are available through both managed and editable installation and consume per-repo configuration emitted by `setup-matt-pocock-skills`.

## Language

**Managed installation**:
The native Codex plugin distribution. Codex installs and updates the promoted skill set as a managed bundle.
_Avoid_: Native installation, read-only installation

**Editable installation**:
The `skills.sh` distribution for Codex users who want local skill files they can modify and update deliberately.
_Avoid_: Universal installation, cross-agent installation

**Promoted skill**:
A production-ready skill included in both the **Managed installation** and the **Editable installation**.
_Avoid_: Shipped skill, public skill

**Workbench skill**:
A preserved draft, personal, miscellaneous, or deprecated skill kept outside the installable `skills/` tree.
_Avoid_: Non-promoted skill, hidden skill, unshipped skill

**Issue tracker**:
The tool that hosts a repo's issues — GitHub Issues, Linear, a local `.scratch/` markdown convention, or similar. Skills like `to-tickets`, `to-spec`, and `triage` read from and write to it.
_Avoid_: backlog manager, backlog backend, issue host

**Issue**:
A single tracked unit of work inside an **Issue tracker** — a bug, task, spec, or slice produced by `to-tickets`.
_Avoid_: ticket (use only when quoting external systems that call them tickets, or for a **Decision ticket** — see below)

**Decision ticket**:
A `wayfinder` unit — a child **Issue** of a `wayfinder:map` holding a *question* whose resolution is a decision, not a slice of a build to execute. The **decision** qualifier is what keeps it distinct from an implementation ticket; `wayfinder` introduces the term, then uses "ticket".

**Triage role**:
A canonical state-machine label applied to an **Issue** during triage (e.g. `needs-triage`, `ready-for-afk`). Each role maps to a real label string in the **Issue tracker** via `docs/agents/triage-labels.md`.

## Relationships

- An **Issue tracker** holds many **Issues**
- An **Issue** carries one **Triage role** at a time
- A **Decision ticket** is an **Issue** (a child of a `wayfinder:map`)

## Flagged ambiguities

- "backlog" was previously used to mean both the *tool* hosting issues and the *body of work* inside it — resolved: the tool is the **Issue tracker**; "backlog" is no longer used as a domain term.
- "backlog backend" / "backlog manager" — resolved: collapsed into **Issue tracker**.
