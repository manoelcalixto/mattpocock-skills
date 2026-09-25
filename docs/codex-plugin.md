# Codex plugin

The native `mattpocock-skills-codex` plugin contains physical Codex-adapted copies of the 25 promoted upstream skills and the fork-only `planning-context` skill. Its `skills/` tree is independent of the upstream `skills/` tree. Scripts, references, and Codex invocation metadata travel with each installed skill.

## Install

```bash
codex plugin marketplace add manoelcalixto/mattpocock-skills
codex plugin add mattpocock-skills-codex@mattpocock-skills
```

Invoke an explicit skill with `$mattpocock-skills-codex:<skill-name>`. Start with `$mattpocock-skills-codex:setup-matt-pocock-skills` in a new repository. The plugin is the recommended Codex installation. The upstream skill tree and Claude plugin remain available for their respective consumers.

For development against this checkout, add the local repository path as the marketplace source instead of the GitHub repository. Install the plugin into an isolated `CODEX_HOME` when validating changes. The installed copy is cached under that profile's `plugins/cache/` directory.

## Planning helper

The Planning script is bundled at `skills/planning-context/scripts/planning_context.py` inside the installed plugin. Resolve the installed `planning-context` skill path from the Codex skill catalog and invoke that script by absolute path with `--repo <target-repository>`. The script uses the Python standard library. The target repository does not need a copy of this skill or script.

## Updating from upstream

The recorded baseline is [`.agents/upstream-skills-ref`](../.agents/upstream-skills-ref). Fetch `upstream/main`, then run `python3 scripts/compare-upstream-skills.py` to list changes since that baseline and the Codex skill directory each promoted source change affects. Review the changed upstream content and adapt the plugin copy manually. Update the baseline only after validating the resulting plugin. The full maintenance contract is in [AGENTS.md](../AGENTS.md).

Run `npm run test:codex-plugin`, `npm run test:planning-context`, `npm run check-plugin-version`, `claude plugin validate . --strict`, and the Codex plugin validator. For a release, install the built plugin into an isolated Codex profile and check skill discovery, explicit invocation metadata, and the Planning helper against a separate consumer repository.
