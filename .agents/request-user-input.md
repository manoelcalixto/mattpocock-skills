# Codex-native user input

A **Decision prompt** is a bounded, user-owned choice among mutually exclusive options. It is not a discoverable fact, a request for free-form data, or a Codex tool-execution permission prompt.

## Enable the Default-mode feature

Codex exposes `request_user_input` in Plan mode. The `default_mode_request_user_input` feature also exposes it in Default mode. The feature is under development, disabled by default, and may change.

Enable it persistently:

```bash
codex features enable default_mode_request_user_input
```

Or set it in `~/.codex/config.toml`:

```toml
[features]
default_mode_request_user_input = true
```

For one invocation, pass `--enable default_mode_request_user_input` to `codex`.

The request tool is registered by default unless the user explicitly disables it:

```toml
[tools.experimental_request_user_input]
enabled = false
```

A skill must never enable the feature, edit Codex configuration, or invent the tool. Use `request_user_input` only when it is listed among the available tools for the current turn.

## Decide whether to prompt

Explore before asking. Resolve repository and environment facts with read-only inspection.

- In an explicitly invoked interview, every material user-owned decision is a **Decision prompt**; assuming it would defeat the interview.
- In other flows, prompt only when the decision materially changes the result and a safe inference is unavailable. Otherwise, state the reasonable assumption and continue.
- Ask free-form questions in concise plain text. Use the native tool only when two or three meaningful, mutually exclusive options represent the choice.
- Keep Codex tool-execution approvals, authentication, and secret entry in their dedicated flows. A user-owned workflow decision to authorize an irreversible outcome is a blocking **Decision prompt**, but it never replaces any permission prompt Codex also requires for the eventual tool call.

## Build the native prompt

Preserve the cadence defined by the owning skill:

- Prefer one question.
- Use up to three only when the skill already defines one joint checkpoint of independent decisions.
- Keep `grilling` at one question per turn.
- In `batch-grill-me`, use one native call for a frontier of at most three option-shaped decisions. When the frontier is larger or contains open decisions, preserve the complete round as numbered plain-text questions with a recommendation for each; do not turn it into a textual option menu.

For every native question:

- Use a stable `snake_case` `id`.
- Keep `header` to 12 characters or fewer.
- Write one sentence for `question`.
- Provide two or three mutually exclusive options.
- Put the recommended option first and suffix its label with `(Recommended)`.
- Keep labels to one to five words and descriptions to one short trade-off sentence.
- Omit `Other`; the client adds it.

## Wait or auto-resolve

Omit `autoResolutionMs` by default. A blocking decision waits for an explicit answer.

Set `autoResolutionMs` only when the preference is useful but non-blocking and the skill can safely continue with its best judgment if the user does not answer. The supported range is 60,000–240,000 milliseconds: use 60,000 for lightly helpful context and reserve longer windows for answers that would materially improve the work.

Interview decisions, approval/revision gates, irreversible choices, and any answer required before mutation are blocking.

## Fallback

When `request_user_input` is unavailable, ask one concise plain-text question and express the recommendation in prose. Do not render a multiple-choice menu in the assistant message.

The `batch-grill-me` frontier rule above is the only cadence exception: it may ask several numbered questions in one textual round, but each remains an open question with a recommendation rather than a textual option menu.

## Ownership

The skill that creates a **Decision prompt** owns the context pointer to this file. A skill that delegates the interaction to another skill inherits the owner's behavior and does not repeat the pointer.

## Codex sources

- [`default_mode_request_user_input` feature definition](https://github.com/openai/codex/blob/main/codex-rs/features/src/lib.rs)
- [Mode availability derived from the feature](https://github.com/openai/codex/blob/main/codex-rs/tools/src/tool_config.rs)
- [`request_user_input` schema and timeout bounds](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input_spec.rs)
- [Default collaboration-mode instructions](https://github.com/openai/codex/blob/main/codex-rs/collaboration-mode-templates/templates/default.md)
