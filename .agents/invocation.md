# Model-invoked vs user-invoked

Every `SKILL.md` in this repo is a skill. The upstream `skills/` tree and the native Codex plugin use different invocation metadata, but preserve the same user versus model boundary:

- **User-invoked**: reachable **only by the human typing its name**. The upstream source uses `disable-model-invocation: true` in frontmatter (Claude Code). The Codex plugin copy omits that unsupported key and sets `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. The `description` is **human-facing**: a one-line summary read by a person browsing skills. Strip trigger lists.
- **Model-invoked**: reachable by **model or user**. The default: omit `disable-model-invocation` and the `policy` block from `agents/openai.yaml`. The `description` is **model-facing** and keeps rich trigger phrasing ("Use when the user wants…, mentions…, asks for…") so auto-invocation fires. The test for whether a skill should stay model-invoked: _could the model usefully reach for this autonomously?_ (Reuse is the reason to extract a skill, not the test.)

Each harness excludes a user-invoked skill from the model's reach in its own way, so nothing but the human can fire it: no other skill can. A user-invoked skill may follow model-invoked skills, but it can never reach another user-invoked skill implicitly.

Every skill also carries an `agents/openai.yaml` beside its `SKILL.md`. The Codex plugin copy holds Codex UI metadata and, for user-invoked skills, `policy.allow_implicit_invocation: false`. Upstream metadata is preserved as upstream provides it. Keep the invocation classification in sync across the two distributions.

Bucket `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**.

## Dependencies between them

Upstream skills keep their own dependency convention. Codex plugin copies direct the agent to read and follow an installed model-invoked companion skill by its namespaced `mattpocock-skills-codex:<name>` identity. Do not assume a separate Skill tool exists in Codex. Shared reference docs live inside the skill that owns them, and bundled scripts are resolved from the installed skill directory.

This is about **operative** instructions: a skill's own steps telling the agent to follow another skill now. Router prose names skills for a human to pick and does not invoke them. In the Codex plugin router, use namespaced `$mattpocock-skills-codex:<name>` labels for those choices.

When a step needs two model-invoked companion skills, follow them separately in the stated order. Keep each skill's ownership and stopping conditions distinct.

This convention only holds when the companion skill is **model-invoked**. A user-invoked skill cannot be reached implicitly. When a step requires one, let the user invoke it by name unless their existing task instruction already authorizes that setup work.

## Passive vs active domain work

Merely _reading_ `CONTEXT.md` for vocabulary is a one-line prose pointer, not the `domain-modeling` skill. Only the active build/sharpen discipline (challenge terms, edge-case scenarios, write ADRs, update `CONTEXT.md` inline) is `domain-modeling`.
