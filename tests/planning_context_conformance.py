#!/usr/bin/env python3
"""Public conformance harness for the planning-context contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "skills" / "engineering" / "planning-context" / "scripts" / "planning_context.py"
IMPLEMENT_SKILL = REPO_ROOT / "skills" / "engineering" / "implement" / "SKILL.md"
IMPLEMENT_DOCS = REPO_ROOT / "docs" / "engineering" / "implement.md"
PLANNING_CONTRACT = REPO_ROOT / "skills" / "engineering" / "planning-context" / "references" / "planning-contract.md"
IMPLEMENT_SPEC_SKILL = REPO_ROOT / "skills" / "in-progress" / "implement-spec" / "SKILL.md"
IMPLEMENT_SPEC_METADATA = REPO_ROOT / "skills" / "in-progress" / "implement-spec" / "agents" / "openai.yaml"
IN_PROGRESS_README = REPO_ROOT / "skills" / "in-progress" / "README.md"
ISSUE_TRACKER = REPO_ROOT / "docs" / "agents" / "issue-tracker.md"
BOUNDARY_SKILLS = {
    "ask-matt": REPO_ROOT / "skills" / "engineering" / "ask-matt" / "SKILL.md",
    "handoff": REPO_ROOT / "skills" / "productivity" / "handoff" / "SKILL.md",
    "setup-matt-pocock-skills": REPO_ROOT / "skills" / "engineering" / "setup-matt-pocock-skills" / "SKILL.md",
    "planning-context": REPO_ROOT / "skills" / "engineering" / "planning-context" / "SKILL.md",
}
BOUNDARY_METADATA = {
    name: path.parent / "agents" / "openai.yaml" for name, path in BOUNDARY_SKILLS.items()
}
BOUNDARY_DOCS = {
    "ask-matt": REPO_ROOT / "docs" / "engineering" / "ask-matt.md",
    "handoff": REPO_ROOT / "docs" / "productivity" / "handoff.md",
    "setup-matt-pocock-skills": REPO_ROOT / "docs" / "engineering" / "setup-matt-pocock-skills.md",
    "planning-context": REPO_ROOT / "docs" / "engineering" / "planning-context.md",
}


class HarnessFailure(AssertionError):
    """Raised when a public planning-context behavior is not observable."""


def assert_ordered(text: str, label: str, *phrases: str) -> None:
    """Require a contract's milestones to appear in the stated order."""

    cursor = -1
    for phrase in phrases:
        position = text.find(phrase, cursor + 1)
        if position < 0:
            raise HarnessFailure(f"{label} is missing ordered milestone: {phrase}")
        cursor = position


def run_git(
    repo: Path,
    *args: str,
    check: bool = True,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        input=input_text,
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


def reference_decision(repo: Path, effort: str, decision: str) -> dict[str, object]:
    return payload(
        run_helper(
            repo,
            "decision",
            "reference",
            "--effort",
            effort,
            "--decision",
            decision,
        )
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


def prepare_multi_decision_final_context(repo: Path, output: str = "ticket.md") -> tuple[Path, str]:
    create_effort(repo)
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Keep final review evidence decision-specific",
        "--context",
        "A ticket graph may split decisions across worker surfaces",
        "--rationale",
        "The final union must prove every selected decision without overclaiming",
    )
    for decision in ("DEC-001", "DEC-002"):
        for obligation, evidence in (("specification", "spec.md"), ("tickets", f"issue-{decision[-1]}")):
            add_coverage(repo, "demo", decision, obligation, evidence)
    checkpoint = payload(
        run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "multi-decision final plan")
    )
    sha = str(checkpoint["sha"])
    context = write_marked_artifact(
        repo,
        "demo",
        sha,
        "DEC-001,DEC-002",
        output,
        "## What to build\n\nImplement the ticket as a complete vertical slice.",
    )
    return context, sha


def prepare_parallel_graph(repo: Path) -> str:
    create_effort(repo)
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Keep parallel tickets independently verifiable",
        "--context",
        "Two workers share one Planning decision",
        "--rationale",
        "Separate evidence surfaces avoid ledger contention",
    )
    for decision in ("DEC-001", "DEC-002"):
        for obligation, evidence in (("specification", "spec.md"), ("tickets", f"issue-{decision[-1]}")):
            add_coverage(repo, "demo", decision, obligation, evidence)
    checkpoint = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "final",
            "--message",
            "parallel graph final checkpoint",
        )
    )
    return str(checkpoint["sha"])


def create_worker_branch(
    repo: Path,
    branch: str,
    checkpoint: str,
    filename: str,
    message: str,
    trailers: tuple[str, ...] = (),
) -> str:
    run_git(repo, "switch", "-c", branch, checkpoint)
    (repo / filename).write_text(f"{branch}\n")
    run_git(repo, "add", filename)
    body_parts = [message]
    if trailers:
        body_parts.extend(("", *trailers))
    body = "\n".join(body_parts)
    run_git(repo, "commit", "-m", body)
    return run_git(repo, "rev-parse", "HEAD").stdout.strip()


def commit_change(
    repo: Path,
    filename: str,
    message: str,
    trailers: tuple[str, ...] = (),
) -> str:
    (repo / filename).write_text(f"{filename}\n")
    run_git(repo, "add", filename)
    body_parts = [message]
    if trailers:
        body_parts.extend(("", *trailers))
    run_git(repo, "commit", "-m", "\n".join(body_parts))
    return run_git(repo, "rev-parse", "HEAD").stdout.strip()


def commit_files(repo: Path, filenames: tuple[str, ...], message: str) -> str:
    """Commit a prepared set of files with one exact message."""

    run_git(repo, "add", "--", *filenames)
    run_git(repo, "commit", "-m", message)
    return run_git(repo, "rev-parse", "HEAD").stdout.strip()


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
    legacy_path = agents / "planning.md"
    legacy_before = "# Existing local planning notes\n"
    legacy_path.write_text(legacy_before)
    migrated = payload(run_helper(legacy_config, "init"))
    if migrated["status"] != "migrated":
        raise HarnessFailure(f"existing configuration did not receive lazy migration: {migrated}")
    migrated_text = legacy_path.read_text()
    if not migrated_text.startswith(legacy_before) or migrated_text.count("planning-context:v1") != 1:
        raise HarnessFailure("lazy migration replaced existing planning notes or duplicated its marker")
    if "planning-context:v1" not in migrated_text:
        raise HarnessFailure("lazy migration marker is missing")
    repeated = payload(run_helper(legacy_config, "init"))
    if repeated["status"] != "existing" or legacy_path.read_text() != migrated_text:
        raise HarnessFailure("lazy migration rewrote the initialized planning configuration")


def test_invalid_marked_configuration_fails_closed() -> None:
    repo = init_repo()
    run_helper(repo, "init")
    config = repo / "docs" / "agents" / "planning.md"
    invalid_text = config.read_text().replace("- Ledger directory: `docs/planning`\n", "")
    config.write_text(invalid_text)
    invalid = run_helper(repo, "init", expected=2)
    error = invalid.stdout.lower() + invalid.stderr.lower()
    if "missing `ledger directory" not in error or "repair" not in error:
        raise HarnessFailure(f"marked configuration without Ledger directory did not fail clearly: {invalid}")
    if config.read_text() != invalid_text:
        raise HarnessFailure("invalid marked configuration was rewritten during failed initialization")
    if (repo / "docs" / "planning").exists():
        raise HarnessFailure("invalid marked configuration silently created a fallback ledger directory")


def test_optional_decision_fields_are_supported_and_immutable() -> None:
    repo = init_repo()
    run_helper(repo, "init")
    run_helper(repo, "ledger", "create", "--effort", "demo")
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Use a bounded planning seam",
        "--context",
        "The seam must remain stable across sessions",
        "--rationale",
        "Optional decision meaning belongs in the ledger",
        "--constraints",
        "Keep the adapter deterministic",
        "--rejected-alternatives",
        "Do not infer a repository target",
    )
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    ledger_text = ledger.read_text()
    if "- Constraints: Keep the adapter deterministic" not in ledger_text:
        raise HarnessFailure("decision add did not persist optional constraints")
    if "- Rejected alternatives: Do not infer a repository target" not in ledger_text:
        raise HarnessFailure("decision add did not persist rejected alternatives")
    checkpoint = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "intermediate",
            "--message",
            "optional meaning checkpoint",
        )
    )["sha"]
    original = ledger.read_text()
    ledger.write_text(original.replace("Keep the adapter deterministic", "Changed after checkpoint", 1))
    invalid = run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        str(checkpoint),
        "--decisions",
        "DEC-001",
        expected=2,
    )
    if "immutable" not in (invalid.stdout + invalid.stderr).lower():
        raise HarnessFailure(f"checkpointed optional meaning was accepted after mutation: {invalid}")

    sentinel = init_repo()
    run_helper(sentinel, "init")
    run_helper(sentinel, "ledger", "create", "--effort", "demo")
    run_helper(
        sentinel,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Preserve an explicit empty constraint set",
        "--context",
        "The presence of optional meaning is observable",
        "--rationale",
        "A sentinel remains distinct from an omitted field",
        "--constraints",
        "none",
        "--rejected-alternatives",
        "none",
    )
    sentinel_checkpoint = str(
        payload(
            run_helper(
                sentinel,
                "checkpoint",
                "--effort",
                "demo",
                "--phase",
                "intermediate",
                "--message",
                "sentinel meaning checkpoint",
            )
        )["sha"]
    )
    sentinel_ledger = sentinel / "docs" / "planning" / "demo" / "decision-ledger.md"
    sentinel_original = sentinel_ledger.read_text()
    for field in ("- Constraints: none\n", "- Rejected alternatives: none\n"):
        sentinel_ledger.write_text(sentinel_original.replace(field, "", 1))
        invalid = run_helper(
            sentinel,
            "marker",
            "--effort",
            "demo",
            "--checkpoint",
            sentinel_checkpoint,
            "--decisions",
            "DEC-001",
            expected=2,
        )
        if "immutable" not in (invalid.stdout + invalid.stderr).lower():
            raise HarnessFailure(f"removing checkpointed {field.strip()} was accepted: {invalid}")
        sentinel_ledger.write_text(sentinel_original)

    omitted = init_repo()
    run_helper(omitted, "init")
    run_helper(omitted, "ledger", "create", "--effort", "demo")
    run_helper(
        omitted,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Preserve an omitted optional field",
        "--context",
        "An omitted field has distinct meaning",
        "--rationale",
        "Adding a sentinel after checkpoint changes the entry",
    )
    omitted_checkpoint = str(
        payload(
            run_helper(
                omitted,
                "checkpoint",
                "--effort",
                "demo",
                "--phase",
                "intermediate",
                "--message",
                "omitted meaning checkpoint",
            )
        )["sha"]
    )
    omitted_ledger = omitted / "docs" / "planning" / "demo" / "decision-ledger.md"
    omitted_original = omitted_ledger.read_text()
    for field in (
        "- Constraints: none\n",
        "- Rejected alternatives: none\n",
    ):
        omitted_ledger.write_text(omitted_original.replace("- ADR: none\n", f"- ADR: none\n{field}", 1))
        invalid = run_helper(
            omitted,
            "marker",
            "--effort",
            "demo",
            "--checkpoint",
            omitted_checkpoint,
            "--decisions",
            "DEC-001",
            expected=2,
        )
        if "immutable" not in (invalid.stdout + invalid.stderr).lower():
            raise HarnessFailure(f"adding checkpointed {field.strip()} was accepted: {invalid}")
        omitted_ledger.write_text(omitted_original)


