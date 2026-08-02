# Invocation

Every promoted `SKILL.md` carries a standards-compliant `name` and `description`. Every promoted skill supports both Codex invocation paths:

- **Explicit** — the human selects or types `$skill-name`.
- **Implicit** — Codex selects the skill when its description matches the task.

Omit the invocation `policy` block from every promoted `agents/openai.yaml`; implicit invocation is the default. Write each `SKILL.md` description as a concise model-facing trigger with concrete conditions so Codex can choose the skill reliably.

Every promoted skill carries `agents/openai.yaml` beside `SKILL.md`. It holds `interface.display_name`, `interface.short_description`, and an `interface.default_prompt` that explicitly names `$skill-name`.

Bucket `README.md`s and the top-level `README.md` may group skills into **Workflow entry points** and **Reusable disciplines** for orientation. Those groups do not change invocation behavior.

## Dependencies between them

Dependencies are expressed with Codex's **`$skill-name` syntax** ("Run `$grilling`"), not deep `../other-skill/FILE.md` cross-references. Shared reference docs live inside the skill that owns them; other skills reach that material by invoking the skill, not by linking across folders.

## Passive vs active domain work

Merely _reading_ `CONTEXT.md` for vocabulary is a one-line prose pointer, not the `domain-modeling` skill. Only the active build/sharpen discipline (challenge terms, edge-case scenarios, write ADRs, update `CONTEXT.md` inline) is `domain-modeling`.
