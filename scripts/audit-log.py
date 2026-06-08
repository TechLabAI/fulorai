#!/usr/bin/env python3
"""audit-log.py - consolidated audit trail for due-diligence (D-141, Pole Position S3 Fase B).

Joins three independent signals into one report:

    git history          -> author + GPG verification + timestamp
    D-NNN in commit msg  -> cross-checked against consolidation doc
    files touched        -> smoke evidence + lock impact tags

Stdlib only. Reads `git log --pretty=...` once, walks consolidation doc once,
correlates in memory. JSON for tooling, Markdown for humans.

Usage:
    python scripts/audit-log.py --last 30
    python scripts/audit-log.py --since 2026-05-01 --until HEAD --json
    python scripts/audit-log.py --last 50 --output tmp/audit.md

Exit codes (per scripts I/O convention, CLAUDE.md R3):
    0 success
    1 user error (bad flag, no commits in range)
    2 validation failure (consolidation doc unreadable, git not a repo)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

from cli_utils import force_utf8_stdio


# ── Constants ────────────────────────────────────────────────────────────────

D_NNN_RE = re.compile(r"D-\d{3}")
ARCH_ASPECT_RE = re.compile(r"templates/architecture/decisions/[\w\-]+\.arch\.json")
LOCK_FILE_RE = re.compile(r"architecture\.lock")
SMOKE_FILE_RE = re.compile(r"tests/(?:smoke_[\w]+|run_all_smokes)\.py")

CONSOLIDATION_REL = "plans/techlab-architecture-plan-consolidation-v4.md"
CHARTER_REL = "docs/governance/audit-charter.md"


# ── Data shapes ──────────────────────────────────────────────────────────────


@dataclass
class CommitEntry:
    sha: str
    short_sha: str
    author_name: str
    author_email: str
    timestamp: str
    subject: str
    gpg_verified: bool
    gpg_status: str
    decision_ids: list[str] = field(default_factory=list)
    decision_known: list[str] = field(default_factory=list)
    decision_unknown: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    aspect_changes: list[str] = field(default_factory=list)
    lock_touched: bool = False
    smoke_files: list[str] = field(default_factory=list)


@dataclass
class AuditReport:
    workspace: str
    range_spec: str
    generated_at: str
    total_commits: int
    gpg_verified_count: int
    commits_with_decision: int
    distinct_decisions: list[str]
    unknown_decisions: list[str]
    entries: list[CommitEntry] = field(default_factory=list)


# ── Workspace discovery ──────────────────────────────────────────────────────


def find_workspace(start: Path) -> Path:
    """Walk up from start until we find pyproject.toml + scripts/ + docs/."""
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "scripts").is_dir():
            return candidate
    sys.exit(f"error: workspace root not found from {start}")


# ── Consolidation doc parsing ────────────────────────────────────────────────


def load_known_decisions(workspace: Path) -> set[str]:
    """Extract D-NNN ids referenced in the consolidation doc.

    Returns the set of unique D-NNN tokens that appear in the doc — that
    set defines "known decisions" for cross-checking. We deliberately do
    NOT require strict positional anchoring (no `**D-NNN**` requirement);
    any occurrence counts. Consolidation doc is the workspace's
    authoritative ledger per R1.
    """
    path = workspace / CONSOLIDATION_REL
    if not path.is_file():
        sys.exit(f"error: consolidation doc not found at {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(D_NNN_RE.findall(text))


# ── Git interaction ──────────────────────────────────────────────────────────


def run_git(args: list[str], workspace: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(workspace),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        sys.exit(f"error: git {' '.join(args)} failed:\n{proc.stderr}")
    return proc.stdout


def git_log_entries(
    workspace: Path,
    *,
    since: str | None,
    until: str | None,
    last: int | None,
    path_filter: list[str] | None,
) -> list[dict]:
    """Run git log with a stable record separator and parse to dicts.

    %H %an %ae %ct %G? %s on one line; %B body; then files via --name-only.
    We use a NUL-byte separator between commits so subject/body can contain
    any printable character without collision.
    """
    # With -z: git separates files within a commit with \0 and commits
    # with \0\0. The format string itself ends with a literal sentinel so
    # we can split metadata-from-files reliably even when the commit body
    # contains arbitrary characters.
    #
    # Layout after substitution + -z:
    #   SHA\tAUTHOR\tEMAIL\tUNIX_TS\tGPG\tSUBJECT\nBODY\n===END===\n
    #   file1\0file2\0...\0\0
    fmt = "%H%x09%an%x09%ae%x09%ct%x09%G?%x09%s%n%b%n===END==="
    args = ["log", f"--pretty=format:{fmt}", "--name-only", "-z"]
    if last is not None:
        args.append(f"-n{last}")
    if since:
        args.append(f"--since={since}")
    if until:
        args.append(f"--until={until}")
    if path_filter:
        args.append("--")
        args.extend(path_filter)
    raw = run_git(args, workspace)
    return _parse_git_log_z(raw)


_END_SENTINEL = "===END==="


def _parse_git_log_z(raw: str) -> list[dict]:
    """Parse the NUL-separated git log output. See git_log_entries() for layout."""
    if not raw.strip("\x00\n "):
        return []
    entries: list[dict] = []
    # Commits separated by NUL+NUL when files are present, or by NUL alone
    # when a commit had zero files (rare but possible for empty commits).
    for chunk in raw.split("\x00\x00"):
        # Each chunk may still contain a trailing \x00 from the last file
        chunk = chunk.strip("\x00")
        if not chunk:
            continue
        if _END_SENTINEL in chunk:
            meta_block, _, file_block = chunk.partition(_END_SENTINEL)
            file_block = file_block.lstrip("\n")
        else:
            # Empty commit (no files): only metadata, ===END=== was the last char
            meta_block = chunk
            file_block = ""
        meta_block = meta_block.rstrip("\n")
        lines = meta_block.split("\n", 1)
        header = lines[0]
        body = lines[1] if len(lines) > 1 else ""
        parts = header.split("\t")
        if len(parts) < 6:
            continue
        sha, an, ae, ct, gpg, subject = parts[:6]
        files = [f for f in file_block.split("\x00") if f.strip()]
        try:
            ts_unix = int(ct)
        except ValueError:
            continue
        entries.append({
            "sha": sha,
            "author_name": an,
            "author_email": ae,
            "timestamp_unix": ts_unix,
            "gpg": gpg,
            "subject": subject,
            "body": body.rstrip("\n"),
            "files": files,
        })
    return entries


# ── Correlation ──────────────────────────────────────────────────────────────


GPG_VERIFIED_MARKERS = {"G", "U", "E"}  # G=good, U=good w/ unknown, E=missing key but signed
GPG_STATUS_LABELS = {
    "G": "good",
    "U": "good (unknown validity)",
    "B": "bad",
    "X": "good but expired",
    "Y": "good but expired key",
    "R": "good but revoked key",
    "E": "missing key",
    "N": "unsigned",
}


def correlate(entry: dict, known: set[str]) -> CommitEntry:
    """Build a CommitEntry from a raw git-log dict + known D-NNN set."""
    body_and_subject = entry["subject"] + "\n" + entry["body"]
    decisions = sorted(set(D_NNN_RE.findall(body_and_subject)))
    aspect_changes = sorted({
        Path(f).stem.replace(".arch", "")
        for f in entry["files"]
        if ARCH_ASPECT_RE.search(f.replace("\\", "/"))
    })
    lock_touched = any(LOCK_FILE_RE.search(f.replace("\\", "/")) for f in entry["files"])
    smoke_files = sorted({
        f.replace("\\", "/")
        for f in entry["files"]
        if SMOKE_FILE_RE.search(f.replace("\\", "/"))
    })
    gpg = entry["gpg"] or "N"
    iso_ts = _unix_to_iso(entry["timestamp_unix"])
    decision_known = [d for d in decisions if d in known]
    decision_unknown = [d for d in decisions if d not in known]
    return CommitEntry(
        sha=entry["sha"],
        short_sha=entry["sha"][:8],
        author_name=entry["author_name"],
        author_email=entry["author_email"],
        timestamp=iso_ts,
        subject=entry["subject"],
        gpg_verified=gpg in GPG_VERIFIED_MARKERS,
        gpg_status=GPG_STATUS_LABELS.get(gpg, f"unknown:{gpg}"),
        decision_ids=decisions,
        decision_known=decision_known,
        decision_unknown=decision_unknown,
        files=entry["files"],
        aspect_changes=aspect_changes,
        lock_touched=lock_touched,
        smoke_files=smoke_files,
    )


def _unix_to_iso(ts: int) -> str:
    """ISO-8601 UTC. Stdlib only."""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_report(
    entries: list[CommitEntry],
    *,
    workspace: Path,
    range_spec: str,
) -> AuditReport:
    from datetime import datetime, timezone
    all_decisions = sorted({d for e in entries for d in e.decision_ids})
    unknown = sorted({d for e in entries for d in e.decision_unknown})
    return AuditReport(
        workspace=str(workspace),
        range_spec=range_spec,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        total_commits=len(entries),
        gpg_verified_count=sum(1 for e in entries if e.gpg_verified),
        commits_with_decision=sum(1 for e in entries if e.decision_ids),
        distinct_decisions=all_decisions,
        unknown_decisions=unknown,
        entries=entries,
    )


# ── Renderers ────────────────────────────────────────────────────────────────


def render_json(report: AuditReport) -> str:
    return json.dumps(asdict(report), indent=2, ensure_ascii=False)


def render_markdown(report: AuditReport) -> str:
    lines: list[str] = []
    lines.append("# Audit log — techlab-architecture")
    lines.append("")
    lines.append(f"> **Generated:** {report.generated_at}")
    lines.append(f"> **Range:** {report.range_spec}")
    lines.append(f"> **Workspace:** `{report.workspace}`")
    lines.append(f"> **Charter:** see `{CHARTER_REL}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Commits in range:** {report.total_commits}")
    pct = (report.gpg_verified_count / report.total_commits * 100) if report.total_commits else 0
    lines.append(f"- **GPG-verified:** {report.gpg_verified_count} ({pct:.0f}%)")
    lines.append(f"- **Linked to D-NNN:** {report.commits_with_decision}")
    lines.append(f"- **Distinct decisions referenced:** {len(report.distinct_decisions)}")
    if report.unknown_decisions:
        lines.append(f"- **Unknown D-NNN (not in consolidation doc):** {', '.join(report.unknown_decisions)} - REVIEW")
    else:
        lines.append("- **Unknown D-NNN (not in consolidation doc):** none")
    lines.append("")
    lines.append("## Entries")
    lines.append("")
    if not report.entries:
        lines.append("_No commits in range._")
        return "\n".join(lines) + "\n"
    for e in report.entries:
        gpg_badge = "[GPG ok]" if e.gpg_verified else f"[GPG {e.gpg_status}]"
        decision_badge = f" {{{', '.join(e.decision_ids)}}}" if e.decision_ids else ""
        lines.append(f"### `{e.short_sha}` {gpg_badge}{decision_badge}")
        lines.append("")
        lines.append(f"- **Subject:** {e.subject}")
        lines.append(f"- **Author:** {e.author_name} <{e.author_email}>")
        lines.append(f"- **Timestamp:** {e.timestamp}")
        if e.decision_known:
            lines.append(f"- **Decisions (known):** {', '.join(e.decision_known)}")
        if e.decision_unknown:
            lines.append(f"- **Decisions (unknown - not in consolidation doc):** {', '.join(e.decision_unknown)}")
        if e.aspect_changes:
            lines.append(f"- **Aspects touched:** {', '.join(e.aspect_changes)}")
        if e.lock_touched:
            lines.append("- **architecture.lock:** touched")
        if e.smoke_files:
            lines.append(f"- **Smoke evidence:** {', '.join(e.smoke_files)}")
        if e.files:
            preview = e.files[:8]
            more = f" (+{len(e.files) - 8} more)" if len(e.files) > 8 else ""
            lines.append(f"- **Files:** {len(e.files)} - {', '.join(preview)}{more}")
        lines.append("")
    return "\n".join(lines) + "\n"


# ── Public API (for smoke and library use) ───────────────────────────────────


def build_audit_report(
    workspace: Path,
    *,
    since: str | None = None,
    until: str | None = None,
    last: int | None = 30,
    path_filter: list[str] | None = None,
) -> AuditReport:
    """Programmatic entry point used by smoke + ai-ops-report."""
    known = load_known_decisions(workspace)
    raw = git_log_entries(
        workspace,
        since=since,
        until=until,
        last=last,
        path_filter=path_filter,
    )
    entries = [correlate(r, known) for r in raw]
    range_spec = _format_range_spec(since=since, until=until, last=last, path_filter=path_filter)
    return build_report(entries, workspace=workspace, range_spec=range_spec)


def _format_range_spec(*, since, until, last, path_filter) -> str:
    parts = []
    if last is not None:
        parts.append(f"last {last} commits")
    if since:
        parts.append(f"since {since}")
    if until:
        parts.append(f"until {until}")
    if path_filter:
        parts.append(f"paths={','.join(path_filter)}")
    return " | ".join(parts) if parts else "all history"


# ── CLI ──────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="audit-log",
        description="Consolidated audit trail for due-diligence reviews.",
    )
    p.add_argument("--workspace", type=Path, default=None,
                   help="Workspace root (default: walk up from cwd).")
    p.add_argument("--last", type=int, default=30,
                   help="Last N commits (default 30). Use 0 for no limit.")
    p.add_argument("--since", type=str, default=None,
                   help="git --since spec (e.g. '2026-05-01').")
    p.add_argument("--until", type=str, default=None,
                   help="git --until spec.")
    p.add_argument("--path", type=str, action="append", default=[],
                   help="Limit to commits touching this path (repeatable).")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", type=Path, default=None,
                   help="Write to file (default: stdout).")
    p.add_argument("--strict", action="store_true",
                   help="Exit 2 if any commit references an unknown D-NNN.")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = _build_parser()
    args = parser.parse_args(argv)

    workspace = args.workspace.resolve() if args.workspace else find_workspace(Path.cwd().resolve())
    last = None if args.last == 0 else args.last
    path_filter = args.path or None

    report = build_audit_report(
        workspace,
        since=args.since,
        until=args.until,
        last=last,
        path_filter=path_filter,
    )

    rendered = render_json(report) if args.format == "json" else render_markdown(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"OK: audit log written to {args.output} ({report.total_commits} commits)")
    else:
        print(rendered)

    if args.strict and report.unknown_decisions:
        print(
            f"error: {len(report.unknown_decisions)} unknown D-NNN found: "
            f"{', '.join(report.unknown_decisions)}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