def test_validate_ledger_override_validates_configuration_and_is_atomic() -> None:
    repo = init_repo()
    context, _ = prepare_final_context(repo)
    config = repo / "docs" / "agents" / "planning.md"
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    original_config = config.read_text()
    original_ledger = ledger.read_text()
    original_head = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    original_index = run_git(repo, "diff", "--cached", "--name-only").stdout
    config.write_text(original_config.replace("- Ledger directory: `docs/planning`\n", "", 1))
    invalid_config = config.read_text()
    invalid = run_helper(
        repo,
        "validate",
        "--context-file",
        context.name,
        "--phase",
        "final",
        "--ledger",
        "docs/planning/demo/decision-ledger.md",
        expected=2,
    )
    error = invalid.stdout.lower() + invalid.stderr.lower()
    if "missing `ledger directory" not in error or "repair" not in error:
        raise HarnessFailure(f"ledger override bypassed invalid marked configuration: {invalid}")
    if config.read_text() != invalid_config or ledger.read_text() != original_ledger:
        raise HarnessFailure("invalid configuration override changed Planning artifacts")
    if run_git(repo, "rev-parse", "HEAD").stdout.strip() != original_head:
        raise HarnessFailure("invalid configuration override created a commit")
    if run_git(repo, "diff", "--cached", "--name-only").stdout != original_index:
        raise HarnessFailure("invalid configuration override changed the index")
    config.write_text(original_config.replace("- Ledger directory: `docs/planning`", "- Ledger directory: `../outside`", 1))
    unsafe_config = config.read_text()
    invalid_unsafe = run_helper(
        repo,
        "validate",
        "--context-file",
        context.name,
        "--phase",
        "final",
        "--ledger",
        "docs/planning/demo/decision-ledger.md",
        expected=2,
    )
    unsafe_error = invalid_unsafe.stdout.lower() + invalid_unsafe.stderr.lower()
    if "path escapes the repository" not in unsafe_error:
        raise HarnessFailure(f"ledger override bypassed unsafe configured path: {invalid_unsafe}")
    if config.read_text() != unsafe_config or ledger.read_text() != original_ledger:
        raise HarnessFailure("unsafe configuration override changed Planning artifacts")
    if run_git(repo, "diff", "--cached", "--name-only").stdout != original_index:
        raise HarnessFailure("unsafe configuration override changed the index")
    config.write_text(original_config)
    valid = payload(
        run_helper(
            repo,
            "validate",
            "--context-file",
            context.name,
            "--phase",
            "final",
            "--ledger",
            "docs/planning/demo/decision-ledger.md",
        )
    )
    if valid.get("status") != "valid" or valid.get("ledger") != "docs/planning/demo/decision-ledger.md":
        raise HarnessFailure(f"a coherent local ledger override was rejected: {valid}")
    external_marker = context.read_text().replace(
        "- Decision ledger: `docs/planning/demo/decision-ledger.md`",
        "- Decision ledger: `https://example.invalid/decision-ledger.md`",
        1,
    )
    context.write_text(external_marker)
    external_override = payload(
        run_helper(
            repo,
            "validate",
            "--context-file",
            context.name,
            "--phase",
            "final",
            "--ledger",
            "docs/planning/demo/decision-ledger.md",
        )
    )
    if external_override.get("status") != "valid":
        raise HarnessFailure(f"a local override did not resolve an external ledger pointer: {external_override}")


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
    referenced = reference_decision(repo, "demo", "DEC-002")
    if referenced.get("status") != "referenced" or referenced.get("id") != "DEC-002":
        raise HarnessFailure(f"active decision reference did not preserve its stable ID: {referenced}")
    rejected = run_helper(repo, "decision", "reference", "--effort", "demo", "--decision", "DEC-001", expected=2)
    if "superseded" not in (rejected.stdout + rejected.stderr).lower():
        raise HarnessFailure("superseded decisions were still referenceable")


def test_none_obligation_requires_applicability_evidence() -> None:
    repo = init_repo()
    create_effort(repo)
    run_helper(
        repo,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Keep this process choice out of delivery tickets",
        "--context",
        "The decision changes workflow accounting only",
        "--rationale",
        "An artificial ticket would misrepresent the work",
        "--obligations",
        "none",
    )
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    before = ledger.read_text()
    missing = run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", expected=2)
    missing_text = missing.stdout.lower() + missing.stderr.lower()
    if "dec-002:applicability" not in missing_text:
        raise HarnessFailure(f"none obligation did not expose its applicability gate: {missing}")
    if ledger.read_text() != before:
        raise HarnessFailure("applicability gate failure changed the ledger")

    empty = run_helper(
        repo,
        "coverage",
        "add",
        "--effort",
        "demo",
        "--decision",
        "DEC-002",
        "--obligation",
        "applicability",
        "--evidence",
        "[]",
        expected=2,
    )
    if "non-empty" not in (empty.stdout + empty.stderr).lower() or ledger.read_text() != before:
        raise HarnessFailure(f"empty applicability evidence was accepted or changed the ledger: {empty}")

    add_coverage(repo, "demo", "DEC-002", "applicability", "non-ticket: process-only decision")
    for obligation, evidence in (("specification", "spec.md"), ("tickets", "issue-7")):
        add_coverage(repo, "demo", "DEC-001", obligation, evidence)
    final = payload(
        run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "applicability gate")
    )
    context = write_marked_artifact(
        repo,
        "demo",
        str(final["sha"]),
        "DEC-001,DEC-002",
        "none-obligation.md",
        "## What to build\n\nNo delivery ticket is needed for the process-only choice.",
    )
    valid = payload(run_helper(repo, "validate", "--context-file", context.name, "--phase", "final"))
    applicability = valid["coverage"]["DEC-002"]["applicability"]
    if applicability != {"status": "complete", "evidence": "non-ticket: process-only decision"}:
        raise HarnessFailure(f"applicability evidence was not exposed in validation JSON: {valid}")

    legacy = init_repo()
    create_effort(legacy)
    run_helper(
        legacy,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Keep legacy none entries readable",
        "--context",
        "An older ledger has no applicability lines",
        "--rationale",
        "Markerless and legacy ledgers remain supported",
        "--obligations",
        "none",
    )
    legacy_ledger = legacy / "docs" / "planning" / "demo" / "decision-ledger.md"
    legacy_ledger.write_text(
        legacy_ledger.read_text()
        .replace("  - applicability: pending\n", "", 1)
        .replace("  - applicability: none\n", "", 1)
    )
    add_coverage(legacy, "demo", "DEC-002", "applicability", "not-applicable: legacy process entry")
    legacy_text = legacy_ledger.read_text()
    if "  - applicability: complete" not in legacy_text or "not-applicable: legacy process entry" not in legacy_text:
        raise HarnessFailure("legacy none entry did not migrate to applicability coverage idempotently")

    malformed = init_repo()
    create_effort(malformed)
    run_helper(
        malformed,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Reject an artificial process ticket",
        "--context",
        "The process decision has no delivery owner",
        "--rationale",
        "Its applicability evidence must remain explicit",
        "--obligations",
        "none",
    )
    for obligation, evidence in (("specification", "spec.md"), ("tickets", "issue-7")):
        add_coverage(malformed, "demo", "DEC-001", obligation, evidence)
    add_coverage(malformed, "demo", "DEC-002", "applicability", "non-ticket: no delivery owner")
    final = payload(
        run_helper(malformed, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "valid applicability")
    )
    context = write_marked_artifact(
        malformed,
        "demo",
        str(final["sha"]),
        "DEC-001,DEC-002",
        "malformed-applicability.md",
        "## What to build\n\nThe marker remains tied to the validated final checkpoint.",
    )
    malformed_ledger = malformed / "docs" / "planning" / "demo" / "decision-ledger.md"
    valid_ledger = malformed_ledger.read_text()
    for invalid_evidence in ("bogus", "none"):
        corrupted_ledger = valid_ledger.replace("non-ticket: no delivery owner", invalid_evidence, 1)
        malformed_ledger.write_text(corrupted_ledger)
        invalid = run_helper(
            malformed,
            "validate",
            "--context-file",
            context.name,
            "--phase",
            "final",
            expected=2,
        )
        error = invalid.stdout.lower() + invalid.stderr.lower()
        if "non-ticket:" not in error or "not-applicable:" not in error:
            raise HarnessFailure(
                f"malformed applicability evidence was accepted by ledger validation: {invalid}"
            )
        if malformed_ledger.read_text() != corrupted_ledger:
            raise HarnessFailure("malformed applicability validation changed the ledger")

    tickets_only = init_repo()
    run_helper(tickets_only, "init")
    run_helper(tickets_only, "ledger", "create", "--effort", "demo")
    run_helper(
        tickets_only,
        "decision",
        "add",
        "--effort",
        "demo",
        "--decision",
        "Keep a justified non-ticket outcome",
        "--context",
        "The ticket obligation can be explicitly inapplicable",
        "--rationale",
        "The ledger records the reason without weakening other obligations",
        "--obligations",
        "tickets",
    )
    add_coverage(tickets_only, "demo", "DEC-001", "tickets", "non-ticket: no implementation slice applies")
    final = payload(
        run_helper(tickets_only, "checkpoint", "--effort", "demo", "--phase", "final", "--message", "ticket applicability")
    )
    ticket_context = write_marked_artifact(
        tickets_only,
        "demo",
        str(final["sha"]),
        "DEC-001",
        "ticket-applicability.md",
        "## What to build\n\nThe ticket obligation is justified as non-ticket.",
    )
    valid = payload(run_helper(tickets_only, "validate", "--context-file", ticket_context.name, "--phase", "final"))
    if valid.get("status") != "valid":
        raise HarnessFailure(f"non-ticket evidence on a tickets obligation was rejected: {valid}")


def test_case_insensitive_none_applicability_coverage_is_atomic() -> None:
    for sentinel in ("None", "NONE"):
        repo = init_repo()
        create_effort(repo)
        run_helper(
            repo,
            "decision",
            "add",
            "--effort",
            "demo",
            "--decision",
            "Keep this process choice out of delivery tickets",
            "--context",
            "The decision changes workflow accounting only",
            "--rationale",
            "An artificial ticket would misrepresent the work",
            "--obligations",
            "none",
        )
        ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
        sentinel_ledger = ledger.read_text().replace(
            "  - applicability: none\n",
            f"  - applicability: {sentinel}\n",
            1,
        )
        ledger.write_text(sentinel_ledger)

        invalid = run_helper(
            repo,
            "coverage",
            "add",
            "--effort",
            "demo",
            "--decision",
            "DEC-002",
            "--obligation",
            "applicability",
            "--evidence",
            "bogus",
            expected=2,
        )
        if "non-ticket:" not in (invalid.stdout + invalid.stderr) or ledger.read_text() != sentinel_ledger:
            raise HarnessFailure(f"invalid applicability evidence changed a {sentinel} ledger: {invalid}")

        evidence = "not-applicable: process-only decision"
        add_coverage(repo, "demo", "DEC-002", "applicability", evidence)
        for obligation, item in (("specification", "spec.md"), ("tickets", "issue-7")):
            add_coverage(repo, "demo", "DEC-001", obligation, item)
        final = payload(
            run_helper(
                repo,
                "checkpoint",
                "--effort",
                "demo",
                "--phase",
                "final",
                "--message",
                f"case-insensitive {sentinel} applicability",
            )
        )
        if final.get("status") != "created" or len(str(final.get("sha"))) != 40:
            raise HarnessFailure(f"case-insensitive {sentinel} applicability did not checkpoint: {final}")
        final_ledger = ledger.read_text()
        if f"  - applicability: {evidence}" not in final_ledger or f"{sentinel};" in final_ledger:
            raise HarnessFailure(f"case-insensitive {sentinel} applicability evidence was not replaced cleanly")


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


def test_marker_requires_exact_full_checkpoint_sha() -> None:
    repo = init_repo()
    context, checkpoint = prepare_final_context(repo)
    original = context.read_text()
    run_git(repo, "tag", "planning-tag", checkpoint)
    revisions = ("HEAD", "main", "planning-tag", checkpoint[:8])
    for revision in revisions:
        context.write_text(original.replace(checkpoint, revision))
        invalid = run_helper(repo, "validate", "--context-file", context.name, expected=2)
        error = invalid.stdout.lower() + invalid.stderr.lower()
        if "exact 40-character hexadecimal" not in error:
            raise HarnessFailure(f"marker accepted a non-full checkpoint revision {revision!r}: {invalid}")
    context.write_text(original)
    valid = payload(run_helper(repo, "validate", "--context-file", context.name, "--phase", "final"))
    if valid.get("status") != "valid" or valid.get("checkpoint") != checkpoint:
        raise HarnessFailure(f"full checkpoint SHA marker was rejected: {valid}")
    generated = payload(
        run_helper(
            repo,
            "marker",
            "--effort",
            "demo",
            "--checkpoint",
            "HEAD",
            "--decisions",
            "DEC-001",
        )
    )
    if generated.get("checkpoint") != checkpoint or len(str(generated.get("checkpoint"))) != 40:
        raise HarnessFailure(f"marker generation did not emit a full SHA: {generated}")


