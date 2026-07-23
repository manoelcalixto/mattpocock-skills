---
name: codex-git-guardrails
description: Set up Codex hooks that block dangerous git commands before execution. Use when the user wants to prevent push, hard reset, clean, destructive branch deletion, checkout, or restore operations in Codex.
---

# Codex Git Guardrails

Install a `PreToolUse` hook that intercepts Codex's `Bash` tool alias and rejects dangerous git commands with exit code 2.

When installation scope or customization becomes a **Decision prompt**, apply the [Codex-native user-input contract](../../../.agents/request-user-input.md).

The bundled script blocks:

- `git push`, including force pushes.
- `git reset --hard`.
- `git clean -f` and `git clean -fd`.
- `git branch -D`.
- `git checkout .` and `git restore .`.

## Install

Ask whether the hook should apply to this project or every project:

- Project config: `.codex/config.toml`; script: `.codex/hooks/block-dangerous-git.sh`.
- Global config: `~/.codex/config.toml`; script: `~/.codex/hooks/block-dangerous-git.sh`.

Copy [scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh) to the selected script path and make it executable. Resolve the script's absolute path for the config.

Confirm `jq` and `python3` are available because the hook uses them to decode the Codex event and tokenize shell commands without evaluating them. Install the narrow missing dependency when the environment permits it; otherwise stop and tell the user what is missing.

Parse the selected TOML file and preserve every existing field and hook. Add one `PreToolUse` matcher group with one command handler, unless an equivalent handler for the same absolute script path already exists:

```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"

[[hooks.PreToolUse.hooks]]
type = "command"
command = "<absolute-script-path>"
```

Project and user hooks run only when trusted. Tell the user to open `/hooks`, inspect the command and source path, and enable/trust it if Codex prompts.

Ask whether the blocked patterns need customization, then edit the copied script rather than the bundled source.

## Verify

Run the installed script directly with hook-shaped JSON:

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <absolute-script-path>
```

It must exit 2 and write a `BLOCKED` reason to stderr. Repeat with `git status`; it must exit 0. Run `bash -n <absolute-script-path>` before finishing.
