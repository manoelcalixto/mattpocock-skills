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
IMPLEMENT_SKILL = REPO_ROOT / "skills" / "engineering" / "implement" / "SKILL.md"
IMPLEMENT_DOCS = REPO_ROOT / "docs" / "engineering" / "implement.md"


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
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(HELPER), "--repo", str(repo), "--json", *args],
        cwd=REPO_ROOT,
        text=True,
        input=input_text,
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


def add_coverage(repo: Path, effort: str, decision: str, obligation: str, evidence: str) -> None:
    run_helper(
        repo,
        "coverage",
        "add",
        "--effort",
        effort,
        "--decision",
        decision,
        "--obligation",
        obligation,
        "--evidence",
        evidence,
    )


def write_marked_artifact(
    repo: Path,
    effort: str,
    checkpoint: str,
    decisions: str,
    output: str,
    body: str,
) -> Path:
    run_helper(
        repo,
        "marker",
        "--effort",
        effort,
        "--checkpoint",
        checkpoint,
        "--decisions",
        decisions,
        "--repository",
        "https://github.com/manoelcalixto/mattpocock-skills",
        "--output",
        output,
    )
    path = repo / output
    path.write_text(f"{path.read_text()}\n{body.strip()}\n")
    return path


def prepare_final_context(repo: Path, output: str = "ticket.md") -> tuple[Path, str]:
    create_effort(repo)
    for obligation, evidence in (("specification", "spec.md"), ("tickets", "issue-7")):
        add_coverage(repo, "demo", "DEC-001", obligation, evidence)
    checkpoint = payload(
        run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "final plan")
    )
    sha = str(checkpoint["sha"])
    context = write_marked_artifact(
        repo,
        "demo",
        sha,
        "DEC-001",
        output,
        "## What to build\n\nImplement the ticket as a complete vertical slice.",
    )
    return context, sha


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


def test_implement_preflight_wiring() -> None:
    skill = IMPLEMENT_SKILL.read_text()
    docs = IMPLEMENT_DOCS.read_text()
    preflight = skill.find("## Planning preflight")
    tdd = skill.find('Call the Skill tool with "tdd"')
    if preflight < 0 or tdd < 0 or preflight > tdd:
        raise HarnessFailure("implement does not place Planning preflight before TDD")
    for phrase in (
        "planning_context.py",
        "--context-file",
        "--context-stdin",
        "--phase final",
        '"status": "valid"',
        '"status": "legacy"',
        "exact failed invariant",
        "A declared marker never falls back to the legacy path",
    ):
        if phrase not in skill:
            raise HarnessFailure(f"implement preflight wiring is missing: {phrase}")
    if "Call the Skill tool with `planning-context`" not in skill:
        raise HarnessFailure("implement does not return decision conflicts to planning-context")
    if "## Planning preflight" not in docs or "Active decision conflicts with the implementation" not in docs:
        raise HarnessFailure("implement documentation does not describe the Planning preflight")