def test_checkpoint_coverage_and_evidence_are_monotonic() -> None:
    repo = init_repo()
    context, checkpoint = prepare_final_context(repo)
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    original = ledger.read_text()

    downgrade = original.replace("  - specification: complete", "  - specification: pending", 1)
    ledger.write_text(downgrade)
    invalid = run_helper(repo, "validate", "--context-file", context.name, "--phase", "final", expected=2)
    error = invalid.stdout.lower() + invalid.stderr.lower()
    if "monotonic" not in error or "coverage" not in error:
        raise HarnessFailure(f"complete coverage downgrade was accepted: {invalid}")
    if ledger.read_text() != downgrade:
        raise HarnessFailure("coverage downgrade validation unexpectedly rewrote the ledger")

    removed = original.replace("  - specification: spec.md", "  - specification: none", 1)
    ledger.write_text(removed)
    invalid = run_helper(repo, "validate", "--context-file", context.name, "--phase", "final", expected=2)
    error = invalid.stdout.lower() + invalid.stderr.lower()
    if "evidence" not in error or "append-only" not in error:
        raise HarnessFailure(f"checkpointed evidence removal was accepted: {invalid}")

    replaced = original.replace("  - specification: spec.md", "  - specification: other-spec.md", 1)
    ledger.write_text(replaced)
    invalid = run_helper(repo, "validate", "--context-file", context.name, "--phase", "final", expected=2)
    error = invalid.stdout.lower() + invalid.stderr.lower()
    if "evidence" not in error or "append-only" not in error:
        raise HarnessFailure(f"checkpointed evidence replacement was accepted: {invalid}")

    ledger.write_text(original)
    add_coverage(repo, "demo", "DEC-001", "verification", "npm run test:planning-context")
    valid = payload(run_helper(repo, "validate", "--context-file", context.name, "--phase", "final"))
    verification = valid["coverage"]["DEC-001"]["verification"]
    if verification != {"status": "complete", "evidence": "npm run test:planning-context"}:
        raise HarnessFailure(f"pending verification did not advance monotonically: {valid}")
    implementation = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "implementation",
            "--message",
            "implementation monotonicity checkpoint",
        )
    )
    implementation_sha = str(implementation["sha"])
    run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        implementation_sha,
        "--decisions",
        "DEC-001",
        "--output",
        context.name,
    )
    validated = payload(run_helper(repo, "validate", "--context-file", context.name, "--phase", "implementation"))
    if validated.get("status") != "valid" or validated.get("checkpoint") != implementation_sha:
        raise HarnessFailure(f"pending-to-complete verification did not validate at implementation phase: {validated}")


def test_empty_structured_evidence_fails_closed_and_atomically() -> None:
    repo = init_repo()
    create_effort(repo)
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    before = ledger.read_text()
    for evidence in ("[]", '[""]', '["   "]'):
        invalid = run_helper(
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
            evidence,
            expected=2,
        )
        if "non-empty" not in (invalid.stdout + invalid.stderr).lower():
            raise HarnessFailure(f"empty structured evidence did not fail clearly: {invalid}")
        if ledger.read_text() != before:
            raise HarnessFailure(f"empty structured evidence changed the ledger: {evidence}")

    corrupted = before
    corrupted = corrupted.replace("  - specification: pending", "  - specification: complete", 1)
    corrupted = corrupted.replace("  - specification: none", "  - specification: []", 1)
    corrupted = corrupted.replace("  - tickets: pending", "  - tickets: complete", 1)
    corrupted = corrupted.replace("  - tickets: none", '  - tickets: [""]', 1)
    ledger.write_text(corrupted)
    final = run_helper(repo, "checkpoint", "--effort", "demo", "--phase", "final", expected=2)
    final_text = final.stdout + final.stderr
    if "dec-001:specification" not in final_text.lower() or "dec-001:tickets" not in final_text.lower():
        raise HarnessFailure(f"final gate accepted empty structured evidence: {final}")
    if ledger.read_text() != corrupted:
        raise HarnessFailure("final empty-evidence failure changed the ledger")

    implementation_repo = init_repo()
    create_effort(implementation_repo)
    for obligation, evidence in (("specification", "spec.md"), ("tickets", "issue-7")):
        add_coverage(implementation_repo, "demo", "DEC-001", obligation, evidence)
    prepare = payload(
        run_helper(
            implementation_repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "final",
            "--message",
            "empty implementation evidence base",
        )
    )
    implementation_ledger = implementation_repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    implementation_before = implementation_ledger.read_text()
    implementation_corrupted = implementation_before.replace("  - verification: pending", "  - verification: complete", 1)
    implementation_corrupted = implementation_corrupted.replace("  - verification: none", "  - verification: []", 1)
    implementation_ledger.write_text(implementation_corrupted)
    implementation = run_helper(
        implementation_repo,
        "checkpoint",
        "--effort",
        "demo",
        "--phase",
        "implementation",
        expected=2,
    )
    if "verification" not in (implementation.stdout + implementation.stderr).lower():
        raise HarnessFailure(f"implementation gate accepted empty structured evidence: {implementation}")
    if implementation_ledger.read_text() != implementation_corrupted:
        raise HarnessFailure("implementation empty-evidence failure changed the ledger")
    if str(prepare["phase"]) != "final":
        raise HarnessFailure(f"final empty-evidence fixture did not create a final checkpoint: {prepare}")

    for evidence in ("[]", '[""]'):
        aggregate_repo = init_repo()
        _, planning_checkpoint = prepare_final_context(aggregate_repo)
        tip = commit_change(
            aggregate_repo,
            "empty-verification.txt",
            f"forged empty verification\n\nPlanning-Verification: DEC-001 | {evidence}",
        )
        aggregate_ledger = aggregate_repo / "docs" / "planning" / "demo" / "decision-ledger.md"
        aggregate_before = aggregate_ledger.read_text()
        invalid = run_helper(
            aggregate_repo,
            "coverage",
            "aggregate",
            "--effort",
            "demo",
            "--checkpoint",
            planning_checkpoint,
            "--head",
            tip,
            "--decisions",
            "DEC-001",
            "--commit",
            tip,
            expected=2,
        )
        if "non-empty" not in (invalid.stdout + invalid.stderr).lower():
            raise HarnessFailure(f"aggregation accepted empty structured verification evidence: {invalid}")
        if aggregate_ledger.read_text() != aggregate_before:
            raise HarnessFailure("empty verification aggregation failure changed the ledger")


def test_checkpointed_json_evidence_is_append_only() -> None:
    repo = init_repo()
    context, planning_checkpoint = prepare_final_context(repo)
    tip = commit_change(
        repo,
        "verification.txt",
        "verification evidence",
        ("Planning-Verification: DEC-001 | first structured evidence",),
    )
    payload(
        run_helper(
            repo,
            "coverage",
            "aggregate",
            "--effort",
            "demo",
            "--checkpoint",
            planning_checkpoint,
            "--head",
            tip,
            "--decisions",
            "DEC-001",
            "--commit",
            tip,
        )
    )
    implementation = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "implementation",
            "--message",
            "structured evidence checkpoint",
        )
    )
    implementation_sha = str(implementation["sha"])
    run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        implementation_sha,
        "--decisions",
        "DEC-001",
        "--output",
        context.name,
    )
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    before = ledger.read_text()
    verification_line = next(
        line
        for line in before.splitlines()
        if line.startswith("  - verification:")
        and line.split(":", 1)[1].strip().startswith("[")
    )
    values = json.loads(verification_line.split(":", 1)[1].strip())
    extended_values = [*values, "manually appended evidence"]
    extended_line = "  - verification: " + json.dumps(
        extended_values,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    ledger.write_text(before.replace(verification_line, extended_line, 1))
    valid = payload(run_helper(repo, "validate", "--context-file", context.name, "--phase", "implementation"))
    if valid.get("status") != "valid":
        raise HarnessFailure(f"ordered JSON evidence extension was rejected: {valid}")

    invalid_values = ([], [""], [" "], [*values, ""], ["arbitrary replacement"])
    for values_after in invalid_values:
        replacement_line = "  - verification: " + json.dumps(
            values_after,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        corrupted = before.replace(verification_line, replacement_line, 1)
        ledger.write_text(corrupted)
        invalid = run_helper(repo, "validate", "--context-file", context.name, "--phase", "final", expected=2)
        error = invalid.stdout.lower() + invalid.stderr.lower()
        if "append-only" not in error or ledger.read_text() != corrupted:
            raise HarnessFailure(f"invalid JSON evidence append was accepted: {values_after!r}, {invalid}")
        ledger.write_text(before)


def test_implement_preflight_wiring() -> None:
    skill = IMPLEMENT_SKILL.read_text()
    docs = IMPLEMENT_DOCS.read_text()
    planning_contract = PLANNING_CONTRACT.read_text()
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
    unsafe_tracker_pipe = re.compile(r"gh issue view[^\n]*(?:\|\s*python3|(?:\\\n[ \t]*)+\|\s*python3)")
    for name, text in (("implement skill", skill), ("planning contract", planning_contract)):
        if unsafe_tracker_pipe.search(text):
            raise HarnessFailure(f"{name} invokes the validator through an unchecked tracker pipeline")
    safe_validator = "python3 skills/engineering/planning-context/scripts/planning_context.py --repo . --json validate --context-stdin --phase final <<<\"$issue_body\""
    if 'issue_body="$(gh issue view' not in skill or safe_validator not in skill:
        raise HarnessFailure("implement does not capture tracker content before stdin validation")
    if "never interpret a tracker read failure as `legacy`" not in skill:
        raise HarnessFailure("implement does not keep tracker read failures out of the legacy path")


def test_implement_planning_closeout_wiring() -> None:
    skill = IMPLEMENT_SKILL.read_text()
    docs = IMPLEMENT_DOCS.read_text()
    implement_spec = IMPLEMENT_SPEC_SKILL.read_text()
    assert_ordered(
        skill,
        "implement Planning closeout",
        "## Planning preflight",
        'Call the Skill tool with "tdd"',
        "Commit the completed implementation",
        'Call the Skill tool with "code-review"',
        "## Planning implementation closeout",
        "coverage aggregate",
        "checkpoint --phase implementation",
    )
    for phrase in (
        "one for each applicable decision returned by preflight",
        "--decisions <comma-separated-preflight-decision-IDs>",
        "--head <final-reviewed-head-sha>",
        "--commit <final-reviewed-head-sha>",
        "whose behavior that commit verifies or changes",
        "the union of the final history and validated ticket evidence",
        "Only after aggregation succeeds",
        'If preflight returned "status": "legacy"',
        "never infer a ledger, checkpoint, or coverage aggregation",
    ):
        if phrase not in skill:
            raise HarnessFailure(f"implement Planning closeout contract is missing: {phrase}")
    assert_ordered(
        docs,
        "implement documentation Planning closeout",
        "## Planning preflight",
        "Commit the implementation",
        "code-review",
        "coverage aggregate",
        "checkpoint --phase implementation",
    )
    assert_ordered(
        implement_spec,
        "implement-spec Planning closeout",
        "## Merge and review checkpoint",
        "code-review",
        "## Planning implementation closeout",
        "coverage aggregate",
        "checkpoint --phase implementation",
    )
    for phrase in (
        "the final reviewed integration head",
        "--commit <final-reviewed-head-sha>",
        "A worker records only decisions relevant to its ticket",
        "the union of the final history and validated ticket evidence",
        "every decision ID returned by preflight",
        "Skip this closeout for an entirely markerless graph",
        "do not infer a ledger, coverage aggregation, or Planning checkpoint",
    ):
        if phrase not in implement_spec:
            raise HarnessFailure(f"implement-spec Planning closeout contract is missing: {phrase}")


def test_implement_single_ticket_planning_closeout() -> None:
    repo = init_repo()
    context, planning_checkpoint = prepare_multi_decision_final_context(repo)
    implementation_tip = commit_change(
        repo,
        "implementation.txt",
        "single-ticket implementation",
        (
            "Planning-Verification: DEC-001 | single-ticket implementation verification",
            "Planning-Verification: DEC-002 | single-ticket implementation verification",
        ),
    )
    review_fix_tip = commit_change(
        repo,
        "review-fix.txt",
        "single-ticket review fix",
        ("Planning-Verification: DEC-002 | single-ticket review-fix verification",),
    )
    review_fix_message = run_git(repo, "show", "-s", "--format=%B", review_fix_tip).stdout
    if "Planning-Verification: DEC-001" in review_fix_message or "Planning-Verification: DEC-002" not in review_fix_message:
        raise HarnessFailure("single-ticket fix did not record only its changed decision")
    aggregated = payload(
        run_helper(
            repo,
            "coverage",
            "aggregate",
            "--effort",
            "demo",
            "--checkpoint",
            planning_checkpoint,
            "--head",
            review_fix_tip,
            "--decisions",
            "DEC-001,DEC-002",
            "--commit",
            review_fix_tip,
        )
    )
    if aggregated.get("status") != "aggregated" or aggregated.get("decisions") != ["DEC-001", "DEC-002"]:
        raise HarnessFailure(f"single-ticket closeout did not aggregate preflight decisions: {aggregated}")
    if implementation_tip not in run_git(repo, "rev-list", "--reverse", f"{planning_checkpoint}..{review_fix_tip}").stdout:
        raise HarnessFailure("single-ticket review-fix tip does not include the implementation commit")
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    ledger_text = ledger.read_text()
    for evidence in (
        "single-ticket implementation verification",
        "single-ticket review-fix verification",
    ):
        if evidence not in ledger_text:
            raise HarnessFailure(f"final reviewed evidence was not aggregated: {evidence}")
    for decision in ("DEC-001", "DEC-002"):
        block = ledger_text[ledger_text.index(f"## {decision}") :]
        if "  - verification: complete" not in block:
            raise HarnessFailure(f"single-ticket closeout did not complete verification coverage for {decision}")

    implementation = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "implementation",
            "--message",
            "single-ticket implementation evidence checkpoint",
        )
    )
    implementation_sha = str(implementation["sha"])
    parent = run_git(repo, "rev-parse", f"{implementation_sha}^").stdout.strip()
    if implementation_sha == review_fix_tip or parent != review_fix_tip:
        raise HarnessFailure("implementation checkpoint was not created after the final reviewed head")
    message = run_git(repo, "show", "-s", "--format=%B", implementation_sha).stdout
    if "Planning-Phase: implementation" not in message:
        raise HarnessFailure("single-ticket implementation checkpoint lacks its phase trailer")
    run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        implementation_sha,
        "--decisions",
        "DEC-001,DEC-002",
        "--output",
        context.name,
    )
    validated = payload(run_helper(repo, "validate", "--context-file", context.name, "--phase", "implementation"))
    if validated.get("status") != "valid" or validated.get("checkpoint") != implementation_sha:
        raise HarnessFailure(f"single-ticket final Planning checkpoint did not validate: {validated}")


