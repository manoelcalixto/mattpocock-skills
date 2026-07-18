---
"mattpocock-skills": minor
---

Make the fork Codex-native and installable from its own marketplace as `mattpocock-skills@manoelcalixto`.

- Add `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`, shipping exactly the promoted skills from `manoelcalixto/mattpocock-skills`.
- Replace legacy-harness frontmatter, invocation, setup, hooks, and session guidance with Codex contracts and `$skill` syntax.
- Add adaptive V1/V2 multi-agent orchestration, native session routing, and Codex handoff/guardrail skills.
- Add repository validation and automatic plugin/package version synchronization.
