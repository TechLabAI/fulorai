#!/usr/bin/env python3
"""checklist.py — Update project-checklist.md (human mirror of project-context.json).

The checklist is the human-friendly view of project state. JSON is the source
of truth (D-011), but humans read the checklist. This script keeps the two in
sync and offers convenience operations.

Status convention (D-009):
    [ ]  pending
    [~]  in-progress
    [x]  done
    [/]  skipped (not applicable)
    [!]  blocked

Usage:
    # Mark a single task as done by exact text match (or longest substring)
    python scripts/checklist.py mark --task "Bootstrap do repositório" --status done

    # Mark by line number
    python scripts/checklist.py mark --line 23 --status done

    # Count progress
    python scripts/checklist.py progress

    # Sync from project-context.json (refresh setup phase statuses)
    python scripts/checklist.py sync

    # Add a module section under "ETAPA 2 — Desenvolvimento"
    python scripts/checklist.py add-module OBR --display-name "Worksites" --service obras-service

    # Verify structure
    python scripts/checklist.py verify

Exit codes:
    0 — success
    1 — file not found, parse error
    2 — validation failure
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_CHECKLIST_FILE = "project-checklist.md"
DEFAULT_CONTEXT_FILE = "project-context.json"

# Match a checklist item line: "- [x] text..." or "  - [ ] text..." (with indent)
CHECKLIST_LINE_RE = re.compile(r"^(\s*-\s+)\[([ x~/!])\](\s+.*)$")

# Map status name → bracket char
STATUS_TO_CHAR = {
    "pending": " ",
    "in-progress": "~",
    "done": "x",
    "skipped": "/",
    "blocked": "!",
}
CHAR_TO_STATUS = {v: k for k, v in STATUS_TO_CHAR.items()}


# ── I/O ───────────────────────────────────────────────────────────────────────


def find_file(name: str, explicit: Path | None) -> Path:
    if explicit:
        if not explicit.exists():
            sys.exit(f"error: file not found: {explicit}")
        return explicit
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / name
        if candidate.exists():
            return candidate
    sys.exit(f"error: {name} not found in cwd or any parent directory")


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def write_lines(path: Path, lines: list[str]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(lines), encoding="utf-8")
    tmp.replace(path)


# ── Matching ─────────────────────────────────────────────────────────────────


def find_item_line(lines: list[str], task_text: str) -> int | None:
    """Return 0-based index of the line matching task_text (longest substring).

    Search is case-insensitive. If multiple lines match, returns the one with
    the closest length. Returns None if no match.
    """
    task_lower = task_text.lower()
    best: tuple[int, int] | None = None  # (index, score)
    for i, line in enumerate(lines):
        m = CHECKLIST_LINE_RE.match(line)
        if not m:
            continue
        text = m.group(3).strip().lower()
        if task_lower in text:
            score = abs(len(text) - len(task_lower))
            if best is None or score < best[1]:
                best = (i, score)
    return best[0] if best else None


def set_status_on_line(line: str, new_status_char: str) -> str:
    m = CHECKLIST_LINE_RE.match(line)
    if not m:
        return line
    prefix, _old, suffix = m.group(1), m.group(2), m.group(3)
    return f"{prefix}[{new_status_char}]{suffix}\n" if not line.endswith("\n") else f"{prefix}[{new_status_char}]{suffix}\n"


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_mark(args: argparse.Namespace) -> int:
    if args.status not in STATUS_TO_CHAR:
        sys.exit(f"error: invalid status {args.status!r}. Valid: {', '.join(STATUS_TO_CHAR)}")
    char = STATUS_TO_CHAR[args.status]

    path = find_file(DEFAULT_CHECKLIST_FILE, args.file)
    lines = read_lines(path)

    if args.line is not None:
        idx = args.line - 1
        if idx < 0 or idx >= len(lines):
            sys.exit(f"error: line {args.line} out of range (1..{len(lines)})")
        if not CHECKLIST_LINE_RE.match(lines[idx]):
            sys.exit(f"error: line {args.line} is not a checklist item")
    elif args.task:
        idx_opt = find_item_line(lines, args.task)
        if idx_opt is None:
            sys.exit(f"error: no checklist item matches {args.task!r}")
        idx = idx_opt
    else:
        sys.exit("error: provide either --task or --line")

    # Re-parse to preserve trailing newline
    m = CHECKLIST_LINE_RE.match(lines[idx])
    assert m is not None
    prefix, _old_char, suffix = m.group(1), m.group(2), m.group(3)
    # Preserve original line ending
    ending = "\n" if lines[idx].endswith("\n") else ""
    lines[idx] = f"{prefix}[{char}]{suffix}{ending}"

    write_lines(path, lines)
    print(f"OK: line {idx + 1} marked as {args.status}")
    return 0


def cmd_progress(args: argparse.Namespace) -> int:
    """Print per-status counts."""
    path = find_file(DEFAULT_CHECKLIST_FILE, args.file)
    lines = read_lines(path)
    counts = {k: 0 for k in STATUS_TO_CHAR}
    for line in lines:
        m = CHECKLIST_LINE_RE.match(line)
        if not m:
            continue
        char = m.group(2)
        status = CHAR_TO_STATUS.get(char)
        if status:
            counts[status] += 1
    total = sum(counts.values())
    print(f"Total checklist items: {total}")
    for status, count in counts.items():
        if total > 0:
            pct = count * 100 / total
            print(f"  [{STATUS_TO_CHAR[status]}] {status:13} {count:4} ({pct:5.1f}%)")
        else:
            print(f"  [{STATUS_TO_CHAR[status]}] {status:13} {count:4}")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync setup phase statuses from project-context.json into the checklist."""
    ctx_path = find_file(DEFAULT_CONTEXT_FILE, args.context_file)
    chk_path = find_file(DEFAULT_CHECKLIST_FILE, args.file)
    ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
    phases = ctx.get("setup", {}).get("phases", [])
    if not phases:
        print("warning: no setup phases found in context", file=sys.stderr)
        return 0

    lines = read_lines(chk_path)
    changes = 0
    for phase in phases:
        phase_id = phase.get("id", "")
        status = phase.get("status", "pending")
        char = STATUS_TO_CHAR.get(status, " ")
        # Find the section heading for this phase: "### P0 — Bootstrap..." etc.
        section_re = re.compile(rf"^### {re.escape(phase_id.split('-', 1)[0])}\b", re.IGNORECASE)
        # Find the section start
        sect_start = None
        for i, line in enumerate(lines):
            if section_re.match(line):
                sect_start = i
                break
        if sect_start is None:
            continue
        # Find section end (next `### ` heading or end of file)
        sect_end = len(lines)
        for j in range(sect_start + 1, len(lines)):
            if lines[j].startswith("### ") or lines[j].startswith("## "):
                sect_end = j
                break
        # If phase is done, set all items in section to done; if pending, leave as-is
        if status == "done":
            for k in range(sect_start, sect_end):
                m = CHECKLIST_LINE_RE.match(lines[k])
                if m and m.group(2) != char:
                    prefix, _, suffix = m.group(1), m.group(2), m.group(3)
                    lines[k] = f"{prefix}[{char}]{suffix}\n"
                    changes += 1

    if changes:
        write_lines(chk_path, lines)
    print(f"OK: synced {changes} item(s) from context phases")
    return 0