def test_implementation_checkpoint_selection_is_scoped_and_fail_closed() -> None:
    repo = init_repo()
    _, planning_checkpoint = prepare_multi_decision_final_context(repo)
    final_selection = run_helper(
        repo,
        "checkpoint",
        "--effort",
        "demo",
        "--phase",
        "final",
        "--decisions",
        "DEC-001",
        expected=2,
    )
    if "only supported for the implementation phase" not in (final_selection.stdout + final_selection.stderr):
        raise HarnessFailure(f"final checkpoint accepted an implementation-only decision subset: {final_selection}")

    worker = commit_change(
        repo,
        "selected-implementation.txt",
        "selected implementation",
        ("Planning-Verification: DEC-001 | selected implementation verification",),
    )
    aggregate = payload(
        run_helper(
            repo,
            "coverage",
            "aggregate",
            "--effort",
            "demo",
            "--checkpoint",
            planning_checkpoint,
            "--head",
            worker,
            "--decisions",
            "DEC-001",
            "--commit",
            worker,
        )
    )
    if aggregate.get("status") != "aggregated" or aggregate.get("decisions") != ["DEC-001"]:
        raise HarnessFailure(f"selected implementation evidence did not aggregate safely: {aggregate}")

    default = run_helper(
        repo,
        "checkpoint",
        "--effort",
        "demo",
        "--phase",
        "implementation",
        expected=2,
    )
    default_text = default.stdout + default.stderr
    if "dec-002:verification" not in default_text.lower():
        raise HarnessFailure(f"default implementation gate bypassed an unselected decision: {default}")
    selected = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "implementation",
            "--decisions",
            "DEC-001",
            "--message",
            "selected implementation checkpoint",
        )
    )
    if selected.get("decisions") != ["DEC-001"]:
        raise HarnessFailure(f"implementation checkpoint did not expose its selected decisions: {selected}")
    marker = write_marked_artifact(
        repo,
        "demo",
        str(selected["sha"]),
        "DEC-001",
        "selected-implementation.md",
        "## What to build\n\nImplement the selected decision.",
    )
    valid = payload(run_helper(repo, "validate", "--context-file", marker.name, "--phase", "implementation"))
    if valid.get("status") != "valid" or valid.get("decisions") != ["DEC-001"]:
        raise HarnessFailure(f"selected implementation marker did not validate: {valid}")


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


def test_implement_spec_preflight_wiring() -> None:
    skill = IMPLEMENT_SPEC_SKILL.read_text()
    metadata = IMPLEMENT_SPEC_METADATA.read_text()
    bucket = IN_PROGRESS_README.read_text()
    tracker = ISSUE_TRACKER.read_text()
    preflight = skill.find("## Planning context preflight")
    branch = skill.find("creating an integration branch")
    if preflight < 0 or branch < 0 or preflight > branch:
        raise HarnessFailure("implement-spec does not gate branch creation on Planning preflight")
    skill_lower = skill.lower()
    for phrase in (
        "the specification and every ticket",
        '"status": "valid"',
        "full `checkpoint` SHA",
        "same effort, ledger, and checkpoint",
        "ancestry.is_ancestor: true",
        "issue_body=\"$(gh issue view",
        "--context-stdin",
        "never pass an empty body",
        "markerless",
        "mixes marked and markerless",
        "context pointers",
        "common checkpoint lineage",
        "Planning-Verification:",
        "observable evidence",
        "--ticket-evidence",
        "coverage aggregate",
        "--phase implementation",
        "frontier",
        "merger",
        "only review checkpoint",
        "Clean up all",
        "worktrees",
    ):
        if phrase.lower() not in skill_lower:
            raise HarnessFailure(f"implement-spec coordination contract is missing: {phrase}")
    unsafe_tracker_pipe = re.compile(r"gh issue view[^\n]*(?:\|\s*python3|(?:\\\n[ \t]*)+\|\s*python3)")
    if unsafe_tracker_pipe.search(skill):
        raise HarnessFailure("implement-spec invokes validation through an unchecked tracker pipeline")
    if "docs/agents/issue-tracker.md" not in skill:
        raise HarnessFailure("implement-spec does not read the configured issue tracker before remote reads")
    if "manoelcalixto/mattpocock-skills" in skill:
        raise HarnessFailure("implement-spec hardcodes the fork instead of using issue-tracker configuration")
    if "--repo owner/repository" not in skill or "fully qualified tracker target configured there" not in skill:
        raise HarnessFailure("implement-spec does not use an explicit configured tracker target")
    if "Every `gh` issue and pull request command must pass `--repo manoelcalixto/mattpocock-skills`." not in tracker:
        raise HarnessFailure("the fork issue-tracker contract is not explicit for this repository")
    if "interface:\n  display_name:" not in metadata or "\n  short_description:" not in metadata:
        raise HarnessFailure("implement-spec OpenAI metadata is not nested under interface")
    if "validated Planning checkpoint" not in bucket or "implement-spec" not in bucket:
        raise HarnessFailure("in-progress catalog does not describe checkpointed implement-spec coordination")
    if "\u2014" in skill or "\u2014" in metadata:
        raise HarnessFailure("implement-spec artifacts contain an em dash")
    plugin = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text())
    if "./skills/in-progress/implement-spec" in plugin.get("skills", []):
        raise HarnessFailure("in-progress implement-spec was added to the Claude plugin")


def test_implement_spec_markerless_and_mixed_graph() -> None:
    legacy = init_repo()
    spec = legacy / "spec.md"
    ticket = legacy / "ticket.md"
    spec.write_text("# Legacy spec\n")
    ticket.write_text("# Legacy ticket\n")
    spec_result = payload(run_helper(legacy, "validate", "--context-file", spec.name))
    ticket_result = payload(run_helper(legacy, "validate", "--context-file", ticket.name))
    if spec_result.get("status") != "legacy" or ticket_result.get("status") != "legacy":
        raise HarnessFailure(f"an entirely markerless graph did not preserve the legacy path: {spec_result}, {ticket_result}")

    mixed = init_repo()
    marked, _ = prepare_final_context(mixed, "marked-spec.md")
    markerless = mixed / "markerless-ticket.md"
    markerless.write_text("# Ticket without Planning context\n")
    marked_result = payload(run_helper(mixed, "validate", "--context-file", marked.name, "--phase", "final"))
    markerless_result = payload(run_helper(mixed, "validate", "--context-file", markerless.name))
    if marked_result.get("status") != "valid" or markerless_result.get("status") != "legacy":
        raise HarnessFailure(f"mixed graph inputs did not expose their incompatible states: {marked_result}, {markerless_result}")
    if marked_result.get("status") == "valid" and markerless_result.get("status") == "legacy":
        return
    raise HarnessFailure("unreachable mixed graph assertion")


def test_parallel_ticket_branches_share_checkpoint_without_ledger_edits() -> None:
    repo = init_repo()
    checkpoint = prepare_parallel_graph(repo)
    checkpoint_ledger = run_git(
        repo,
        "show",
        f"{checkpoint}:docs/planning/demo/decision-ledger.md",
    ).stdout
    first = create_worker_branch(
        repo,
        "ticket-one",
        checkpoint,
        "ticket-one.txt",
        "ticket one implementation",
        (
            "Planning-Verification: DEC-001 | ticket one test",
        ),
    )
    first_ledger = run_git(repo, "show", "HEAD:docs/planning/demo/decision-ledger.md").stdout
    if first_ledger != checkpoint_ledger:
        raise HarnessFailure("first parallel implementer changed the shared ledger")
    second = create_worker_branch(
        repo,
        "ticket-two",
        checkpoint,
        "ticket-two.txt",
        "ticket two implementation",
        (
            "Planning-Verification: DEC-001 | ticket two test",
            "Planning-Verification: DEC-002 | ticket two test",
        ),
    )
    second_ledger = run_git(repo, "show", "HEAD:docs/planning/demo/decision-ledger.md").stdout
    if second_ledger != checkpoint_ledger:
        raise HarnessFailure("second parallel implementer changed the shared ledger")
    run_git(repo, "switch", "-c", "integration", checkpoint)
    run_git(repo, "merge", "--no-ff", "ticket-one", "-m", "merge ticket one")
    run_git(repo, "merge", "--no-ff", "ticket-two", "-m", "merge ticket two")
    integration_ledger = run_git(repo, "show", "HEAD:docs/planning/demo/decision-ledger.md").stdout
    if integration_ledger != checkpoint_ledger:
        raise HarnessFailure("merging parallel ticket branches produced a ledger conflict or edit")
    if run_git(repo, "merge-base", "--is-ancestor", checkpoint, "HEAD", check=False).returncode != 0:
        raise HarnessFailure("integration branch does not descend from the validated checkpoint")
    for worker in (first, second):
        if run_git(repo, "merge-base", "--is-ancestor", worker, "HEAD", check=False).returncode != 0:
            raise HarnessFailure(f"merged worker tip is not an integration ancestor: {worker}")


