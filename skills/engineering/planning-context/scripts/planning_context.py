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
APPLICABILITY_OBLIGATION = "applicability"
PHASES = ("intermediate", "final", "implementation")
PHASE_ORDER = {phase: index for index, phase in enumerate(PHASES)}
PHASE_REQUIREMENTS = {
    "intermediate": (),
    "final": ("specification", "tickets", APPLICABILITY_OBLIGATION),
    "implementation": (*OBLIGATIONS, APPLICABILITY_OBLIGATION),
}
ID_PATTERN = re.compile(r"^DEC-(\d{3,})$")
EFFORT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")
FULL_CHECKPOINT_SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
VERIFICATION_PATTERN = re.compile(r"^Planning-Verification:\s*(DEC-\d{3,})\s*\|\s*(\S.*)$")
APPLICABILITY_EVIDENCE_PATTERN = re.compile(
    r"^(?:non-ticket|not-applicable):\s*\S.*$", re.IGNORECASE
)
FIELD_PATTERN = re.compile(
    r"^- (Status|Decision|Context|Rationale|ADR|Constraints|Rejected alternatives|Obligations|Superseded by|Supersedes):\s*(.*)$"
)
SUBFIELD_PATTERN = re.compile(
    r"^\s{2,}- (specification|tickets|verification|applicability):\s*(.*)$"
)
ENTRY_PATTERN = re.compile(r"^## (DEC-\d{3,})\s*$", re.MULTILINE)
PLANNING_PATHS_TRAILER = "Planning-Paths"


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
    constraints: str | None
    rejected_alternatives: str | None
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
            self.constraints,
            self.rejected_alternatives,
            self.obligations,
        )


@dataclass(frozen=True)
class Verification:
    """One observable verification record found on an implementation surface."""

    decision: str
    evidence: str
    origin: str | None = None


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
    if not match:
        fail(
            f"planning configuration at {CONFIG_REL.as_posix()} is invalid: "
            "missing `Ledger directory: ...`; repair it before using Planning context"
        )
    raw_directory = match.group(1)
    return relative_path(repo, raw_directory)


def ledger_relative_path(repo: Path, effort: str, config: str | None = None) -> Path:
    return ledger_directory(repo, config) / validate_effort(effort) / "decision-ledger.md"


