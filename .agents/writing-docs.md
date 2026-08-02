# Writing skill pages

Every promoted skill has a human-facing GitHub page at `docs/<bucket>/<skill-name>.md`. The page orients a reader; it is not the skill and does not duplicate the agent-facing steps in `SKILL.md`.

Only `skills/engineering/` and `skills/productivity/` are promoted. Material under `workbench/` has no product page. When a promoted skill is added, renamed, moved, or changes behavior, create or update its corresponding page and remove stale pages.

Use repository-relative links throughout. A page links to its source as `../../skills/<bucket>/<name>/SKILL.md`; cross-skill links point to the matching file under `docs/engineering/` or `docs/productivity/`. Installation and source coordinates use `manoelcalixto/mattpocock-skills`.

## Page structure

Every page begins with this fixed frame:

````markdown
# <Display name>

## Install

Native Codex plugin (installs all promoted skills):

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills@manoelcalixto
```

Editable single-skill install:

```bash
npx skills add manoelcalixto/mattpocock-skills --skill=<name>
```

Select Codex when prompted. Use `npx skills update <name>` to refresh an editable install.

[Skill source](../../skills/<bucket>/<name>/SKILL.md)
````

Then use these sections:

- `## What it does` — one or two plain-language paragraphs. Lead with the one-sentence job and state the defining constraint that makes the skill differ from the obvious default.
- `## When to reach for it` — state the invocation mode and trigger boundary. For explicit workflows: "Type `$<name>`; Codex will not select it implicitly." For reusable disciplines: "Type `$<name>`, or Codex may select it automatically when the task fits."
- `## Prerequisites` — optional; include only for a required workspace, prior setup, or repository-specific tooling.
- One to three free-form sections — use the skill's own leading words and explain the artifact, loop, fork, or anti-pattern that makes it click.
- `## It's working if` — optional; a short list of crisp observable signals.
- `## Where it fits` — always present. Name its role in the larger flow, link the one or two relevant neighbors, and point to [ask-matt](../engineering/ask-matt.md) as the router.

Explain why and when, not the internal runbook. Keep pages short, use `$skill-name` for invocation, preserve actual Codex slash commands such as `/compact`, and make every relative link resolve from the page that contains it.

## Done when

- The page path mirrors the promoted skill path and begins with an H1.
- Both install modes and the relative source link name the correct repository, bucket, and skill.
- Invocation mode and trigger boundary match `agents/openai.yaml`.
- The defining constraint and leading vocabulary are visible without copying `SKILL.md`.
- `## Where it fits` links to relevant neighbors and the router.
- Every relative link resolves, and no historical `aihero.dev/skills-*` publishing URL remains.
