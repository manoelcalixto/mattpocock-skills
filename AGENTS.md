Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `misc/` — kept around but rarely used, not promoted
- `personal/` — tied to the maintainer's setup, not promoted
- `in-progress/` — drafts not yet ready to ship
- `deprecated/` — no longer used

Every skill in `engineering/` or `productivity/` (the **promoted** buckets) must have a reference in the top-level `README.md`, an entry in `.codex-plugin/plugin.json`'s `skills` array, and a human-facing docs page at `docs/<bucket>/<skill-name>.md`. The Codex plugin ships exactly the promoted set. Skills in `misc/`, `personal/`, `in-progress/`, and `deprecated/` must not appear in the top-level README or plugin and get no docs page.

The repo is its own Codex marketplace. `.agents/plugins/marketplace.json` exposes `mattpocock-skills@manoelcalixto` from this repository root. Keep its source as `./`, its marketplace name as `manoelcalixto`, and its policies explicit. `.codex-plugin/plugin.json`'s `version` must match `package.json`; `npm run version` synchronizes them. Run `npm run validate` after changing either manifest. See [.agents/adr/0003-ship-the-fork-as-a-codex-plugin.md](./.agents/adr/0003-ship-the-fork-as-a-codex-plugin.md).

Each skill entry in any README must link the skill name to its `SKILL.md`. Each bucket README lists every skill in that bucket with a one-line description. Promoted bucket READMEs group entries into **User-invoked** and **Model-invoked**; non-promoted bucket READMEs use a flat list.

The published docs URL remains `https://aihero.dev/skills-<skill-name>` regardless of bucket. When adding, renaming, or changing a promoted skill, create or resync its page following [.agents/writing-docs.md](./.agents/writing-docs.md). Repository source links in docs point to this fork.

Every non-deprecated `SKILL.md` has only `name` and `description` in frontmatter. A skill is user-invoked when its `agents/openai.yaml` sets `policy.allow_implicit_invocation: false`; otherwise it is model-invoked. Every `agents/openai.yaml` has a `default_prompt` that explicitly mentions the installed invocation: `$mattpocock-skills:<skill-name>` for promoted plugin skills and `$<skill-name>` for standalone non-promoted skills. See [.agents/invocation.md](./.agents/invocation.md).

[`ask-matt`](./skills/engineering/ask-matt/SKILL.md) maps every user-reachable skill and how the flows relate. Whenever a user-reachable skill is added, renamed, removed, or changes place in a flow, update `ask-matt` and its docs page.

To relink every non-deprecated skill into Codex's local harness directory, run `scripts/link-skills.sh`. Each entry is a symlink into this repo, so a `git pull` keeps installed skills current; rerun the script after adding, removing, or renaming a skill.