def ledger_header(effort: str) -> str:
    return (
        "# Decision ledger\n\n"
        f"- Format: v1\n- Effort: {effort}\n\n"
        "Decision meanings are immutable after a Planning checkpoint. "
        "Coverage advances from pending to complete, and evidence may be appended without replacing prior values.\n"
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
    for optional in ("Constraints", "Rejected alternatives"):
        if optional in fields and not fields[optional]:
            fail(f"{identifier} has an empty {optional} field")
    constraints = fields.get("Constraints") or None
    rejected_alternatives = fields.get("Rejected alternatives") or None
    for obligation in obligations:
        if obligation not in coverage:
            fail(f"{identifier} is missing {obligation} coverage")
        if coverage[obligation] not in {"pending", "complete"}:
            fail(f"{identifier} has invalid {obligation} coverage status")
        if obligation not in evidence:
            fail(f"{identifier} is missing {obligation} evidence")
    if not obligations:
        has_applicability_coverage = APPLICABILITY_OBLIGATION in coverage
        has_applicability_evidence = APPLICABILITY_OBLIGATION in evidence
        if has_applicability_coverage != has_applicability_evidence:
            fail(f"{identifier} needs both applicability coverage and evidence lines")
        if not has_applicability_coverage:
            # Preserve the markerless and pre-v1 ledger shape while making its
            # missing justification visible to every phase gate.
            coverage[APPLICABILITY_OBLIGATION] = "pending"
            evidence[APPLICABILITY_OBLIGATION] = "none"
        elif coverage[APPLICABILITY_OBLIGATION] not in {"pending", "complete"}:
            fail(f"{identifier} has invalid applicability coverage status")
        applicability_evidence = evidence[APPLICABILITY_OBLIGATION]
        if (
            (
                coverage[APPLICABILITY_OBLIGATION] == "complete"
                or applicability_evidence.strip().lower() not in {"", "none"}
            )
            and not APPLICABILITY_EVIDENCE_PATTERN.fullmatch(applicability_evidence)
        ):
            fail(
                f"{identifier} applicability evidence must start with "
                "non-ticket: or not-applicable:"
            )
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
        constraints=constraints,
        rejected_alternatives=rejected_alternatives,
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
    constraints: str | None = None,
    rejected_alternatives: str | None = None,
    supersedes: str | None = None,
) -> str:
    lines = [
        f"## {identifier}",
        "- Status: active",
        f"- Decision: {decision}",
        f"- Context: {context}",
        f"- Rationale: {rationale}",
        f"- ADR: {adr or 'none'}",
    ]
    if constraints:
        lines.append(f"- Constraints: {constraints}")
    if rejected_alternatives:
        lines.append(f"- Rejected alternatives: {rejected_alternatives}")
    lines.append(f"- Obligations: {', '.join(obligations) if obligations else 'none'}")
    if supersedes:
        lines.append(f"- Supersedes: {supersedes}")
    lines.append("- Coverage:")
    if obligations:
        for obligation in OBLIGATIONS:
            if obligation in obligations:
                lines.append(f"  - {obligation}: pending")
    else:
        lines.append(f"  - {APPLICABILITY_OBLIGATION}: pending")
    lines.append("- Evidence:")
    if obligations:
        for obligation in OBLIGATIONS:
            if obligation in obligations:
                lines.append(f"  - {obligation}: none")
    else:
        lines.append(f"  - {APPLICABILITY_OBLIGATION}: none")
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
    status, config = ensure_config(repo)
    ledger_directory(repo, config)
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
    constraints = clean_single_line(args.constraints, "constraints") if args.constraints else None
    rejected_alternatives = (
        clean_single_line(args.rejected_alternatives, "rejected alternatives")
        if args.rejected_alternatives
        else None
    )
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
        constraints=constraints,
        rejected_alternatives=rejected_alternatives,
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
    if obligation not in (*OBLIGATIONS, APPLICABILITY_OBLIGATION):
        fail(f"unknown obligation: {obligation}")
    evidence = clean_single_line(args.evidence, "evidence")
    if not has_non_empty_evidence(evidence):
        fail("evidence must contain a non-empty value or JSON string list")
    relative, text, entries = read_ledger(repo, effort)
    if args.decision not in entries:
        fail(f"decision {args.decision} does not exist")
    entry = entries[args.decision]
    if obligation == APPLICABILITY_OBLIGATION:
        if entry.obligations:
            fail(f"{args.decision} declares delivery obligations; applicability is only for Obligations: none")
        if not APPLICABILITY_EVIDENCE_PATTERN.fullmatch(evidence):
            fail("applicability evidence must explain the decision with non-ticket: or not-applicable:")
    elif obligation not in entry.obligations:
        fail(f"{args.decision} does not declare {obligation} as an obligation")
    matches = list(ENTRY_PATTERN.finditer(text))
    match = next(item for item in matches if item.group(1) == args.decision)
    end = next((item.start() for item in matches if item.start() > match.start()), len(text))
    block = text[match.start() : end]
    lines = block.splitlines()
    coverage_prefix = f"  - {obligation}:"
    if obligation == APPLICABILITY_OBLIGATION and not any(
        line.startswith(coverage_prefix) for line in lines
    ):
        coverage_index = next(
            (index for index, line in enumerate(lines) if line.strip() == "- Coverage:"),
            None,
        )
        evidence_index = next(
            (index for index, line in enumerate(lines) if line.strip() == "- Evidence:"),
            None,
        )
        if coverage_index is None or evidence_index is None:
            fail(f"{args.decision} has no applicability coverage and evidence sections")
        lines.insert(coverage_index + 1, f"  - {APPLICABILITY_OBLIGATION}: pending")
        if evidence_index > coverage_index:
            evidence_index += 1
        lines.insert(evidence_index + 1, f"  - {APPLICABILITY_OBLIGATION}: none")
    section = None
    changed_coverage = False
    changed_evidence = False
    for index, line in enumerate(lines):
        if line.strip() == "- Coverage:":
            section = "coverage"
        elif line.strip() == "- Evidence:":
            section = "evidence"
        elif line.startswith(coverage_prefix):
            if section == "coverage":
                lines[index] = f"  - {obligation}: complete"
                changed_coverage = True
            elif section == "evidence":
                old = line.split(":", 1)[1].strip()
                combined = evidence if not old or old.lower() == "none" else f"{old}; {evidence}"
                lines[index] = f"  - {obligation}: {combined}"
                changed_evidence = True
    if not changed_coverage or not changed_evidence:
        fail(f"{args.decision} has no {obligation} coverage and evidence lines")
    updated = "\n".join(lines) + "\n"
    updated_text = text[: match.start()] + updated + text[end:]
    parse_ledger(updated_text)
    path = repo / relative
    path.write_text(updated_text)
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
            if obligation not in entry.obligations and not (
                obligation == APPLICABILITY_OBLIGATION and not entry.obligations
            ):
                continue
            if entry.coverage.get(obligation, "pending") != "complete" or not has_non_empty_evidence(
                entry.evidence.get(obligation)
            ):
                missing.append(f"{entry.identifier}:{obligation}")
    return missing


