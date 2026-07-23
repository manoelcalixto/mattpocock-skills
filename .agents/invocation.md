# Model-invoked vs user-invoked

Every non-deprecated `SKILL.md` uses Codex's native skill contract: frontmatter contains only `name` and `description`, and `agents/openai.yaml` owns product-specific UI and invocation policy.

- **User-invoked** — reachable only when the human explicitly types the installed name. For this plugin that is `$mattpocock-skills:skill-name`; a standalone skill uses `$skill-name`. Set `policy.allow_implicit_invocation: false`. Keep the description human-facing and concise.
- **Model-invoked** — reachable by the model or by an explicit installed name. Omit the policy block. Keep rich trigger language in the description so automatic invocation is reliable.

Every `agents/openai.yaml` contains quoted `interface.display_name`, `interface.short_description`, and `interface.default_prompt`. The default prompt is one short sentence that explicitly mentions `$mattpocock-skills:skill-name` for a promoted plugin skill or `$skill-name` for a standalone non-promoted skill.

A user-invoked skill cannot invoke another user-invoked skill. When a flow needs one, tell the human its exact installed name. A user-invoked skill may directly use a model-invoked skill.

## Dependencies between skills

Express internal dependencies as harness-neutral prose, such as "Use the `grilling` skill." Reserve `$mattpocock-skills:skill-name` or standalone `$skill-name` for text the human should type. Skill-specific references live with the skill that owns them; repository-wide Codex contracts with no independent invocation live under `.agents/`. Other skills use an owning skill rather than duplicating its context pointers.

## Decision prompts

A skill that directly creates a bounded, user-owned choice points to a co-located `REQUEST-USER-INPUT.md`, synchronized from [the canonical Codex-native user-input contract](./request-user-input.md). Co-location keeps standalone copies self-contained; validation keeps the generated files from becoming independent sources of truth. Consumers that delegate the interaction inherit the owning skill's behavior and carry no copy.

## Passive vs active domain work

Reading `CONTEXT.md` for vocabulary is a lightweight habit, not invocation of `domain-modeling`. Use the `domain-modeling` skill only for active work: challenging terms, testing scenarios, updating the glossary, or recording ADRs.
