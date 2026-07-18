#!/usr/bin/env bash
set -euo pipefail

# NOTE: This is a dev-only script, intended for use by maintainers of this repo.
# It is not a supported installer. Modifications to it — or requests for
# modifications — will not be approved.
#
# Links all non-deprecated skills in the repository into Codex's user skill
# directory:
#   - ~/.agents/skills
# Each entry is a symlink into this repo, so a `git pull` is all that's needed
# to keep installed skills up to date.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.agents/skills"

names=()
srcs=()
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  names+=("$(basename "$src")")
  srcs+=("$src")
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -print0)

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

has_current_name() {
  wanted="$1"
  for current_name in "${names[@]}"; do
    if [ "$current_name" = "$wanted" ]; then
      return 0
    fi
  done
  return 1
}

# Remove only stale symlinks that point into this repository. This cleans up
# renamed or removed skills without touching user-managed directories or links.
for target in "$DEST"/*; do
  [ -L "$target" ] || continue
  resolved="$(readlink -f "$target")"
  case "$resolved" in
    "$REPO"/skills/*)
      name="$(basename "$target")"
      if ! has_current_name "$name"; then
        unlink "$target"
        echo "unlinked stale skill $name"
      fi
      ;;
  esac
done

for i in "${!names[@]}"; do
  name="${names[$i]}"
  src="${srcs[$i]}"
  target="$DEST/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    rm -rf "$target"
  fi

  ln -sfn "$src" "$target"
  echo "linked $name -> $src"
done
