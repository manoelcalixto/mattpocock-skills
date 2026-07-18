#!/bin/bash
set -u

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')

block() {
  reason="$1"
  echo "BLOCKED: '$COMMAND' contains $reason. Codex does not have authority to run it." >&2
  exit 2
}

has_force_flag() {
  for argument in "$@"; do
    [ "$argument" = "--" ] && break
    case "$argument" in
      --force|-f*|-[!-]*f*) return 0 ;;
    esac
  done
  return 1
}

has_hard_flag() {
  for argument in "$@"; do
    [ "$argument" = "--" ] && break
    [ "$argument" = "--hard" ] && return 0
  done
  return 1
}

has_forced_delete_flags() {
  has_delete=false
  has_force=false
  for argument in "$@"; do
    [ "$argument" = "--" ] && break
    case "$argument" in
      -D) has_delete=true; has_force=true ;;
      --delete) has_delete=true ;;
      --force) has_force=true ;;
      -[!-]*)
        case "$argument" in *d*) has_delete=true ;; esac
        case "$argument" in *f*) has_force=true ;; esac
        ;;
    esac
  done
  [ "$has_delete" = true ] && [ "$has_force" = true ]
}

has_dot_operand() {
  for argument in "$@"; do
    [ "$argument" = "." ] && return 0
  done
  return 1
}

inspect_git_invocation() {
  tokens=("$@")
  index=1

  # Skip Git-wide options before the subcommand, including options whose value
  # is provided as the following token (`git -C repo push`).
  while [ "$index" -lt "${#tokens[@]}" ]; do
    token="${tokens[$index]}"
    case "$token" in
      -C|-c|--git-dir|--work-tree|--namespace|--super-prefix|--config-env)
        index=$((index + 2))
        ;;
      --git-dir=*|--work-tree=*|--namespace=*|--super-prefix=*|--config-env=*|--no-pager|--paginate|-p|--literal-pathspecs|--no-literal-pathspecs|--glob-pathspecs|--noglob-pathspecs|--icase-pathspecs|--no-optional-locks|--bare)
        index=$((index + 1))
        ;;
      --)
        index=$((index + 1))
        break
        ;;
      -*)
        index=$((index + 1))
        ;;
      *)
        break
        ;;
    esac
  done

  [ "$index" -lt "${#tokens[@]}" ] || return 0
  subcommand="${tokens[$index]}"
  arguments=("${tokens[@]:$((index + 1))}")

  case "$subcommand" in
    push)
      block "a git push invocation"
      ;;
    reset)
      has_hard_flag "${arguments[@]}" && block "git reset --hard"
      ;;
    clean)
      has_force_flag "${arguments[@]}" && block "a forced git clean"
      ;;
    branch)
      has_forced_delete_flags "${arguments[@]}" && block "a forced git branch deletion"
      ;;
    checkout|restore)
      has_dot_operand "${arguments[@]}" && block "git $subcommand targeting the working tree"
      ;;
  esac
}

# Split common shell command separators into independent segments, then scan
# every token for `git` or an absolute/path-qualified Git binary. This does not
# evaluate the command and errs on the side of blocking ambiguous input.
while IFS= read -r segment; do
  read -r -a words <<< "$segment"
  for index in "${!words[@]}"; do
    candidate="${words[$index]}"
    candidate="${candidate#\"}"
    candidate="${candidate%\"}"
    candidate="${candidate#\'}"
    candidate="${candidate%\'}"
    if [ "${candidate##*/}" = "git" ]; then
      inspect_git_invocation "${words[@]:$index}"
    fi
  done
done < <(printf '%s\n' "$COMMAND" | tr ';&|()' '\n')

exit 0
