#!/usr/bin/env python3
"""impact_analysis.py - Tier 2.3 MVP: which clients are impacted by an aspect change? (D-096)

Reads the workspace's ``clients/<id>.json`` registry, locates each
client's ``architecture.lock``, and reports which entries reference the
given aspect plus whether the pinned source SHA still matches the
workspace's current SHA.

Usage:

    python scripts/impact_analysis.py --aspect rbac
    python scripts/impact_analysis.py --aspect persistence --clients-dir clients/
    python scripts/impact_analysis.py --aspect events --json

Exit codes:
  0 - analysis ran (regardless of whether any client is drifted)
  1 - usage error or registry/lock unreadable
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from cli_utils import force_utf8_stdio
from lockfile import (
    LOCK_FILENAME,
    sha256_of_file,
    _recompute_composite_source_sha,
    _recompute_aggregate_source_sha,
)


def _find_workspace_root(start: Path) -> Path:
    """Walk up until we find the workspace marker."""
    cur = start.resolve()
    while cur != cur.parent:
        if (cur / "scripts" / "new-project.py").exists() and (cur / "templates").is_dir():
            return cur
        cur = cur.parent
    sys.exit("error: could not locate workspace root (no scripts/new-project.py upstream)")


def _load_clients(clients_dir: Path) -> list[dict]:
    """Load every <id>.json from clients_dir. Skip README.md and dotfiles."""
    if not clients_dir.is_dir():
        sys.exit(f"error: clients directory not found: {clients_dir}")
    out: list[dict] = []
    for p in sorted(clients_dir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"warning: skipping {p.name} (invalid JSON: {e})", file=sys.stderr)
            continue
        data["_registry_file"] = p.name
        out.append(data)
    return out


def _resolve_project_path(workspace: Path, client: dict) -> Path | None:
    raw = client.get("project_path")
    if not raw:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = (workspace / raw).resolve()
    return p if p.exists() else None


_VERSION_RE = re.compile(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?$")
_CONSTRAINT_RE = re.compile(r"^(>=|<=|>|<|=)?\s*(\d+(?:\.\d+){0,2})$")


def parse_version(text: str) -> tuple[int, int, int] | None:
    """Parse a 'X', 'X.Y', or 'X.Y.Z' string into a 3-tuple (D-105).

    Missing minor/patch default to 0. Returns None when the string doesn't
    match. ``v`` or ``V`` prefix is not accepted — keep the surface narrow
    until something concrete needs it.
    """
    if not isinstance(text, str):
        return None
    m = _VERSION_RE.match(text.strip())
    if not m:
        return None
    return (
        int(m.group(1)),
        int(m.group(2) or 0),
        int(m.group(3) or 0),
    )


def _expand_caret(base: tuple[int, int, int]) -> list[tuple[str, tuple[int, int, int]]]:
    """npm-style ^X.Y.Z (D-106). For X>0 allows minor+patch within same major.
    For X=0 the *minor* becomes the breaking axis (^0.2.3 -> >=0.2.3,<0.3.0)."""
    if base[0] > 0:
        upper = (base[0] + 1, 0, 0)
    else:
        upper = (0, base[1] + 1, 0)
    return [(">=", base), ("<", upper)]


def _expand_tilde(base: tuple[int, int, int]) -> list[tuple[str, tuple[int, int, int]]]:
    """npm-style ~X.Y.Z (D-106): allows patch updates within same minor."""
    return [(">=", base), ("<", (base[0], base[1] + 1, 0))]


def parse_constraint(
    text: str,
) -> list[list[tuple[str, tuple[int, int, int]]]] | None:
    """Parse a constraint string into a list of OR alternatives, each being a
    list of AND clauses ``(op, version_tuple)`` (D-105, D-106).

    Supported syntax:
      >=, <=, >, <, =                 explicit op
      ^X[.Y[.Z]]                      caret (npm-style; ^0.x special-cases minor)
      ~X[.Y[.Z]]                      tilde (npm-style; patch updates within minor)
      ,                               AND between clauses
      ||                              OR between alternatives

    Returns:
      [[(op, version), ...], ...]     each inner list is an AND group; any
                                      matching group satisfies the constraint
      []                              no constraint (None / empty input)
      None                            parse failure on at least one clause
    """
    if not text:
        return []
    alternatives: list[list[tuple[str, tuple[int, int, int]]]] = []
    for or_branch in text.split("||"):
        and_clauses: list[tuple[str, tuple[int, int, int]]] = []
        for raw in or_branch.split(","):
            clause = raw.strip()
            if not clause:
                continue
            if clause.startswith("^"):
                base = parse_version(clause[1:].strip())
                if base is None:
                    return None
                and_clauses.extend(_expand_caret(base))
                continue
            if clause.startswith("~"):
                base = parse_version(clause[1:].strip())
                if base is None:
                    return None
                and_clauses.extend(_expand_tilde(base))
                continue
            m = _CONSTRAINT_RE.match(clause)
            if not m:
                return None
            op = m.group(1) or "="
            version = parse_version(m.group(2))
            if version is None:
                return None
            and_clauses.append((op, version))
        # An OR branch with zero clauses (e.g. "rbac: '|| >=1.0'") is meaningless;
        # skip rather than count as a wildcard match.
        if and_clauses:
            alternatives.append(and_clauses)
    return alternatives


def _and_satisfies(
    version: tuple[int, int, int],
    clauses: list[tuple[str, tuple[int, int, int]]],
) -> bool:
    for op, target in clauses:
        if op == ">=" and not (version >= target):
            return False
        if op == "<=" and not (version <= target):
            return False
        if op == ">" and not (version > target):
            return False
        if op == "<" and not (version < target):
            return False
        if op == "=" and version != target:
            return False
    return True


def satisfies(
    version: tuple[int, int, int],
    constraints: list[list[tuple[str, tuple[int, int, int]]]] | None,
) -> bool:
    """True iff ``version`` matches any OR alternative of ``constraints``.

    Empty list = no constraint declared = always satisfied.
    None       = parse failure                 = unsatisfied (safe default).
    """
    if constraints is None:
        return False
    if not constraints:
        return True
    return any(_and_satisfies(version, alt) for alt in constraints)


def _parse_simple_frontmatter(text: str) -> dict | None:
    """Parse a minimal YAML-like frontmatter block at the top of `text`.

    Supports two shapes only (no nested dicts, no flow syntax):
        key: scalar
        key:
          - item
          - item

    Returns the parsed dict, or None when the file has no ``---`` block at
    the very top. Lines we can't classify are silently skipped — this is a
    diagnostic helper, not a strict YAML implementation.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None

    out: dict = {}
    current_list_key: str | None = None
    for raw in lines[1:end]:
        stripped = raw.rstrip()
        if not stripped:
            current_list_key = None
            continue
        if stripped.startswith("  - ") and current_list_key:
            out[current_list_key].append(stripped[4:].strip())
            continue
        if stripped.startswith("- ") and current_list_key:
            out[current_list_key].append(stripped[2:].strip())
            continue
        if ":" not in stripped:
            current_list_key = None
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if not value:
            out[key] = []
            current_list_key = key
        else:
            out[key] = value
            current_list_key = None
    return out


