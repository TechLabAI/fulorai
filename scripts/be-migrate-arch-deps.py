#!/usr/bin/env python3
"""be-migrate-arch-deps.py - inject D-100 frontmatter into legacy service-specs (D-109).

Walks `<project>/docs/architecture/backend/services/*/service-spec.md` and,
for each spec that has no YAML frontmatter at the top, inserts a default
block matching the current `service-spec.md.j2` template:

    ---
    service: <directory name>
    module_prefix: <derived from project-context.modules.registry, or "TBD">
    arch_dependencies:
      - rbac: ">=1.0"
      - permission-catalogue: ">=1.0"
      - entity-scope: ">=1.0"
      - multi-tenancy: ">=1.0"
      - error-model: ">=1.0"
      - events: ">=1.0"
      - persistence: ">=1.0"
    ---

Specs that already have a frontmatter block (D-100 onward, or hand-edited)
are left untouched. The script is idempotent — re-running is safe.

Usage:
    python scripts/be-migrate-arch-deps.py            # dry-run report
    python scripts/be-migrate-arch-deps.py --apply    # actually write
    python scripts/be-migrate-arch-deps.py --project-root <path>
    python scripts/be-migrate-arch-deps.py --apply --aspects rbac,events
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cli_utils import force_utf8_stdio
from impact_analysis import (
    _parse_simple_frontmatter,
    find_service_specs,
)


DEFAULT_ASPECTS = [
    "rbac",
    "permission-catalogue",
    "entity-scope",
    "multi-tenancy",
    "error-model",
    "events",
    "persistence",
]


def _find_project_root(start: Path | None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / "project-context.json").is_file():
            return p
    sys.exit(
        "error: project-context.json not found in cwd or any parent.\n"
        "  Pass --project-root explicitly or run from inside a generated project."
    )


def _derive_module_prefix(
    spec_dir: Path, ctx: dict, fallback: str
) -> str:
    """Best-effort guess of the module prefix that owns this service.

    Heuristic (D-109): split the service directory name on '-', take the
    first token; match (case-insensitive) against
    project-context.modules.registry[*].prefix.lower(). Returns the
    registry prefix in its canonical (uppercase) form. Falls back to the
    supplied `fallback` (the spec dir uppercase first token) when no
    match — better than silently writing the wrong prefix.
    """
    head = spec_dir.name.split("-", 1)[0].lower()
    modules = (ctx.get("modules") or {}).get("registry") or []
    for m in modules:
        prefix = (m.get("prefix") or "").lower()
        if prefix and prefix == head:
            return m["prefix"]
    return fallback


def _render_frontmatter(service: str, module_prefix: str,
                        aspects: list[str]) -> str:
    lines = [
        "---",
        f"service: {service}",
        f"module_prefix: {module_prefix}",
        "arch_dependencies:",
    ]
    for aspect in aspects:
        lines.append(f'  - {aspect}: ">=1.0"')
    lines.append("---")
    lines.append("")  # blank line before the existing body
    return "\n".join(lines) + "\n"


def _has_frontmatter(text: str) -> bool:
    return _parse_simple_frontmatter(text) is not None


def migrate_one(spec_path: Path, ctx: dict, aspects: list[str],
                apply: bool) -> dict:
    """Return a dict describing the action taken for one spec."""
    text = spec_path.read_text(encoding="utf-8")
    result: dict = {
        "path": str(spec_path),
        "service_dir": spec_path.parent.name,
        "status": None,
        "module_prefix": None,
    }
    if _has_frontmatter(text):
        result["status"] = "skipped (has frontmatter)"
        return result

    service = spec_path.parent.name
    fallback_prefix = service.split("-", 1)[0].upper() or "TBD"
    module_prefix = _derive_module_prefix(spec_path.parent, ctx, fallback_prefix)
    result["module_prefix"] = module_prefix

    new_block = _render_frontmatter(service, module_prefix, aspects)
    new_text = new_block + text
    if apply:
        spec_path.write_text(new_text, encoding="utf-8")
        result["status"] = "migrated"
    else:
        result["status"] = "would-migrate"
    return result


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-migrate-arch-deps.py",
        description="Inject D-100 arch_dependencies frontmatter into legacy "
                    "service-specs that predate it (D-109).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/be-migrate-arch-deps.py                 # dry-run\n"
            "  python scripts/be-migrate-arch-deps.py --apply         # write\n"
            "  python scripts/be-migrate-arch-deps.py --aspects rbac,events --apply\n"
        ),
    )
    parser.add_argument(
        "--project-root", type=Path, default=None,
        help="Path to the generated project (default: walk up to find "
             "project-context.json).",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually write the migrated frontmatter. Default is dry-run.",
    )
    parser.add_argument(
        "--aspects", default=None,
        help="Comma-separated subset of aspects to declare in arch_dependencies. "
             "Default lists all 7 Tier 2.1 aspects.",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit JSON instead of human-readable text.",
    )
    args = parser.parse_args(argv)

    project_root = _find_project_root(args.project_root)
    ctx_path = project_root / "project-context.json"
    try:
        ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        sys.exit(f"error: cannot read project-context.json: {e}")

    aspects = (
        [a.strip() for a in args.aspects.split(",") if a.strip()]
        if args.aspects else DEFAULT_ASPECTS
    )
    if not aspects:
        sys.exit("error: --aspects resolved to an empty list")

    specs = find_service_specs(project_root)
    reports = [migrate_one(p, ctx, aspects, args.apply) for p in specs]

    if args.json:
        print(json.dumps({
            "project_root": str(project_root),
            "apply": args.apply,
            "aspects": aspects,
            "specs": reports,
        }, indent=2))
        return 0

    n_specs = len(reports)
    n_migrated = sum(1 for r in reports if r["status"] in ("migrated", "would-migrate"))
    n_skipped = n_specs - n_migrated
    header = "APPLYING" if args.apply else "DRY-RUN"
    print(f"be-migrate-arch-deps.py [{header}]")
    print(f"  project_root: {project_root}")
    print(f"  service-specs: {n_specs}")
    print(f"  to migrate:   {n_migrated}")
    print(f"  already have frontmatter (skipped): {n_skipped}")
    print(f"  aspects to declare: {', '.join(aspects)}")
    print()
    for r in reports:
        tag = r["status"]
        print(f"  [{tag}]")
        print(f"    {r['path']}")
        if r["module_prefix"]:
            print(f"    module_prefix={r['module_prefix']}")
    if not args.apply and n_migrated > 0:
        print()
        print(f"Re-run with --apply to write the frontmatter for {n_migrated} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
