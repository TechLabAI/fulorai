#!/usr/bin/env python3
"""be-architect-drift-check.py — report architecture drift in a generated project.

Reads ``architecture.lock`` at the current project root, recomputes SHA-256 of
each source template (in the workspace) and each rendered output (in the
project), and classifies every aspect into one of four states:

- **synced** — both SHAs match the lock; nothing to do.
- **source_changed** — workspace template evolved since apply. The project
  is behind workspace. Safe to upgrade (output untouched locally).
- **locally_modified** — the project edited the rendered file. Workspace is
  unchanged. Upgrade would not touch this file.
- **drifted** — both differ. Conflict. Requires human review.

Exit codes:
    0 — no drift (everything synced or only locally_modified, which the user
        is presumed to have done intentionally)
    1 — workspace evolved (source_changed or drifted detected); CI-friendly
        signal that ``/be-architect-upgrade`` should be considered
    2 — usage error (lock not found, schema mismatch, workspace not found)

Workspace resolution:
    1. ``--workspace`` flag
    2. ``TECHLAB_ARCH_HOME`` env var
    3. Walk up from cwd looking for ``scripts/new-project.py`` + ``templates/architecture/``

Usage:
    python scripts/be-architect-drift-check.py [--workspace PATH] [--json] [--verbose]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path
from typing import Any

# Resolve sibling imports regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Force UTF-8 stdout for cross-platform safety (Windows cp1252 console chokes
# on non-ASCII characters that may appear in aspect paths or template content).
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from lockfile import (  # noqa: E402
    LOCK_FILENAME,
    classify_aspect,
    read_lock,
    read_workspace_arch_version,
    read_workspace_git_sha,
    read_workspace_tool_version,
)


# ── Workspace + project resolution ───────────────────────────────────────────


def find_workspace(explicit: Path | None) -> Path:
    if explicit:
        if not _is_workspace(explicit):
            sys.exit(f"error: --workspace {explicit} is not a techlab-architecture workspace")
        return explicit.resolve()
    env = os.environ.get("TECHLAB_ARCH_HOME")
    if env:
        p = Path(env)
        if not _is_workspace(p):
            sys.exit(f"error: TECHLAB_ARCH_HOME={env} is not a workspace")
        return p.resolve()
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if _is_workspace(parent):
            return parent.resolve()
    sys.exit(
        "error: could not locate techlab-architecture workspace.\n"
        "  Pass --workspace, set TECHLAB_ARCH_HOME, or run from inside the workspace."
    )


def _is_workspace(p: Path) -> bool:
    return (p / "scripts" / "new-project.py").is_file() and (p / "templates" / "architecture").is_dir()


def find_project_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / LOCK_FILENAME).is_file():
            return p
    sys.exit(f"error: {LOCK_FILENAME} not found in cwd or any parent. Is this a generated project?")


# ── Reporting ────────────────────────────────────────────────────────────────


STATE_GLYPH = {
    "synced": "  OK",
    "source_changed": "  ->",
    "locally_modified": "  *",
    "drifted": "  !!",
    "source_missing": "  ??",
    "output_missing": "  --",
}

STATE_LABEL = {
    "synced": "synced",
    "source_changed": "workspace evolved (safe to upgrade)",
    "locally_modified": "modified locally (workspace unchanged)",
    "drifted": "DRIFTED — workspace evolved AND modified locally",
    "source_missing": "source template no longer in workspace",
    "output_missing": "rendered output deleted from project",
}


def group_by_aspect_area(classifications: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group classifications by their top-level area (first 1-2 path segments)."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for c in classifications:
        # docs/architecture/backend/standards/foo.md -> backend/standards
        # docs/architecture/shared/rbac/foo.md       -> shared/rbac
        parts = c["aspect"].split("/")
        try:
            anchor = parts.index("architecture")
            area_parts = parts[anchor + 1 : anchor + 3]
            area = "/".join(area_parts) if area_parts else "(root)"
        except ValueError:
            area = "/".join(parts[:2])
        grouped.setdefault(area, []).append(c)
    return grouped


def print_report(
    lock: dict[str, Any],
    workspace: Path,
    classifications: list[dict[str, Any]],
    verbose: bool,
) -> int:
    arch_pinned = lock["architecture"]["version"]
    arch_current = read_workspace_arch_version(workspace)
    tool_pinned = lock["techlab_architecture"]["version"]
    tool_current = read_workspace_tool_version(workspace)
    sha_pinned = lock["techlab_architecture"].get("source_sha", "?")
    sha_current = read_workspace_git_sha(workspace) or "?"
    applied = lock["architecture"]["applied_at"]

    counts: dict[str, int] = {}
    for c in classifications:
        counts[c["state"]] = counts.get(c["state"], 0) + 1

    arch_drift = arch_pinned != arch_current
    has_evolution = (counts.get("source_changed", 0) + counts.get("drifted", 0)) > 0

    print("Architecture drift report")
    print(f"  Pinned:  arch {arch_pinned} | tool {tool_pinned} | sha {sha_pinned} | applied {applied}")
    print(f"  Current: arch {arch_current} | tool {tool_current} | sha {sha_current}")
    print()
    if arch_drift:
        print(f"  [drift] architecture version differs ({arch_pinned} -> {arch_current})")
    else:
        print(f"  architecture version: {arch_pinned} (no bump)")
    print()

    grouped = group_by_aspect_area(classifications)
    for area in sorted(grouped):
        items = grouped[area]
        states = sorted({c["state"] for c in items})
        if states == ["synced"] and not verbose:
            print(f"  [ok] {area} ({len(items)} synced)")
            continue
        worst = (
            "drifted" if any(c["state"] == "drifted" for c in items)
            else "source_missing" if any(c["state"] == "source_missing" for c in items)
            else "output_missing" if any(c["state"] == "output_missing" for c in items)
            else "source_changed" if any(c["state"] == "source_changed" for c in items)
            else "locally_modified" if any(c["state"] == "locally_modified" for c in items)
            else "synced"
        )
        glyph = STATE_GLYPH.get(worst, "  ?")
        print(f"  {glyph} {area} — {STATE_LABEL[worst]} ({len(items)} file(s))")
        if worst != "synced" or verbose:
            for c in items:
                if c["state"] == "synced" and not verbose:
                    continue
                tag = STATE_GLYPH.get(c["state"], "  ?").strip()
                rel = c["aspect"].split("/architecture/", 1)[-1] if "/architecture/" in c["aspect"] else c["aspect"]
                print(f"      [{tag}] {rel}")
    print()
    print("Summary:")
    for state in ("synced", "source_changed", "locally_modified", "drifted", "source_missing", "output_missing"):
        n = counts.get(state, 0)
        if n:
            print(f"  {STATE_LABEL[state]:48s} {n}")
    print()
    if has_evolution:
        print("Workspace has evolved. Run /be-architect-upgrade to preview a safe upgrade.")
        return 1
    if arch_drift:
        print("Architecture version differs but no aspect templates changed (likely metadata-only bump).")
        return 1
    print("In sync with workspace.")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-architect-drift-check.py",
        description="Detect architecture drift between a generated project and the workspace.",
        epilog=(
            "Scope: this script runs INSIDE a generated project. It answers "
            "'am I behind the workspace?'.\n"
            "For the workspace-side counterpart ('which of my registered "
            "clients are behind ME?'), use\n"
            "  python scripts/impact_analysis.py --all-aspects\n"
            "which iterates the clients/ registry and reports drift across "
            "every aspect (D-099)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Path to the techlab-architecture workspace.")
    parser.add_argument("--project-root", type=Path, default=None,
                        help="Path to the generated project (default: walk up to find architecture.lock).")
    parser.add_argument("--json", action="store_true",
                        help="Emit classifications as JSON instead of a human report.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show every file, including synced ones.")
    args = parser.parse_args(argv)

    workspace = find_workspace(args.workspace)
    project_root = find_project_root(args.project_root)
    try:
        lock = read_lock(project_root)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"error: {e}")

    classifications = [
        classify_aspect(key, entry, workspace, project_root)
        for key, entry in lock["aspects"].items()
    ]

    if args.json:
        out = {
            "project_root": str(project_root),
            "workspace": str(workspace),
            "pinned": {
                "architecture_version": lock["architecture"]["version"],
                "tool_version": lock["techlab_architecture"]["version"],
                "source_sha": lock["techlab_architecture"].get("source_sha"),
                "applied_at": lock["architecture"]["applied_at"],
            },
            "current": {
                "architecture_version": read_workspace_arch_version(workspace),
                "tool_version": read_workspace_tool_version(workspace),
                "source_sha": read_workspace_git_sha(workspace),
            },
            "aspects": classifications,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        # Exit code still meaningful
        has_evolution = any(c["state"] in ("source_changed", "drifted") for c in classifications)
        return 1 if has_evolution else 0

    return print_report(lock, workspace, classifications, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