def selected_checkpoint_entries(
    entries: Mapping[str, Entry], phase: str, raw_decisions: str | None
) -> dict[str, Entry]:
    """Select implementation decisions without weakening the final planning gate."""

    if raw_decisions is None:
        return {
            identifier: entry
            for identifier, entry in entries.items()
            if entry.status == "active"
        }
    if phase != "implementation":
        fail("checkpoint decision selection is only supported for the implementation phase")
    values = [item.strip() for item in raw_decisions.split(",") if item.strip()]
    if not values:
        fail("checkpoint decisions must name at least one active decision")
    selected: dict[str, Entry] = {}
    for raw_identifier in values:
        identifier = active_decision_identifier(entries, raw_identifier)
        selected[identifier] = entries[identifier]
    return selected


def entry_coverage_obligations(entry: Entry) -> tuple[str, ...]:
    """Return delivery obligations plus the synthetic none-applicability gate."""

    if entry.obligations:
        return entry.obligations
    return (APPLICABILITY_OBLIGATION,)


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
    selected_entries = selected_checkpoint_entries(entries, phase, args.decisions)
    missing = missing_coverage(selected_entries, required)
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
        if relative.as_posix() not in {
            CONFIG_REL.as_posix(),
            ledger_relative.as_posix(),
        } and not is_current_planning_artifact(repo, relative):
            fail(
                f"checkpoint path is not identifiable as a Planning context artifact: "
                f"{relative.as_posix()}"
            )
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
        f"{PLANNING_PATHS_TRAILER}: {json.dumps([path.as_posix() for path in paths], separators=(',', ':'))}\n"
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
        "decisions": list(selected_entries),
        "paths": [path.as_posix() for path in paths],
    }


def parse_trailers_lines(message: str) -> tuple[str, ...]:
    """Return the final trailer block using Git's deterministic parser."""

    parsed = subprocess.run(
        ["git", "interpret-trailers", "--parse"],
        input=message,
        text=True,
        capture_output=True,
        check=False,
    )
    if parsed.returncode != 0:
        detail = parsed.stderr.strip() or parsed.stdout.strip() or "git trailer parsing failed"
        fail(f"git interpret-trailers --parse failed: {detail}")
    return tuple(parsed.stdout.splitlines())


def parse_trailers(message: str) -> dict[str, str]:
    """Parse only the final Git trailer block, preserving Git's semantics."""

    trailers: dict[str, str] = {}
    for line in parse_trailers_lines(message):
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s*(.+)$", line)
        if match:
            trailers[match.group(1)] = match.group(2).strip()
    return trailers


def parse_verification_trailers(message: str) -> tuple[Verification, ...]:
    """Read repeatable Planning-Verification trailers without collapsing them."""

    records: list[Verification] = []
    for line in parse_trailers_lines(message):
        match = VERIFICATION_PATTERN.fullmatch(line)
        if match:
            evidence = match.group(2).strip()
            if not has_non_empty_evidence(evidence):
                fail("Planning-Verification evidence must contain a non-empty value")
            records.append(Verification(match.group(1), evidence))
    return tuple(records)


def parse_ticket_evidence(raw_evidence: str) -> Verification:
    """Parse one already-read ticket record without accepting an implicit source."""

    value = clean_single_line(raw_evidence, "ticket evidence")
    parts = [part.strip() for part in value.split("|", 2)]
    if len(parts) != 3 or any(not part for part in parts):
        fail("ticket evidence must use DEC-NNN | origin | observable evidence")
    identifier, origin, evidence = parts
    if not ID_PATTERN.fullmatch(identifier):
        fail("ticket evidence must name a DEC-NNN identifier")
    if not has_non_empty_evidence(evidence):
        fail("ticket evidence must contain a non-empty value")
    return Verification(identifier, evidence, origin)


