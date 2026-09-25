Skills are organized into bucket folders under `skills/`:

- `engineering/`: daily code work
- `productivity/`: daily non-code workflow tools
- `misc/`: kept around but rarely used, not promoted
- `in-progress/`: beta: public on purpose, feedback wanted, not shipped in the plugin
- `deprecated/`: no longer used

The `skills/` tree tracks `upstream/main`. Do not put fork-only behavior there. Every skill in `engineering/` or `productivity/` (the **promoted** buckets) must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json`'s `skills` array (the Claude Code plugin ships exactly the upstream promoted set). Skills in `misc/`, `in-progress/`, and `deprecated/` must not appear in either.

The native Codex plugin lives at [`plugins/mattpocock-skills-codex/`](./plugins/mattpocock-skills-codex/). Its `skills/` directory contains physical Codex-adapted copies of every upstream promoted skill and the fork-only `planning-context` skill, including each skill's scripts, references, and `agents/openai.yaml`. Codex users install this plugin through [`.agents/plugins/marketplace.json`](./.agents/plugins/marketplace.json). The plugin is the recommended Codex route; do not recommend installing the unadapted `skills/` tree directly into Codex. Keep `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, and `package.json` at the same version with `npm run check-plugin-version`.

When asked to update from upstream, fetch `upstream/main` and compare it with the recorded baseline in [`.agents/upstream-skills-ref`](./.agents/upstream-skills-ref). Review every changed promoted skill and resource, plus additions, removals, renames, invocation policy, router coverage, and Claude manifest changes. Bring `skills/` and the Claude plugin back to the new upstream state, then adapt the affected physical Codex plugin copies with judgment. Preserve Codex-only behavior, especially Planning, installed resource paths, and invocation policy. Update the baseline only after the plugin passes validation. Do not overwrite plugin copies from upstream automatically. Use `python3 scripts/compare-upstream-skills.py` to inspect the changed source files and their plugin destinations. If a changed upstream skill affects a promoted skill's human docs, keep the upstream docs in sync; document Codex differences separately in [`docs/codex-plugin.md`](./docs/codex-plugin.md).

Install commands are copied verbatim from [.agents/install-block.md](./.agents/install-block.md). `.claude-plugin/marketplace.json` makes the repo its own single-plugin marketplace (a fallback the install block explains, not the documented route). Run `claude plugin validate . --strict` after touching either Claude manifest. Validate the Codex manifest and packaged skills with the plugin validator and a real installation in an isolated Codex profile. [ADR 0004](./.agents/adr/0004-separate-upstream-skills-from-codex-plugin.md) records the current distribution decision; [ADR 0002](./.agents/adr/0002-ship-as-a-claude-code-plugin.md) is historical.

Each skill entry in the top-level `README.md` must link the skill name to its `SKILL.md`.

Each bucket folder has a `README.md` that lists every skill in the bucket with a one-line description, with the skill name linked to its `SKILL.md`. The promoted buckets' `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**; non-promoted bucket `README.md`s (`misc/`, `in-progress/`) use a flat list.

Skills in `engineering/` and `productivity/` also have a human-facing docs page at `docs/<bucket>/<skill-name>.md` (the docs tree mirrors those two bucket folders under `skills/`). The published URL is `https://aihero.dev/skills-<skill-name>` regardless of bucket: the docs path is repo organisation only. When you add, rename, or change the behaviour of a skill in `engineering/` or `productivity/`, create or re-sync its docs page following [.agents/writing-docs.md](./.agents/writing-docs.md). A finished page carries four sections: **What it does**, **When to reach for it**, **Common questions**, and **It's working if**. `writing-docs.md` holds the template, the section order, and where to hunt for the questions. Skills in the non-promoted buckets (`misc/`, `in-progress/`, `deprecated/`) get **no** docs page.

In the upstream `skills/` tree, invocation follows upstream frontmatter. In the Codex plugin copies, user-invoked skills use `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; remove unsupported `disable-model-invocation` frontmatter. Model-invoked skills remain model- or user-reachable. See [.agents/invocation.md](./.agents/invocation.md).

[`ask-matt`](./skills/engineering/ask-matt/SKILL.md) is the upstream router. The Codex plugin carries its adapted copy. Whenever a promoted skill changes how it fits the flows, review both routers. Keep the upstream router aligned with the upstream catalog and the plugin router aligned with the plugin catalog, including `planning-context`.

To (re)link upstream skills into the local Claude development directory (`~/.claude/skills`), run `scripts/link-skills.sh`. It removes only symlinks owned by this repository from the legacy Codex directory (`~/.agents/skills`); it leaves other installed skills alone. Use the native plugin for local Codex development.

No em-dashes anywhere in this repo's prose (`SKILL.md` files, docs, `README.md`, `CHANGELOG.md`, ADRs, changesets, code comments). Where a sentence reaches for one, rewrite it instead with a comma, colon, period, parentheses, or a conjunction, whichever the sentence actually wants; never do a blind character substitution.

## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues on `manoelcalixto/mattpocock-skills`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage role names are used unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout with a root `CONTEXT.md` and repository-wide ADRs in `.agents/adr/`. See `docs/agents/domain.md`.
