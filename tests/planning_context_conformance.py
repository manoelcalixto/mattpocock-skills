#!/usr/bin/env python3
"""Public conformance harness for the planning-context contract."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "skills" / "engineering" / "planning-context" / "scripts" / "planning_context.py"


class HarnessFailure(AssertionError):
    """Raised when a public planning-context behavior is not observable."""


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise HarnessFailure(
            f"git {' '.join(args)} failed ({result.returncode}):\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


def run_helper(
    repo: Path,
    *args: str,
    expected: int = 0,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--json", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != expected:
        raise HarnessFailure(
            f"planning_context {' '.join(args)} returned {result.returncode}, expected {expected}:\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


def payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise HarnessFailure(f"helper did not return JSON: {result.stdout!r}") from error


def init_repo() -> Path:
    path = Path(tempfile.mkdtemp(prefix="planning-context-conformance-"))
    run_git(path, "init", "--initial-branch", "main")
    run_git(path, "config", "user.name", "Planning Context Harness")
    run_git(path, "config", "user.email", "planning-context@example.invalid")
    (path / "README.md").write_text("fixture\n")
    run_git(path, "add", "README.md")
    run_git(path, "commit", "-m", "fixture")
    return path


def create_effort(repo: Path, effort: str = "demo") -> None:
    run_helper(repo, "init")
    run_helper(repo, "ledger", "create", "--effort", effort)
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        effort,
        "--decision",
        "Use the shared planning seam",
        "--context",
        "Several sessions consume the same plan",
        "--rationale",
        "A versioned contract prevents drift",
    )


def test_configuration_and_lazy_migration() -> None:
    repo = init_repo()
    first = payload(run_helper(repo, "init"))
    if first["status"] != "created":
        raise HarnessFailure(f"initial configuration was not created: {first}")
    config = repo / "docs" / "agents" / "planning.md"
    original = config.read_text()
    second = payload(run_helper(repo, "init"))
    if second["status"] != "existing" or config.read_text() != original:
        raise HarnessFailure("re-running init rewrote the planning configuration")

    legacy_config = init_repo()
    agents = legacy_config / "docs" / "agents"
    agents.mkdir(parents=True)
    (agents / "planning.md").write_text("# Existing local planning notes\n")
    migrated = payload(run_helper(legacy_config, "init"))
    if migrated["status"] != "migrated":
        raise HarnessFailure(f"existing configuration did not receive lazy migration: {migrated}")
    if "planning-context:v1" not in (agents / "planning.md").read_text():
        raise HarnessFailure("lazy migration marker is missing")


def test_ledger_ids_and_supersession() -> None:
    repo = init_repo()
    create_effort(repo)
    added = payload(
        run_helper(
            repo,
            "decision",
            "add",
            "--effort",
            "demo",
            "--decision",
            "Keep the ledger per effort",
            "--context",
            "Independent efforts need independent histories",
            "--rationale",
            "A repository-wide allocator creates conflicts",
            "--obligations",
            "none",
        )
    )
    if added["id"] != "DEC-002":
        raise HarnessFailure(f"stable per-effort ID allocation failed: {added}")
    superseded = payload(
        run_helper(
            repo,
            "decision",
            "add",
            "--effort",
            "demo",
            "--supersedes",
            "DEC-001",
            "--decision",
            "Use a new shared planning seam",
            "--context",
            "The first seam did not cover all consumers",
            "--rationale",
            "The new seam keeps validation in one owner",
        )
    )
    if superseded["id"] != "DEC-003":
        raise HarnessFailure(f"supersession did not allocate a new ID: {superseded}")
    ledger = (repo / "docs" / "planning" / "demo" / "decision-ledger.md").read_text()
    if "- Status: superseded" not in ledger or "- Superseded by: DEC-003" not in ledger:
        raise HarnessFailure("supersession did not preserve an auditable old entry")
    if "- Obligations: none" not in ledger:
        raise HarnessFailure("non-ticket obligation was not preserved")


def test_checkpoint_gates_staging_and_trailer() -> str:
    repo = init_repo()
    create_effort(repo)
    (repo / "unrelated.txt").write_text("must remain outside the checkpoint\n")
    (repo / "README.md").write_text("unrelated tracked work\n")
    incomplete = run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", expected=2)
    if "coverage" not in incomplete.stdout.lower() + incomplete.stderr.lower():
        raise HarnessFailure(f"final gate failed without an actionable coverage error: {incomplete}")
    intermediate = payload(
        run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "intermediate", "--message", "initial plan")
    )
    if len(str(intermediate["sha"])) != 40:
        raise HarnessFailure(f"intermediate checkpoint did not return a full commit SHA: {intermediate}")
    run_helper(
        repo,
        "coverage",
        "add",
        "--effort",
        "demo",
        "--decision",
        "DEC-001",
        "--obligation",
        "specification",
        "--evidence",
        "spec.md#planning-context",
    )
    run_helper(
        repo,
        "coverage",
        "add",
        "--effort",
        "demo",
        "--decision",
        "DEC-001",
        "--obligation",
        "tickets",
        "--evidence",
        "issue-4",
    )
    run_git(repo, "add", "README.md")
    checkpoint = payload(
        run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "planning checkpoint")
    )
    sha = str(checkpoint["sha"])
    if len(sha) != 40:
        raise HarnessFailure(f"checkpoint did not return a full commit SHA: {checkpoint}")
    if not (repo / "unrelated.txt").exists():
        raise HarnessFailure("unrelated worktree file was removed")
    readme_status = run_git(repo, "status", "--porcelain", "--", "README.md").stdout.strip()
    if not readme_status.startswith("M "):
        raise HarnessFailure(f"unrelated staged work was not preserved: {readme_status!r}")
    committed_readme = run_git(repo, "show", f"{sha}:README.md").stdout
    if committed_readme != "fixture\n":
        raise HarnessFailure("unrelated tracked work was included in the checkpoint")
    if run_git(repo, "cat-file", "-e", f"{sha}:unrelated.txt", check=False).returncode == 0:
        raise HarnessFailure("unrelated file was included in the checkpoint")
    message = run_git(repo, "show", "-s", "--format=%B", sha).stdout
    for trailer in ("Planning-Checkpoint: demo", "Planning-Phase: final", "Planning-Ledger:"):
        if trailer not in message:
            raise HarnessFailure(f"checkpoint trailer {trailer!r} is missing from {message!r}")
    return sha


def test_validation_and_immutability() -> None:
    repo = init_repo()
    create_effort(repo)
    for obligation, evidence in (("specification", "spec.md"), ("tickets", "issue-4")):
        run_helper(
            repo,
            "coverage",
            "add",
            "--effort",
            "demo",
            "--decision",
            "DEC-001",
            "--obligation",
            obligation,
            "--evidence",
            evidence,
        )
    checkpoint = payload(
        run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "planning checkpoint")
    )
    sha = str(checkpoint["sha"])
    context = repo / "spec.md"
    local_context = repo / "local-ticket.md"
    local_context.write_text("# Local ticket\n")
    local_result = payload(
        run_helper(repo, "validate", "--context-file", "local-ticket.md", "--effort", "demo", "--phase", "final")
    )
    if local_result.get("source") != "trailer" or local_result.get("checkpoint") != sha:
        raise HarnessFailure(f"local trailer pointer was not resolved: {local_result}")
    run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        sha,
        "--decisions",
        "DEC-001",
        "--repository",
        "https://github.com/example/project",
        "--output",
        "spec.md",
    )
    run_helper(repo, "validate", "--context-file", "spec.md", "--phase", "final")


    marker_text = context.read_text()

    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    original = ledger.read_text()
    ledger.write_text(original.replace("Use the shared planning seam", "Rewrite the checkpointed meaning"))
    invalid = run_helper(repo, "validate", "--context-file", "spec.md", expected=2)
    if "immutable" not in invalid.stdout.lower() + invalid.stderr.lower():
        raise HarnessFailure("checkpointed decision meaning was not rejected after an edit")
    ledger.write_text(original)

    legacy = repo / "legacy-ticket.md"
    legacy.write_text("# Legacy ticket\n")
    legacy_result = payload(run_helper(repo, "validate", "--context-file", "legacy-ticket.md"))
    if legacy_result.get("status") != "legacy":
        raise HarnessFailure(f"legacy input was not accepted: {legacy_result}")

    config_text = (repo / "docs" / "agents" / "planning.md").read_text()
    ledger_text = ledger.read_text()
    root_commit = run_git(repo, "rev-list", "--max-parents=0", "HEAD").stdout.strip()
    run_git(repo, "switch", "-c", "wrong-lineage", root_commit)
    (repo / "docs" / "agents").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "agents" / "planning.md").write_text(config_text)
    (repo / "docs" / "planning" / "demo").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "planning" / "demo" / "decision-ledger.md").write_text(ledger_text)
    wrong_context = repo / "spec.md"
    wrong_context.write_text(context.read_text())
    run_git(repo, "add", "docs", "spec.md")
    run_git(repo, "commit", "-m", "wrong lineage")
    invalid_lineage = run_helper(repo, "validate", "--context-file", "spec.md", expected=2)
    if "ancestor" not in invalid_lineage.stdout.lower() + invalid_lineage.stderr.lower():
        raise HarnessFailure(
            "wrong-lineage input did not fail with an ancestry error: "
            f"stdout={invalid_lineage.stdout} stderr={invalid_lineage.stderr}"
        )

    run_git(repo, "switch", "-")
    context.write_text(marker_text)
    run_helper(
        repo,
        "coverage",
        "add",
        "--effort",
        "demo",
        "--decision",
        "DEC-001",
        "--obligation",
        "verification",
        "--evidence",
        "later verification",
    )
    run_helper(repo, "validate", "--context-file", "spec.md", "--phase", "final")


def test_repository_wiring() -> None:
    skill = REPO_ROOT / "skills" / "engineering" / "planning-context"
    skill_text = (skill / "SKILL.md").read_text()
    if "disable-model-invocation:" in skill_text:
        raise HarnessFailure("planning-context must remain model-invoked")
    metadata = (skill / "agents" / "openai.yaml").read_text()
    if "interface:" not in metadata or "display_name:" not in metadata or "short_description:" not in metadata:
        raise HarnessFailure("planning-context OpenAI metadata is incomplete")
    if "policy:" in metadata:
        raise HarnessFailure("model-invoked planning-context must not disable implicit invocation")

    plugin = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text())
    if "./skills/engineering/planning-context" not in plugin.get("skills", []):
        raise HarnessFailure("planning-context is missing from the Claude plugin manifest")
    for catalog, link in (
        (REPO_ROOT / "README.md", "[planning-context](./skills/engineering/planning-context/SKILL.md)"),
        (REPO_ROOT / "skills" / "engineering" / "README.md", "[planning-context](./planning-context/SKILL.md)"),
    ):
        if link not in catalog.read_text():
            raise HarnessFailure(f"planning-context is missing from {catalog.relative_to(REPO_ROOT)}")

    docs = (REPO_ROOT / "docs" / "engineering" / "planning-context.md").read_text()
    sections = ["## What it does", "## When to reach for it", "## Common questions", "## It's working if", "## Where it fits"]
    positions = [docs.find(section) for section in sections]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise HarnessFailure("planning-context documentation sections are incomplete or out of order")
    if "\u2014" in skill_text or "\u2014" in docs or "\u2014" in metadata:
        raise HarnessFailure("planning-context artifacts contain an em dash")
    package = json.loads((REPO_ROOT / "package.json").read_text())
    if package.get("scripts", {}).get("test:planning-context") != "python3 tests/planning_context_conformance.py":
        raise HarnessFailure("the public planning-context harness is not wired to package.json")
    setup = (REPO_ROOT / "skills" / "engineering" / "setup-matt-pocock-skills" / "SKILL.md").read_text()
    router = (REPO_ROOT / "skills" / "engineering" / "ask-matt" / "SKILL.md").read_text()
    if 'call the Skill tool with `planning-context`' not in setup:
        raise HarnessFailure("setup does not delegate Planning initialization to planning-context")
    if "`/planning-context`" not in router:
        raise HarnessFailure("ask-matt does not route to planning-context")


def test_implementation_verification_gate() -> None:
    repo = init_repo()
    create_effort(repo)
    for obligation, evidence in (("specification", "spec.md"), ("tickets", "issue-4")):
        run_helper(
            repo,
            "coverage",
            "add",
            "--effort",
            "demo",
            "--decision",
            "DEC-001",
            "--obligation",
            obligation,
            "--evidence",
            evidence,
        )
    incomplete = run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "implementation", expected=2)
    if "verification" not in incomplete.stdout.lower() + incomplete.stderr.lower():
        raise HarnessFailure("implementation gate did not require verification evidence")
    run_helper(
        repo,
        "coverage",
        "add",
        "--effort",
        "demo",
        "--decision",
        "DEC-001",
        "--obligation",
        "verification",
        "--evidence",
        "npm run test:planning-context",
    )
    run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "implementation", "--message", "verified")


def main() -> int:
    tests = [
        test_repository_wiring,
        test_configuration_and_lazy_migration,
        test_ledger_ids_and_supersession,
        test_checkpoint_gates_staging_and_trailer,
        test_validation_and_immutability,
        test_implementation_verification_gate,
    ]
    for test in tests:
        test()
        print(f"ok: {test.__name__}")
    print(f"Planning context conformance: {len(tests)} scenarios passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except HarnessFailure as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
