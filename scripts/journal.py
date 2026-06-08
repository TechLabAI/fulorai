#!/usr/bin/env python3
"""journal.py — Append entries to project-journal.md.

The journal is an append-only log of activities (D-011). Every command that
mutates the project state must record what happened: actor, action, artifacts
affected. Manual deletion of entries is forbidden — corrections are added as
new `[CORRECTION]` entries referencing the original timestamp.

This script enforces:
- Entries are always appended at the bottom (never inserted).
- Timestamps are UTC, ISO 8601 (matching project-context.json convention).
- Each entry has a category tag in square brackets (e.g., [PHASE-START]).
- Entries are grouped by date heading; a new date heading is added when needed.
- Idempotent at the timestamp level: re-running with the same timestamp+message
  is a no-op (skipped with a warning).

Categories (recognized — others trigger a warning):
- SETUP             — /new-project orchestrator started/ended
- PHASE-START       — beginning of a setup phase (P0..P6)
- PHASE-END         — end of a setup phase
- HANDOFF           — orchestrator handed control back to user
- PROJECT-INIT      — project ready, awaiting first /be-architect-*
- COMMAND-START     — a project command (be-architect-*, /fe-*, etc.) started
- COMMAND-END       — a project command finished
- VALIDATOR-BASELINE — /be-validator in BASELINE mode ran
- VALIDATOR-DECISION — /be-validator in DECISION mode emitted a decision
- PLANNER           — /be-planner produced a plan
- IMPLEMENTER       — /be-implement processed a priority
- AUTOPILOT-CHECKPOINT — /be-autopilot checkpointed state
- TLAB-SYNC         — sync-techlab-ai.py ran
- MODULE-REGISTERED — a new module was registered in the registry
- CORRECTION        — correction note referencing a previous entry

Usage:
    # Simple log message
    python scripts/journal.py append --category PHASE-START \\
        --actor "/new-project orchestrator" \\
        --message "P3 techlab-ai sync started"

    # With explicit details (renders as bullet list)
    python scripts/journal.py append --category PHASE-END \\
        --actor "scripts/sync-techlab-ai.py" \\
        --message "P3 → done" \\
        --details "duration:3m12s,artifacts:integrations/techlab-ai/{README.md,openapi.json}"

    # Correction
    python scripts/journal.py correction --reference "2026-05-23 20:14:00 UTC" \\
        --note "checkpoint inconsistent due to gradlew crash; re-ran manually"

Exit codes:
    0 — entry appended (or no-op due to idempotency)
    1 — file not found, format error, or invalid argument
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_JOURNAL_FILE = "project-journal.md"

KNOWN_CATEGORIES = {
    "SETUP",
    "PHASE-START",
    "PHASE-END",
    "HANDOFF",
    "PROJECT-INIT",
    "COMMAND-START",
    "COMMAND-END",
    "VALIDATOR-BASELINE",
    "VALIDATOR-DECISION",
    "VALIDATOR-VALIDATION",
    "PLANNER",
    "IMPLEMENTER",
    "AUTOPILOT-CHECKPOINT",
    "TLAB-SYNC",
    "MODULE-REGISTERED",
    "CORRECTION",
}


# ── I/O ───────────────────────────────────────────────────────────────────────


def find_journal_file(explicit: Path | None) -> Path:
    if explicit:
        if not explicit.exists():
            sys.exit(f"error: file not found: {explicit}")
        return explicit
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / DEFAULT_JOURNAL_FILE
        if candidate.exists():
            return candidate
    sys.exit(
        f"error: {DEFAULT_JOURNAL_FILE} not found in cwd or any parent directory"
    )


def read_journal(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_journal(path: Path, content: str) -> None:
    """Write atomically."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


# ── Formatting ───────────────────────────────────────────────────────────────


def utc_now() -> tuple[str, str, str]:
    """Return (date_heading 'YYYY-MM-DD', time_part 'HH:MM:SS UTC', iso_full)."""
    now = datetime.now(timezone.utc)
    date_heading = now.strftime("%Y-%m-%d")
    time_part = now.strftime("%H:%M:%S UTC")
    iso_full = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return date_heading, time_part, iso_full


def render_entry(
    time_part: str,
    category: str,
    message: str,
    actor: str | None,
    details: dict[str, str] | None,
) -> str:
    """Render a single journal entry block."""
    lines = [f"### {time_part} — [{category}] {message}", ""]
    if actor:
        lines.append(f"- **Ator:** {actor}")
    if details:
        for key, value in details.items():
            label = key.replace("_", " ").capitalize()
            lines.append(f"- **{label}:** {value}")
    lines.append("")
    return "\n".join(lines)


def parse_details(raw: str | None) -> dict[str, str]:
    """Parse `key1:value1,key2:value2` into a dict, preserving order."""
    if not raw:
        return {}
    out: dict[str, str] = {}
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            out[chunk] = "(no value)"
            continue
        key, value = chunk.split(":", 1)
        out[key.strip()] = value.strip()
    return out


# ── Heading management ───────────────────────────────────────────────────────


_DATE_HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
_ENTRY_HEADING_RE = re.compile(r"^### (\d{2}:\d{2}:\d{2} UTC) — \[([A-Z\-]+)\] (.+)$", re.MULTILINE)


def has_date_heading(content: str, date_heading: str) -> bool:
    return any(m.group(1) == date_heading for m in _DATE_HEADING_RE.finditer(content))