def test_trailers_are_read_only_from_the_final_block() -> None:
    repo = init_repo()
    _, planning_checkpoint = prepare_final_context(repo)
    forged_message = (
        "forged checkpoint subject\n\n"
        "Planning-Checkpoint: demo\n"
        "Planning-Phase: final\n"
        "Planning-Ledger: docs/planning/demo/decision-ledger.md\n\n"
        "trailing prose that is not trailer metadata\n"
    )
    run_git(repo, "commit", "--allow-empty", "-m", forged_message)
    forged_checkpoint = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    invalid = run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        forged_checkpoint,
        "--decisions",
        "DEC-001",
        expected=2,
    )
    if "does not name the declared effort" not in (invalid.stdout + invalid.stderr):
        raise HarnessFailure(f"body metadata followed by prose was accepted as checkpoint trailers: {invalid}")

    verification_tip = commit_change(
        repo,
        "forged-verification.txt",
        "forged verification subject\n\nPlanning-Verification: DEC-001 | fake evidence\n\ntrailing prose",
    )
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    before = ledger.read_text()
    missing = run_helper(
        repo,
        "coverage",
        "aggregate",
        "--effort",
        "demo",
        "--checkpoint",
        planning_checkpoint,
        "--head",
        verification_tip,
        "--decisions",
        "DEC-001",
        "--commit",
        verification_tip,
        expected=2,
    )
    error = missing.stdout + missing.stderr
    if "at least one verification commit or ticket evidence record is required" not in error.lower():
        raise HarnessFailure(f"body verification metadata followed by prose was accepted: {missing}")
    if ledger.read_text() != before:
        raise HarnessFailure("forged verification trailer failure changed the ledger")


def test_checkpoint_ownership_rejects_non_planning_and_mixed_diffs() -> None:
    repo = init_repo()
    _, planning_checkpoint = prepare_final_context(repo)
    before_head = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    evil_path = repo / "evil-at-creation.txt"
    evil_path.write_text("unrelated checkpoint input\n")
    invalid_creation = run_helper(
        repo,
        "checkpoint",
        "--effort",
        "demo",
        "--phase",
        "final",
        "--path",
        evil_path.name,
        expected=2,
    )
    creation_error = invalid_creation.stdout + invalid_creation.stderr
    if "not identifiable as a planning context artifact" not in creation_error.lower():
        raise HarnessFailure(f"checkpoint creation accepted an unrelated path: {invalid_creation}")
    if run_git(repo, "rev-parse", "HEAD").stdout.strip() != before_head:
        raise HarnessFailure("rejected checkpoint path created a commit")
    if run_git(repo, "diff", "--cached", "--name-only").stdout.strip():
        raise HarnessFailure("rejected checkpoint path staged unrelated content")

    legacy_repo = init_repo()
    _, generated_legacy_checkpoint = prepare_final_context(legacy_repo)
    legacy_message = "\n".join(
        line
        for line in run_git(
            legacy_repo, "show", "-s", "--format=%B", generated_legacy_checkpoint
        ).stdout.splitlines()
        if not line.startswith("Planning-Paths:")
    )
    run_git(legacy_repo, "commit", "--amend", "-F", "-", input_text=legacy_message)
    legacy_checkpoint = run_git(legacy_repo, "rev-parse", "HEAD").stdout.strip()
    legacy_context = write_marked_artifact(
        legacy_repo,
        "demo",
        legacy_checkpoint,
        "DEC-001",
        "legacy-ticket.md",
        "## What to build\n\nRead an old checkpoint without an ownership trailer.",
    )
    legacy_valid = payload(
        run_helper(
            legacy_repo,
            "validate",
            "--context-file",
            legacy_context.name,
            "--phase",
            "final",
        )
    )
    if legacy_valid.get("status") != "valid":
        raise HarnessFailure(f"old checkpoint without Planning-Paths lost compatibility: {legacy_valid}")

    legacy_variants = {
        "empty": None,
        "config-only": "config",
        "ledger-only": "ledger",
    }
    for name, changed_path in legacy_variants.items():
        variant_repo = init_repo()
        variant_context, generated = prepare_final_context(variant_repo, f"{name}-ticket.md")
        variant_message = (
            f"{name} legacy checkpoint\n\n"
            "Planning-Checkpoint: demo\n"
            "Planning-Phase: final\n"
            "Planning-Ledger: docs/planning/demo/decision-ledger.md"
        )
        if changed_path == "config":
            config_path = variant_repo / "docs" / "agents" / "planning.md"
            config_path.write_text(config_path.read_text() + "\nlegacy config change\n")
            run_git(variant_repo, "add", "docs/agents/planning.md")
            run_git(variant_repo, "commit", "-m", variant_message)
        elif changed_path == "ledger":
            ledger_path = variant_repo / "docs" / "planning" / "demo" / "decision-ledger.md"
            ledger_path.write_text(ledger_path.read_text() + "\nlegacy ledger change\n")
            run_git(variant_repo, "add", "docs/planning/demo/decision-ledger.md")
            run_git(variant_repo, "commit", "-m", variant_message)
        else:
            run_git(variant_repo, "commit", "--allow-empty", "-m", variant_message)
        variant_checkpoint = run_git(variant_repo, "rev-parse", "HEAD").stdout.strip()
        variant_context.write_text(variant_context.read_text().replace(generated, variant_checkpoint, 1))
        before_variant_head = variant_checkpoint
        before_variant_index = run_git(variant_repo, "diff", "--cached", "--name-only").stdout
        before_variant_config = (variant_repo / "docs" / "agents" / "planning.md").read_text()
        before_variant_ledger = (
            variant_repo / "docs" / "planning" / "demo" / "decision-ledger.md"
        ).read_text()
        invalid_variant = run_helper(
            variant_repo,
            "validate",
            "--context-file",
            variant_context.name,
            "--phase",
            "final",
            expected=2,
        )
        variant_error = invalid_variant.stdout.lower() + invalid_variant.stderr.lower()
        if "legacy checkpoints" not in variant_error or "config" not in variant_error or "ledger" not in variant_error:
            raise HarnessFailure(f"invalid {name} legacy checkpoint was accepted unclearly: {invalid_variant}")
        if run_git(variant_repo, "rev-parse", "HEAD").stdout.strip() != before_variant_head:
            raise HarnessFailure(f"invalid {name} legacy checkpoint created a commit")
        if (variant_repo / "docs" / "agents" / "planning.md").read_text() != before_variant_config:
            raise HarnessFailure(f"invalid {name} legacy checkpoint changed the configuration")
        if (
            variant_repo / "docs" / "planning" / "demo" / "decision-ledger.md"
        ).read_text() != before_variant_ledger:
            raise HarnessFailure(f"invalid {name} legacy checkpoint changed the ledger")
        if run_git(variant_repo, "diff", "--cached", "--name-only").stdout != before_variant_index:
            raise HarnessFailure(f"invalid {name} legacy checkpoint changed the index")

    new_empty_repo = init_repo()
    new_context, generated = prepare_final_context(new_empty_repo, "new-empty-ticket.md")
    new_message = (
        "new empty checkpoint\n\n"
        "Planning-Checkpoint: demo\n"
        "Planning-Phase: final\n"
        "Planning-Ledger: docs/planning/demo/decision-ledger.md\n"
        'Planning-Paths: ["docs/agents/planning.md","docs/planning/demo/decision-ledger.md"]'
    )
    run_git(new_empty_repo, "commit", "--allow-empty", "-m", new_message)
    new_checkpoint = run_git(new_empty_repo, "rev-parse", "HEAD").stdout.strip()
    new_context.write_text(new_context.read_text().replace(generated, new_checkpoint, 1))
    new_empty_ledger = new_empty_repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    new_empty_index = run_git(new_empty_repo, "diff", "--cached", "--name-only").stdout
    new_empty_config = new_empty_repo / "docs" / "agents" / "planning.md"
    new_empty_config_before = new_empty_config.read_text()
    new_empty_before = new_empty_ledger.read_text()
    invalid_new = run_helper(
        new_empty_repo,
        "validate",
        "--context-file",
        new_context.name,
        "--phase",
        "final",
        expected=2,
    )
    if "empty diff" not in (invalid_new.stdout + invalid_new.stderr).lower():
        raise HarnessFailure(f"new checkpoint with an empty diff was accepted: {invalid_new}")
    if new_empty_config.read_text() != new_empty_config_before:
        raise HarnessFailure("new empty checkpoint validation changed the configuration")
    if new_empty_ledger.read_text() != new_empty_before:
        raise HarnessFailure("new empty checkpoint validation changed the ledger")
    if run_git(new_empty_repo, "diff", "--cached", "--name-only").stdout != new_empty_index:
        raise HarnessFailure("new empty checkpoint validation changed the index")

    forged = commit_change(
        repo,
        "evil.txt",
        "forged checkpoint\n\n"
        "Planning-Checkpoint: demo\n"
        "Planning-Phase: final\n"
        "Planning-Ledger: docs/planning/demo/decision-ledger.md\n"
        'Planning-Paths: ["docs/agents/planning.md","docs/planning/demo/decision-ledger.md"]',
    )
    invalid = run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        forged,
        "--decisions",
        "DEC-001",
        expected=2,
    )
    if "non-owned paths" not in (invalid.stdout + invalid.stderr).lower():
        raise HarnessFailure(f"checkpoint changing only a non-planning file was accepted: {invalid}")

    config = repo / "docs" / "agents" / "planning.md"
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    config.write_text(config.read_text() + "\n# owned planning note\n")
    ledger.write_text(ledger.read_text() + "\n# owned planning note\n")
    mixed = repo / "mixed-evil.txt"
    mixed.write_text("unrelated\n")
    mixed_message = (
        "mixed forged checkpoint\n\n"
        "Planning-Checkpoint: demo\n"
        "Planning-Phase: final\n"
        "Planning-Ledger: docs/planning/demo/decision-ledger.md\n"
        'Planning-Paths: ["docs/agents/planning.md","docs/planning/demo/decision-ledger.md"]'
    )
    mixed_tip = commit_files(
        repo,
        ("docs/agents/planning.md", "docs/planning/demo/decision-ledger.md", mixed.name),
        mixed_message,
    )
    invalid_mixed = run_helper(
        repo,
        "marker",
        "--effort",
        "demo",
        "--checkpoint",
        mixed_tip,
        "--decisions",
        "DEC-001",
        expected=2,
    )
    if "non-owned paths" not in (invalid_mixed.stdout + invalid_mixed.stderr).lower():
        raise HarnessFailure(f"mixed planning and non-planning checkpoint diff was accepted: {invalid_mixed}")