def _split_dep_constraint(raw: str) -> tuple[str, str | None]:
    """Split a frontmatter list item into ``(aspect, constraint)``.

    Accepts both shapes:
        "rbac"                  -> ("rbac", None)
        "rbac: '>=1.0'"         -> ("rbac", ">=1.0")
        "rbac: \">=1.0, <2.0\"" -> ("rbac", ">=1.0, <2.0")
    The constraint is returned trimmed of surrounding quotes/whitespace
    so callers can hand it straight to ``parse_constraint`` (D-105).
    """
    if ":" not in raw:
        return raw.strip(), None
    aspect, _, constraint = raw.partition(":")
    aspect = aspect.strip()
    constraint = constraint.strip().strip("'\"").strip()
    return aspect, constraint or None


def parse_service_arch_deps(spec_path: Path) -> dict | None:
    """Return the parsed arch_dependencies metadata for a service-spec.md.

    Output shape (D-100 + D-105):
        {
          "service": "<service-name>",
          "module_prefix": "<PREFIX>",
          "arch_dependencies": [
            {"aspect": "rbac",        "constraint": ">=1.0"},
            {"aspect": "persistence", "constraint": None},
            ...
          ],
        }
    None when the file is missing or has no parseable frontmatter.
    The list shape replaces D-100's flat list of aspect names — the new
    dict-per-item form is backward-compatible since every legacy bare-name
    entry now becomes ``{"aspect": <name>, "constraint": None}``.
    """
    if not spec_path.is_file():
        return None
    try:
        text = spec_path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm = _parse_simple_frontmatter(text)
    if fm is None:
        return None
    raw_deps = fm.get("arch_dependencies") or []
    deps: list[dict] = []
    if isinstance(raw_deps, list):
        for item in raw_deps:
            if not isinstance(item, str):
                continue
            aspect, constraint = _split_dep_constraint(item)
            if aspect:
                deps.append({"aspect": aspect, "constraint": constraint})
    return {
        "service": fm.get("service"),
        "module_prefix": fm.get("module_prefix"),
        "arch_dependencies": deps,
    }