def resolve_commit(repo: Path, raw_commit: str, field: str) -> str:
    commit = clean_single_line(raw_commit, field)
    resolved = run_git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}", check=False)
    if resolved.returncode != 0:
        fail(f"{field} {commit} cannot be resolved")
    return resolved.stdout.strip()


def require_ancestor(repo: Path, ancestor: str, descendant: str, message: str) -> None:
    result = run_git(repo, "merge-base", "--is-ancestor", ancestor, descendant, check=False)
    if result.returncode != 0:
        fail(message)


def commits_since(repo: Path, checkpoint: str, tip: str) -> tuple[str, ...]:
    result = run_git(repo, "rev-list", "--reverse", f"{checkpoint}..{tip}")
    return tuple(commit for commit in result.stdout.split() if commit)


def changed_paths(repo: Path, commit: str) -> tuple[str, ...]:
    result = run_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-m", "--root", commit)
    return tuple(path for path in result.stdout.splitlines() if path)


def checkpoint_path_text(repo: Path, checkpoint: str, relative: Path) -> str | None:
    result = run_git(repo, "show", f"{checkpoint}:{relative.as_posix()}", check=False)
    if result.returncode != 0:
        return None
    return result.stdout


def is_planning_artifact(
    repo: Path, checkpoint: str, relative: Path
) -> bool:
    """Recognize explicitly owned planning artifacts beyond config and ledger."""

    if is_planning_artifact_name(relative):
        return True
    try:
        text = checkpoint_path_text(repo, checkpoint, relative)
    except UnicodeDecodeError:
        return False
    if text is None:
        return False
    return has_planning_artifact_markers(text)


def is_planning_artifact_name(relative: Path) -> bool:
    """Recognize well-known Planning artifact paths without reading their contents."""

    path_parts = relative.parts
    if relative == Path("CONTEXT.md"):
        return True
    if (
        len(path_parts) >= 3
        and path_parts[:2] in {(".agents", "adr"), ("docs", "adr")}
        and relative.suffix.lower() == ".md"
    ):
        return True
    return relative.name.lower() in {"map.md", "spec.md", "ticket.md"}


def has_planning_artifact_markers(text: str) -> bool:
    """Recognize content that identifies an explicitly owned Planning artifact."""

    if CONFIG_MARKER in text or re.search(r"^## Planning context\s*$", text, re.MULTILINE):
        return True
    return bool(
        re.search(r"^# .*planning (?:map|context)\s*$", text, re.IGNORECASE | re.MULTILINE)
        and re.search(r"\b(?:checkpoint|ledger|effort)\b", text, re.IGNORECASE)
    )


def current_path_text(repo: Path, relative: Path) -> str | None:
    """Read the content that checkpoint would stage for a path, when textual."""

    absolute = repo / relative
    if absolute.exists():
        try:
            return absolute.read_text()
        except (OSError, UnicodeDecodeError):
            return None
    for object_name in (f":{relative.as_posix()}", f"HEAD:{relative.as_posix()}"):
        try:
            result = run_git(repo, "show", object_name, check=False)
        except UnicodeDecodeError:
            return None
        if result.returncode == 0:
            return result.stdout
    return None


def is_current_planning_artifact(repo: Path, relative: Path) -> bool:
    """Apply checkpoint ownership rules before staging a newly requested path."""

    if is_planning_artifact_name(relative):
        return True
    text = current_path_text(repo, relative)
    return text is not None and has_planning_artifact_markers(text)


