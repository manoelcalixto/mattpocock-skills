# Separate upstream skills from the native Codex plugin

The `skills/` tree will track the upstream skill library, while one native Codex plugin will contain physical skill files adapted for Codex. This replaces the Codex plugin deferral in [ADR 0002](0002-ship-as-a-claude-code-plugin.md): the plugin needs a curated, self-contained skill tree, and the user chose to maintain Codex-specific behavior in that distribution instead of modifying the upstream base. Upstream updates therefore require reviewing their effect on the plugin copies.