def find_appendable_position(content: str) -> int:
    """Return the offset where new entries should be appended.

    Strategy: find the FIRST horizontal rule separator after the date headings
    section (the "Padrão de entrada futura" placeholder block in the v1
    journal); insert before it. If no such separator, append at end.
    """
    # Look for "## Padrão de entrada futura" or similar template markers
    template_marker = content.find("## Padrão de entrada futura")
    if template_marker == -1:
        template_marker = content.find("## Future entry pattern")
    if template_marker != -1:
        # Find the "---" before this marker
        before = content[:template_marker]
        last_hr = before.rfind("\n---\n")
        if last_hr != -1:
            return last_hr + 1  # insert AT the position of the \n after first ---
    # Fallback: append at end (before final newline if present)
    return len(content.rstrip()) + 1


def has_exact_entry(content: str, time_part: str, category: str, message: str) -> bool:
    """Idempotency check."""
    needle = f"### {time_part} — [{category}] {message}"
    return needle in content


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_append(args: argparse.Namespace) -> int:
    if args.category not in KNOWN_CATEGORIES:
        print(
            f"warning: unknown category {args.category!r}. "
            f"Known: {', '.join(sorted(KNOWN_CATEGORIES))}",
            file=sys.stderr,
        )

    path = find_journal_file(args.file)
    content = read_journal(path)
    date_heading, time_part, _iso = utc_now()

    if args.timestamp:
        # Override with explicit timestamp (must match HH:MM:SS UTC)
        if not re.match(r"^\d{2}:\d{2}:\d{2} UTC$", args.timestamp):
            sys.exit(f"error: --timestamp must match 'HH:MM:SS UTC' format, got {args.timestamp!r}")
        time_part = args.timestamp

    if has_exact_entry(content, time_part, args.category, args.message):
        print(f"OK: entry already present (no-op): {time_part} [{args.category}]", file=sys.stderr)
        return 0

    details = parse_details(args.details)
    entry = render_entry(time_part, args.category, args.message, args.actor, details)

    # Ensure date heading exists
    insert_pos = find_appendable_position(content)
    block_to_insert = ""
    if not has_date_heading(content, date_heading):
        block_to_insert += f"## {date_heading}\n\n"
    block_to_insert += entry + "\n"

    new_content = content[:insert_pos] + block_to_insert + content[insert_pos:]
    write_journal(path, new_content)
    print(f"OK: appended {time_part} [{args.category}] {args.message[:60]}")
    return 0


def cmd_correction(args: argparse.Namespace) -> int:
    """Add a CORRECTION entry referencing a previous timestamp."""
    path = find_journal_file(args.file)
    content = read_journal(path)
    date_heading, time_part, _ = utc_now()

    message = f"referência a entrada de {args.reference}"
    note_block = f"> NOTA HUMANA: {args.note}"
    entry = render_entry(time_part, "CORRECTION", message, args.actor, None)
    entry = entry.rstrip() + "\n\n" + note_block + "\n\n"

    if has_exact_entry(content, time_part, "CORRECTION", message):
        print("OK: correction already present (no-op)", file=sys.stderr)
        return 0

    insert_pos = find_appendable_position(content)
    block_to_insert = ""
    if not has_date_heading(content, date_heading):
        block_to_insert += f"## {date_heading}\n\n"
    block_to_insert += entry

    new_content = content[:insert_pos] + block_to_insert + content[insert_pos:]
    write_journal(path, new_content)
    print(f"OK: correction appended (ref: {args.reference})")
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    """Print the last N entries (default 5)."""
    path = find_journal_file(args.file)
    content = read_journal(path)
    entries = list(_ENTRY_HEADING_RE.finditer(content))
    if not entries:
        print("(no entries found)")
        return 0
    take = entries[-args.count :]
    for m in take:
        print(f"{m.group(1)} [{m.group(2)}] {m.group(3)}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Check that file exists and has at least one valid entry."""
    path = find_journal_file(args.file)
    content = read_journal(path)
    headings = _DATE_HEADING_RE.findall(content)
    entries = _ENTRY_HEADING_RE.findall(content)

    if not headings:
        print("FAIL: no date headings (## YYYY-MM-DD) found", file=sys.stderr)
        return 2
    if not entries:
        print("FAIL: no entries found", file=sys.stderr)
        return 2

    unknown_categories = {cat for _, cat, _ in entries} - KNOWN_CATEGORIES
    if unknown_categories:
        print(
            f"warning: found unknown categories: {sorted(unknown_categories)}",
            file=sys.stderr,
        )

    print(f"OK: {len(headings)} date heading(s), {len(entries)} entries")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="journal.py",
        description="Append entries to project-journal.md (append-only log)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help=f"Path to {DEFAULT_JOURNAL_FILE} (default: search from cwd upward)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_app = sub.add_parser("append", help="Append a new entry")
    p_app.add_argument("--category", required=True, help="Entry category (e.g. PHASE-START)")
    p_app.add_argument("--message", required=True, help="Brief message")
    p_app.add_argument("--actor", default=None, help="Actor (human or command/script)")
    p_app.add_argument(
        "--details",
        default=None,
        help="Optional details as 'key1:value1,key2:value2'",
    )
    p_app.add_argument(
        "--timestamp",
        default=None,
        help="Override timestamp (HH:MM:SS UTC). Default: now.",
    )
    p_app.set_defaults(func=cmd_append)

    p_corr = sub.add_parser("correction", help="Add a correction referencing an earlier entry")
    p_corr.add_argument("--reference", required=True, help="Original timestamp being corrected")
    p_corr.add_argument("--note", required=True, help="Correction note")
    p_corr.add_argument("--actor", default="human", help="Actor (default: human)")
    p_corr.set_defaults(func=cmd_correction)

    p_tail = sub.add_parser("tail", help="Show last N entries")
    p_tail.add_argument("--count", type=int, default=5, help="Number of entries (default: 5)")
    p_tail.set_defaults(func=cmd_tail)

    p_ver = sub.add_parser("verify", help="Check structural integrity of the journal")
    p_ver.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
