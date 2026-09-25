# The canonical install block

One install story, one wording. `README.md`, `.changeset/*`, and every page under `docs/` must use the applicable route below. Change it here first, then propagate.

`mattpocock-skills` is listed in **Claude Code's official marketplace** (configured name `claude-plugins-official`, source repo `anthropics/claude-plugins-official`), which every Claude Code install has out of the box. There is no marketplace to add first. Official Anthropic marketplaces have auto-update enabled by default ([discover-plugins](https://code.claude.com/docs/en/discover-plugins)), so "updates arrive automatically" is a true claim, not a hope.

## Claude Code: the plugin

<canonical-block name="claude-code">

```bash
claude plugins install mattpocock-skills
```

Or, from inside a session:

```
/plugin install mattpocock-skills
```

It's in Claude Code's official marketplace, so there's nothing to add first, and updates arrive automatically.

</canonical-block>

## Codex: the native plugin

The Codex plugin ships physical copies adapted from the upstream skills plus `planning-context`. Its public marketplace is this fork. Use this route for Codex:

<canonical-block name="codex-plugin">

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills-codex@mattpocock-skills
```

Invoke a skill as `$mattpocock-skills-codex:<skill-name>`.

</canonical-block>

## Other agents and editable copies: skills.sh

[skills.sh](https://skills.sh/mattpocock/skills) copies the upstream skill files into the project. Use the whole-set form on `README.md`:

<canonical-block name="skills-sh-whole-set">

```bash
npx skills@latest add mattpocock/skills
```

Pick the skills you want and the target harness. For Codex, use the native plugin above to get the adapted skills. For other agents, make sure `setup-matt-pocock-skills` is among the selected skills.

</canonical-block>

…and the single-skill form wherever one skill is named on its own. Note that **`docs/` pages are not a consumer of this block**: ai-hero renders the install widget above the body, so a page that writes the commands out duplicates it. See [writing-docs.md](./writing-docs.md).

<canonical-block name="skills-sh-one-skill">

```bash
npx skills@latest add mattpocock/skills --skill=<name>
```

```bash
npx skills@latest update <name>
```

</canonical-block>

`skills@latest` is the pinned spelling in all three. The pages under `docs/` used to carry their own copy of these commands; those blocks are now deleted rather than corrected, because the site renders the install commands itself.

## Avoid duplicate installations

The plugins are managed bundles. skills.sh writes files you own and edit. Do not install the same skills through the plugin and skills.sh in one harness.

## Not the install story

`.claude-plugin/marketplace.json` makes the repo its own single-plugin marketplace (`/plugin marketplace add mattpocock/skills`, then `/plugin install mattpocock-skills@mattpocock`). The official listing supersedes it. It is kept as a fallback for installing the repo directly (an unreleased commit, or a fork), and is **not** documented to users.