def test_implement_preflight_valid() -> None:
    repo = init_repo()
    context, checkpoint = prepare_final_context(repo)
    sentinel = repo / "implementation.txt"
    sentinel.write_text("before preflight\n")
    before_stdin_files = {
        path.relative_to(repo).as_posix()
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    result = payload(run_helper(repo, "validate", "--context-file", context.name, "--phase", "final"))
    expected = {
        "status": "valid",
        "source": "marker",
        "effort": "demo",
        "checkpoint": checkpoint,
        "ledger": "docs/planning/demo/decision-ledger.md",
        "decisions": ["DEC-001"],
        "coverage": {
            "DEC-001": {
                "specification": {"status": "complete", "evidence": "spec.md"},
                "tickets": {"status": "complete", "evidence": "issue-7"},
                "verification": {"status": "pending", "evidence": "none"},
            }
        },
        "ancestry": {
            "checkpoint_sha": checkpoint,
            "head_sha": checkpoint,
            "is_ancestor": True,
        },
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise HarnessFailure(f"valid implement preflight did not resolve {key}: {result}")
    if sentinel.read_text() != "before preflight\n":
        raise HarnessFailure("valid implement preflight changed implementation state")

    stdin_result = payload(
        run_helper(
            repo,
            "validate",
            "--context-stdin",
            "--phase",
            "final",
            input_text=context.read_text(),
        )
    )
    stdin_expected = dict(expected)
    stdin_expected.update({"context": "<stdin>", "source": "stdin"})
    for key, value in stdin_expected.items():
        if stdin_result.get(key) != value:
            raise HarnessFailure(f"stdin implement preflight did not resolve {key}: {stdin_result}")
    after_stdin_files = {
        path.relative_to(repo).as_posix()
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    if after_stdin_files != before_stdin_files:
        raise HarnessFailure(
            f"stdin context transport created or removed repository files: {sorted(after_stdin_files ^ before_stdin_files)}"
        )
    if sentinel.read_text() != "before preflight\n":
        raise HarnessFailure("stdin implement preflight changed implementation state")


def test_implement_preflight_legacy() -> None:
    repo = init_repo()
    context = repo / "legacy-ticket.md"
    context.write_text("# Legacy ticket\n")
    sentinel = repo / "implementation.txt"
    sentinel.write_text("before legacy\n")
    result = payload(run_helper(repo, "validate", "--context-file", context.name))
    if result.get("status") != "legacy":
        raise HarnessFailure(f"marker-less implement input did not use the legacy path: {result}")
    if (repo / "docs" / "agents" / "planning.md").exists() or (repo / "docs" / "planning").exists():
        raise HarnessFailure("legacy implement preflight created Planning artifacts")
    if sentinel.read_text() != "before legacy\n":
        raise HarnessFailure("legacy implement preflight changed implementation state")


def test_implement_preflight_invalid() -> None:
    repo = init_repo()
    context, checkpoint = prepare_final_context(repo)
    context.write_text(context.read_text().replace(checkpoint, "0" * 40))
    sentinel = repo / "implementation.txt"
    sentinel.write_text("before invalid\n")
    invalid = run_helper(repo, "validate", "--context-file", context.name, "--phase", "final", expected=2)
    error = invalid.stdout.lower() + invalid.stderr.lower()
    if "cannot be resolved" not in error:
        raise HarnessFailure(f"invalid declared context did not expose the failed invariant: {invalid}")
    if sentinel.read_text() != "before invalid\n":
        raise HarnessFailure("invalid implement preflight changed implementation state")


def test_implement_preflight_wrong_lineage() -> None:
    repo = init_repo()
    context, _ = prepare_final_context(repo)
    marker_text = context.read_text()
    config_text = (repo / "docs" / "agents" / "planning.md").read_text()
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    ledger_text = ledger.read_text()
    root_commit = run_git(repo, "rev-list", "--max-parents=0", "HEAD").stdout.strip()
    run_git(repo, "switch", "-c", "wrong-lineage", root_commit)
    (repo / "docs" / "agents").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "agents" / "planning.md").write_text(config_text)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(ledger_text)
    context = repo / "wrong-lineage-ticket.md"
    context.write_text(marker_text)
    run_git(repo, "add", "docs", context.name)
    run_git(repo, "commit", "-m", "wrong lineage")
    sentinel = repo / "implementation.txt"
    sentinel.write_text("before wrong lineage\n")
    invalid = run_helper(repo, "validate", "--context-file", context.name, "--phase", "final", expected=2)
    error = invalid.stdout.lower() + invalid.stderr.lower()
    if "not an ancestor" not in error:
        raise HarnessFailure(f"wrong-lineage implement preflight did not fail closed: {invalid}")
    if sentinel.read_text() != "before wrong lineage\n":
        raise HarnessFailure("wrong-lineage preflight changed implementation state")


def test_implement_preflight_decision_conflict() -> None:
    skill_text = IMPLEMENT_SKILL.read_text()
    for phrase in (
        "If an active decision cannot be honored",
        "Call the Skill tool with `planning-context`",
        "superseding decision",
        "new Planning checkpoint",
        "silent deviation",
    ):
        if phrase not in skill_text:
            raise HarnessFailure(f"implement decision-conflict contract is missing: {phrase}")

    repo = init_repo()
    old_context, _ = prepare_final_context(repo, "old-ticket.md")
    sentinel = repo / "implementation.txt"
    sentinel.write_text("before decision conflict\n")
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        "demo",
        "--supersedes",
        "DEC-001",
        "--decision",
        "Use the resolved planning seam",
        "--context",
        "The active decision cannot be honored as written",
        "--rationale",
        "An explicit supersession preserves the decision history",
    )
    for obligation, evidence in (("specification", "spec.md"), ("tickets", "issue-7")):
        add_coverage(repo, "demo", "DEC-002", obligation, evidence)
    new_checkpoint = payload(
        run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "resolved plan")
    )["sha"]

    stale = run_helper(repo, "validate", "--context-file", old_context.name, "--phase", "final", expected=2)
    stale_error = stale.stdout.lower() + stale.stderr.lower()
    if "validity" not in stale_error and "changed after the checkpoint" not in stale_error:
        raise HarnessFailure(f"decision conflict did not reject the stale Planning marker: {stale}")
    if sentinel.read_text() != "before decision conflict\n":
        raise HarnessFailure("decision-conflict preflight changed implementation state")

    new_context = write_marked_artifact(
        repo,
        "demo",
        str(new_checkpoint),
        "DEC-002",
        "resolved-ticket.md",
        "## What to build\n\nImplement the resolved decision.",
    )
    resolved = payload(run_helper(repo, "validate", "--context-file", new_context.name, "--phase", "final"))
    if resolved.get("status") != "valid" or resolved.get("decisions") != ["DEC-002"]:
        raise HarnessFailure(f"supersession and new checkpoint did not restore a valid context: {resolved}")