def validate_checkpoint_ownership(
    repo: Path,
    checkpoint: str,
    ledger_relative: Path,
    trailers: Mapping[str, str],
) -> None:
    """Prove that a checkpoint commit changes only owned planning artifacts."""

    base_paths = {CONFIG_REL.as_posix(), ledger_relative.as_posix()}
    changed = set(changed_paths(repo, checkpoint))
    raw_owned = trailers.get(PLANNING_PATHS_TRAILER)
    if raw_owned is None:
        if changed == base_paths:
            # Checkpoints created before the ownership trailer remain readable
            # when their non-empty diff proves both built-in owned paths.
            return
        if not changed:
            fail(
                f"Planning checkpoint {checkpoint} has an empty diff and no "
                f"{PLANNING_PATHS_TRAILER} trailer; legacy checkpoints must change "
                "both the planning configuration and declared ledger"
            )
        missing = sorted(base_paths - changed)
        if missing:
            fail(
                f"Planning checkpoint {checkpoint} has no {PLANNING_PATHS_TRAILER} trailer; "
                "legacy checkpoints must change both the planning configuration and "
                f"declared ledger (missing: {', '.join(missing)})"
            )
        fail(
            f"Planning checkpoint {checkpoint} lacks the {PLANNING_PATHS_TRAILER} ownership trailer; "
            "create a new checkpoint with explicitly owned planning paths"
        )
    if not changed:
        fail(
            f"Planning checkpoint {checkpoint} has an empty diff; "
            f"{PLANNING_PATHS_TRAILER} cannot prove ownership without a changed path"
        )
    try:
        decoded = json.loads(raw_owned)
    except json.JSONDecodeError:
        fail(f"Planning checkpoint {checkpoint} has invalid {PLANNING_PATHS_TRAILER} JSON")
    if not isinstance(decoded, list) or not decoded or not all(isinstance(item, str) for item in decoded):
        fail(f"Planning checkpoint {checkpoint} must list owned paths in {PLANNING_PATHS_TRAILER}")
    owned: set[str] = set()
    for raw_path in decoded:
        relative = relative_path(repo, raw_path)
        if relative.as_posix() != raw_path:
            fail(f"Planning checkpoint {checkpoint} has a non-canonical owned path: {raw_path}")
        owned.add(relative.as_posix())
    if not base_paths.issubset(owned):
        fail(
            f"Planning checkpoint {checkpoint} ownership must include config and declared ledger "
            f"({', '.join(sorted(base_paths))})"
        )
    unexpected = sorted(changed - owned)
    if unexpected:
        fail(
            f"Planning checkpoint {checkpoint} changes non-owned paths: {', '.join(unexpected)}; "
            "list only explicitly owned Planning context artifacts"
        )
    for raw_path in sorted(changed - base_paths):
        relative = Path(raw_path)
        if not is_planning_artifact(repo, checkpoint, relative):
            fail(
                f"Planning checkpoint {checkpoint} changes {raw_path}, which is not identifiable as a "
                "Planning context artifact"
            )


def selected_verification_decisions(
    entries: Mapping[str, Entry], raw_decisions: str | None
) -> tuple[str, ...]:
    if raw_decisions is None:
        return tuple(
            identifier
            for identifier, entry in entries.items()
            if entry.status == "active" and "verification" in entry.obligations
        )
    values = [item.strip() for item in raw_decisions.split(",") if item.strip()]
    if not values:
        fail("decisions must name at least one active decision")
    selected: list[str] = []
    for raw_identifier in values:
        identifier = active_decision_identifier(entries, raw_identifier)
        if identifier not in selected:
            selected.append(identifier)
    for identifier in selected:
        if "verification" not in entries[identifier].obligations:
            fail(f"{identifier} does not declare verification as an obligation")
    return tuple(selected)


def evidence_values(raw: str | None) -> list[str]:
    """Decode new JSON evidence and preserve older opaque evidence verbatim."""

    if raw in {None, "", "none"}:
        return []
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return [str(raw)]
    if isinstance(decoded, list) and all(isinstance(item, str) for item in decoded):
        return list(decoded)
    return [str(raw)]


def has_non_empty_evidence(raw: str | None) -> bool:
    """Require meaningful evidence, including for structured JSON values."""

    if raw is None:
        return False
    value = str(raw).strip()
    if not value or value.lower() == "none":
        return False
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return True
    if decoded is None:
        return False
    if isinstance(decoded, list):
        return bool(decoded) and all(isinstance(item, str) and item.strip() for item in decoded)
    if isinstance(decoded, str):
        return bool(decoded.strip())
    return True


def structured_evidence_values(raw: str | None) -> list[str] | None:
    """Decode only the canonical JSON evidence list representation."""

    if raw in {None, "", "none"}:
        return None
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if isinstance(decoded, list) and all(isinstance(item, str) for item in decoded):
        return list(decoded)
    return None


