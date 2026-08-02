#!/usr/bin/env bash
set -euo pipefail

# NOTE: This is a dev-only maintainer convenience, not a supported installer.
#
# Links all promoted and workbench skills in the repository into Codex's local
# Agent Skills directory:
#   - ~/.agents/skills
# Each entry is a symlink into this repo, so a `git pull` is all that's needed
# to keep installed skills up to date.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.agents/skills"

# Collect the repo's skills once, link into every destination.
names=()
srcs=()
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  names+=("$(basename "$src")")
  srcs+=("$src")
done < <(find "$REPO/skills" "$REPO/workbench" -name SKILL.md -not -path '*/node_modules/*' -print0)

# If $DEST is a symlink that resolves into this repo, we'd end up writing the
# per-skill symlinks back into the repo's own skills/ tree. Detect and bail out
# instead of polluting the working copy.
if [ -L "$DEST" ]; then
  resolved="$(readlink -f "$DEST")"
  case "$resolved" in
    "$REPO"|"$REPO"/*)
      echo "error: $DEST is a symlink into this repo ($resolved)." >&2
      echo "Remove it (rm \"$DEST\") and re-run; the script will recreate it as a real dir." >&2
      exit 1
      ;;
  esac
fi

mkdir -p "$DEST"

for i in "${!names[@]}"; do
  name="${names[$i]}"
  src="${srcs[$i]}"
  target="$DEST/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    rm -rf "$target"
  fi

  ln -sfn "$src" "$target"
  echo "linked $name -> $src ($DEST)"
done
