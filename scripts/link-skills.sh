#!/usr/bin/env bash
set -euo pipefail

# Local Claude Code development links. Codex uses the native plugin instead.
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
claude_dest="$HOME/.claude/skills"
legacy_codex_dest="$HOME/.agents/skills"

remove_owned_links() {
  local dest="$1" target resolved
  [ -d "$dest" ] || return 0
  while IFS= read -r -d '' target; do
    resolved="$(readlink -f "$target" || true)"
    case "$resolved" in
      "$repo_root/skills/"*)
        rm -- "$target"
        echo "removed legacy link $target"
        ;;
    esac
  done < <(find "$dest" -mindepth 1 -maxdepth 1 -type l -print0)
}

for dest in "$claude_dest" "$legacy_codex_dest"; do
  if [ -L "$dest" ]; then
    resolved="$(readlink -f "$dest" || true)"
    case "$resolved" in
      "$repo_root"|"$repo_root/"*)
        echo "error: $dest points into this repository ($resolved)" >&2
        exit 1
        ;;
    esac
  fi
done

remove_owned_links "$legacy_codex_dest"
remove_owned_links "$claude_dest"
mkdir -p "$claude_dest"

while IFS= read -r -d '' skill_md; do
  source_dir="$(dirname "$skill_md")"
  skill_name="$(basename "$source_dir")"
  target="$claude_dest/$skill_name"
  if [ -e "$target" ] || [ -L "$target" ]; then
    echo "error: refusing to replace existing $target" >&2
    exit 1
  fi
  ln -s -- "$source_dir" "$target"
  echo "linked $skill_name -> $source_dir ($claude_dest)"
done < <(find "$repo_root/skills" -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -not -path '*/misc/*' -print0)