def test_verification_aggregation_requires_merged_tips_and_is_atomic() -> None:
    repo = init_repo()
    checkpoint = prepare_parallel_graph(repo)
    first = create_worker_branch(
        repo,
        "ticket-one",
        checkpoint,
        "ticket-one.txt",
        "ticket one implementation",
        (
            "Planning-Verification: DEC-001 | ticket one test; item A\n continuation",
            "Planning-Verification: DEC-001 | ticket one test; item B",
        ),
    )
    second = create_worker_branch(
        repo,
        "ticket-two",
        checkpoint,
        "ticket-two.txt",
        "ticket two implementation",
        ("Planning-Verification: DEC-002 | ticket two test",),
    )
    run_git(repo, "switch", "-c", "integration", checkpoint)
    run_git(repo, "merge", "--no-ff", "ticket-one", "-m", "merge ticket one")
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    before = ledger.read_text()
    unmerged = run_helper(
        repo,
        "coverage",
        "aggregate",
        "--effort",
        "demo",
        "--checkpoint",
        checkpoint,
        "--head",
        "HEAD",
        "--decisions",
        "DEC-001,DEC-002",
        "--commit",
        first,
        "--commit",
        second,
        expected=2,
    )
    if "not an ancestor of integration head" not in (unmerged.stdout + unmerged.stderr).lower():
        raise HarnessFailure(f"aggregation accepted an unmerged worker tip: {unmerged}")
    if ledger.read_text() != before:
        raise HarnessFailure("unmerged-tip failure changed the ledger")

    missing = run_helper(
        repo,
        "coverage",
        "aggregate",
        "--effort",
        "demo",
        "--checkpoint",
        checkpoint,
        "--head",
        "HEAD",
        "--decisions",
        "DEC-001,DEC-002",
        "--commit",
        first,
        expected=2,
    )
    missing_text = missing.stdout + missing.stderr
    if "verification" not in missing_text.lower() or "dec-002" not in missing_text.lower():
        raise HarnessFailure(f"incomplete verification did not fail with the missing decision: {missing}")
    if ledger.read_text() != before:
        raise HarnessFailure("incomplete verification failure changed the ledger")


def test_merged_coordinator_aggregation_and_implementation_checkpoint() -> None:
    repo = init_repo()
    checkpoint = prepare_parallel_graph(repo)
    first = create_worker_branch(
        repo,
        "ticket-one",
        checkpoint,
        "ticket-one.txt",
        "ticket one implementation",
        (
            "Planning-Verification: DEC-001 | ticket one test; item A\n continuation",
            "Planning-Verification: DEC-001 | ticket one test; item B",
        ),
    )
    second = create_worker_branch(
        repo,
        "ticket-two",
        checkpoint,
        "ticket-two.txt",
        "ticket two implementation",
        ("Planning-Verification: DEC-002 | ticket two test",),
    )
    run_git(repo, "switch", "-c", "integration", checkpoint)
    run_git(repo, "merge", "--no-ff", "ticket-one", "-m", "merge ticket one")
    run_git(repo, "merge", "--no-ff", "ticket-two", "-m", "merge ticket two")
    result = payload(
        run_helper(
            repo,
            "coverage",
            "aggregate",
            "--effort",
            "demo",
            "--checkpoint",
            checkpoint,
            "--head",
            "HEAD",
            "--decisions",
            "DEC-001,DEC-002",
            "--commit",
            first,
            "--commit",
            second,
        )
    )
    if result.get("status") != "aggregated":
        raise HarnessFailure(f"merged coordinator aggregation did not write evidence: {result}")
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    ledger_text = ledger.read_text()
    for decision in ("DEC-001", "DEC-002"):
        block = ledger_text[ledger_text.index(f"## {decision}") :]
        if "  - verification: complete" not in block:
            raise HarnessFailure(f"coordinator did not complete verification for {decision}")
    if "ticket one test; item A continuation" not in ledger_text or "ticket one test; item B" not in ledger_text:
        raise HarnessFailure("repeatable or continued evidence was not retained as separate values")
    repeat = payload(
        run_helper(
            repo,
            "coverage",
            "aggregate",
            "--effort",
            "demo",
            "--checkpoint",
            checkpoint,
            "--head",
            "HEAD",
            "--decisions",
            "DEC-001,DEC-002",
            "--commit",
            second,
            "--commit",
            first,
        )
    )
    if repeat.get("status") != "unchanged" or ledger.read_text() != ledger_text:
        raise HarnessFailure("repeating aggregation was not deterministic and idempotent")
    implementation = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            "demo",
            "--phase",
            "implementation",
            "--message",
            "implementation evidence checkpoint",
        )
    )
    implementation_sha = str(implementation["sha"])
    if implementation_sha == checkpoint:
        raise HarnessFailure("implementation checkpoint did not advance after aggregation")
    message = run_git(repo, "show", "-s", "--format=%B", implementation_sha).stdout
    if "Planning-Phase: implementation" not in message:
        raise HarnessFailure("implementation checkpoint lacks its phase trailer")


def test_aggregation_rejects_ledger_edit_in_merge_commit() -> None:
    repo = init_repo()
    checkpoint = prepare_parallel_graph(repo)
    create_worker_branch(
        repo,
        "merge-side-one",
        checkpoint,
        "merge-side-one.txt",
        "merge side one",
        ("Planning-Verification: DEC-001 | side one test",),
    )
    create_worker_branch(
        repo,
        "merge-side-two",
        checkpoint,
        "merge-side-two.txt",
        "merge side two",
        ("Planning-Verification: DEC-001 | side two test",),
    )
    run_git(repo, "switch", "merge-side-one")
    run_git(repo, "merge", "--no-ff", "--no-commit", "merge-side-two")
    ledger = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    ledger.write_text(ledger.read_text().replace("  - verification: pending", "  - verification: complete"))
    run_git(repo, "add", ledger.relative_to(repo).as_posix())
    run_git(
        repo,
        "commit",
        "-m",
        "resolve merge with an invalid ledger edit\n\nPlanning-Verification: DEC-001 | merged test",
    )
    tip = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    before = ledger.read_text()
    invalid = run_helper(
        repo,
        "coverage",
        "aggregate",
        "--effort",
        "demo",
        "--checkpoint",
        checkpoint,
        "--head",
        "HEAD",
        "--decisions",
        "DEC-001",
        "--commit",
        tip,
        expected=2,
    )
    error = invalid.stdout + invalid.stderr
    if "edits the shared Decision ledger" not in error:
        raise HarnessFailure(f"merge-commit ledger edit was not rejected: {invalid}")
    if ledger.read_text() != before:
        raise HarnessFailure("merge-commit ledger-edit failure changed the ledger")


def test_ticket_only_evidence_surface() -> None:
    repo = init_repo()
    checkpoint = prepare_parallel_graph(repo)
    run_git(repo, "switch", "-c", "integration", checkpoint)
    result = payload(
        run_helper(
            repo,
            "coverage",
            "aggregate",
            "--effort",
            "demo",
            "--checkpoint",
            checkpoint,
            "--head",
            "HEAD",
            "--decisions",
            "DEC-001",
            "--ticket-evidence",
            "DEC-001 | issue #8 | ticket-only acceptance evidence",
        )
    )
    if result.get("status") != "aggregated":
        raise HarnessFailure(f"ticket-only evidence was not aggregated: {result}")
    ledger = (repo / "docs" / "planning" / "demo" / "decision-ledger.md").read_text()
    decision_block = ledger[ledger.index("## DEC-001") :]
    if "  - verification: complete" not in decision_block:
        raise HarnessFailure("ticket-only evidence did not complete verification coverage")
    if "ticket issue #8: ticket-only acceptance evidence" not in decision_block:
        raise HarnessFailure("ticket-only evidence did not retain its origin")
    invalid_before = ledger
    missing_evidence = run_helper(
        repo,
        "coverage",
        "aggregate",
        "--effort",
        "demo",
        "--checkpoint",
        checkpoint,
        "--head",
        "HEAD",
        "--decisions",
        "DEC-002",
        expected=2,
    )
    if "at least one verification" not in (missing_evidence.stdout + missing_evidence.stderr).lower():
        raise HarnessFailure(f"ticket-only aggregation accepted an empty evidence set: {missing_evidence}")
    if (repo / "docs" / "planning" / "demo" / "decision-ledger.md").read_text() != invalid_before:
        raise HarnessFailure("empty ticket-only evidence failure changed the ledger")

    incomplete = run_helper(
        repo,
        "coverage",
        "aggregate",
        "--effort",
        "demo",
        "--checkpoint",
        checkpoint,
        "--head",
        "HEAD",
        "--decisions",
        "DEC-001,DEC-002",
        "--ticket-evidence",
        "DEC-001 | issue #8 | repeated ticket evidence",
        expected=2,
    )
    incomplete_text = incomplete.stdout + incomplete.stderr
    if "dec-002:verification" not in incomplete_text.lower():
        raise HarnessFailure(f"incomplete ticket-only coverage did not fail with the missing decision: {incomplete}")
    if (repo / "docs" / "planning" / "demo" / "decision-ledger.md").read_text() != invalid_before:
        raise HarnessFailure("incomplete ticket-only coverage failure changed the ledger")

    invalid = run_helper(
        repo,
        "coverage",
        "aggregate",
        "--effort",
        "demo",
        "--checkpoint",
        checkpoint,
        "--head",
        "HEAD",
        "--decisions",
        "DEC-002",
        "--ticket-evidence",
        "missing origin separator",
        expected=2,
    )
    if "ticket evidence must use" not in (invalid.stdout + invalid.stderr).lower():
        raise HarnessFailure(f"malformed ticket evidence did not fail closed: {invalid}")
    ledger_path = repo / "docs" / "planning" / "demo" / "decision-ledger.md"
    if ledger_path.read_text() != invalid_before:
        raise HarnessFailure("malformed ticket evidence changed the ledger")


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


