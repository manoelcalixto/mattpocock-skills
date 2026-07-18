# Model-invoked vs user-invoked

Every non-deprecated `SKILL.md` uses Codex's native skill contract: frontmatter contains only `name` and `description`, and `agents/openai.yaml` owns product-specific UI and invocation policy.

- **User-invoked** — reachable only when the human explicitly types the installed name. For this plugin that is `$mattpocock-skills:skill-name`; a standalone skill uses `$skill-name`. Set `policy.allow_implicit_invocation: false`. Keep the description human-facing and concise.
- **Model-invoked** — reachable by the model or by an explicit installed name. Omit the policy block. Keep rich trigger language in the description so automatic invocation is reliable.

Every `agents/openai.yaml` contains quoted `interface.display_name`, `interface.short_description`, and `interface.default_prompt`. The default prompt is one short sentence that explicitly mentions `$mattpocock-skills:skill-name` for a promoted plugin skill or `$skill-name` for a standalone non-promoted skill.

A user-invoked skill cannot invoke another user-invoked skill. When a flow needs one, tell the human its exact installed name. A user-invoked skill may directly use a model-invoked skill.

## Dependencies between skills

Express internal dependencies as harness-neutral prose, such as "Use the `grilling` skill." Reserve `$mattpocock-skills:skill-name` or standalone `$skill-name` for text the human should type. Shared references live with the skill that owns them; other skills use the owning skill rather than deep-linking across folders.

## Passive vs active domain work

Reading `CONTEXT.md` for vocabulary is a lightweight habit, not invocation of `domain-modeling`. Use the `domain-modeling` skill only for active work: challenging terms, testing scenarios, updating the glossary, or recording ADRs.
