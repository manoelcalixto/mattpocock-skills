#!/bin/bash
set -u

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')

python3 - "$COMMAND" <<'PY'
import os
import shlex
import sys

command = sys.argv[1]


def block(reason: str) -> None:
    print(
        f"BLOCKED: {command!r} contains {reason}. Codex does not have authority to run it.",
        file=sys.stderr,
    )
    raise SystemExit(2)


def options_before_separator(arguments: list[str]):
    for argument in arguments:
        if argument == "--":
            return
        yield argument


def has_force_flag(arguments: list[str]) -> bool:
    return any(
        argument == "--force"
        or (
            argument.startswith("-")
            and not argument.startswith("--")
            and "f" in argument[1:]
        )
        for argument in options_before_separator(arguments)
    )


def has_forced_delete_flags(arguments: list[str]) -> bool:
    has_delete = False
    has_force = False
    for argument in options_before_separator(arguments):
        if argument == "-D":
            has_delete = True
            has_force = True
        elif argument == "--delete":
            has_delete = True
        elif argument == "--force":
            has_force = True
        elif argument.startswith("-") and not argument.startswith("--"):
            flags = argument[1:]
            has_delete = has_delete or "d" in flags
            has_force = has_force or "f" in flags
    return has_delete and has_force


def inspect_git_invocation(tokens: list[str]) -> None:
    index = 1
    value_options = {
        "-C",
        "-c",
        "--git-dir",
        "--work-tree",
        "--namespace",
        "--super-prefix",
        "--config-env",
    }
    value_prefixes = tuple(f"{option}=" for option in value_options if option.startswith("--"))

    while index < len(tokens):
        token = tokens[index]
        if token in value_options:
            index += 2
        elif token.startswith(value_prefixes):
            index += 1
        elif token == "--":
            index += 1
            break
        elif token.startswith("-"):
            index += 1
        else:
            break

    if index >= len(tokens):
        return

    subcommand = tokens[index]
    arguments = tokens[index + 1 :]
    if any(character in subcommand for character in "$`*?["):
        block("a dynamic Git subcommand that cannot be inspected safely")

    if subcommand == "push":
        block("a git push invocation")
    if subcommand == "reset" and "--hard" in options_before_separator(arguments):
        block("git reset --hard")
    if subcommand == "clean" and has_force_flag(arguments):
        block("a forced git clean")
    if subcommand == "branch" and has_forced_delete_flags(arguments):
        block("a forced git branch deletion")
    if subcommand in {"checkout", "restore"} and "." in arguments:
        block(f"git {subcommand} targeting the working tree")


try:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    words = list(lexer)
except ValueError:
    if "git" in command:
        block("an unparseable Git command")
    raise SystemExit(0)

# Shell expansion can assemble an executable name that static tokenization
# cannot prove is safe (`g$()it`, `$GIT`, or `$(printf git)`). Fail closed when
# the same command also contains a subcommand this hook is responsible for.
guarded_subcommands = {"push", "reset", "clean", "branch", "checkout", "restore"}
if ("$" in command or "`" in command) and any(word in guarded_subcommands for word in words):
    block("a dynamically assembled command containing a guarded Git operation")

segments: list[list[str]] = []
segment: list[str] = []
for word in words:
    if word and all(character in ";&|()" for character in word):
        if segment:
            segments.append(segment)
            segment = []
    else:
        segment.append(word)
if segment:
    segments.append(segment)

for segment in segments:
    for index, candidate in enumerate(segment):
        if os.path.basename(candidate) == "git":
            inspect_git_invocation(segment[index:])
PY
