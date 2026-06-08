#!/usr/bin/env python3
"""be-check-orphans.py - workspace orphan-files check (D-112, automations A2.5).

Walks the workspace and reports two classes of inconsistency:

  ORPHAN_NARRATIVE  An item under templates/architecture/shared/ doesn't tie
                    back to any aspect (no .arch.json companion) AND isn't
                    declared in the in-script allow-list of prose-only docs.
                    Signal: either add the missing aspect, or update the
                    allow-list to record the item as intentional narrative.

  MISSING_NARRATIVE A formal aspect (decisions/<name>.arch.json) lacks a
                   shared/ narrative entry AND isn't listed as
                   narrative-optional. Signal: write the narrative, or mark
                   the aspect as JSON-only in the allow-list.

The default allow-list mirrors the current workspace so a clean checkout
reports zero issues; the script trips when you add new content without
updating the allow-list. That's the regression signal — the allow-list is
intentional, every change to it goes through code review.

Usage:
    python scripts/be-check-orphans.py                # default workspace walk
    python scripts/be-check-orphans.py --workspace .  # explicit root
    python scripts/be-check-orphans.py --json         # machine-readable
    python scripts/be-check-orphans.py --strict       # exit 1 on warnings too
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cli_utils import force_utf8_stdio


# ── Allow-list (D-112) ───────────────────────────────────────────────────────
#
# Maps each item under templates/architecture/shared/ to the aspect it
# narrates, or None when the item is intentional prose with no
# corresponding decisions/<name>.arch.json.
#
# Keys end with `/` for directories, otherwise treated as files.
SHARED_ALLOW_LIST: dict[str, str | None] = {
    "README.md.j2": None,
    "blueprint-core.md.j2": None,
    "distributed-architecture.md.j2": None,
    "multi-empresa.md.j2": "multi-tenancy",  # D-076 alias
    "rbac/": "rbac",                          # also covers permission-catalogue
    "contratos/": None,                       # narrative
    "etl-legado/": None,                      # narrative
    "modelo-dados/": None,                    # narrative
    "code-mapping/": None,                    # meta-framework drift detection (D-161)
}

# Aspects that legitimately ship without a shared/ narrative — the JSON
# decision is sufficient (consumed directly by code-gen, no prose needed).
ASPECTS_NARRATIVE_OPTIONAL: set[str] = {
    "entity-scope",
    "error-model",
    "events",
    "permission-catalogue",
    "persistence",
}


def _workspace_root(explicit: Path | None) -> Path:
    if explicit:
        return explicit.resolve()
    cur = Path.cwd().resolve()
    for p in [cur, *cur.parents]:
        if (p / "scripts" / "new-project.py").is_file() and (p / "templates").is_dir():
            return p
    sys.exit(
        "error: could not locate workspace root (no scripts/new-project.py "
        "upstream). Pass --workspace explicitly."
    )


def discover_aspects(decisions_dir: Path) -> list[str]:
    """List aspect names from decisions/*.arch.json (excludes _examples/, _schema/)."""
    if not decisions_dir.is_dir():
        return []
    out: list[str] = []
    for p in sorted(decisions_dir.glob("*.arch.json")):
        if p.name.startswith("_"):
            continue
        out.append(p.stem.removesuffix(".arch"))
    return out


def discover_shared_items(shared_dir: Path) -> list[str]:
    """List immediate children of templates/architecture/shared/. Directories
    are reported with a trailing `/` to disambiguate from files of the same
    base name."""
    if not shared_dir.is_dir():
        return []
    out: list[str] = []
    for entry in sorted(shared_dir.iterdir()):
        name = entry.name + ("/" if entry.is_dir() else "")
        out.append(name)
    return out


def analyze(workspace: Path) -> dict:
    """Cross-check aspects ↔ shared/ items and return a structured report."""
    decisions_dir = workspace / "templates" / "architecture" / "decisions"
    shared_dir = workspace / "templates" / "architecture" / "shared"

    aspects = discover_aspects(decisions_dir)
    items = discover_shared_items(shared_dir)

    # Aspects covered by some allow-list mapping (directly or via alias).
    aspects_covered = {
        v for v in SHARED_ALLOW_LIST.values() if v
    }

    orphan_narratives: list[dict] = []
    for item in items:
        if item not in SHARED_ALLOW_LIST:
            orphan_narratives.append({
                "item": item,
                "reason": "not in SHARED_ALLOW_LIST",
                "fix": (
                    f"add {item!r} to SHARED_ALLOW_LIST in "
                    f"scripts/be-check-orphans.py: map to aspect name or None"
                ),
            })

    missing_narratives: list[dict] = []
    for aspect in aspects:
        if aspect in aspects_covered:
            continue
        if aspect in ASPECTS_NARRATIVE_OPTIONAL:
            continue
        missing_narratives.append({
            "aspect": aspect,
            "reason": "no shared/ entry and not in ASPECTS_NARRATIVE_OPTIONAL",
            "fix": (
                f"create templates/architecture/shared/{aspect}/<file>.md.j2 OR "
                f"add {aspect!r} to ASPECTS_NARRATIVE_OPTIONAL"
            ),
        })

    return {
        "workspace": str(workspace),
        "aspects": aspects,
        "shared_items": items,
        "orphan_narratives": orphan_narratives,
        "missing_narratives": missing_narratives,
    }


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-check-orphans.py",
        description=(
            "Report orphan items between templates/architecture/decisions/*.arch.json "
            "and templates/architecture/shared/ (D-112, automations A2.5)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Default exit: 0 when clean.\n"
            "  ORPHAN_NARRATIVE (shared/ item without aspect) -> exit 1\n"
            "  MISSING_NARRATIVE (aspect without narrative)   -> exit 1 in --strict\n"
        ),
    )
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Workspace root (default: walk up from cwd).")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of human-readable text.")
    parser.add_argument("--strict", action="store_true",
                        help="Also fail when there are MISSING_NARRATIVE entries.")
    args = parser.parse_args(argv)

    workspace = _workspace_root(args.workspace)
    report = analyze(workspace)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        n_aspects = len(report["aspects"])
        n_items = len(report["shared_items"])
        n_orphans = len(report["orphan_narratives"])
        n_missing = len(report["missing_narratives"])
        print(f"be-check-orphans — {workspace}")
        print(f"  aspects:        {n_aspects} ({', '.join(report['aspects'])})")
        print(f"  shared/ items:  {n_items}")
        print(f"  orphans:        {n_orphans}")
        print(f"  missing:        {n_missing}")
        print()
        for o in report["orphan_narratives"]:
            print(f"  [ORPHAN_NARRATIVE] {o['item']}")
            print(f"    {o['reason']}")
            print(f"    fix: {o['fix']}")
        for m in report["missing_narratives"]:
            tag = "MISSING_NARRATIVE"
            print(f"  [{tag}] {m['aspect']}")
            print(f"    {m['reason']}")
            print(f"    fix: {m['fix']}")
        if not (report["orphan_narratives"] or report["missing_narratives"]):
            print("  All shared/ items and aspects match allow-list expectations.")

    if report["orphan_narratives"]:
        return 1
    if args.strict and report["missing_narratives"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
