#!/usr/bin/env python3
"""fe-discover-scan.py -- deterministic inventory of existing FE code (D-320).

READ-ONLY. Mirrors what the backend discovery already does: scans
``frontend/libs/<module>/*`` and emits ``<MOD>.inventory.json`` so the
fe-feature-architect-discover agent INTERPRETS the inventory instead of
hand-scanning files. Reuses the shared ``code_inventory.inventory()`` (P1).

Adds two FE-discovery aggregates on top of the raw lib inventory:
    - sharedUsed: which ``@<scope>/shared/*`` libs the module imports;
    - missingTaxonomy: canonical sublibs absent (feature-*/data-access/ui/access).

R3: argparse subcommand, root walk-up, atomic write, OK:/error:, exit 0/1/2.
Exit 2 == frontend/libs not found.

Usage:
    python scripts/fe-discover-scan.py scan --module lead --report
    python scripts/fe-discover-scan.py scan --all --output inv.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

try:
    from cli_utils import force_utf8_stdio
    from code_inventory import inventory
    from issue_state import atomic_write, find_root
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cli_utils import force_utf8_stdio
    from code_inventory import inventory
    from issue_state import atomic_write, find_root


_SHARED_IMPORT = re.compile(r"""from\s+['"](@[\w.-]+/shared/[\w.-]+)['"]""")
_CANONICAL_SUBLIBS = ("data-access", "ui", "access")


def shared_used(module_dir: Path) -> list[str]:
    found: set[str] = set()
    if module_dir.is_dir():
        for f in module_dir.rglob("*.ts"):
            try:
                found.update(_SHARED_IMPORT.findall(f.read_text(encoding="utf-8", errors="replace")))
            except (OSError, UnicodeError):
                continue
    return sorted(found)


def missing_taxonomy(libs: list[dict]) -> list[str]:
    names = {li["name"] for li in libs}
    miss: list[str] = []
    if not any(n.startswith("feature-") for n in names):
        miss.append("nenhuma feature-* lib")
    for canon in _CANONICAL_SUBLIBS:
        if canon not in names:
            miss.append(f"{canon} ausente")
    return miss


def scan_module(root: Path, module: str) -> dict:
    inv = inventory(root, "fe", module)
    libs = inv["libs"]
    flat = {"components": [], "services": [], "facades": [], "routes": []}
    for li in libs:
        for key in flat:
            flat[key].extend(li.get(key, []))
    module_dir = root / "frontend" / "libs" / module
    return {
        "module": module,
        "layer": "fe",
        "libs": libs,
        **{k: sorted(set(v)) for k, v in flat.items()},
        "sharedUsed": shared_used(module_dir),
        "missingTaxonomy": missing_taxonomy(libs),
    }


def cmd_scan(args) -> int:
    root = find_root(args.root)
    libs_root = root / "frontend" / "libs"
    if not libs_root.is_dir():
        print(f"error: frontend/libs nao encontrado em {root}", file=sys.stderr)
        return 2

    if args.all:
        modules = sorted(d.name for d in libs_root.iterdir()
                         if d.is_dir() and d.name not in ("shared",) and not d.name.startswith("."))
        result = {"layer": "fe", "modules": [scan_module(root, m) for m in modules]}
        default_name = "frontend.inventory.json"
    elif args.module:
        result = scan_module(root, args.module)
        default_name = f"{args.module}.inventory.json"
    else:
        print("error: informe --module <MOD> ou --all", file=sys.stderr)
        return 1

    result["computedAt"] = _dt.datetime.now().isoformat(timespec="seconds")
    out_path = Path(args.output) if args.output else \
        root / "docs/architecture/frontend" / default_name
    atomic_write(out_path, json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    if args.report:
        mods = result.get("modules", [result])
        for m in mods:
            print(f"\n{m['module']}: {len(m['libs'])} lib(s) | "
                  f"{len(m['components'])} comp / {len(m['facades'])} facade / {len(m['services'])} svc")
            if m["missingTaxonomy"]:
                print(f"  missingTaxonomy: {', '.join(m['missingTaxonomy'])}")

    print(f"OK: inventory -- {out_path.name}")
    return 0


def main() -> None:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="fe-discover-scan",
        description="Deterministic FE code inventory (D-320). Read-only.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sc = sub.add_parser("scan", help="emit <MOD>.inventory.json")
    sc.add_argument("--module", metavar="MOD")
    sc.add_argument("--all", action="store_true", help="scan every module under frontend/libs")
    sc.add_argument("--root", metavar="PATH")
    sc.add_argument("--output", metavar="PATH")
    sc.add_argument("--report", action="store_true")
    sc.set_defaults(func=cmd_scan)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