def find_service_specs(project_root: Path) -> list[Path]:
    """Locate every ``docs/architecture/backend/services/*/service-spec.md``.

    Empty when the project hasn't scaffolded any service yet.
    """
    services_dir = project_root / "docs" / "architecture" / "backend" / "services"
    if not services_dir.is_dir():
        return []
    return sorted(services_dir.glob("*/service-spec.md"))


def _aspect_matches(aspect: str, source: str) -> bool:
    """Return True when a lock entry's ``source`` path references this aspect.

    Handles three cases:
      - formal decision file:   ``templates/architecture/decisions/<aspect>.arch.json``
      - derived shared doc:     ``templates/architecture/shared/<aspect>/*``
      - composite source (D-077): contains ``decisions/<aspect>.arch.json``
    """
    if not source:
        return False
    decisions_marker = f"decisions/{aspect}.arch.json"
    if decisions_marker in source:
        return True
    if f"/shared/{aspect}/" in source or source.startswith(f"templates/architecture/shared/{aspect}/"):
        return True
    return False


def _current_workspace_sha(
    workspace: Path,
    source_path: str,
    project_root: Path | None = None,
    entry: dict | None = None,
) -> str | None:
    """Recompute the SHA we want to compare against the lock's pinned
    ``source_sha`` for one entry. D-108 extends D-096 with two new cases.

    Composite sources (D-077, ``"a + b"``) — when ``project_root`` and
    ``entry`` are both supplied, delegate to
    ``lockfile._recompute_composite_source_sha`` which re-applies the same
    deep-merge logic that produced the snapshot. Without those args we
    fall back to the D-096 behaviour (return None → caller flags
    ``composite``).

    Aggregate sources (D-072 constitution, ``"aggregate(arch/decisions/*.arch.json)"``)
    — when ``project_root`` is supplied, delegate to
    ``_recompute_aggregate_source_sha``.

    Simple sources stay one ``sha256_of_file`` of the workspace template.
    """
    if " + " in source_path:
        if project_root is not None and entry is not None:
            try:
                return _recompute_composite_source_sha(entry, workspace, project_root)
            except (OSError, ValueError, KeyError):
                return None
        return None
    if source_path.startswith("aggregate(") and source_path.endswith(")"):
        if project_root is None:
            return None
        try:
            return _recompute_aggregate_source_sha({}, project_root)
        except (OSError, ValueError):
            return None
    abs_path = (workspace / source_path).resolve()
    if not abs_path.is_file():
        return None
    return sha256_of_file(abs_path)


