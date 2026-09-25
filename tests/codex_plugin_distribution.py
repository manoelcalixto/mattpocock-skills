#!/usr/bin/env python3
"""Verify the native plugin's catalog, resources, and invocation contract."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "mattpocock-skills-codex"
SKILLS = PLUGIN / "skills"
PROMOTED = ("engineering", "productivity")


def main() -> None:
    claude = json.loads((REPO / ".claude-plugin/plugin.json").read_text())
    codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    package = json.loads((REPO / "package.json").read_text())
    assert claude["version"] == codex["version"] == package["version"]
    assert codex["skills"] == "./skills/"

    source_dirs = {
        path.name: path
        for bucket in PROMOTED
        for path in (REPO / "skills" / bucket).iterdir()
        if (path / "SKILL.md").is_file()
    }
    claude_dirs = {Path(value).name for value in claude["skills"]}
    assert set(source_dirs) == claude_dirs, (set(source_dirs) ^ claude_dirs)
    actual = {path.name for path in SKILLS.iterdir() if (path / "SKILL.md").is_file()}
    assert actual == claude_dirs | {"planning-context"}, (actual ^ (claude_dirs | {"planning-context"}))

    for name, source in source_dirs.items():
        dest = SKILLS / name
        missing = [
            str(path.relative_to(source))
            for path in source.rglob("*")
            if path.is_file() and not (dest / path.relative_to(source)).is_file()
        ]
        assert not missing, (name, missing)
        source_frontmatter = source.joinpath("SKILL.md").read_text().split("---", 2)[1]
        dest_frontmatter = dest.joinpath("SKILL.md").read_text().split("---", 2)[1]
        assert "disable-model-invocation:" not in dest_frontmatter, name
        metadata = dest.joinpath("agents/openai.yaml").read_text()
        assert ("allow_implicit_invocation: false" in metadata) == (
            "disable-model-invocation: true" in source_frontmatter
        ), name
    assert (SKILLS / "planning-context/scripts/planning_context.py").is_file()
    for name in ("implement", "planning-context"):
        skill = (SKILLS / name / "SKILL.md").read_text()
        assert "skills/engineering/planning-context/scripts/" not in skill, name
    setup = (SKILLS / "setup-matt-pocock-skills/SKILL.md").read_text()
    assert "If `AGENTS.md` exists, update it" in setup
    assert "If `AGENTS.md` does not exist, create it" in setup
    assert "If `CLAUDE.md` exists, edit it" not in setup
    compatibility = (REPO / "docs/codex-plugin.md").read_text()
    assert "codex-cli 0.158.0-alpha.8" in compatibility
    print(f"Codex plugin distribution: {len(actual)} skills and bundled resources verified")


if __name__ == "__main__":
    main()
