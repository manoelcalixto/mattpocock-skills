---
status: accepted
---

# Ship the Codex-focused fork as a root plugin

This fork supports Codex through two distributions: a managed native plugin and an editable `skills.sh` install. The repository root is the single `mattpocock-skills` plugin, the `manoelcalixto` marketplace points to it with `source.path: "./"`, and only production-ready engineering and productivity skills remain under `skills/`; preserved drafts, personal utilities, miscellaneous experiments, and deprecated skills live under `workbench/` so recursive Codex discovery cannot ship them.

## Considered options

- Nesting the plugin under `plugins/mattpocock-skills/` matches multi-plugin marketplace repositories, but pushes promoted skills too deep for the editable installer's default discovery and would require `--full-depth`.
- Keeping every bucket under `skills/` would expose workbench material through the native plugin.
- Maintaining a generated flat copy would create a second source of truth.

## Consequences

- Claude-specific manifests, frontmatter, invocation syntax, and repository guidance are removed from the promoted product surface. Workbench files retain their inherited form outside plugin and editable-installer discovery.
- The existing engineering and productivity category paths remain stable for editable installs and documentation.
- The plugin remains named `mattpocock-skills`, while the marketplace and repository URL identify the `manoelcalixto` fork.
- Plugin and package versions advance together, beginning with the Codex-only `2.0.0` release.