def _analyze_client(workspace: Path, client: dict, aspect: str) -> dict:
    """Return a structured per-client report."""
    proj = _resolve_project_path(workspace, client)
    report: dict = {
        "project": client.get("project", client.get("_registry_file")),
        "registry_file": client.get("_registry_file"),
        "project_path": str(proj) if proj else client.get("project_path"),
        "status": "ok",
        "arch_version": None,
        "applied_at": None,
        "entries": [],
        "summary": {"matched": 0, "drifted": 0, "synced": 0, "composite": 0, "missing": 0},
    }
    if proj is None:
        report["status"] = "project_path_missing"
        return report

    lock_path = proj / LOCK_FILENAME
    if not lock_path.is_file():
        report["status"] = "no_lock"
        return report

    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        report["status"] = f"lock_unreadable: {e}"
        return report

    arch_info = lock.get("architecture") or {}
    report["arch_version"] = arch_info.get("version")
    report["applied_at"] = arch_info.get("applied_at")

    for output_path, entry in (lock.get("aspects") or {}).items():
        source = entry.get("source", "")
        if not _aspect_matches(aspect, source):
            continue
        pinned = entry.get("source_sha", "")
        current = _current_workspace_sha(workspace, source, proj, entry)
        if current is None:
            state = "composite" if " + " in source else "missing"
        elif current == pinned:
            state = "synced"
        else:
            state = "drifted"
        report["entries"].append({
            "output": output_path,
            "source": source,
            "pinned_sha": pinned,
            "current_sha": current,
            "state": state,
        })
        report["summary"]["matched"] += 1
        report["summary"][state] += 1

    # D-100 + D-105: collect every service-spec under this project that
    # declares the aspect as a dependency. For each match, evaluate the
    # version constraint (if any) against the pinned aspect version in
    # this project AND the current workspace aspect version. The result
    # shapes whether the service is at-risk under the current snapshot or
    # only after a hypothetical upgrade.
    workspace_aspect_version = _aspect_version_from_file(
        workspace / "templates" / "architecture" / "decisions" / f"{aspect}.arch.json"
    )
    pinned_aspect_version = _aspect_version_from_file(
        proj / "arch" / "decisions" / f"{aspect}.arch.json"
    )

    services_affected: list[str] = []
    service_details: list[dict] = []
    for spec_path in find_service_specs(proj):
        deps = parse_service_arch_deps(spec_path)
        if not deps:
            continue
        match = next(
            (d for d in deps.get("arch_dependencies", [])
             if d.get("aspect") == aspect),
            None,
        )
        if match is None:
            continue
        name = deps.get("service") or spec_path.parent.name
        services_affected.append(name)
        constraint_raw = match.get("constraint")
        clauses = parse_constraint(constraint_raw) if constraint_raw else []
        detail = {
            "service": name,
            "constraint": constraint_raw,
            "constraint_parsed": clauses is not None,
            "pinned_version": _fmt_version(pinned_aspect_version),
            "workspace_version": _fmt_version(workspace_aspect_version),
            "satisfies_pinned": (
                satisfies(pinned_aspect_version, clauses)
                if pinned_aspect_version is not None else None
            ),
            "satisfies_workspace": (
                satisfies(workspace_aspect_version, clauses)
                if workspace_aspect_version is not None else None
            ),
        }
        service_details.append(detail)

    report["services_affected"] = sorted(set(services_affected))
    report["service_details"] = service_details

    # D-107: surface "stale frontmatter" signal. When the aspect HAS lock
    # entries (the project uses this aspect) AND the project HAS
    # service-specs AND none of them declares this aspect as a dependency,
    # the most likely cause is legacy specs predating D-100 — the impact
    # report under-reports the actual surface. Emit a per-aspect warning.
    warnings: list[str] = []
    if report["summary"]["matched"] > 0 and not services_affected:
        spec_paths = find_service_specs(proj)
        if spec_paths:
            n_total = len(spec_paths)
            n_with_fm = sum(
                1 for p in spec_paths if parse_service_arch_deps(p) is not None
            )
            warnings.append(
                f"aspect {aspect!r} has {report['summary']['matched']} lock "
                f"entr{'y' if report['summary']['matched'] == 1 else 'ies'} "
                f"but 0 of {n_total} service-spec(s) declare it as "
                f"arch_dependency ({n_with_fm} have frontmatter at all) — "
                f"add the dependency or run the auto-migration script"
            )
    report["warnings"] = warnings

    return report


