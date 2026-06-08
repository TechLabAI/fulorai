#!/usr/bin/env python3
"""context.py — CRUD utility for project-context.json.

This script is the canonical interface for reading and mutating the project
context JSON. Every command in .claude/commands/ that needs to query or
update structured project state must go through this script, not direct file
I/O. This keeps the schema stable, normalizes paths, and updates the
`lastUpdatedAt` field automatically.

Invariants enforced:
- JSON remains valid (json.load round-trip after every write).
- `lastUpdatedAt` is refreshed to current UTC time after every mutation.
- Mutations are atomic: written to a temp file, then renamed.
- Reads NEVER modify the file.

Usage examples:
    # Read top-level keys
    python scripts/context.py get project.name
    # → bosq

    # Read a nested path (dotted notation)
    python scripts/context.py get stack.backend.packageBase

    # List all module prefixes
    python scripts/context.py get modules.registry --jsonpath
    # → outputs JSON array

    # Update a value
    python scripts/context.py set ai.techlabAi.sourceSha abc123def

    # Append to an array
    python scripts/context.py append modules.registry '{"prefix":"OBR",...}'

    # Mark a setup phase as done
    python scripts/context.py mark-phase P3-techlab-ai-sync done

    # Add to consumedByModules list of techlab-ai
    python scripts/context.py techlabai-add-consumer OBR /v1/orchestrate /v1/analytics/pareto

    # Verify integrity (no parse error, required fields present)
    python scripts/context.py verify

    # Print summary
    python scripts/context.py summary

Exit codes:
    0 — success
    1 — file not found, parse error, or invalid path
    2 — validation failure (missing required field, wrong type)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_CONTEXT_FILE = "project-context.json"

# Top-level keys that must exist in any valid project-context.json
REQUIRED_TOP_LEVEL = [
    "version",
    "locale",
    "project",
    "stack",
    "modules",
    "architecture",
    "setup",
    "agents",
]

# Setup phase IDs that are recognized (others trigger a warning, not an error)
KNOWN_PHASE_IDS = {
    "P0-bootstrap",
    "P1-claude-folder",
    "P2-docs-skeleton",
    "P3-techlab-ai-sync",
    "P4-backend-skeleton",
    "P5-frontend-skeleton",
    "P6-handoff",
}

VALID_PHASE_STATUSES = {"pending", "in-progress", "done", "skipped", "blocked"}


# ── Core I/O ──────────────────────────────────────────────────────────────────


def find_context_file(explicit: Path | None) -> Path:
    """Return the path to project-context.json.

    Priority: explicit arg → cwd → walk up to find it.
    """
    if explicit:
        if not explicit.exists():
            sys.exit(f"error: file not found: {explicit}")
        return explicit

    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / DEFAULT_CONTEXT_FILE
        if candidate.exists():
            return candidate
    sys.exit(
        f"error: {DEFAULT_CONTEXT_FILE} not found in cwd or any parent directory"
    )


def load_context(path: Path) -> dict[str, Any]:
    """Parse the JSON, exit with clear error on parse failure."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"error: {path} is not valid JSON: {e}")


