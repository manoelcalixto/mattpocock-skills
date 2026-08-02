# Repository Guidance

This fork packages Matt Pocock's skill set for Codex. Codex is the only supported agent host; active product guidance uses only Codex manifests, metadata, invocation syntax, and installation flows.

## Repository layout

- `skills/engineering/` and `skills/productivity/` contain the promoted skills distributed through both the native Codex plugin and `skills.sh`.
- `workbench/` preserves deprecated, in-progress, miscellaneous, and personal skills. Workbench skills are outside the plugin's configured skill surface, are not documented as product features, and are not included in promoted-skill validation.
- `docs/engineering/` and `docs/productivity/` contain the GitHub-native human documentation for promoted skills.
- `docs/adr/` contains architectural decision records.

Every promoted skill must be linked from the top-level `README.md` and its bucket `README.md`. A workbench skill must not appear as an installable skill in either place.

## Codex plugin

The repository root is the plugin root:

- `.codex-plugin/plugin.json` describes the `mattpocock-skills` plugin and points at `./skills/`.
- `.agents/plugins/marketplace.json` describes the `manoelcalixto` marketplace and points at the repository root with `source.path: "./"`.
- `package.json` and `.codex-plugin/plugin.json` must use the same release version.

The marketplace is Codex-only. Keep the plugin skills-only unless a future change genuinely requires an MCP server, app, hook, command, or asset.

After changing plugin metadata, validate from the repository root with:

```powershell
python C:\Users\msilvane\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .
```

The current helper scans only immediate children of `skills/`, so it reports `engineering` and `productivity` as missing `SKILL.md`. Those are known false positives for this accepted category layout; do not flatten the skills to satisfy them. Validate each actual skill directory and treat a successful Codex marketplace install with all 22 discovered skills as the authoritative plugin check.

## Skill authoring

Follow the Agent Skills specification and the Codex skill metadata contract:

- A promoted `SKILL.md` frontmatter contains only standard fields. In this repository, use `name` and `description` unless another standard field is genuinely required.
- The frontmatter `name` must match the skill directory.
- Use imperative instructions and keep `SKILL.md` concise. Put conditional detail in a directly linked sibling reference.
- Every promoted skill has `agents/openai.yaml` with `interface.display_name`, `interface.short_description`, and an `interface.default_prompt` that explicitly names `$skill-name`.
- User-invoked orchestrators set `policy.allow_implicit_invocation: false`; model-invoked disciplines omit the policy block.
- Refer to another skill with Codex's `$skill-name` syntax. Preserve real Codex slash commands such as `/compact` and third-party command syntax such as GitLab quick actions.
- When a workflow benefits from parallel or background subagents, use Codex collaboration tools when available and provide a clearly disclosed sequential fallback when they are unavailable.

See `.agents/invocation.md` for the invocation split.

Whenever a promoted skill is added, renamed, removed, or changes behavior:

1. Update its GitHub-native page using `.agents/writing-docs.md`.
2. Re-read `skills/engineering/ask-matt/SKILL.md` and update the router if the flow map changed.
3. Run both the Codex quick validator and the Agent Skills reference validator for every promoted skill.

## Documentation

Each promoted skill has one page at `docs/<bucket>/<skill-name>.md`. These pages are read on GitHub, use repository-relative links, teach `$skill-name` invocation, and include both native-plugin and editable-install instructions. They are orientation pages, not copies of the agent-facing workflow.

Source links and install commands target `manoelcalixto/mattpocock-skills`. Preserve upstream attribution and historical upstream changelog links.

Superseded ADRs and historical changelog entries preserve earlier decisions as evidence; they are not active product guidance. Keep their status explicit instead of rewriting history to match the current host.

## Router and setup

`skills/engineering/ask-matt/SKILL.md` is the router over every user-reachable workflow. A stale router is a product bug.

`skills/engineering/setup-matt-pocock-skills/SKILL.md` configures downstream repositories through `AGENTS.md` and `docs/agents/*.md`. Keep its output Codex-native.

## Releases

Changesets owns version pull requests and Git tags. Keep `.changeset/config.json` pointed at `manoelcalixto/mattpocock-skills`. When preparing a release, keep `package.json` and `.codex-plugin/plugin.json` synchronized and include user-visible Codex migration notes in `CHANGELOG.md`.

## Local maintainer links

Run `scripts/link-skills.sh` to relink every repository skill into `~/.agents/skills`. The script is a maintainer convenience, not a supported installer. Re-run it after adding, removing, or renaming any promoted or workbench skill.
