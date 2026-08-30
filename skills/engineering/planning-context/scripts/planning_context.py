#!/usr/bin/env python3
"""Deterministic adapter for the versioned Planning context contract."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


CONFIG_REL = Path("docs/agents/planning.md")
CONFIG_MARKER = "<!-- planning-context:v1 -->"
DEFAULT_LEDGER_DIR = Path("docs/planning")
OBLIGATIONS = ("specification", "tickets", "verification")
PHASES = ("intermediate", "final", "implementation")
PHASE_ORDER = {phase: index for index, phase in enumerate(PHASES)}
PHASE_REQUIREMENTS = {
    "intermediate": (),
    "final": ("specification", "tickets"),
    "implementation": OBLIGATIONS,
}
ID_PATTERN = re.compile(r"^DEC-(\d{3,})$")
EFFORT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")
FIELD_PATTERN = re.compile(
    r"^- (Status|Decision|Context|Rationale|ADR|Obligations|Superseded by|Supersedes):\s*(.*)$"
)
SUBFIELD_PATTERN = re.compile(r"^\s{2,}- (specification|tickets|verification):\s*(.*)$")
ENTRY_PATTERN = re.compile(r"^## (DEC-\d{3,})\s*$", re.MULTILINE)


DEFAULT_CONFIG = f"""{CONFIG_MARKER}
# Planning context

