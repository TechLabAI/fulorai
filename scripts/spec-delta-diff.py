#!/usr/bin/env python3
"""spec-delta-diff.py -- diff existing code inventory x module SPEC (D-321).

READ-ONLY. Consumes the FE inventory (D-320) + the module SPECs and emits
``<MOD>.spec-delta.json`` so the fe-feature-architect-spec-delta agent CURATES
a precomputed delta instead of hand-comparing. Depends on D-320 (or recomputes
the inventory via the shared ``code_inventory``).

Deterministic comparison of typed identifiers (PascalCase Component/Facade/
Service) + route paths between SPEC-02/04/route-map and the code:
    - specRequiresMissing: in SPEC, absent in code;
    - codeHasUnspecced:    in code, absent in SPEC;
    - routeMismatch:       routes present on one side only.

R3: argparse subcommand, root walk-up, atomic write, OK:/error:, exit 0/1/2.
Exit 2 == no SPEC dir resolved.

Usage:
    python scripts/spec-delta-diff.py diff --module lead --report
    python scripts/spec-delta-diff.py diff --module lead --inventory lead.inventory.json
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


_COMPONENT = re.compile(r"\b([A-Z]\w+Component)\b")
_FACADE = re.compile(r"\b([A-Z]\w+Facade)\b")
_SERVICE = re.compile(r"\b([A-Z]\w+Service)\b")
_ROUTE = re.compile(r"(?<![\w.])/[a-z][\w-]*(?:/:?[\w-]+)*")


# ── SPEC side ──────────────────────────────────────────────────────────────────

def resolve_spec_dir(root: Path, module: str, explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.is_dir() else None
    for c in (root / "docs/architecture/frontend/modules" / module / "frontend" / "frontend-spec",
              root / "docs/architecture/frontend/libs" / module):
        if c.is_dir():
            return c
    return None


def extract_spec(spec_dir: Path) -> dict:
    comps: set[str] = set()
    facades: set[str] = set()
    services: set[str] = set()
    routes: set[str] = set()
    for f in sorted(spec_dir.glob("SPEC-*.md")) or sorted(spec_dir.glob("*.md")):
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeError):
            continue
        comps.update(_COMPONENT.findall(txt))
        facades.update(_FACADE.findall(txt))
        services.update(_SERVICE.findall(txt))
        # routes only from route-map-ish files to limit false positives
        low = f.name.lower()
        if "route" in low or "01" in low:
            routes.update(_ROUTE.findall(txt))
    return {"components": comps, "facades": facades, "services": services, "routes": routes}


# ── Code side ──────────────────────────────────────────────────────────────────

def load_code_sets(root: Path, module: str, inventory_path: str | None) -> dict:
    if inventory_path:
        data = json.loads(Path(inventory_path).read_text(encoding="utf-8"))
    else:
        inv = inventory(root, "fe", module)
        data = {"components": [], "facades": [], "services": [], "routes": []}
        for li in inv["libs"]:
            for key in data:
                data[key].extend(li.get(key, []))
    return {k: set(data.get(k, [])) for k in ("components", "facades", "services", "routes")}


# ── Diff ───────────────────────────────────────────────────────────────────────

def diff_sets(spec: dict, code: dict) -> dict:
    requires_missing: list[dict] = []
    has_unspecced: list[dict] = []
    matched = 0
    for kind in ("components", "facades", "services"):
        sp, cd = spec[kind], code[kind]
        for name in sorted(sp - cd):
            requires_missing.append({"kind": kind[:-1], "name": name})
        for name in sorted(cd - sp):
            has_unspecced.append({"kind": kind[:-1], "name": name})
        matched += len(sp & cd)
    route_mismatch = (
        [{"route": r, "side": "spec-only"} for r in sorted(spec["routes"] - code["routes"])]
        + [{"route": r, "side": "code-only"} for r in sorted(code["routes"] - spec["routes"])]
    )
    return {
        "specRequiresMissing": requires_missing,
        "codeHasUnspecced": has_unspecced,
        "routeMismatch": route_mismatch,
        "summary": {
            "missing": len(requires_missing),
            "unspecced": len(has_unspecced),
            "matched": matched,
            "routeMismatch": len(route_mismatch),
        },
    }


def cmd_diff(args) -> int:
    root = find_root(args.root)
    spec_dir = resolve_spec_dir(root, args.module, args.spec_dir)
    if spec_dir is None:
        print(f"error: SPEC dir nao encontrado para {args.module} (use --spec-dir)", file=sys.stderr)
        return 2

    spec = extract_spec(spec_dir)
    code = load_code_sets(root, args.module, args.inventory)
    result = {
        "module": args.module,
        "layer": args.layer,
        "computedAt": _dt.datetime.now().isoformat(timespec="seconds"),
        "specDir": str(spec_dir.relative_to(root)) if spec_dir.is_relative_to(root) else str(spec_dir),
        **diff_sets(spec, code),
    }

    out_path = Path(args.output) if args.output else \
        root / "docs/architecture/frontend" / f"{args.module}.spec-delta.json"
    atomic_write(out_path, json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    if args.report:
        s = result["summary"]
        print(f"\n{args.module}: {s['matched']} matched | {s['missing']} faltam (spec) | "
              f"{s['unspecced']} fora-da-spec | {s['routeMismatch']} rotas divergentes")
        for it in result["specRequiresMissing"][:10]:
            print(f"  - SPEC pede, falta: {it['kind']} {it['name']}")

    print(f"OK: spec-delta -- {out_path.name} "
          f"[missing={result['summary']['missing']} unspecced={result['summary']['unspecced']}]")
    return 0


def main() -> None:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="spec-delta-diff",
        description="Diff code inventory x module SPEC (D-321). Read-only.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("diff", help="emit <MOD>.spec-delta.json")
    d.add_argument("--module", required=True, metavar="MOD")
    d.add_argument("--layer", choices=["fe", "be"], default="fe")
    d.add_argument("--inventory", metavar="PATH", help="<MOD>.inventory.json (default: recompute)")
    d.add_argument("--spec-dir", metavar="PATH", help="override SPEC dir resolution")
    d.add_argument("--root", metavar="PATH")
    d.add_argument("--output", metavar="PATH")
    d.add_argument("--report", action="store_true")
    d.set_defaults(func=cmd_diff)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
