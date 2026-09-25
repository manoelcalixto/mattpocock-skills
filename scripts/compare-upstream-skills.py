#!/usr/bin/env python3
"""List upstream source changes that need human-guided Codex plugin reconciliation."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / ".agents" / "upstream-skills-ref"
PROMOTED = {"engineering", "productivity"}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="upstream/main", help="upstream revision to inspect")
    parser.add_argument("--baseline", help="baseline revision; defaults to the recorded file")
    args = parser.parse_args()
    baseline = args.baseline or BASELINE.read_text().strip()
    before = git("rev-parse", "--verify", f"{baseline}^{{commit}}")
    after = git("rev-parse", "--verify", f"{args.ref}^{{commit}}")
    if not subprocess.run(
        ["git", "merge-base", "--is-ancestor", before, after], cwd=REPO, check=False
    ).returncode == 0:
        parser.error("baseline is not an ancestor of the selected upstream ref")

    raw = subprocess.run(
        ["git", "diff", "--name-status", "-z", "--no-renames", before, after, "--", "skills", ".claude-plugin/plugin.json", "docs/engineering", "docs/productivity"],
        cwd=REPO, check=True, capture_output=True
    ).stdout
    fields = raw.split(b"\0")
    if fields and not fields[-1]:
        fields.pop()
    if len(fields) % 2:
        raise RuntimeError("unexpected git diff name-status output")

    print(f"Baseline: {before}\nUpstream: {after}")
    if not fields:
        print("No source or Claude distribution changes.")
        return 0
    for status_bytes, path_bytes in zip(fields[::2], fields[1::2]):
        status = status_bytes.decode()
        path = path_bytes.decode(errors="backslashreplace")
        parts = Path(path).parts
        if len(parts) > 2 and parts[0] == "skills" and parts[1] in PROMOTED:
            target = f"plugins/mattpocock-skills-codex/skills/{parts[2]}"
        else:
            target = "review distribution and documentation"
        print(f"{status}\t{path}\t=> {target}")
    print("Review each item, adapt the plugin copy, validate, then update the baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