def _aspect_version_from_file(path: Path) -> tuple[int, int, int] | None:
    """Read ``version`` from an aspect JSON file (D-105). Returns None when
    the file is missing/unreadable or the version isn't parseable."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    raw = data.get("version")
    return parse_version(raw) if isinstance(raw, str) else None


def _fmt_version(v: tuple[int, int, int] | None) -> str | None:
    return None if v is None else f"{v[0]}.{v[1]}.{v[2]}"


def _print_human(reports: list[dict], aspect: str) -> None:
    print(f"Impact analysis for aspect: {aspect}")
    print(f"Clients registered: {len(reports)}")
    print()
    if not reports:
        print("  (no clients in registry)")
        return
    for r in reports:
        print(f"--- {r['project']} ({r['registry_file']}) ---")
        if r["status"] != "ok":
            print(f"  status: {r['status']}")
            print()
            continue
        print(f"  project_path: {r['project_path']}")
        print(f"  arch version: {r['arch_version']}  applied: {r['applied_at']}")
        s = r["summary"]
        if not r["entries"]:
            print(f"  matched: 0   (aspect {aspect!r} not used in this client)")
            print()
            continue
        print(f"  matched: {s['matched']}  drifted: {s['drifted']}  "
              f"synced: {s['synced']}  composite: {s['composite']}  missing: {s['missing']}")
        services = r.get("services_affected") or []
        if services:
            print(f"  services declaring {aspect!r} as arch_dependency: "
                  f"{', '.join(services)}")
        for w in r.get("warnings") or []:
            print(f"  [WARN] {w}")
        # D-105: surface constraint violations on the same line as the
        # service that owns the contract so a scan reveals at-risk services.
        for detail in r.get("service_details") or []:
            if not detail.get("constraint"):
                continue
            sp = detail.get("satisfies_pinned")
            sw = detail.get("satisfies_workspace")
            if sp is False or sw is False:
                pinned = detail["pinned_version"] or "n/a"
                ws = detail["workspace_version"] or "n/a"
                tag = "PIN-VIOL" if sp is False else "WS-VIOL"
                print(f"    [{tag:8s}] {detail['service']} requires "
                      f"{detail['constraint']!r} — pinned={pinned} workspace={ws}")
        for e in r["entries"]:
            tag = e["state"].upper()
            pinned = (e["pinned_sha"] or "")[:10]
            current = (e["current_sha"] or "")[:10] if e["current_sha"] else "n/a"
            print(f"    [{tag:9s}] {e['output']}")
            print(f"               source={e['source']}")
            print(f"               pinned={pinned}  current={current}")
        print()


def discover_aspects(workspace: Path) -> list[str]:
    """List the aspect names backed by ``templates/architecture/decisions/*.arch.json``.

    Excludes schema files (under ``_schema/``) and any name starting with
    underscore. Returns sorted basenames without the ``.arch.json`` suffix.
    """
    decisions = workspace / "templates" / "architecture" / "decisions"
    if not decisions.is_dir():
        return []
    out: list[str] = []
    for p in sorted(decisions.glob("*.arch.json")):
        if p.name.startswith("_"):
            continue
        out.append(p.stem.removesuffix(".arch"))
    return out


def analyze_all_aspects(
    workspace: Path, clients_dir: Path
) -> list[dict]:
    """D-099: pivot per-aspect reports into a per-client view.

    Returns a list shaped:

        [
          {
            "project": "fake-bosq",
            "registry_file": "fake-bosq.json",
            "status": "ok",
            "arch_version": "1.0.0",
            "applied_at": "...",
            "aspects": [
              {"aspect": "rbac", "summary": {...}, "entries": [...]},
              {"aspect": "persistence", ...},
              ...
            ],
            "rollup": {"matched": N, "drifted": K, "synced": ...},
          },
          ...
        ]
    """
    aspects = discover_aspects(workspace)
    clients = _load_clients(clients_dir)
    out: list[dict] = []
    for client in clients:
        per_aspect: list[dict] = []
        rollup = {"matched": 0, "drifted": 0, "synced": 0, "composite": 0, "missing": 0}
        ok_status: str | None = None
        arch_version: str | None = None
        applied_at: str | None = None
        registry_file = client.get("_registry_file")
        for aspect in aspects:
            report = _analyze_client(workspace, client, aspect)
            if ok_status is None:
                ok_status = report["status"]
                arch_version = report["arch_version"]
                applied_at = report["applied_at"]
            per_aspect.append({
                "aspect": aspect,
                "summary": report["summary"],
                "entries": report["entries"],
                "services_affected": report.get("services_affected", []),
                "service_details": report.get("service_details", []),
                "warnings": report.get("warnings", []),
            })
            for k, v in report["summary"].items():
                rollup[k] += v
        out.append({
            "project": client.get("project", registry_file),
            "registry_file": registry_file,
            "status": ok_status or "ok",
            "arch_version": arch_version,
            "applied_at": applied_at,
            "aspects": per_aspect,
            "rollup": rollup,
        })
    return out


def _print_all_aspects(reports: list[dict]) -> None:
    """Human-readable layout for --all-aspects."""
    print("Workspace-wide impact analysis (all aspects)")
    print(f"Clients registered: {len(reports)}")
    print()
    if not reports:
        print("  (no clients in registry)")
        return
    for r in reports:
        print(f"--- {r['project']} ({r['registry_file']}) ---")
        if r["status"] != "ok":
            print(f"  status: {r['status']}")
            print()
            continue
        print(f"  arch version: {r['arch_version']}  applied: {r['applied_at']}")
        ro = r["rollup"]
        print(f"  rollup: matched={ro['matched']}  drifted={ro['drifted']}  "
              f"synced={ro['synced']}  composite={ro['composite']}  missing={ro['missing']}")
        # Only show aspects with any matches; suppress noise for aspects this
        # client never used.
        any_matched = False
        for a in r["aspects"]:
            if a["summary"]["matched"] == 0:
                continue
            any_matched = True
            s = a["summary"]
            tag = "DRIFT" if s["drifted"] > 0 else "OK"
            print(f"    [{tag:5s}] {a['aspect']:18s} "
                  f"matched={s['matched']}  drifted={s['drifted']}  "
                  f"synced={s['synced']}  composite={s['composite']}  missing={s['missing']}")
            services = a.get("services_affected") or []
            if services:
                print(f"             services: {', '.join(services)}")
            for w in a.get("warnings") or []:
                print(f"             [WARN] {w}")
        if not any_matched:
            print("    (no aspect from the workspace registry is pinned in this client)")
        print()


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="impact_analysis.py",
        description=(
            "Workspace-side impact analysis: which registered clients are "
            "affected by aspect changes? (D-096, D-099)"
        ),
        epilog=(
            "Usage modes:\n"
            "  --aspect <name>          single-aspect detail report\n"
            "  --all-aspects            rollup across every aspect discovered\n"
            "                           in templates/architecture/decisions/\n"
            "\n"
            "Note: this is the workspace-side complement to "
            "scripts/be-architect-drift-check.py (which runs inside a project)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--aspect", default=None,
                      help="Aspect name (e.g. rbac, persistence, events).")
    mode.add_argument("--all-aspects", action="store_true",
                      help="Scan every aspect in templates/architecture/decisions/ "
                           "and emit a per-client rollup (D-099).")
    parser.add_argument("--clients-dir", type=Path, default=None,
                        help="Directory with <id>.json registry files (default: <workspace>/clients/).")
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Workspace root (default: walk up from cwd).")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of human-readable text.")
    parser.add_argument("--fail-on-drift", action="store_true",
                        help="Exit 1 when any registered client has at least one "
                             "drifted entry for the analyzed aspect(s). Default "
                             "exit 0 — the script is informational unless this "
                             "flag is set (D-110).")
    args = parser.parse_args(argv)

    workspace = (args.workspace or _find_workspace_root(Path.cwd())).resolve()
    clients_dir = (args.clients_dir or (workspace / "clients")).resolve()

    if args.all_aspects:
        reports = analyze_all_aspects(workspace, clients_dir)
        if args.json:
            print(json.dumps({"mode": "all-aspects", "clients": reports}, indent=2))
        else:
            _print_all_aspects(reports)
        if args.fail_on_drift:
            drifted = sum(
                (r.get("rollup") or {}).get("drifted", 0) for r in reports
            )
            if drifted > 0:
                print(f"\nFAIL: {drifted} drifted entr"
                      f"{'y' if drifted == 1 else 'ies'} across registered clients "
                      f"(--fail-on-drift).", file=sys.stderr)
                return 1
        return 0

    aspect_file = workspace / "templates" / "architecture" / "decisions" / f"{args.aspect}.arch.json"
    if not aspect_file.is_file():
        print(
            f"warning: no aspect file at {aspect_file.relative_to(workspace)} "
            f"— analysis will still run (matches by source path), but the "
            f"aspect name may be wrong",
            file=sys.stderr,
        )

    clients = _load_clients(clients_dir)
    reports = [_analyze_client(workspace, c, args.aspect) for c in clients]

    if args.json:
        print(json.dumps({"aspect": args.aspect, "clients": reports}, indent=2))
    else:
        _print_human(reports, args.aspect)
    if args.fail_on_drift:
        drifted = sum(
            (r.get("summary") or {}).get("drifted", 0) for r in reports
        )
        if drifted > 0:
            print(f"\nFAIL: {drifted} drifted entr"
                  f"{'y' if drifted == 1 else 'ies'} for aspect {args.aspect!r} "
                  f"across registered clients (--fail-on-drift).", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
