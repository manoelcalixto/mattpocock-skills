# Ship the fork as a native Codex plugin

The fork targets Codex only. It must be installable as a managed plugin from the fork's own marketplace while shipping exactly the promoted `engineering/` and `productivity/` buckets.

Current Codex accepts `.codex-plugin/plugin.json`, discovers `.agents/plugins/marketplace.json`, accepts `skills` as either a path or an array of paths, and identifies an installation as `<plugin>@<marketplace>`. A root marketplace entry with `source.path: "./"` resolves to the repository root.

## Decision

- Publish the marketplace as `manoelcalixto` from `manoelcalixto/mattpocock-skills`.
- Keep the plugin name `mattpocock-skills`, producing `mattpocock-skills@manoelcalixto`.
- List every promoted skill explicitly in the manifest and exclude every other bucket.
- Keep `AGENTS.md` canonical and use Codex-native `$skill` invocation, metadata, hooks, sessions, and multi-agent tools.
- Preserve attribution to Matt Pocock while identifying Manoel Calixto as maintainer of the Codex fork.

## Invariants

- The plugin manifest, promoted READMEs, docs tree, and actual promoted directories contain the same set.
- The plugin version matches `package.json`.
- Installation uses `codex plugin marketplace add manoelcalixto/mattpocock-skills`, then `codex plugin add mattpocock-skills@manoelcalixto`.
- Deprecated material may retain historical legacy-harness references; active material may not.