def test_wayfinder_decision_to_build_flow() -> None:
    """Exercise Wayfinder resolution, canonical ADR ownership, and the final gate."""

    repo = init_repo()
    effort = "wayfinder-to-build"
    run_helper(repo, "init")
    run_helper(repo, "ledger", "create", "--effort", effort)

    initial = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            effort,
            "--phase",
            "intermediate",
            "--message",
            "Wayfinder map checkpoint",
        )
    )
    initial_sha = str(initial["sha"])
    map_path = repo / "wayfinder-map.md"
    map_path.write_text(
        "## Destination\n\nA specification and implementation ticket for the shared planning contract.\n\n"
        "## Decisions so far\n\n"
    )
    run_helper(
        repo,
        "marker",
        "--effort",
        effort,
        "--checkpoint",
        initial_sha,
        "--repository",
        "https://github.com/manoelcalixto/mattpocock-skills",
        "--output",
        map_path.name,
    )
    initial_map = map_path.read_text()
    if f"Planning checkpoint: {initial_sha}" not in initial_map or "Decisions:" in initial_map:
        raise HarnessFailure("the initial Wayfinder map did not point to its empty planning checkpoint")

    adr = repo / "docs" / "adr" / "0004-wayfinder-decision.md"
    adr.parent.mkdir(parents=True)
    canonical_rationale = "The ADR records the canonical rationale for preserving the shared planning contract."
    adr.write_text(f"# Wayfinder planning contract\n\n{canonical_rationale}\n")
    created = payload(
        run_helper(
            repo,
            "decision",
            "add",
            "--effort",
            effort,
            "--decision",
            "Carry the shared planning contract into the build",
            "--context",
            "A resolved Wayfinder choice must cross fresh sessions",
            "--rationale",
            "See the ADR for the canonical architectural rationale",
            "--adr",
            "docs/adr/0004-wayfinder-decision.md",
            "--obligations",
            "specification,tickets",
        )
    )
    decision_id = str(created["id"])
    if decision_id != "DEC-001":
        raise HarnessFailure(f"Wayfinder resolution did not create the first stable ID: {created}")

    ledger_path = repo / "docs" / "planning" / effort / "decision-ledger.md"
    before_reference = ledger_path.read_text()
    referenced = reference_decision(repo, effort, decision_id)
    if referenced.get("status") != "referenced" or referenced.get("id") != decision_id:
        raise HarnessFailure(f"Wayfinder reference did not return the active stable ID: {referenced}")
    after_reference = ledger_path.read_text()
    if after_reference != before_reference or after_reference.count("## DEC-") != 1:
        raise HarnessFailure("referencing a Wayfinder decision created duplicate ledger state")
    if "- ADR: docs/adr/0004-wayfinder-decision.md" not in after_reference:
        raise HarnessFailure("the ledger does not point to the canonical ADR")

    resolution_checkpoint = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            effort,
            "--phase",
            "intermediate",
            "--message",
            "Wayfinder decision checkpoint",
            "--path",
            "docs/adr/0004-wayfinder-decision.md",
        )
    )
    resolution_sha = str(resolution_checkpoint["sha"])
    run_helper(
        repo,
        "marker",
        "--effort",
        effort,
        "--checkpoint",
        resolution_sha,
        "--decisions",
        decision_id,
        "--repository",
        "https://github.com/manoelcalixto/mattpocock-skills",
        "--output",
        map_path.name,
    )
    resolved_map = map_path.read_text()
    if resolution_sha == initial_sha or f"Planning checkpoint: {resolution_sha}" not in resolved_map:
        raise HarnessFailure("the Wayfinder map marker did not advance with the resolved decision checkpoint")
    if f"Decisions: {decision_id}" not in resolved_map:
        raise HarnessFailure("the Wayfinder map marker did not represent its resolved decision ID")
    marker_heading = "## Planning context"
    marker_index = resolved_map.index(marker_heading)
    map_path.write_text(
        f"{resolved_map[:marker_index]}"
        "- [Carry the shared planning contract into the build](wayfinder-decision.md): "
        "link to the resolved Decision ticket\n\n"
        f"{resolved_map[marker_index:]}"
    )

    decision_ticket = write_marked_artifact(
        repo,
        effort,
        resolution_sha,
        decision_id,
        "wayfinder-decision.md",
        """## Resolution

The ADR-backed planning contract is the selected answer.

- ADR: [0004-wayfinder-decision.md](docs/adr/0004-wayfinder-decision.md)
- Specification handoff: wayfinder-spec.md
""",
    )
    spec = write_marked_artifact(
        repo,
        effort,
        resolution_sha,
        decision_id,
        "wayfinder-spec.md",
        """## Implementation Decisions

- DEC-001: carry the shared planning contract through the build
- Implementation ticket: wayfinder-implementation-ticket.md
""",
    )
    add_coverage(repo, effort, decision_id, "specification", "wayfinder-spec.md#implementation-decisions")

    missing = run_helper(repo, "checkpoint", "--effort", effort, "--phase", "final", expected=2)
    if "dec-001:tickets" not in (missing.stdout + missing.stderr).lower():
        raise HarnessFailure(f"Wayfinder resolution crossed the final gate without ticket coverage: {missing}")

    implementation_ticket = write_marked_artifact(
        repo,
        effort,
        resolution_sha,
        decision_id,
        "wayfinder-implementation-ticket.md",
        """## Decision consequences

- DEC-001: keep the shared planning contract observable in implementation
- Source specification: wayfinder-spec.md

## Acceptance criteria

- [ ] A fresh implementation session can verify the complete path.
""",
    )
    add_coverage(repo, effort, decision_id, "tickets", "wayfinder-implementation-ticket.md")

    final = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            effort,
            "--phase",
            "final",
            "--message",
            "Wayfinder to build planning checkpoint",
        )
    )
    final_sha = str(final["sha"])
    if final_sha == resolution_sha or len(final_sha) != 40:
        raise HarnessFailure(f"Wayfinder final checkpoint did not advance: {final}")

    for output in (map_path, decision_ticket, spec, implementation_ticket):
        run_helper(
            repo,
            "marker",
            "--effort",
            effort,
            "--checkpoint",
            final_sha,
            "--decisions",
            decision_id,
            "--repository",
            "https://github.com/manoelcalixto/mattpocock-skills",
            "--output",
            output.name,
        )

    for output in (map_path, decision_ticket, spec, implementation_ticket):
        run_helper(repo, "validate", "--context-file", output.name, "--phase", "final")

    map_text = map_path.read_text()
    decision_text = decision_ticket.read_text()
    spec_text = spec.read_text()
    implementation_text = implementation_ticket.read_text()
    downstream = map_text + decision_text + spec_text + implementation_text
    if canonical_rationale in downstream:
        raise HarnessFailure("canonical ADR rationale leaked into the Wayfinder or build artifacts")
    if "wayfinder-decision.md" not in map_text or "wayfinder-spec.md" not in implementation_text:
        raise HarnessFailure("Wayfinder resolution did not retain the Decision to spec to ticket chain")
    if f"Planning checkpoint: {final_sha}" not in map_text:
        raise HarnessFailure("the Wayfinder map marker was not refreshed for the final checkpoint")
    adr_text = adr.read_text()
    if (
        canonical_rationale not in adr_text
        or "- ADR: docs/adr/0004-wayfinder-decision.md" not in ledger_path.read_text()
        or "docs/adr/0004-wayfinder-decision.md" not in decision_text
    ):
        raise HarnessFailure("ADR canonical rationale and ledger pointer are not both present")


def test_session_boundary_router_and_catalogs() -> None:
    """Check the routed boundary contract and every promoted distribution surface."""

    ask = BOUNDARY_SKILLS["ask-matt"].read_text()
    phase_boundaries = BOUNDARY_SKILLS["ask-matt"].parent.joinpath("PHASE-BOUNDARIES.md").read_text()
    handoff = BOUNDARY_SKILLS["handoff"].read_text()
    handoff_docs = BOUNDARY_DOCS["handoff"].read_text()
    setup = BOUNDARY_SKILLS["setup-matt-pocock-skills"].read_text()
    setup_docs = BOUNDARY_DOCS["setup-matt-pocock-skills"].read_text()
    planning = BOUNDARY_SKILLS["planning-context"].read_text()
    planning_contract = PLANNING_CONTRACT.read_text()

    route_start = ask.find("The multi-session route is therefore:")
    if route_start < 0:
        raise HarnessFailure("ask-matt is missing its explicit multi-session route")
    route_end = ask.find("\n", route_start)
    route = ask[route_start:] if route_end < 0 else ask[route_start:route_end]
    assert_ordered(
        route,
        "ask-matt multi-session route",
        "grill-with-docs",
        "intermediate Planning checkpoint",
        "to-spec",
        "to-tickets",
        "final Planning checkpoint",
        "fresh implementation session",
        "implement-spec or implement",
        "code-review",
    )
    wayfinder_start = ask.find("When the map clears")
    if wayfinder_start < 0:
        raise HarnessFailure("ask-matt is missing the Wayfinder build handoff")
    wayfinder_end = ask.find("\n\n", wayfinder_start)
    wayfinder = ask[wayfinder_start:] if wayfinder_end < 0 else ask[wayfinder_start:wayfinder_end]
    assert_ordered(
        wayfinder,
        "ask-matt Wayfinder handoff",
        "/to-spec",
        "/to-tickets",
        "final Planning checkpoint",
        "fresh implementation session",
    )
    for phrase in (
        "lightweight path for small work without a formal Planning context",
        "right here, in the same context window",
        "genuinely small and has no formal Planning context",
    ):
        if phrase not in ask:
            raise HarnessFailure(f"ask-matt lightweight route is missing: {phrase}")
    ask_docs = BOUNDARY_DOCS["ask-matt"].read_text()
    for phrase in ("intermediate Planning checkpoint", "final checkpoint", "fresh session", "Small work without a formal Planning context"):
        if phrase not in ask_docs:
            raise HarnessFailure(f"ask-matt documentation is missing routed boundary behavior: {phrase}")

    assert_ordered(
        phase_boundaries,
        "phase-boundaries structure",
        "## Planning context gate",
        "## The five options",
        "## The tree",
    )
    for phrase in (
        "current map, specification, or ticket declares its `## Planning context` marker",
        "create the checkpoint before `/compact`, `/handoff`, `/clear`, dispatching a `Subagent`",
        "dispatching a `Subagent`",
        "any other fresh context",
        "`intermediate` checkpoint",
        "`final` checkpoint",
        "`implementation` checkpoint",
        "exact full checkpoint SHA",
        "A handoff carries pointers instead of copying their contents",
        "small markerless work",
    ):
        if phrase not in phase_boundaries:
            raise HarnessFailure(f"phase-boundaries gate is missing: {phrase}")

    for name, text in (("handoff skill", handoff), ("planning skill", planning), ("planning contract", planning_contract)):
        for phrase in ("fresh session", "active Planning context", "checkpoint"):
            if phrase not in text:
                raise HarnessFailure(f"{name} does not describe the fresh-session gate: {phrase}")
    for name, text in (("planning skill", planning), ("planning contract", planning_contract), ("phase boundaries", phase_boundaries)):
        for phrase in ("Subagent", "other fresh context"):
            if phrase not in text:
                raise HarnessFailure(f"{name} does not describe the subagent fresh-context boundary: {phrase}")
    for phrase in (
        "call the Skill tool with `planning-context` first",
        "exact full checkpoint SHA",
        "effort",
        "ledger path",
        "current branch",
        "resolvable paths or URLs",
        "present in or resolvable from that checkpoint commit",
        "final checkpoint",
        "marker validation path",
        "do not copy their ledger, specification, ticket, ADR, or decision content",
    ):
        if phrase not in handoff:
            raise HarnessFailure(f"handoff pointer bridge is missing: {phrase}")
    for phrase in ("pointer bridge", "exact full checkpoint SHA", "does not repeat any artifact's content"):
        if phrase not in handoff_docs:
            raise HarnessFailure(f"handoff documentation is missing the pointer bridge: {phrase}")
    if "subagent" not in ask_docs.lower() or "changed Planning artifact" not in ask_docs:
        raise HarnessFailure("ask-matt documentation does not describe the subagent Planning boundary")

    for phrase in ("New repository", "Existing repository", "lazy migration", "byte-for-byte", "docs/agents/planning.md"):
        if phrase not in setup:
            raise HarnessFailure(f"setup Planning discovery is missing: {phrase}")
    if "does not replace existing planning content" not in setup:
        raise HarnessFailure("setup does not preserve existing Planning content")
    for phrase in ("New repository", "Existing repository", "lazy migration", "byte-for-byte", "never replaces existing planning content"):
        if phrase not in setup_docs:
            raise HarnessFailure(f"setup documentation is missing Planning discovery behavior: {phrase}")

    docs_sections = ("## What it does", "## When to reach for it", "## Common questions", "## It's working if", "## Where it fits")
    for name, path in BOUNDARY_DOCS.items():
        text = path.read_text()
        positions = [text.find(section) for section in docs_sections]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            raise HarnessFailure(f"{name} documentation sections are incomplete or out of order")
        if "\u2014" in text:
            raise HarnessFailure(f"{name} documentation contains an em dash")
    planning_docs = BOUNDARY_DOCS["planning-context"].read_text()
    assert_ordered(
        planning_docs,
        "planning-context documentation structure",
        "## When to reach for it",
        "## Prerequisites",
        "## The ledger and checkpoint",
        "## Common questions",
    )

    plugin = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text())
    plugin_skills = plugin.get("skills", [])
    for name, skill_path in BOUNDARY_SKILLS.items():
        relative_skill = "./" + skill_path.parent.relative_to(REPO_ROOT).as_posix()
        if relative_skill not in plugin_skills:
            raise HarnessFailure(f"{name} is missing from the Claude plugin manifest")
        metadata = BOUNDARY_METADATA[name].read_text()
        if not metadata.startswith("interface:\n  display_name:") or "\n  short_description:" not in metadata:
            raise HarnessFailure(f"{name} metadata is not nested under interface")
        if "policy:" in metadata or "allow_implicit_invocation" in metadata:
            raise HarnessFailure(f"{name} metadata reintroduced an implicit-invocation policy")
        if name == "planning-context":
            if "disable-model-invocation:" in skill_path.read_text():
                raise HarnessFailure("planning-context must remain model-invoked")
        elif "disable-model-invocation: true" not in skill_path.read_text():
            raise HarnessFailure(f"{name} invocation metadata changed unexpectedly")
    for metadata_path in (REPO_ROOT / "skills").rglob("openai.yaml"):
        metadata = metadata_path.read_text()
        if "policy:" in metadata or "allow_implicit_invocation" in metadata:
            raise HarnessFailure(f"OpenAI metadata reintroduced an implicit-invocation policy: {metadata_path}")

    expected_promoted = {
        "./" + skill_path.parent.relative_to(REPO_ROOT).as_posix()
        for bucket in ("engineering", "productivity")
        for skill_path in (REPO_ROOT / "skills" / bucket).glob("*/SKILL.md")
    }
    if set(plugin_skills) != expected_promoted:
        missing = sorted(expected_promoted - set(plugin_skills))
        unexpected = sorted(set(plugin_skills) - expected_promoted)
        raise HarnessFailure(f"Claude plugin membership is out of parity: missing={missing}, unexpected={unexpected}")
    top_readme = (REPO_ROOT / "README.md").read_text()
    for bucket in ("engineering", "productivity"):
        bucket_readme = (REPO_ROOT / "skills" / bucket / "README.md").read_text()
        for skill_path in sorted((REPO_ROOT / "skills" / bucket).glob("*/SKILL.md")):
            name = skill_path.parent.name
            top_link = f"[{name}](./skills/{bucket}/{name}/SKILL.md)"
            bucket_link = f"[{name}](./{name}/SKILL.md)"
            if top_link not in top_readme or bucket_link not in bucket_readme:
                raise HarnessFailure(f"{name} catalog links are out of parity")
            docs_path = REPO_ROOT / "docs" / bucket / f"{name}.md"
            if not docs_path.exists():
                raise HarnessFailure(f"promoted skill docs are missing: {docs_path.relative_to(REPO_ROOT)}")
            metadata_path = skill_path.parent / "agents" / "openai.yaml"
            metadata = metadata_path.read_text()
            if not metadata.startswith("interface:\n  display_name:") or "\n  short_description:" not in metadata:
                raise HarnessFailure(f"promoted skill metadata is not nested under interface: {metadata_path}")
            docs_text = docs_path.read_text()
            if "\u2014" in docs_text or "\u2014" in skill_path.read_text():
                raise HarnessFailure(f"promoted skill contains an em dash: {skill_path}")

    catalogs = {
        REPO_ROOT / "README.md": {
            "ask-matt": "[ask-matt](./skills/engineering/ask-matt/SKILL.md)",
            "handoff": "[handoff](./skills/productivity/handoff/SKILL.md)",
            "setup-matt-pocock-skills": "[setup-matt-pocock-skills](./skills/engineering/setup-matt-pocock-skills/SKILL.md)",
            "planning-context": "[planning-context](./skills/engineering/planning-context/SKILL.md)",
        },
        REPO_ROOT / "skills" / "engineering" / "README.md": {
            "ask-matt": "[ask-matt](./ask-matt/SKILL.md)",
            "setup-matt-pocock-skills": "[setup-matt-pocock-skills](./setup-matt-pocock-skills/SKILL.md)",
            "planning-context": "[planning-context](./planning-context/SKILL.md)",
        },
        REPO_ROOT / "skills" / "productivity" / "README.md": {
            "handoff": "[handoff](./handoff/SKILL.md)",
        },
    }
    for catalog, links in catalogs.items():
        text = catalog.read_text()
        for name, link in links.items():
            if link not in text:
                raise HarnessFailure(f"{name} is missing from {catalog.relative_to(REPO_ROOT)}")