def preserves_checkpointed_evidence(before: str, after: str) -> bool:
    """Allow an unchanged value or a deterministic append that keeps its prefix."""

    after_values = structured_evidence_values(after)
    if after_values is not None and not has_non_empty_evidence(after):
        return False
    before_values = structured_evidence_values(before)
    if before_values is not None and not has_non_empty_evidence(before):
        return False
    if before == after:
        return True
    if before_values is not None and after_values is not None:
        return after_values[: len(before_values)] == before_values
    return after.startswith(f"{before}; ") and bool(after[len(before) + 2 :].strip())


def append_verification_evidence(
    text: str, updates: Mapping[str, Sequence[str]]
) -> str:
    """Apply all verified coverage updates to one ledger text in memory."""

    matches = list(ENTRY_PATTERN.finditer(text))
    replacements: list[tuple[int, int, str]] = []
    for index, match in enumerate(matches):
        identifier = match.group(1)
        evidence = updates.get(identifier)
        if not evidence:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start() : end]
        lines = block.rstrip("\n").splitlines()
        section: str | None = None
        existing_evidence: str | None = None
        evidence_line_index: int | None = None
        for line_index, line in enumerate(lines):
            if line.strip() == "- Coverage:":
                section = "coverage"
            elif line.strip() == "- Evidence:":
                section = "evidence"
            elif line.startswith("  - verification:"):
                if section == "coverage":
                    lines[line_index] = "  - verification: complete"
                elif section == "evidence":
                    existing_evidence = line.split(":", 1)[1].strip()
                    evidence_line_index = line_index
        if existing_evidence is None:
            fail(f"{identifier} has no verification evidence line")
        current_values = evidence_values(existing_evidence)
        if existing_evidence not in {"", "none"} and not has_non_empty_evidence(existing_evidence):
            fail(f"{identifier} has empty verification evidence; record a non-empty value before aggregation")
        for item in evidence:
            if item not in current_values:
                current_values.append(item)
        if evidence_line_index is not None:
            lines[evidence_line_index] = (
                "  - verification: " + json.dumps(current_values, ensure_ascii=False, separators=(",", ":"))
            )
        replacements.append((match.start(), end, "\n".join(lines) + "\n"))

    for start, end, replacement in reversed(replacements):
        text = text[:start] + replacement + text[end:]
    return text