def cmd_add_module(args: argparse.Namespace) -> int:
    """Add a module section under ETAPA 2 → Módulos backend."""
    path = find_file(DEFAULT_CHECKLIST_FILE, args.file)
    lines = read_lines(path)

    # Search for an existing section for this module
    target_prefix = args.module.upper()
    existing = None
    for i, line in enumerate(lines):
        if re.match(rf"^#### {re.escape(target_prefix)}\b", line):
            existing = i
            break
    if existing is not None:
        print(f"OK: module {target_prefix} already exists in checklist (line {existing + 1})")
        return 0

    # Find the "Módulos backend" header to anchor insertion
    anchor = None
    for i, line in enumerate(lines):
        if "Módulos backend" in line or "Backend modules" in line:
            anchor = i
            break
    if anchor is None:
        sys.exit("error: could not find 'Módulos backend' section to anchor the new module")

    # Find next "### " or "## " heading after anchor, insert just before it
    insert_at = len(lines)
    for j in range(anchor + 1, len(lines)):
        if lines[j].startswith("### ") or lines[j].startswith("## "):
            insert_at = j
            break

    display = args.display_name or args.module
    service = args.service or f"{args.module.lower()}-service"

    block = (
        f"\n#### {target_prefix} — {display} (`{service}`)\n"
        f"- [ ] **Arquitetura** (4 etapas)\n"
        f"  - [ ] `/be-architect-vision {target_prefix}` → docs/services/{service}/01..06.md + adr/\n"
        f"  - [ ] `/be-architect-specs {target_prefix}` → contracts/\n"
        f"  - [ ] `/be-architect-backlog {target_prefix}` → issues + plan\n"
        f"  - [ ] `/be-architect-scaffold {target_prefix}` → backend/services/{service}/\n"
        f"- [ ] **Ciclo de desenvolvimento**\n"
        f"  - [ ] `/be-validator {target_prefix} BASELINE`\n"
        f"  - [ ] `/be-planner {target_prefix}`\n"
        f"  - [ ] `/be-implement {target_prefix} P1`\n"
        f"- **Status atual:** declared\n\n"
    )

    new_lines = lines[:insert_at] + [block] + lines[insert_at:]
    write_lines(path, new_lines)
    print(f"OK: added module {target_prefix} section at line {insert_at + 1}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Basic structural check."""
    path = find_file(DEFAULT_CHECKLIST_FILE, args.file)
    lines = read_lines(path)
    items = [line for line in lines if CHECKLIST_LINE_RE.match(line)]
    sections = [line for line in lines if line.startswith("### ")]
    if not items:
        print("FAIL: no checklist items found", file=sys.stderr)
        return 2
    print(f"OK: {len(sections)} section(s), {len(items)} checklist item(s)")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="checklist.py",
        description="Update project-checklist.md (human mirror of project-context.json)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help=f"Path to {DEFAULT_CHECKLIST_FILE} (default: search from cwd upward)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_mark = sub.add_parser("mark", help="Mark a checklist item with a status")
    group = p_mark.add_mutually_exclusive_group(required=True)
    group.add_argument("--task", help="Substring match against the task text")
    group.add_argument("--line", type=int, help="1-based line number")
    p_mark.add_argument(
        "--status",
        required=True,
        choices=list(STATUS_TO_CHAR.keys()),
        help="Target status",
    )
    p_mark.set_defaults(func=cmd_mark)

    p_prog = sub.add_parser("progress", help="Show counts and percentages per status")
    p_prog.set_defaults(func=cmd_progress)

    p_sync = sub.add_parser("sync", help="Sync setup phase statuses from project-context.json")
    p_sync.add_argument(
        "--context-file",
        type=Path,
        default=None,
        help=f"Path to {DEFAULT_CONTEXT_FILE}",
    )
    p_sync.set_defaults(func=cmd_sync)

    p_add = sub.add_parser("add-module", help="Add a new module section under ETAPA 2")
    p_add.add_argument("module", help="Module prefix (e.g. OBR)")
    p_add.add_argument("--display-name", default=None, help="Human-readable display name")
    p_add.add_argument("--service", default=None, help="Backend service name (default: <module>-service)")
    p_add.set_defaults(func=cmd_add_module)

    p_ver = sub.add_parser("verify", help="Structural validation")
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