def test_fresh_session_pointer_bridge() -> None:
    """Prove that a handoff can validate checkpoint pointers without copying decisions."""

    repo = init_repo()
    effort = "session-boundary"
    create_effort(repo, effort)
    (repo / "map.md").write_text("# Planning map\n\nResolve the implementation route.\n")
    intermediate = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            effort,
            "--phase",
            "intermediate",
            "--message",
            "boundary planning checkpoint",
            "--path",
            "map.md",
        )
    )
    intermediate_sha = str(intermediate["sha"])
    planning_handoff = write_marked_artifact(
        repo,
        effort,
        intermediate_sha,
        "DEC-001",
        "planning-handoff.md",
        f"""## Next session

- Checkpoint SHA: {intermediate_sha}
- Effort: {effort}
- Ledger: docs/planning/{effort}/decision-ledger.md
- Branch: feature/session-boundary
- Map: map.md
- Specification: spec.md (to be created)
- Tickets: issue-9 (to be created)
""",
    )
    planning_result = payload(
        run_helper(repo, "validate", "--context-file", planning_handoff.name, "--phase", "intermediate")
    )
    if planning_result.get("status") != "valid" or planning_result.get("checkpoint") != intermediate_sha:
        raise HarnessFailure(f"intermediate handoff pointer did not validate: {planning_result}")
    planning_text = planning_handoff.read_text()
    if "A versioned contract prevents drift" in planning_text or "Use the shared planning seam" in planning_text:
        raise HarnessFailure("intermediate handoff copied canonical Decision content")
    if run_git(repo, "cat-file", "-e", f"{intermediate_sha}:map.md", check=False).returncode != 0:
        raise HarnessFailure("intermediate handoff map pointer is not versioned by its checkpoint")

    (repo / "spec.md").write_text("# Session boundary specification\n")
    (repo / "ticket.md").write_text("# Session boundary ticket\n")
    add_coverage(repo, effort, "DEC-001", "specification", "spec.md")
    add_coverage(repo, effort, "DEC-001", "tickets", "ticket.md")
    final = payload(
        run_helper(
            repo,
            "checkpoint",
            "--effort",
            effort,
            "--phase",
            "final",
            "--message",
            "boundary final checkpoint",
            "--path",
            "map.md",
            "--path",
            "spec.md",
            "--path",
            "ticket.md",
        )
    )
    final_sha = str(final["sha"])
    for versioned in (
        "docs/agents/planning.md",
        f"docs/planning/{effort}/decision-ledger.md",
        "map.md",
        "spec.md",
        "ticket.md",
    ):
        if run_git(repo, "cat-file", "-e", f"{final_sha}:{versioned}", check=False).returncode != 0:
            raise HarnessFailure(f"final checkpoint does not contain pointer target {versioned}")
    implementation_handoff = write_marked_artifact(
        repo,
        effort,
        final_sha,
        "DEC-001",
        "implementation-handoff.md",
        f"""## Fresh implementation session

- Checkpoint SHA: {final_sha}
- Effort: {effort}
- Ledger: docs/planning/{effort}/decision-ledger.md
- Branch: feature/session-boundary
- Map: map.md
- Specification: spec.md
- Tickets: ticket.md
- Marker validation: planning_context.py validate --context-file implementation-handoff.md --phase final
""",
    )
    implementation_result = payload(
        run_helper(repo, "validate", "--context-file", implementation_handoff.name, "--phase", "final")
    )
    if implementation_result.get("status") != "valid" or implementation_result.get("checkpoint") != final_sha:
        raise HarnessFailure(f"final implementation handoff pointer did not validate: {implementation_result}")
    implementation_text = implementation_handoff.read_text()
    if "A versioned contract prevents drift" in implementation_text or "Use the shared planning seam" in implementation_text:
        raise HarnessFailure("implementation handoff copied canonical Decision content")


def test_fork_targeting_operations() -> None:
    """Ensure operational examples target this fork while generic templates stay generic."""

    target = "manoelcalixto/mattpocock-skills"
    operational_files = (
        REPO_ROOT / "skills" / "engineering" / "triage" / "AGENT-BRIEF.md",
        REPO_ROOT / "docs" / "engineering" / "setup-matt-pocock-skills.md",
        REPO_ROOT / "docs" / "engineering" / "triage.md",
        REPO_ROOT / "docs" / "agents" / "issue-tracker.md",
        REPO_ROOT / ".agents" / "writing-docs.md",
    )
    for path in operational_files:
        for line in path.read_text().splitlines():
            if re.search(r"\bgh (?:issue|pr)\s+", line) and f"--repo {target}" not in line:
                raise HarnessFailure(f"operational GitHub command does not target the fork: {path}:{line}")
            if re.search(r"\bgh api\s+", line) and f"repos/{target}/" not in line:
                raise HarnessFailure(f"operational GitHub API command does not target the fork: {path}:{line}")
    if "gh issue list --label needs-triage" in (operational_files[0]).read_text():
        raise HarnessFailure("triage brief retained an inferred issue target")
    if "gh issue create --label <missing>" in (operational_files[1]).read_text():
        raise HarnessFailure("setup docs retained an inferred issue target")
    if "gh pr list`" in (operational_files[2]).read_text():
        raise HarnessFailure("triage docs retained an inferred pull request target")


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

    coverage_help = subprocess.run(
        [sys.executable, str(HELPER), "coverage", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if coverage_help.returncode != 0:
        raise HarnessFailure(f"coverage help failed: {coverage_help.stderr}")
    for phrase in ("verified commits", "ticket evidence"):
        if phrase not in coverage_help.stdout:
            raise HarnessFailure(f"coverage aggregate help does not expose both evidence modes: {phrase}")
    aggregate_help = subprocess.run(
        [sys.executable, str(HELPER), "coverage", "aggregate", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if aggregate_help.returncode != 0 or "optional with ticket evidence" not in aggregate_help.stdout:
        raise HarnessFailure(f"coverage aggregate option help omits ticket-only mode: {aggregate_help.stderr}")

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
    planning_context = (REPO_ROOT / "skills" / "engineering" / "planning-context" / "SKILL.md").read_text()
    planning_context_docs = (REPO_ROOT / "docs" / "engineering" / "planning-context.md").read_text()
    wayfinder = (REPO_ROOT / "skills" / "engineering" / "wayfinder" / "SKILL.md").read_text()
    wayfinder_docs = (REPO_ROOT / "docs" / "engineering" / "wayfinder.md").read_text()
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
    for name, text in (
        ("to-spec skill", to_spec),
        ("to-tickets skill", to_tickets),
        ("planning-context skill", planning_context),
        ("wayfinder skill", wayfinder),
        ("to-spec docs", (REPO_ROOT / "docs" / "engineering" / "to-spec.md").read_text()),
        ("to-tickets docs", (REPO_ROOT / "docs" / "engineering" / "to-tickets.md").read_text()),
        ("planning-context docs", planning_context_docs),
        ("wayfinder docs", wayfinder_docs),
    ):
        for phrase in ("configured Git remote and branch", "git push <configured-remote> HEAD:<configured-branch>", "checkpoint is reachable"):
            if phrase not in text:
                raise HarnessFailure(f"{name} does not require a resolvable remote checkpoint before publication: {phrase}")
    if re.search(r"\]\((?!https?://|#)[^)]+\)", wayfinder_docs):
        raise HarnessFailure("wayfinder documentation contains a non-absolute link")
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
        "wayfinder": wayfinder_docs,
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
        test_invalid_marked_configuration_fails_closed,
        test_ledger_ids_and_supersession,
        test_none_obligation_requires_applicability_evidence,
        test_case_insensitive_none_applicability_coverage_is_atomic,
        test_optional_decision_fields_are_supported_and_immutable,
        test_validate_ledger_override_validates_configuration_and_is_atomic,
        test_checkpoint_gates_staging_and_trailer,
        test_validation_and_immutability,
        test_marker_requires_exact_full_checkpoint_sha,
        test_checkpoint_coverage_and_evidence_are_monotonic,
        test_empty_structured_evidence_fails_closed_and_atomically,
        test_checkpointed_json_evidence_is_append_only,
        test_implement_preflight_wiring,
        test_implement_planning_closeout_wiring,
        test_implement_single_ticket_planning_closeout,
        test_implement_preflight_valid,
        test_implement_preflight_legacy,
        test_implement_preflight_invalid,
        test_implement_preflight_wrong_lineage,
        test_implement_preflight_decision_conflict,
        test_implement_spec_preflight_wiring,
        test_implement_spec_markerless_and_mixed_graph,
        test_parallel_ticket_branches_share_checkpoint_without_ledger_edits,
        test_trailers_are_read_only_from_the_final_block,
        test_checkpoint_ownership_rejects_non_planning_and_mixed_diffs,
        test_verification_aggregation_requires_merged_tips_and_is_atomic,
        test_merged_coordinator_aggregation_and_implementation_checkpoint,
        test_aggregation_rejects_ledger_edit_in_merge_commit,
        test_ticket_only_evidence_surface,
        test_implementation_checkpoint_selection_is_scoped_and_fail_closed,
        test_grill_to_tickets_flow,
        test_wayfinder_decision_to_build_flow,
        test_session_boundary_router_and_catalogs,
        test_fresh_session_pointer_bridge,
        test_fork_targeting_operations,
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