- Format: v1
- Ledger directory: `docs/planning`
- Checkpoint trailer: `Planning-Checkpoint`
- Checkpoint phases: `intermediate`, `final`, `implementation`
- Legacy inputs: allowed when no Planning context marker is declared.
"""


class PlanningError(Exception):
    """An actionable contract or repository error."""


@dataclass(frozen=True)
class Entry:
    identifier: str
    status: str
    decision: str
    context: str
    rationale: str
    adr: str | None
    obligations: tuple[str, ...]
    coverage: Mapping[str, str]
    evidence: Mapping[str, str]
    superseded_by: str | None = None
    supersedes: str | None = None

    def meaning(self) -> tuple[object, ...]:
        """Fields whose meaning cannot change after a checkpoint."""

        return (
            self.decision,
            self.context,
            self.rationale,
            self.adr,
            self.obligations,
        )


def fail(message: str) -> None:
    raise PlanningError(message)


def run_git(
    repo: Path,
    *args: str,
    input_text: str | None = None,
    check: bool = True,
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
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        fail(f"git {' '.join(args)} failed: {detail}")
    return result


def resolve_repo(raw_repo: str) -> Path:
    candidate = Path(raw_repo).expanduser().resolve()
    if not candidate.exists() or not candidate.is_dir():
        fail(f"repository does not exist: {raw_repo}")
    result = run_git(candidate, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def relative_path(repo: Path, raw_path: str, *, must_exist: bool = False) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        fail(f"path must be relative to the repository: {raw_path}")
    resolved = (repo / candidate).resolve()
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        fail(f"path escapes the repository: {raw_path}")
    if any(part == ".." for part in candidate.parts):
        fail(f"path traversal is not allowed: {raw_path}")
    if must_exist and not resolved.exists():
        fail(f"path does not exist: {relative.as_posix()}")
    return relative


def clean_single_line(raw: str, field: str) -> str:
    value = raw.strip()
    if not value:
        fail(f"{field} must not be empty")
    if "\n" in value or "\r" in value:
        fail(f"{field} must fit on one line")
    return value


def validate_effort(raw_effort: str) -> str:
    effort = clean_single_line(raw_effort, "effort")
    if not EFFORT_PATTERN.fullmatch(effort):
        fail("effort must use lowercase letters, digits, dots, underscores, or hyphens")
    return effort


def config_path(repo: Path) -> Path:
    return repo / CONFIG_REL


def ensure_config(repo: Path) -> tuple[str, str]:
    path = config_path(repo)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(DEFAULT_CONFIG)
        return "created", DEFAULT_CONFIG

    text = path.read_text()
    if CONFIG_MARKER in text:
        return "existing", text

    suffix = "" if text.endswith("\n") else "\n"
    migrated = f"{text}{suffix}\n{DEFAULT_CONFIG}"
    path.write_text(migrated)
    return "migrated", migrated


def load_config(repo: Path) -> str:
    path = config_path(repo)
    if not path.exists():
        fail(f"planning configuration is missing at {CONFIG_REL.as_posix()}; run init first")
    return path.read_text()


def ledger_directory(repo: Path, config: str | None = None) -> Path:
    text = config if config is not None else load_config(repo)
    match = re.search(r"^- Ledger directory:\s*`([^`]+)`\s*$", text, re.MULTILINE)
    raw_directory = match.group(1) if match else DEFAULT_LEDGER_DIR.as_posix()
    return relative_path(repo, raw_directory)


def ledger_relative_path(repo: Path, effort: str, config: str | None = None) -> Path:
    return ledger_directory(repo, config) / validate_effort(effort) / "decision-ledger.md"


def ledger_header(effort: str) -> str:
    return (
        "# Decision ledger\n\n"
        f"- Format: v1\n- Effort: {effort}\n\n"
        "Decision meanings are immutable after a Planning checkpoint. "
        "Coverage and evidence may be appended.\n"
    )


def parse_obligations(raw: str | None) -> tuple[str, ...]:
    if raw is None:
        return OBLIGATIONS
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if values == ["none"]:
        return ()
    if not values:
        fail("obligations must name at least one obligation or use none")
    unknown = sorted(set(values) - set(OBLIGATIONS))
    if unknown:
        fail(f"unknown obligation(s): {', '.join(unknown)}")
    deduped = tuple(item for item in OBLIGATIONS if item in values)
    return deduped


def parse_entry(block: str, identifier: str) -> Entry:
    fields: dict[str, str] = {}
    coverage: dict[str, str] = {}
    evidence: dict[str, str] = {}
    section: str | None = None
    for line in block.splitlines()[1:]:
        field_match = FIELD_PATTERN.match(line)
        if field_match:
            fields[field_match.group(1)] = field_match.group(2).strip()
            section = None
            continue
        subfield_match = SUBFIELD_PATTERN.match(line)
        if subfield_match and section in {"Coverage", "Evidence"}:
            target = coverage if section == "Coverage" else evidence
            target[subfield_match.group(1)] = subfield_match.group(2).strip()
            continue
        if line.strip() == "- Coverage:":
            section = "Coverage"
        elif line.strip() == "- Evidence:":
            section = "Evidence"

    for required in ("Status", "Decision", "Context", "Rationale", "Obligations"):
        if required not in fields or not fields[required]:
            fail(f"{identifier} is missing {required}")
    status = fields["Status"].lower()
    if status not in {"active", "superseded"}:
        fail(f"{identifier} has invalid status {status!r}")
    obligations = parse_obligations(fields["Obligations"])
    for obligation in obligations:
        if obligation not in coverage:
            fail(f"{identifier} is missing {obligation} coverage")
        if coverage[obligation] not in {"pending", "complete"}:
            fail(f"{identifier} has invalid {obligation} coverage status")
        if obligation not in evidence:
            fail(f"{identifier} is missing {obligation} evidence")
    superseded_by = fields.get("Superseded by") or None
    if status == "superseded" and not superseded_by:
        fail(f"{identifier} is superseded but has no Superseded by field")
    supersedes = fields.get("Supersedes") or None
    adr = fields.get("ADR") or None
    if adr == "none":
        adr = None
    return Entry(
        identifier=identifier,
        status=status,
        decision=fields["Decision"],
        context=fields["Context"],
        rationale=fields["Rationale"],
        adr=adr,
        obligations=obligations,
        coverage=coverage,
        evidence=evidence,
        superseded_by=superseded_by,
        supersedes=supersedes,
    )


def parse_ledger(text: str, *, require_entries: bool = False) -> dict[str, Entry]:
    matches = list(ENTRY_PATTERN.finditer(text))
    entries: dict[str, Entry] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        identifier = match.group(1)
        if identifier in entries:
            fail(f"duplicate ledger entry {identifier}")
        entries[identifier] = parse_entry(text[match.start() : end], identifier)
    if require_entries and not entries:
        fail("decision ledger has no DEC-NNN entries")
    for entry in entries.values():
        if entry.superseded_by and entry.superseded_by not in entries:
            fail(f"{entry.identifier} points to missing successor {entry.superseded_by}")
        if entry.supersedes and entry.supersedes not in entries:
            fail(f"{entry.identifier} points to missing predecessor {entry.supersedes}")
    return entries


def read_ledger(repo: Path, effort: str) -> tuple[Path, str, dict[str, Entry]]:
    relative = ledger_relative_path(repo, effort)
    path = repo / relative
    if not path.exists():
        fail(f"decision ledger is missing at {relative.as_posix()}; create it first")
    text = path.read_text()
    return relative, text, parse_ledger(text)


def format_entry(
    identifier: str,
    decision: str,
    context: str,
    rationale: str,
    adr: str | None,
    obligations: Sequence[str],
    *,
    supersedes: str | None = None,
) -> str:
    lines = [
        f"## {identifier}",
        "- Status: active",
        f"- Decision: {decision}",
        f"- Context: {context}",
        f"- Rationale: {rationale}",
        f"- ADR: {adr or 'none'}",
        f"- Obligations: {', '.join(obligations) if obligations else 'none'}",
    ]
    if supersedes:
        lines.append(f"- Supersedes: {supersedes}")
    lines.append("- Coverage:")
    for obligation in OBLIGATIONS:
        if obligation in obligations:
            lines.append(f"  - {obligation}: pending")
    lines.append("- Evidence:")
    for obligation in OBLIGATIONS:
        if obligation in obligations:
            lines.append(f"  - {obligation}: none")
    return "\n".join(lines) + "\n"


def next_identifier(entries: Mapping[str, Entry]) -> str:
    numbers = []
    for identifier in entries:
        match = ID_PATTERN.fullmatch(identifier)
        if match:
            numbers.append(int(match.group(1)))
    return f"DEC-{(max(numbers, default=0) + 1):03d}"


def active_decision_identifier(entries: Mapping[str, Entry], raw_identifier: str) -> str:
    identifier = clean_single_line(raw_identifier, "decision")
    if not ID_PATTERN.fullmatch(identifier):
        fail("decision must use a DEC-NNN identifier")
    if identifier not in entries:
        fail(f"decision {identifier} does not exist")
    if entries[identifier].status != "active":
        fail(f"decision {identifier} is superseded; reference an active entry")
    return identifier


def supersede_entry(text: str, identifier: str, successor: str) -> str:
    matches = list(ENTRY_PATTERN.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1) != identifier:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        lines = text[match.start() : end].rstrip("\n").splitlines()
        status_index = next(
            (line_index for line_index, line in enumerate(lines) if line.startswith("- Status:")),
            None,
        )
        if status_index is None:
            fail(f"{identifier} is missing Status")
        lines[status_index] = "- Status: superseded"
        if not any(line.startswith("- Superseded by:") for line in lines):
            lines.insert(status_index + 1, f"- Superseded by: {successor}")
        replacement = "\n".join(lines) + "\n"
        return text[: match.start()] + replacement + text[end:]
    fail(f"ledger entry {identifier} does not exist")
    return text


def command_init(repo: Path) -> dict[str, object]:
    status, _ = ensure_config(repo)
    return {"status": status, "path": CONFIG_REL.as_posix()}


def command_ledger_create(repo: Path, effort: str) -> dict[str, object]:
    effort = validate_effort(effort)
    ensure_config(repo)
    relative = ledger_relative_path(repo, effort)
    path = repo / relative
    if path.exists():
        parse_ledger(path.read_text())
        return {"status": "existing", "effort": effort, "path": relative.as_posix()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ledger_header(effort))
    return {"status": "created", "effort": effort, "path": relative.as_posix()}


def command_decision_add(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    effort = validate_effort(args.effort)
    ensure_config(repo)
    relative, text, entries = read_ledger(repo, effort)
    decision = clean_single_line(args.decision, "decision")
    context = clean_single_line(args.context, "context")
    rationale = clean_single_line(args.rationale, "rationale")
    adr = clean_single_line(args.adr, "ADR") if args.adr else None
    obligations = parse_obligations(args.obligations)
    supersedes = args.supersedes
    if supersedes:
        if supersedes not in entries:
            fail(f"cannot supersede unknown decision {supersedes}")
        if entries[supersedes].status != "active":
            fail(f"decision {supersedes} is already superseded")
    identifier = next_identifier(entries)
    if supersedes:
        text = supersede_entry(text, supersedes, identifier)
    entry = format_entry(
        identifier,
        decision,
        context,
        rationale,
        adr,
        obligations,
        supersedes=supersedes,
    )
    path = repo / relative
    separator = "" if text.endswith("\n\n") else "\n"
    path.write_text(text + separator + entry)
    parse_ledger(path.read_text())
    return {"status": "created", "effort": effort, "id": identifier, "path": relative.as_posix()}


def command_decision_reference(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    effort = validate_effort(args.effort)
    ensure_config(repo)
    relative, _, entries = read_ledger(repo, effort)
    identifier = active_decision_identifier(entries, args.decision)
    return {
        "status": "referenced",
        "effort": effort,
        "id": identifier,
        "path": relative.as_posix(),
    }


def command_coverage_add(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    effort = validate_effort(args.effort)
    obligation = clean_single_line(args.obligation.lower(), "obligation")
    if obligation not in OBLIGATIONS:
        fail(f"unknown obligation: {obligation}")
    evidence = clean_single_line(args.evidence, "evidence")
    relative, text, entries = read_ledger(repo, effort)
    if args.decision not in entries:
        fail(f"decision {args.decision} does not exist")
    entry = entries[args.decision]
    if obligation not in entry.obligations:
        fail(f"{args.decision} does not declare {obligation} as an obligation")
    matches = list(ENTRY_PATTERN.finditer(text))
    match = next(item for item in matches if item.group(1) == args.decision)
    end = next((item.start() for item in matches if item.start() > match.start()), len(text))
    block = text[match.start() : end]
    coverage_line = re.compile(rf"^(\s{{2,}}- {re.escape(obligation)}):\s*.*$", re.MULTILINE)
    coverage_match = coverage_line.search(block)
    if not coverage_match:
        fail(f"{args.decision} has no {obligation} coverage line")
    lines = block.splitlines()
    coverage_prefix = f"  - {obligation}:"
    section = None
    for index, line in enumerate(lines):
        if line.strip() == "- Coverage:":
            section = "coverage"
        elif line.strip() == "- Evidence:":
            section = "evidence"
        elif line.startswith(coverage_prefix):
            if section == "coverage":
                lines[index] = f"  - {obligation}: complete"
            elif section == "evidence":
                old = line.split(":", 1)[1].strip()
                combined = evidence if old in {"", "none"} else f"{old}; {evidence}"
                lines[index] = f"  - {obligation}: {combined}"
    updated = "\n".join(lines) + "\n"
    path = repo / relative
    path.write_text(text[: match.start()] + updated + text[end:])
    parse_ledger(path.read_text())
    return {
        "status": "recorded",
        "effort": effort,
        "decision": args.decision,
        "obligation": obligation,
        "path": relative.as_posix(),
    }


def required_for_phase(phase: str) -> tuple[str, ...]:
    if phase not in PHASES:
        fail(f"unknown checkpoint phase {phase!r}; use {', '.join(PHASES)}")
    return PHASE_REQUIREMENTS[phase]


def missing_coverage(entries: Mapping[str, Entry], required: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for entry in entries.values():
        if entry.status != "active":
            continue
        for obligation in required:
            if obligation not in entry.obligations:
                continue
            if entry.coverage.get(obligation) != "complete" or entry.evidence.get(obligation) in {None, "", "none"}:
                missing.append(f"{entry.identifier}:{obligation}")
    return missing


def ensure_stage_path(repo: Path, raw_path: str) -> Path:
    relative = relative_path(repo, raw_path)
    absolute = repo / relative
    if absolute.exists():
        if absolute.is_dir():
            fail(f"checkpoint path is a directory: {relative.as_posix()}")
        return relative
    tracked = run_git(repo, "ls-files", "--error-unmatch", "--", relative.as_posix(), check=False)
    if tracked.returncode != 0:
        fail(f"checkpoint path does not exist: {relative.as_posix()}")
    return relative


def command_checkpoint(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    effort = validate_effort(args.effort)
    phase = clean_single_line(args.phase.lower(), "phase")
    required = required_for_phase(phase)
    ensure_config(repo)
    ledger_relative, _, entries = read_ledger(repo, effort)
    missing = missing_coverage(entries, required)
    if missing:
        fail(
            f"coverage incomplete for {phase} checkpoint: {', '.join(missing)}; "
            "record coverage and evidence before checkpointing"
        )

    raw_paths = [CONFIG_REL.as_posix(), ledger_relative.as_posix(), *(args.path or [])]
    paths: list[Path] = []
    seen: set[str] = set()
    for raw_path in raw_paths:
        relative = ensure_stage_path(repo, raw_path)
        if relative.as_posix() not in seen:
            paths.append(relative)
            seen.add(relative.as_posix())
    run_git(repo, "add", "--", *(path.as_posix() for path in paths))
    staged = run_git(
        repo,
        "diff",
        "--cached",
        "--quiet",
        "--",
        *(path.as_posix() for path in paths),
        check=False,
    )
    if staged.returncode == 0:
        fail("checkpoint has no changes in its owned planning artifacts")
    subject = clean_single_line(args.message or f"planning: checkpoint {effort} ({phase})", "message")
    trailer_message = (
        f"{subject}\n\n"
        f"Planning-Checkpoint: {effort}\n"
        f"Planning-Phase: {phase}\n"
        f"Planning-Ledger: {ledger_relative.as_posix()}\n"
    )
    run_git(
        repo,
        "commit",
        "--only",
        "-F",
        "-",
        "--",
        *(path.as_posix() for path in paths),
        input_text=trailer_message,
    )
    sha = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    return {
        "status": "created",
        "effort": effort,
        "phase": phase,
        "sha": sha,
        "ledger": ledger_relative.as_posix(),
        "paths": [path.as_posix() for path in paths],
    }


def parse_trailers(message: str) -> dict[str, str]:
    trailers: dict[str, str] = {}
    for line in message.splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s*(.+)$", line)
        if match:
            trailers[match.group(1)] = match.group(2).strip()
    return trailers


def validate_checkpoint_commit(
    repo: Path,
    sha: str,
    effort: str,
    ledger_relative: Path,
    *,
    required_phase: str | None = None,
) -> dict[str, Entry]:
    resolved = run_git(repo, "rev-parse", "--verify", f"{sha}^{{commit}}", check=False)
    if resolved.returncode != 0:
        fail(f"Planning checkpoint {sha} cannot be resolved")
    checkpoint_sha = resolved.stdout.strip()
    ancestry = run_git(repo, "merge-base", "--is-ancestor", checkpoint_sha, "HEAD", check=False)
    if ancestry.returncode != 0:
        fail(f"Planning checkpoint {checkpoint_sha} is not an ancestor of the current branch")
    message = run_git(repo, "show", "-s", "--format=%B", checkpoint_sha).stdout
    trailers = parse_trailers(message)
    if trailers.get("Planning-Checkpoint") != effort:
        fail("Planning checkpoint trailer does not name the declared effort")
    if trailers.get("Planning-Ledger") != ledger_relative.as_posix():
        fail("Planning checkpoint trailer does not name the declared ledger")
    checkpoint_phase = trailers.get("Planning-Phase")
    if checkpoint_phase not in PHASES:
        fail("Planning checkpoint trailer has no valid Planning-Phase")
    if required_phase is not None and PHASE_ORDER[checkpoint_phase] < PHASE_ORDER[required_phase]:
        fail(
            f"Planning checkpoint phase {checkpoint_phase} cannot satisfy the requested {required_phase} phase; "
            "create a newer checkpoint"
        )
    config_object = f"{checkpoint_sha}:{CONFIG_REL.as_posix()}"
    config_exists = run_git(repo, "cat-file", "-e", config_object, check=False)
    if config_exists.returncode != 0:
        fail("Planning checkpoint does not contain the planning configuration")
    object_path = f"{checkpoint_sha}:{ledger_relative.as_posix()}"
    exists = run_git(repo, "cat-file", "-e", object_path, check=False)
    if exists.returncode != 0:
        fail("Planning checkpoint does not contain the declared Decision ledger")
    snapshot_text = run_git(repo, "show", object_path).stdout
    snapshot = parse_ledger(snapshot_text)
    current_path = repo / ledger_relative
    if not current_path.exists():
        fail("declared Decision ledger is missing from the current branch")
    current = parse_ledger(current_path.read_text())
    if set(current) != set(snapshot):
        added = sorted(set(current) - set(snapshot))
        removed = sorted(set(snapshot) - set(current))
        detail = []
        if added:
            detail.append(f"added {', '.join(added)}")
        if removed:
            detail.append(f"removed {', '.join(removed)}")
        fail(
            f"Decision ledger changed after the checkpoint ({'; '.join(detail)}); "
            "create a new Planning checkpoint"
        )
    for identifier, before in snapshot.items():
        after = current[identifier]
        if before.meaning() != after.meaning():
            fail(f"checkpointed meaning for {identifier} is immutable; create a superseding decision and checkpoint")
        if (
            before.status != after.status
            or before.superseded_by != after.superseded_by
            or before.supersedes != after.supersedes
        ):
            fail(f"validity for {identifier} changed after the checkpoint; create a new Planning checkpoint")
    return current


def find_checkpoint(repo: Path, effort: str, ledger_relative: Path) -> str:
    revisions = run_git(repo, "rev-list", "HEAD").stdout.split()
    for revision in revisions:
        message = run_git(repo, "show", "-s", "--format=%B", revision).stdout
        trailers = parse_trailers(message)
        if (
            trailers.get("Planning-Checkpoint") == effort
            and trailers.get("Planning-Ledger") == ledger_relative.as_posix()
        ):
            return revision
    fail(
        f"no Planning checkpoint trailer was found for {effort} and {ledger_relative.as_posix()}; "
        "create a checkpoint first"
    )
    return ""


def marker_block(
    effort: str,
    ledger_relative: Path,
    checkpoint: str,
    decisions: Sequence[str],
    repository: str | None = None,
) -> str:
    lines = ["## Planning context", "", "- Format: v1"]
    if repository:
        lines.append(f"- Repository: {clean_single_line(repository, 'repository')}")
    lines.extend(
        [
            f"- Effort: {effort}",
            f"- Decision ledger: `{ledger_relative.as_posix()}`",
            f"- Planning checkpoint: {checkpoint}",
        ]
    )
    if decisions:
        lines.append(f"- Decisions: {', '.join(decisions)}")
    return "\n".join(lines) + "\n"


def parse_marker(text: str) -> dict[str, object] | None:
    heading = re.search(r"^## Planning context\s*$", text, re.MULTILINE)
    if not heading:
        return None
    next_heading = re.search(r"^## (?!Planning context\s*$).+?$", text[heading.end() :], re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading else len(text)
    section = text[heading.start() : end]
    values: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"^- (Format|Repository|Effort|Decision ledger|Ledger|Planning checkpoint|Checkpoint|Decisions):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip("`")
    format_version = values.get("Format")
    effort = values.get("Effort")
    ledger = values.get("Decision ledger") or values.get("Ledger")
    checkpoint = values.get("Planning checkpoint") or values.get("Checkpoint")
    if format_version != "v1":
        fail("Planning context marker must declare Format: v1")
    if not effort or not ledger or not checkpoint:
        fail("Planning context marker needs Effort, Decision ledger, and Planning checkpoint")
    decisions_raw = values.get("Decisions", "")
    decisions = tuple(item.strip() for item in decisions_raw.split(",") if item.strip())
    return {
        "effort": validate_effort(effort),
        "ledger": ledger,
        "checkpoint": checkpoint,
        "decisions": decisions,
        "repository": values.get("Repository"),
    }


def write_marker(text: str, block: str) -> str:
    heading = re.search(r"^## Planning context\s*$", text, re.MULTILINE)
    if not heading:
        separator = "" if not text or text.endswith("\n\n") else "\n"
        return f"{text}{separator}{block}"
    rest = text[heading.end() :]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading else len(text)
    prefix = text[: heading.start()]
    suffix = text[end:]
    return f"{prefix}{block}{suffix.lstrip(chr(10))}"


def command_marker(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    effort = validate_effort(args.effort)
    ensure_config(repo)
    ledger_relative, _, entries = read_ledger(repo, effort)
    checkpoint = clean_single_line(args.checkpoint, "checkpoint")
    resolved = run_git(repo, "rev-parse", "--verify", f"{checkpoint}^{{commit}}", check=False)
    if resolved.returncode != 0:
        fail(f"Planning checkpoint {checkpoint} cannot be resolved")
    resolved_sha = resolved.stdout.strip()
    validate_checkpoint_commit(repo, resolved_sha, effort, ledger_relative)
    decisions = tuple(item.strip() for item in (args.decisions or "").split(",") if item.strip())
    for identifier in decisions:
        active_decision_identifier(entries, identifier)
    block = marker_block(effort, ledger_relative, resolved_sha, decisions, args.repository)
    if args.output:
        output = relative_path(repo, args.output)
        path = repo / output
        existing = path.read_text() if path.exists() else ""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(write_marker(existing, block))
        return {"status": "written", "path": output.as_posix(), "checkpoint": resolved_sha}
    return {"status": "generated", "block": block, "checkpoint": resolved_sha}


def command_validate(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    context_path = relative_path(repo, args.context_file, must_exist=True)
    marker = parse_marker((repo / context_path).read_text())
    if marker is None:
        if not args.effort:
            return {"status": "legacy", "context": context_path.as_posix()}
        effort = validate_effort(args.effort)
        load_config(repo)
        ledger_relative = ledger_relative_path(repo, effort)
        checkpoint = find_checkpoint(repo, effort, ledger_relative)
        requested = ()
        source = "trailer"
    else:
        load_config(repo)
        effort = str(marker["effort"])
        if args.effort and validate_effort(args.effort) != effort:
            fail("declared effort does not match the Planning context marker")
        marker_ledger_raw = str(marker["ledger"])
        try:
            ledger_relative = relative_path(repo, marker_ledger_raw)
        except PlanningError as error:
            fail(f"external Decision ledger pointer needs a local clone path: {error}")
        override_ledger = args.ledger
        if override_ledger:
            ledger_relative = relative_path(repo, override_ledger, must_exist=True)
        elif ledger_relative != ledger_relative_path(repo, effort):
            fail("Planning context ledger does not match the repository configuration")
        checkpoint = str(marker["checkpoint"])
        requested = tuple(str(item) for item in marker["decisions"])
        source = "marker"
    current = validate_checkpoint_commit(repo, checkpoint, effort, ledger_relative, required_phase=args.phase)
    selected = requested or tuple(identifier for identifier, entry in current.items() if entry.status == "active")
    for identifier in selected:
        if identifier not in current:
            fail(f"declared decision {identifier} is missing from the Decision ledger")
        if current[identifier].status != "active":
            fail(f"declared decision {identifier} is superseded; update the Planning context")
    required = set(required_for_phase(args.phase)) if args.phase else set()
    for obligation in args.require or []:
        if obligation not in OBLIGATIONS:
            fail(f"unknown required obligation: {obligation}")
        required.add(obligation)
    missing = missing_coverage({identifier: current[identifier] for identifier in selected}, required)
    if missing:
        fail(f"coverage incomplete for declared Planning context: {', '.join(missing)}")
    return {
        "status": "valid",
        "context": context_path.as_posix(),
        "source": source,
        "effort": effort,
        "checkpoint": run_git(repo, "rev-parse", "--verify", f"{checkpoint}^{{commit}}").stdout.strip(),
        "ledger": ledger_relative.as_posix(),
        "decisions": list(selected),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository to operate on")
    parser.add_argument("--json", action="store_true", help="return a machine-readable result")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init", help="create or lazily migrate planning discovery")

    ledger = commands.add_parser("ledger", help="manage a per-effort Decision ledger")
    ledger_commands = ledger.add_subparsers(dest="ledger_command", required=True)
    ledger_create = ledger_commands.add_parser("create")
    ledger_create.add_argument("--effort", required=True)

    decision = commands.add_parser("decision", help="append or supersede a decision")
    decision_commands = decision.add_subparsers(dest="decision_command", required=True)
    decision_add = decision_commands.add_parser("add")
    decision_add.add_argument("--effort", required=True)
    decision_add.add_argument("--decision", required=True)
    decision_add.add_argument("--context", required=True)
    decision_add.add_argument("--rationale", required=True)
    decision_add.add_argument("--adr")
    decision_add.add_argument("--obligations", help="comma-separated obligations or none")
    decision_add.add_argument("--supersedes")

    decision_reference = decision_commands.add_parser(
        "reference", help="reference one existing active decision without creating a ledger entry"
    )
    decision_reference.add_argument("--effort", required=True)
    decision_reference.add_argument("--decision", required=True)

    coverage = commands.add_parser("coverage", help="append coverage and verification evidence")
    coverage_commands = coverage.add_subparsers(dest="coverage_command", required=True)
    coverage_add = coverage_commands.add_parser("add")
    coverage_add.add_argument("--effort", required=True)
    coverage_add.add_argument("--decision", required=True)
    coverage_add.add_argument("--obligation", required=True)
    coverage_add.add_argument("--evidence", required=True)

    checkpoint = commands.add_parser("checkpoint", help="create a phase-aware Git Planning checkpoint")
    checkpoint.add_argument("--effort", required=True)
    checkpoint.add_argument("--phase", required=True, choices=PHASES)
    checkpoint.add_argument("--message")
    checkpoint.add_argument("--path", action="append", help="additional effort-owned planning artifact")

    marker = commands.add_parser("marker", help="generate or write a Planning context block")
    marker.add_argument("--effort", required=True)
    marker.add_argument("--checkpoint", required=True)
    marker.add_argument("--decisions")
    marker.add_argument("--repository")
    marker.add_argument("--output")

    validate = commands.add_parser("validate", help="validate a local or external consumer")
    validate.add_argument("--context-file", required=True)
    validate.add_argument("--effort", help="resolve a local context from the latest Planning checkpoint trailer")
    validate.add_argument("--phase", choices=PHASES)
    validate.add_argument("--require", action="append", default=[])
    validate.add_argument("--ledger")
    return parser


def dispatch(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    if args.command == "init":
        return command_init(repo)
    if args.command == "ledger" and args.ledger_command == "create":
        return command_ledger_create(repo, args.effort)
    if args.command == "decision" and args.decision_command == "add":
        return command_decision_add(repo, args)
    if args.command == "decision" and args.decision_command == "reference":
        return command_decision_reference(repo, args)
    if args.command == "coverage" and args.coverage_command == "add":
        return command_coverage_add(repo, args)
    if args.command == "checkpoint":
        return command_checkpoint(repo, args)
    if args.command == "marker":
        return command_marker(repo, args)
    if args.command == "validate":
        return command_validate(repo, args)
    fail("unknown planning-context command")
    return {}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        repo = resolve_repo(args.repo)
        result = dispatch(repo, args)
    except PlanningError as error:
        if args.json:
            print(json.dumps({"status": "error", "error": str(error)}, sort_keys=True))
        else:
            print(f"planning-context: error: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, sort_keys=True))
    elif "block" in result:
        print(result["block"], end="")
    else:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