def save_context(path: Path, data: dict[str, Any]) -> None:
    """Atomic write: temp file in same dir, then rename.

    Always updates `lastUpdatedAt` to current UTC.
    """
    data["lastUpdatedAt"] = (
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    # Sanity round-trip before writing.
    serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    json.loads(serialized)  # raises if invalid

    parent = path.parent
    fd, tmp_path = tempfile.mkstemp(
        prefix=".project-context-", suffix=".json.tmp", dir=parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(serialized)
        os.replace(tmp_path, path)
    except Exception:
        # Cleanup orphaned temp on failure.
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


# ── Path navigation (dotted) ─────────────────────────────────────────────────


def get_by_path(data: dict[str, Any], dotted: str) -> Any:
    """Walk a dotted path. Lists support [N] indexing (e.g., modules.registry[0]).

    Raises KeyError with the exact failing segment.
    """
    if not dotted:
        return data
    cursor: Any = data
    segments = _split_dotted(dotted)
    for i, seg in enumerate(segments):
        path_so_far = ".".join(segments[: i + 1])
        if isinstance(cursor, dict):
            if seg not in cursor:
                raise KeyError(f"path {path_so_far!r} does not exist")
            cursor = cursor[seg]
        elif isinstance(cursor, list):
            try:
                idx = int(seg)
            except ValueError as e:
                raise KeyError(
                    f"path {path_so_far!r} expects int index on list, got {seg!r}"
                ) from e
            if idx < 0 or idx >= len(cursor):
                raise KeyError(
                    f"path {path_so_far!r}: index {idx} out of range (len={len(cursor)})"
                )
            cursor = cursor[idx]
        else:
            raise KeyError(
                f"path {path_so_far!r}: cannot descend into scalar"
            )
    return cursor


def set_by_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    """Set a value at a dotted path. Intermediate dicts must already exist."""
    if not dotted:
        raise ValueError("empty path")
    segments = _split_dotted(dotted)
    if not segments:
        raise ValueError("empty path")
    parent_segments, last = segments[:-1], segments[-1]
    parent = get_by_path(data, ".".join(parent_segments)) if parent_segments else data
    if isinstance(parent, dict):
        parent[last] = value
    elif isinstance(parent, list):
        try:
            idx = int(last)
        except ValueError as e:
            raise KeyError(f"cannot set list element with non-int index {last!r}") from e
        parent[idx] = value
    else:
        raise KeyError(f"cannot set on scalar at {'.'.join(parent_segments)!r}")


def _split_dotted(dotted: str) -> list[str]:
    """Split 'a.b[2].c' into ['a', 'b', '2', 'c']."""
    out: list[str] = []
    buf = ""
    i = 0
    while i < len(dotted):
        ch = dotted[i]
        if ch == ".":
            if buf:
                out.append(buf)
                buf = ""
        elif ch == "[":
            if buf:
                out.append(buf)
                buf = ""
            j = dotted.find("]", i)
            if j == -1:
                raise ValueError(f"unmatched '[' in path: {dotted!r}")
            out.append(dotted[i + 1 : j])
            i = j
        else:
            buf += ch
        i += 1
    if buf:
        out.append(buf)
    return out


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_get(args: argparse.Namespace) -> int:
    ctx = load_context(find_context_file(args.file))
    try:
        value = get_by_path(ctx, args.path)
    except KeyError as e:
        sys.exit(f"error: {e}")
    if args.json or isinstance(value, (dict, list)):
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        print(value)
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    path = find_context_file(args.file)
    ctx = load_context(path)

    # Try to parse value as JSON; if it fails, treat as raw string.
    try:
        parsed_value = json.loads(args.value)
    except json.JSONDecodeError:
        parsed_value = args.value

    try:
        set_by_path(ctx, args.path, parsed_value)
    except (KeyError, ValueError) as e:
        sys.exit(f"error: {e}")

    save_context(path, ctx)
    print(f"OK: set {args.path} = {parsed_value!r}")
    return 0


def cmd_append(args: argparse.Namespace) -> int:
    """Append a value to a list at a dotted path."""
    path = find_context_file(args.file)
    ctx = load_context(path)
    try:
        target = get_by_path(ctx, args.path)
    except KeyError as e:
        sys.exit(f"error: {e}")
    if not isinstance(target, list):
        sys.exit(f"error: path {args.path!r} is not a list")
    try:
        parsed = json.loads(args.value)
    except json.JSONDecodeError:
        parsed = args.value
    target.append(parsed)
    save_context(path, ctx)
    print(f"OK: appended to {args.path} (new length: {len(target)})")
    return 0


def cmd_mark_phase(args: argparse.Namespace) -> int:
    """Mark a setup phase as done/in-progress/skipped/blocked/pending."""
    if args.status not in VALID_PHASE_STATUSES:
        sys.exit(
            f"error: invalid status {args.status!r}. "
            f"Valid: {', '.join(sorted(VALID_PHASE_STATUSES))}"
        )
    if args.phase_id not in KNOWN_PHASE_IDS:
        print(
            f"warning: phase id {args.phase_id!r} is not a known setup phase",
            file=sys.stderr,
        )

    path = find_context_file(args.file)
    ctx = load_context(path)
    phases = ctx.get("setup", {}).get("phases", [])
    target = None
    for phase in phases:
        if phase.get("id") == args.phase_id:
            target = phase
            break
    if target is None:
        sys.exit(f"error: phase id {args.phase_id!r} not found in setup.phases")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.status == "in-progress" and target.get("status") == "pending":
        target["startedAt"] = now
    if args.status == "done":
        target["completedAt"] = now
        if "startedAt" not in target:
            target["startedAt"] = now
    target["status"] = args.status

    save_context(path, ctx)
    print(f"OK: marked phase {args.phase_id} as {args.status}")
    return 0


def cmd_techlabai_add_consumer(args: argparse.Namespace) -> int:
    """Add a module to ai.techlabAi.consumedByModules with its endpoint list."""
    path = find_context_file(args.file)
    ctx = load_context(path)

    tlab = ctx.get("ai", {}).get("techlabAi")
    if not tlab:
        sys.exit("error: ai.techlabAi not present in project-context.json")

    consumers = tlab.setdefault("consumedByModules", [])
    # Remove existing entry for the same module if present.
    consumers[:] = [c for c in consumers if c.get("module") != args.module]
    consumers.append({"module": args.module, "endpoints": list(args.endpoints)})

    save_context(path, ctx)
    print(
        f"OK: registered {args.module} as consumer of "
        f"{len(args.endpoints)} TechLab AI endpoint(s)"
    )
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Validate the JSON has all required top-level keys and basic structure."""
    ctx = load_context(find_context_file(args.file))
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in ctx]
    if missing:
        print(f"FAIL: missing required top-level keys: {missing}", file=sys.stderr)
        return 2

    # locale must have technicalDocs = en-US (D-013)
    locale = ctx.get("locale", {})
    if locale.get("technicalDocs") != "en-US":
        print(
            f"FAIL: locale.technicalDocs must be 'en-US' (D-013), got "
            f"{locale.get('technicalDocs')!r}",
            file=sys.stderr,
        )
        return 2

    # If hasAi=true, techlabAi block must exist with required fields
    ai = ctx.get("ai", {})
    if ai.get("hasAi"):
        tlab = ai.get("techlabAi", {})
        for field in ("source", "sourceSha", "syncStrategy", "docsCloneTarget"):
            if field not in tlab:
                print(
                    f"FAIL: ai.hasAi=true but ai.techlabAi.{field} is missing",
                    file=sys.stderr,
                )
                return 2

    print("OK: project-context.json is valid")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    """Print a human-friendly summary of the project context."""
    ctx = load_context(find_context_file(args.file))

    project = ctx.get("project", {})
    stack = ctx.get("stack", {}).get("backend", {})
    ai = ctx.get("ai", {})
    modules = ctx.get("modules", {}).get("registry", [])
    setup_phases = ctx.get("setup", {}).get("phases", [])

    done = sum(1 for p in setup_phases if p.get("status") == "done")
    total = len(setup_phases)

    print(f"Project: {project.get('displayName', '?')} ({project.get('name', '?')})")
    print(f"  Segment: {project.get('segment', '?')}")
    print(f"  Rigor:   {project.get('rigorLevel', '?')}")
    print(f"  Backend: {stack.get('language', '?')} {stack.get('version', '')}")
    print(f"  AI:      {'enabled' if ai.get('hasAi') else 'disabled'}")
    if ai.get("hasAi"):
        tlab = ai.get("techlabAi", {})
        print(f"    TechLab AI SHA: {tlab.get('sourceSha', '?')}")
        print(f"    Sync strategy:  {tlab.get('syncStrategy', '?')}")
    print(f"  Modules: {len(modules)} declared")
    for m in modules:
        print(f"    - {m.get('prefix', '?')}: {m.get('displayName', '?')} ({m.get('status', '?')})")
    print(f"  Setup:   {done}/{total} phases done")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="context.py",
        description="CRUD utility for project-context.json",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help=f"Path to {DEFAULT_CONTEXT_FILE} (default: search from cwd upward)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get", help="Read a value at a dotted path")
    p_get.add_argument("path", help="Dotted path, e.g. project.name or modules.registry[0].prefix")
    p_get.add_argument("--json", action="store_true", help="Force JSON output even for scalars")
    p_get.set_defaults(func=cmd_get)

    p_set = sub.add_parser("set", help="Set a value at a dotted path")
    p_set.add_argument("path")
    p_set.add_argument("value", help="Value (JSON-parsed; falls back to raw string)")
    p_set.set_defaults(func=cmd_set)

    p_append = sub.add_parser("append", help="Append a value to a list at a dotted path")
    p_append.add_argument("path")
    p_append.add_argument("value", help="Value to append (JSON-parsed; falls back to raw string)")
    p_append.set_defaults(func=cmd_append)

    p_phase = sub.add_parser("mark-phase", help="Update a setup phase status")
    p_phase.add_argument("phase_id", help="One of: P0-bootstrap, P1-claude-folder, ...")
    p_phase.add_argument("status", help=f"One of: {', '.join(sorted(VALID_PHASE_STATUSES))}")
    p_phase.set_defaults(func=cmd_mark_phase)

    p_tlab = sub.add_parser(
        "techlabai-add-consumer",
        help="Register a module as consumer of TechLab AI endpoints",
    )
    p_tlab.add_argument("module", help="Module prefix, e.g. OBR")
    p_tlab.add_argument("endpoints", nargs="+", help="Endpoint paths consumed by this module")
    p_tlab.set_defaults(func=cmd_techlabai_add_consumer)

    p_verify = sub.add_parser("verify", help="Validate JSON structure and required fields")
    p_verify.set_defaults(func=cmd_verify)

    p_sum = sub.add_parser("summary", help="Print a human-friendly summary")
    p_sum.set_defaults(func=cmd_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
