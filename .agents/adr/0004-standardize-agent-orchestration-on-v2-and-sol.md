# Standardize agent orchestration on MultiAgent V2 and GPT-5.6 Sol

Active skills use only Codex MultiAgent V2 and GPT-5.6 Sol so orchestration has one tool contract, one model family member, and workflow-controlled delegation. Supporting V1 or selecting cheaper model tiers would preserve compatibility or reduce cost, but would also multiply branches and make behavior differ between workers; `ultra` would add automatic delegation outside the workflow's explicit tree.

## Decision

- Require the root agent to run `gpt-5.6-sol` before orchestration and set every spawned agent's model explicitly to `gpt-5.6-sol`.
- Recommend the root's reasoning effort from the complexity of decomposition and integration, but do not make that effort a prerequisite; only the root model is a hard gate.
- Use `fork_turns="none"` by default and a positive turn count only when recent context is essential. Never use `fork_turns="all"`, because full-history forks cannot enforce the explicit model override.
- Set an explicit reasoning effort on every spawn, chosen adaptively by task shape from `low`, `medium`, `high`, `xhigh`, or `max`. Never spawn with `ultra`; reserve recursive delegation for workflows that explicitly authorize it.
- Keep the complete effort rubric and escalation policy in `orchestrate-agents`; consuming workflows declare only a stable starting effort when their activity shape justifies one.
- Correct missing context or an imprecise brief through messaging or a follow-up at the existing effort. When reasoning depth is the actual failure, replace the worker at exactly one higher effort instead of running duplicate attempts concurrently; reuse an agent only when the next activity needs the same effort and its existing context.
- Let an authorized child create and integrate its own descendants. Bound the tree by the session's shared concurrency capacity rather than an artificial depth limit, and reserve slots when recursion is expected.
- Keep current workflow tree shapes non-recursive; recursive delegation remains opt-in for a workflow or an explicit user request.
- Treat `wait_agent` as an event-driven mailbox wait. Do not use sleeps, short-timeout wait loops, or repeated `list_agents` calls for polling.
- If MultiAgent V2 is unavailable or a spawn fails, fall back inline or sequentially when the result can be preserved and disclose lost isolation or parallelism. Stop and explain the blocker when isolation or parallelism is part of the workflow's semantics; never retry through V1 or by switching models.
- Keep every non-deprecated skill, README, and public docs page consistent with this V2-only contract.

## Consequences

The orchestration surface becomes smaller and deterministic, while task effort and recursive tree shape remain adaptive. Active workflows no longer run on Codex V1, non-Sol roots must switch models before delegating, and unavailable V2 capacity may increase latency through an explicit inline or sequential fallback.