def test_grill_to_tickets_flow() -> None:
    """Exercise the public producer, propagation, gate, and marker path."""

    repo = init_repo()
    effort = "grill-to-tickets"
    create_effort(repo, effort)
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        effort,
        "--decision",
        "Keep each ticket independently verifiable",
        "--context",
        "Fresh sessions need a narrow complete slice",
        "--rationale",
        "Focused ownership limits integration drift",
    )
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        effort,
        "--decision",
        "Track the process choice as non-ticket coverage",
        "--context",
        "The process rule does not change product behavior",
        "--rationale",
        "An implementation issue would be artificial",
        "--obligations",
        "tickets",
    )

    intermediate = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            effort,
            "--phase",
            "intermediate",
            "--message",
            "grill decisions",
        )
    )
    intermediate_sha = str(intermediate["sha"])

    spec = write_marked_artifact(
        repo,
        effort,
        intermediate_sha,
        "DEC-001, DEC-002, DEC-003",
        "spec.md",
        """## Implementation Decisions

- DEC-001: use the shared planning seam for cross-session work
- DEC-002: make each implementation ticket independently verifiable
- DEC-003: no specification consequence, process-only coverage is recorded in the ledger
""",
    )
    add_coverage(repo, effort, "DEC-001", "specification", "spec.md#implementation-decisions")
    add_coverage(repo, effort, "DEC-002", "specification", "spec.md#implementation-decisions")

    missing = run_helper(repo, "checkpoint", "--effort", effort, "--phase", "final", expected=2)
    missing_text = missing.stdout.lower() + missing.stderr.lower()
    for pending in ("dec-001:tickets", "dec-002:tickets", "dec-003:tickets"):
        if pending not in missing_text:
            raise HarnessFailure(f"final gate did not expose pending ticket coverage {pending}: {missing}")

    ticket_one = write_marked_artifact(
        repo,
        effort,
        intermediate_sha,
        "DEC-001",
        "ticket-one.md",
        """## What to build

Make the shared planning seam observable from one complete ticket.

## Decision consequences

- DEC-001: preserve the shared seam in this ticket's acceptance path

## Acceptance criteria

- [ ] A fresh session can verify the complete path.
""",
    )
    ticket_two = write_marked_artifact(
        repo,
        effort,
        intermediate_sha,
        "DEC-002",
        "ticket-two.md",
        """## What to build

Keep the implementation ticket independently verifiable.

## Decision consequences

- DEC-002: include a narrow complete slice with observable criteria

## Acceptance criteria

- [ ] The ticket has an independent verification path.
""",
    )
    add_coverage(repo, effort, "DEC-001", "tickets", "ticket-one.md")
    add_coverage(repo, effort, "DEC-002", "tickets", "ticket-two.md")
    add_coverage(repo, effort, "DEC-003", "tickets", "non-ticket: process-only decision")

    final = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            effort,
            "--phase",
            "final",
            "--message",
            "grill to tickets planning checkpoint",
        )
    )
    final_sha = str(final["sha"])
    if final_sha == intermediate_sha or len(final_sha) != 40:
        raise HarnessFailure(f"final checkpoint did not advance to a full SHA: {final}")

    expected_owned = {
        "docs/agents/planning.md",
        "docs/planning/grill-to-tickets/decision-ledger.md",
    }
    owned = set(run_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", final_sha).stdout.splitlines())
    if not owned or not owned.issubset(expected_owned):
        raise HarnessFailure(f"final checkpoint staged non-owned artifacts: {sorted(owned)}")

    for output, decisions in (
        ("spec.md", "DEC-001,DEC-002,DEC-003"),
        ("ticket-one.md", "DEC-001"),
        ("ticket-two.md", "DEC-002"),
    ):
        run_helper(
            repo,
            "marker",
            "--effort",
            effort,
            "--checkpoint",
            final_sha,
            "--decisions",
            decisions,
            "--repository",
            "https://github.com/manoelcalixto/mattpocock-skills",
            "--output",
            output,
        )

    run_helper(repo, "validate", "--context-file", "spec.md", "--phase", "final")
    run_helper(repo, "validate", "--context-file", "ticket-one.md", "--phase", "final")
    run_helper(repo, "validate", "--context-file", "ticket-two.md", "--phase", "final")

    spec_text = spec.read_text()
    ticket_one_text = ticket_one.read_text()
    ticket_two_text = ticket_two.read_text()
    if "A versioned contract prevents drift" in spec_text + ticket_one_text + ticket_two_text:
        raise HarnessFailure("canonical ledger rationale leaked into a planning artifact")
    if "DEC-002" in ticket_one_text or "DEC-001" in ticket_two_text:
        raise HarnessFailure("a ticket received an irrelevant decision ID")
    if f"Planning checkpoint: {final_sha}" not in spec_text + ticket_one_text + ticket_two_text:
        raise HarnessFailure("final marker SHA was not propagated to every artifact")
    if "Repository: https://github.com/manoelcalixto/mattpocock-skills" not in spec_text:
        raise HarnessFailure("external repository metadata was not retained in the marker")
    if "non-ticket" not in (repo / "docs" / "planning" / effort / "decision-ledger.md").read_text():
        raise HarnessFailure("non-ticket coverage evidence was not retained in the ledger")


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

    grill = (REPO_ROOT / "skills" / "engineering" / "grill-with-docs" / "SKILL.md").read_text()
    to_spec = (REPO_ROOT / "skills" / "engineering" / "to-spec" / "SKILL.md").read_text()
    to_tickets = (REPO_ROOT / "skills" / "engineering" / "to-tickets" / "SKILL.md").read_text()
    if "planning-context" not in grill or "domain-modeling" not in grill or "grilling" not in grill:
        raise HarnessFailure("grill-with-docs does not wire all three owned skills")
    for phrase in (
        "Call the Skill tool once with `planning-context`",
        "call the Skill tool once with `grilling`",
        "call the Skill tool once with `domain-modeling`",
        "Each call is separate",
    ):
        if phrase not in grill:
            raise HarnessFailure(f"grill-with-docs does not preserve separate Skill calls: {phrase}")
    for phrase in ("material", "round summary", "CONTEXT.md", "ADR"):
        if phrase not in grill:
            raise HarnessFailure(f"grill-with-docs is missing decision ownership guidance: {phrase}")
    for phrase in ("every active ledger entry", "actionable consequence", "canonical rationale", "coverage add", "--repo owner/repository"):
        if phrase not in to_spec:
            raise HarnessFailure(f"to-spec is missing Planning propagation guidance: {phrase}")
    for phrase in ("every active ledger entry", "ticket obligation", "Decision consequences", "final Planning checkpoint", "--repo owner/repository"):
        if phrase not in to_tickets:
            raise HarnessFailure(f"to-tickets is missing Planning propagation guidance: {phrase}")
    tracker_template = (
        REPO_ROOT / "skills" / "engineering" / "setup-matt-pocock-skills" / "issue-tracker-github.md"
    ).read_text()
    if "--repo <owner>/<repo>" not in tracker_template or "Infer the repo" in tracker_template:
        raise HarnessFailure("GitHub tracker template permits repository inference")
    for phrase in (
        "replace every literal `<owner>/<repo>`",
        "generated `docs/agents/issue-tracker.md` contains no `<owner>/<repo>` placeholder",
        "Never copy the seed verbatim",
    ):
        if phrase not in setup:
            raise HarnessFailure(f"setup does not require deterministic GitHub target resolution: {phrase}")
    configured_target = "manoelcalixto/mattpocock-skills"
    rendered_tracker = tracker_template.replace("<owner>/<repo>", configured_target)
    if "<owner>/<repo>" in rendered_tracker:
        raise HarnessFailure("rendered GitHub tracker still contains the seed placeholder")
    for line in rendered_tracker.splitlines():
        if any(f"`gh issue {verb}" in line for verb in ("create", "view", "list", "comment", "edit", "close")):
            if f"--repo {configured_target}" not in line:
                raise HarnessFailure(f"rendered GitHub issue command lost its configured target: {line}")
        if any(f"`gh pr {verb}" in line for verb in ("create", "view", "list", "diff", "comment", "edit", "close")):
            if f"--repo {configured_target}" not in line:
                raise HarnessFailure(f"rendered GitHub pull request command lost its configured target: {line}")
        if "`gh api " in line and f"repos/{configured_target}/" not in line:
            raise HarnessFailure(f"rendered GitHub API command lost its configured target: {line}")
    for document in (setup, to_spec, to_tickets, tracker_template):
        for line in document.splitlines():
            if any(f"`gh issue {verb}" in line for verb in ("create", "view", "list", "comment", "edit", "close")) and "--repo" not in line:
                raise HarnessFailure(f"ambiguous GitHub issue command remains: {line}")
            if any(f"`gh pr {verb}" in line for verb in ("create", "view", "list", "diff", "comment", "edit", "close")) and "--repo" not in line:
                raise HarnessFailure(f"ambiguous GitHub pull request command remains: {line}")
    docs = {
        "grill-with-docs": (REPO_ROOT / "docs" / "engineering" / "grill-with-docs.md").read_text(),
        "to-spec": (REPO_ROOT / "docs" / "engineering" / "to-spec.md").read_text(),
        "to-tickets": (REPO_ROOT / "docs" / "engineering" / "to-tickets.md").read_text(),
        "ask-matt": (REPO_ROOT / "docs" / "engineering" / "ask-matt.md").read_text(),
        "planning-context": (REPO_ROOT / "docs" / "engineering" / "planning-context.md").read_text(),
        "implement": IMPLEMENT_DOCS.read_text(),
    }
    for name, text in docs.items():
        for section in ("## What it does", "## When to reach for it", "## Common questions", "## It's working if", "## Where it fits"):
            if section not in text:
                raise HarnessFailure(f"{name} documentation is missing {section}")
        if "\u2014" in text:
            raise HarnessFailure(f"{name} documentation contains an em dash")


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
        test_implement_preflight_wiring,
        test_implement_preflight_valid,
        test_implement_preflight_legacy,
        test_implement_preflight_invalid,
        test_implement_preflight_wrong_lineage,
        test_implement_preflight_decision_conflict,
        test_grill_to_tickets_flow,
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
