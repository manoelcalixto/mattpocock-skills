# Explicit `$mattpocock-skills:setup-matt-pocock-skills` pointer only for hard dependencies

Engineering skills depend on per-repo config seeded by `$mattpocock-skills:setup-matt-pocock-skills`. Some cannot function without knowing the issue tracker or label vocabulary; others use domain docs only to sharpen output and degrade gracefully without them.

- **Hard dependency** (`to-tickets`, `to-spec`, `triage`) — tell the human to run `$mattpocock-skills:setup-matt-pocock-skills` when the required mapping is absent. A skill cannot invoke this human-only prerequisite itself.
- **Soft dependency** (`diagnosing-bugs`, `tdd`, `improve-codebase-architecture`) — refer to the project's glossary and relevant ADRs without making setup a blocker.

This keeps soft dependencies lightweight while making truly required configuration explicit.
