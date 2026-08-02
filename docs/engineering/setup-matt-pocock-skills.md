# Setup Matt Pocock Skills

## Install

Native Codex plugin (installs all promoted skills):

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Editable single-skill install:

```bash
npx skills add manoelcalixto/mattpocock-skills --skill=setup-matt-pocock-skills
```

Select Codex when prompted. Use `npx skills update setup-matt-pocock-skills` to refresh an editable install.

[Skill source](../../skills/engineering/setup-matt-pocock-skills/SKILL.md)

## What it does

`setup-matt-pocock-skills` teaches one repo how the engineering skills should behave in it — where issues live, what the triage labels are called, and where the domain docs sit — and records those answers as **config** the other skills read.

It writes config, it does not hard-code behaviour. The engineering chain assumes three files under `docs/agents/` exist; this skill is the one-time bootstrap that produces them, discovered from your actual repo (`git remote`, existing labels, existing `CONTEXT.md`) and confirmed with you rather than guessed. It is prompt-driven — explore, present what it found, confirm, then write — not a deterministic scaffold.

## When to reach for it

Type `$setup-matt-pocock-skills`, or Codex may select it automatically when a repository needs the issue-tracker, triage, and domain-document conventions required by the engineering workflows.

Reach for it **once per repo, before the first use of any other engineering skill**. If [triage](../engineering/triage.md), [to-spec](../engineering/to-spec.md), or [to-tickets](../engineering/to-tickets.md) start guessing where your issues live or applying labels that don't exist, they haven't been set up here yet. Re-run it only to switch issue trackers or start over — day-to-day tweaks are just edits to `docs/agents/*.md`.

## The three decisions

It leads each with a recommended answer you can accept in a word, and skips whatever it can already infer — so most runs are a couple of quick confirmations:

- **Issue tracker** — where work is tracked, so `triage`/`to-spec`/`to-tickets` know whether to call `gh`, `glab`, write markdown under `.scratch/`, or follow a workflow you describe. GitHub, GitLab, local markdown, or other. (It proposes the one that matches your `git remote`.)
- **Triage labels** — asked only if the `triage` skill is installed, and then just: keep the default labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)? Say no only if your tracker already uses other names, so `triage` applies real ones instead of creating duplicates.
- **Domain docs** — assumed single-context (one `CONTEXT.md` + `docs/adr/` at the root), which fits almost every repo; it only raises a multi-context map when it spots monorepo signals.

The output is a set of files under `docs/agents/` — `issue-tracker.md`, `domain.md`, and `triage-labels.md` when `triage` is installed — plus an `## Agent skills` block in the root `AGENTS.md` pointing to them. Those files are the shared substrate the rest of the toolkit stands on.

## It's working if

- `issue-tracker.md` and `domain.md` land under `docs/agents/` (plus `triage-labels.md` when `triage` is installed), and an `## Agent skills` section appears in your root `AGENTS.md`.
- The tracker it proposes matches your real `git remote`, and the labels match strings that already exist in your repo.
- Afterwards, `triage` and `to-tickets` act on the right place with the right labels instead of asking or guessing.

## Where it fits

`setup-matt-pocock-skills` is a **run-once setup** — the foundation the whole engineering set stands on, not a step you repeat. Its neighbours are the skills that read what it writes: [triage](../engineering/triage.md), because it applies the label vocabulary configured here, and [to-spec](../engineering/to-spec.md) / [to-tickets](../engineering/to-tickets.md), because they publish into the issue tracker configured here. Run it first; everything downstream assumes it has. When you're unsure which skill or flow fits, [ask-matt](../engineering/ask-matt.md) routes you.