def command_coverage_aggregate(repo: Path, args: argparse.Namespace) -> dict[str, object]:
    """Aggregate worker or ticket evidence after every supplied tip is merged."""

    effort = validate_effort(args.effort)
    load_config(repo)
    ledger_relative, ledger_text, entries = read_ledger(repo, effort)
    checkpoint_raw = args.checkpoint or find_checkpoint(repo, effort, ledger_relative)
    checkpoint = resolve_commit(repo, checkpoint_raw, "checkpoint")
    validate_checkpoint_commit(
        repo,
        checkpoint,
        effort,
        ledger_relative,
        required_phase="final",
    )
    head = resolve_commit(repo, args.head or "HEAD", "integration head")
    current_head = resolve_commit(repo, "HEAD", "current HEAD")
    if head != current_head:
        fail(
            f"integration head {head} is not the current HEAD {current_head}; "
            "run aggregation on the integration branch without advancing it"
        )
    require_ancestor(
        repo,
        checkpoint,
        head,
        f"Planning checkpoint {checkpoint} is not an ancestor of integration head {head}",
    )
    selected = selected_verification_decisions(entries, args.decisions)

    supplied_commits = [resolve_commit(repo, raw, "verification commit") for raw in (args.commits or [])]
    all_commits: set[str] = set()
    for commit in supplied_commits:
        require_ancestor(
            repo,
            checkpoint,
            commit,
            f"verification commit {commit} does not descend from checkpoint {checkpoint}",
        )
        require_ancestor(
            repo,
            commit,
            head,
            f"verification commit {commit} is not an ancestor of integration head {head}",
        )
        all_commits.update(commits_since(repo, checkpoint, commit))

    records: list[tuple[str, Verification]] = []
    for commit in sorted(all_commits):
        if ledger_relative.as_posix() in changed_paths(repo, commit):
            fail(
                f"verification commit {commit} edits the shared Decision ledger; "
                "workers must record evidence on their own ticket or commit surface"
            )
        message = run_git(repo, "show", "-s", "--format=%B", commit).stdout
        records.extend((commit, record) for record in parse_verification_trailers(message))
    records.extend(
        (f"ticket:{record.origin}", record)
        for raw_evidence in (args.ticket_evidence or [])
        for record in (parse_ticket_evidence(raw_evidence),)
    )
    if not records:
        fail("at least one verification commit or ticket evidence record is required")

    updates: dict[str, list[str]] = {identifier: [] for identifier in selected}
    for commit, record in sorted(records, key=lambda item: (item[0], item[1].decision, item[1].evidence)):
        if record.decision not in entries:
            fail(f"verification trailer names missing decision {record.decision}")
        if entries[record.decision].status != "active":
            fail(f"verification trailer names superseded decision {record.decision}")
        if record.decision not in selected:
            fail(
                f"verification trailer for {record.decision} is outside the selected implementation decisions"
            )
        evidence = (
            f"ticket {record.origin}: {record.evidence}"
            if record.origin is not None
            else f"commit {commit}: {record.evidence}"
        )
        if evidence not in updates[record.decision]:
            updates[record.decision].append(evidence)

    missing: list[str] = []
    for identifier in selected:
        entry = entries[identifier]
        existing = entry.coverage.get("verification") == "complete" and has_non_empty_evidence(
            entry.evidence.get("verification")
        )
        if not existing and not updates[identifier]:
            missing.append(f"{identifier}:verification")
    if missing:
        fail(
            "verification coverage incomplete for implementation aggregation: "
            + ", ".join(missing)
            + "; record evidence on every relevant ticket or commit surface before retrying"
        )

    updated_text = append_verification_evidence(ledger_text, updates)
    path = repo / ledger_relative
    if updated_text == ledger_text:
        return {
            "status": "unchanged",
            "effort": effort,
            "checkpoint": checkpoint,
            "head": head,
            "ledger": ledger_relative.as_posix(),
            "decisions": list(selected),
            "commits": sorted(set(supplied_commits)),
            "ticket_evidence": list(args.ticket_evidence or []),
            "evidence": updates,
        }
    path.write_text(updated_text)
    parse_ledger(path.read_text())
    return {
        "status": "aggregated",
        "effort": effort,
        "checkpoint": checkpoint,
        "head": head,
        "ledger": ledger_relative.as_posix(),
        "decisions": list(selected),
        "commits": sorted(set(supplied_commits)),
        "ticket_evidence": list(args.ticket_evidence or []),
        "evidence": updates,
    }


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
    validate_checkpoint_ownership(repo, checkpoint_sha, ledger_relative, trailers)
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
        for obligation in entry_coverage_obligations(before):
            before_status = before.coverage.get(obligation, "pending")
            after_status = after.coverage.get(obligation, "pending")
            if before_status == "complete" and after_status != "complete":
                fail(
                    f"checkpointed coverage for {identifier}:{obligation} is not monotonic; "
                    f"cannot regress from complete to {after_status}"
                )
            before_evidence = before.evidence.get(obligation, "none")
            after_evidence = after.evidence.get(obligation, "none")
            if has_non_empty_evidence(before_evidence) and not preserves_checkpointed_evidence(
                before_evidence,
                after_evidence,
            ):
                fail(
                    f"checkpointed evidence for {identifier}:{obligation} is not append-only; "
                    "preserve the existing evidence and append new values"
                )
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
    if not FULL_CHECKPOINT_SHA_PATTERN.fullmatch(checkpoint):
        fail("Planning context marker checkpoint must be an exact 40-character hexadecimal commit SHA")
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
    if args.context_stdin:
        context_path = None
        context_label = "<stdin>"
        context_text = sys.stdin.read()
    else:
        context_path = relative_path(repo, args.context_file, must_exist=True)
        context_label = context_path.as_posix()
        context_text = (repo / context_path).read_text()
    marker = parse_marker(context_text)
    if marker is None:
        if not args.effort:
            return {"status": "legacy", "context": context_label}
        effort = validate_effort(args.effort)
        load_config(repo)
        ledger_relative = ledger_relative_path(repo, effort)
        checkpoint = find_checkpoint(repo, effort, ledger_relative)
        requested = ()
        source = "trailer"
    else:
        load_config(repo)
        effort = str(marker["effort"])
        configured_ledger_relative = ledger_relative_path(repo, effort)
        if args.effort and validate_effort(args.effort) != effort:
            fail("declared effort does not match the Planning context marker")
        marker_ledger_raw = str(marker["ledger"])
        override_ledger = args.ledger
        if override_ledger:
            ledger_relative = relative_path(repo, override_ledger, must_exist=True)
        else:
            try:
                ledger_relative = relative_path(repo, marker_ledger_raw)
            except PlanningError as error:
                fail(f"external Decision ledger pointer needs a local clone path: {error}")
            if ledger_relative != configured_ledger_relative:
                fail("Planning context ledger does not match the repository configuration")
        checkpoint = str(marker["checkpoint"])
        requested = tuple(str(item) for item in marker["decisions"])
        source = "stdin" if args.context_stdin else "marker"
    current = validate_checkpoint_commit(repo, checkpoint, effort, ledger_relative, required_phase=args.phase)
    selected = requested or tuple(identifier for identifier, entry in current.items() if entry.status == "active")
    for identifier in selected:
        if identifier not in current:
            fail(f"declared decision {identifier} is missing from the Decision ledger")
        if current[identifier].status != "active":
            fail(f"declared decision {identifier} is superseded; update the Planning context")
    required = set(required_for_phase(args.phase)) if args.phase else set()
    for obligation in args.require or []:
        if obligation not in (*OBLIGATIONS, APPLICABILITY_OBLIGATION):
            fail(f"unknown required obligation: {obligation}")
        required.add(obligation)
    missing = missing_coverage({identifier: current[identifier] for identifier in selected}, required)
    if missing:
        fail(f"coverage incomplete for declared Planning context: {', '.join(missing)}")
    resolved_checkpoint = run_git(repo, "rev-parse", "--verify", f"{checkpoint}^{{commit}}").stdout.strip()
    head_sha = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    coverage = {
        identifier: {
            obligation: {
                "status": current[identifier].coverage.get(obligation, "pending"),
                "evidence": current[identifier].evidence.get(obligation, "none"),
            }
            for obligation in entry_coverage_obligations(current[identifier])
        }
        for identifier in selected
    }
    return {
        "status": "valid",
        "context": context_label,
        "source": source,
        "effort": effort,
        "checkpoint": resolved_checkpoint,
        "ledger": ledger_relative.as_posix(),
        "decisions": list(selected),
        "coverage": coverage,
        "ancestry": {
            "checkpoint_sha": resolved_checkpoint,
            "head_sha": head_sha,
            "is_ancestor": True,
        },
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
    decision_add.add_argument("--constraints", help="optional one-line constraints")
    decision_add.add_argument("--rejected-alternatives", help="optional one-line rejected alternatives")
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

    def add_aggregate_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("--effort", required=True)
        command.add_argument("--checkpoint", help="validated final Planning checkpoint SHA")
        command.add_argument("--head", default="HEAD", help="current integration branch head")
        command.add_argument(
            "--commit",
            "--commits",
            dest="commits",
            action="append",
            help="merged worker commit or branch tip, repeat for each ticket; optional with ticket evidence",
        )
        command.add_argument(
            "--decisions",
            help="comma-separated active decision IDs applicable to this implementation",
        )
        command.add_argument(
            "--ticket-evidence",
            action="append",
            default=[],
            help="already-read ticket record: DEC-NNN | origin | observable evidence",
        )

    coverage_aggregate = coverage_commands.add_parser(
        "aggregate", help="atomically aggregate merged worker verification trailers"
    )
    add_aggregate_arguments(coverage_aggregate)

    checkpoint = commands.add_parser("checkpoint", help="create a phase-aware Git Planning checkpoint")
    checkpoint.add_argument("--effort", required=True)
    checkpoint.add_argument("--phase", required=True, choices=PHASES)
    checkpoint.add_argument("--message")
    checkpoint.add_argument(
        "--decisions",
        help="comma-separated active decision IDs to gate for an implementation checkpoint",
    )
    checkpoint.add_argument("--path", action="append", help="additional effort-owned planning artifact")

    marker = commands.add_parser("marker", help="generate or write a Planning context block")
    marker.add_argument("--effort", required=True)
    marker.add_argument("--checkpoint", required=True)
    marker.add_argument("--decisions")
    marker.add_argument("--repository")
    marker.add_argument("--output")

    validate = commands.add_parser("validate", help="validate a local or stdin consumer")
    context_input = validate.add_mutually_exclusive_group(required=True)
    context_input.add_argument("--context-file")
    context_input.add_argument("--context-stdin", action="store_true")
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
    if args.command == "coverage" and args.coverage_command == "aggregate":
        return command_coverage_aggregate(repo, args)
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
