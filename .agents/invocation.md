# Model-invoked vs user-invoked

Every promoted `SKILL.md` carries a standards-compliant `name` and `description`. Codex's policy metadata decides who may reach it implicitly:

- **User-invoked** — reachable only when the human selects or types `$skill-name`. Set `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Write a concise human-facing description for the skill picker and keep autonomous trigger language out of it.
- **Model-invoked** — reachable by the model or the human. Omit the policy block from `agents/openai.yaml`, which leaves implicit invocation enabled. Write a model-facing description with concrete trigger language so Codex can choose it reliably.

A user-invoked skill may direct the human toward another user-invoked skill, but it cannot silently run that workflow. It may actively invoke model-invoked disciplines that form part of its own workflow.

Every promoted skill carries `agents/openai.yaml` beside `SKILL.md`. It holds `interface.display_name`, `interface.short_description`, and an `interface.default_prompt` that explicitly names `$skill-name`. User-invoked skills additionally carry `policy.allow_implicit_invocation: false`.

Bucket `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**.

## Dependencies between them

Dependencies are expressed with Codex's **`$skill-name` syntax** ("Run `$grilling`"), not deep `../other-skill/FILE.md` cross-references. Shared reference docs live inside the skill that owns them; other skills reach that material by invoking the skill, not by linking across folders.

## Passive vs active domain work

Merely _reading_ `CONTEXT.md` for vocabulary is a one-line prose pointer, not the `domain-modeling` skill. Only the active build/sharpen discipline (challenge terms, edge-case scenarios, write ADRs, update `CONTEXT.md` inline) is `domain-modeling`.
