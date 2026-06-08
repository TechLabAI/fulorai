#!/usr/bin/env python3
"""be-arch-bump.py - suggest a semver bump for an architecture aspect (D-116, automations B3).

Compares two versions of a `templates/architecture/decisions/<aspect>.arch.json`
file (default: working tree vs HEAD), classifies the diff, and suggests
MAJOR / MINOR / PATCH per these heuristics:

  - list item ADDED (matched by canonical id) -> MINOR
  - list item REMOVED                          -> MAJOR
  - list item field changed                    -> MAJOR (except patch fields below)
  - scalar value changed (anywhere)            -> MAJOR (except patch fields)
  - only `description`/`_comment`/`$comment`/
    `label`/`last_changed`/`version` changed   -> PATCH
  - no changes                                 -> NONE

The script never bumps silently. It prints the analysis, suggests the
level, and (unless --auto) asks the operator to confirm. On confirm it
edits the JSON in place (version + last_changed).

Canonical id detection per list: first present key among
  id, code, prefix, name
Lists keyed by none of these are diffed positionally (less precise; works
for short fixed-order lists like enforcement.audit_required).

Usage:
    python scripts/be-arch-bump.py --aspect rbac
    python scripts/be-arch-bump.py --aspect rbac --auto
    python scripts/be-arch-bump.py --aspect rbac --dry-run
    python scripts/be-arch-bump.py --aspect rbac --from <git-ref>
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from cli_utils import force_utf8_stdio


_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# Fields whose changes never warrant more than a PATCH bump.
_PATCH_ONLY_FIELDS = {
    "description", "_comment", "$comment", "label", "last_changed", "version",
    "rationale", "note", "fe_action_hint", "purpose",
}

# Order of preference for the canonical id key when diffing a list.
_ID_KEYS = ("id", "code", "prefix", "name")


def _workspace_root(start: Path) -> Path:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / "scripts" / "new-project.py").is_file() and (p / "templates").is_dir():
            return p
    sys.exit("error: could not locate workspace root from cwd")


def _aspect_path(workspace: Path, aspect: str) -> Path:
    return workspace / "templates" / "architecture" / "decisions" / f"{aspect}.arch.json"


def parse_version(text: str) -> tuple[int, int, int] | None:
    if not isinstance(text, str):
        return None
    m = _SEMVER_RE.match(text.strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def format_version(v: tuple[int, int, int]) -> str:
    return f"{v[0]}.{v[1]}.{v[2]}"


def apply_bump_to_version(v: tuple[int, int, int], level: str) -> tuple[int, int, int]:
    if level == "major":
        return (v[0] + 1, 0, 0)
    if level == "minor":
        return (v[0], v[1] + 1, 0)
    if level == "patch":
        return (v[0], v[1], v[2] + 1)
    return v


def _git_show(workspace: Path, rel_path: str, ref: str) -> str | None:
    """Return file contents at `ref:rel_path` via git show, or None when
    git or the ref is unavailable."""
    try:
        # encoding="utf-8" forces consistent decoding; Windows default cp1252
        # mangles UTF-8 content (e.g. accented Portuguese in descriptions).
        result = subprocess.run(
            ["git", "show", f"{ref}:{rel_path}"],
            cwd=str(workspace),
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False,
        )
    except (FileNotFoundError, OSError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _id_for(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    for key in _ID_KEYS:
        if key in item and isinstance(item[key], (str, int)):
            return f"{key}={item[key]!r}"
    return None


def _diff_lists(prev: list, curr: list, path: str) -> list[dict]:
    """Detect adds/removes/modifies on a list.

    Returns dicts: ``{kind, path, id, severity, summary}`` where kind is
    one of ``added``, ``removed``, ``modified``, ``reordered``.
    """
    out: list[dict] = []
    prev_keyed = {_id_for(i): i for i in prev if _id_for(i) is not None}
    curr_keyed = {_id_for(i): i for i in curr if _id_for(i) is not None}

    if prev_keyed and curr_keyed:
        # Keyed diff
        prev_ids = set(prev_keyed)
        curr_ids = set(curr_keyed)
        for added in sorted(curr_ids - prev_ids):
            out.append({
                "kind": "added", "path": path, "id": added,
                "severity": "minor",
                "summary": f"{path}: added {added}",
            })
        for removed in sorted(prev_ids - curr_ids):
            out.append({
                "kind": "removed", "path": path, "id": removed,
                "severity": "major",
                "summary": f"{path}: removed {removed}",
            })
        for shared in sorted(prev_ids & curr_ids):
            sub = _diff_obj(prev_keyed[shared], curr_keyed[shared],
                            f"{path}[{shared}]")
            out.extend(sub)
        return out

    # Positional diff for scalar lists (e.g. enforcement.audit_required)
    if prev != curr:
        added = [x for x in curr if x not in prev]
        removed = [x for x in prev if x not in curr]
        for a in added:
            out.append({
                "kind": "added", "path": path, "id": repr(a),
                "severity": "minor",
                "summary": f"{path}: added {a!r}",
            })
        for r in removed:
            out.append({
                "kind": "removed", "path": path, "id": repr(r),
                "severity": "major",
                "summary": f"{path}: removed {r!r}",
            })
        if not added and not removed and prev != curr:
            out.append({
                "kind": "reordered", "path": path, "id": None,
                "severity": "patch",
                "summary": f"{path}: reordered",
            })
    return out


def _diff_obj(prev: dict, curr: dict, path: str) -> list[dict]:
    out: list[dict] = []
    keys = set(prev) | set(curr)
    for k in sorted(keys):
        sub_path = f"{path}.{k}" if path else k
        if k not in prev:
            out.append({
                "kind": "added", "path": sub_path, "id": None,
                "severity": "minor",
                "summary": f"{sub_path}: added (was missing)",
            })
            continue
        if k not in curr:
            out.append({
                "kind": "removed", "path": sub_path, "id": None,
                "severity": "major",
                "summary": f"{sub_path}: removed",
            })
            continue
        pv, cv = prev[k], curr[k]
        if pv == cv:
            continue
        if isinstance(pv, dict) and isinstance(cv, dict):
            out.extend(_diff_obj(pv, cv, sub_path))
        elif isinstance(pv, list) and isinstance(cv, list):
            out.extend(_diff_lists(pv, cv, sub_path))
        else:
            sev = "patch" if k in _PATCH_ONLY_FIELDS else "major"
            out.append({
                "kind": "modified", "path": sub_path, "id": None,
                "severity": sev,
                "summary": f"{sub_path}: {pv!r} -> {cv!r}",
            })
    return out


def diff_aspect(prev_payload: dict, curr_payload: dict) -> list[dict]:
    """Top-level diff. Returns a list of structural change records."""
    return _diff_obj(prev_payload, curr_payload, "")


_SEVERITY_RANK = {"patch": 1, "minor": 2, "major": 3}


def suggest_bump(changes: list[dict]) -> str:
    """Roll up the per-change severities into one of major/minor/patch/none."""
    if not changes:
        return "none"
    max_sev = max(_SEVERITY_RANK[c["severity"]] for c in changes)
    return {1: "patch", 2: "minor", 3: "major"}[max_sev]


def apply_bump(payload: dict, level: str) -> tuple[str, str]:
    """Mutate payload in place. Returns (old_version, new_version)."""
    old_str = payload.get("version", "0.0.0")
    old = parse_version(old_str) or (0, 0, 0)
    new = apply_bump_to_version(old, level)
    payload["version"] = format_version(new)
    payload["last_changed"] = date.today().isoformat()
    return format_version(old), format_version(new)


def render_diff(changes: list[dict], aspect: str) -> str:
    if not changes:
        return f"  (no changes detected in {aspect}.arch.json)"
    lines = []
    for c in changes:
        marker = {"added": "+", "removed": "-", "modified": "~", "reordered": "~"}[c["kind"]]
        sev = c["severity"].upper()
        lines.append(f"  [{marker}] [{sev:5s}] {c['summary']}")
    return "\n".join(lines)


def _prompt(suggestion: str) -> str | None:
    """Return the user's choice in {major,minor,patch,none} or None to abort."""
    print()
    print(f"Suggested bump: {suggestion.upper()}")
    print("Continue?  [Y]es / [n]o / m(a)jor / mi(n)or / (p)atch")
    try:
        answer = input("> ").strip().lower()
    except EOFError:
        return None
    if answer in ("", "y", "yes"):
        return suggestion
    if answer in ("n", "no"):
        return None
    if answer in ("a", "major"):
        return "major"
    if answer in ("minor",):
        return "minor"
    if answer in ("p", "patch"):
        return "patch"
    return None


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-arch-bump.py",
        description="Suggest and apply a semver bump for an architecture aspect (D-116).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--aspect", required=True,
                        help="Aspect name (e.g. rbac, persistence).")
    parser.add_argument("--from", dest="from_ref", default="HEAD",
                        help="Git ref to compare working-tree against (default: HEAD).")
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Workspace root (default: walk up from cwd).")
    parser.add_argument("--auto", action="store_true",
                        help="Apply the suggested bump without confirmation.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print analysis only; never write.")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of human-readable output.")
    args = parser.parse_args(argv)

    workspace = _workspace_root(args.workspace or Path.cwd())
    aspect_path = _aspect_path(workspace, args.aspect)
    if not aspect_path.is_file():
        sys.exit(f"error: aspect file not found: {aspect_path}")

    curr_text = aspect_path.read_text(encoding="utf-8")
    try:
        curr = json.loads(curr_text)
    except json.JSONDecodeError as e:
        sys.exit(f"error: current {args.aspect}.arch.json is not valid JSON: {e}")

    rel = str(aspect_path.relative_to(workspace)).replace("\\", "/")
    prev_text = _git_show(workspace, rel, args.from_ref)
    if prev_text is None:
        sys.exit(
            f"error: cannot read {rel} at git ref {args.from_ref!r}. "
            f"Is the file tracked there? Pass --from <other-ref> or commit "
            f"the file first."
        )
    try:
        prev = json.loads(prev_text)
    except json.JSONDecodeError as e:
        sys.exit(f"error: {args.from_ref}:{rel} is not valid JSON: {e}")

    changes = diff_aspect(prev, curr)
    suggestion = suggest_bump(changes)
    old_v = curr.get("version", "0.0.0")
    next_v = (
        format_version(apply_bump_to_version(parse_version(old_v) or (0, 0, 0),
                                             suggestion))
        if suggestion != "none" else old_v
    )

    if args.json:
        print(json.dumps({
            "aspect": args.aspect,
            "from_ref": args.from_ref,
            "current_version": old_v,
            "suggested_bump": suggestion,
            "next_version": next_v,
            "changes": changes,
        }, indent=2))
    else:
        print(f"be-arch-bump - aspect={args.aspect}  from={args.from_ref}")
        print(f"  current version: {old_v}")
        print()
        print("Changes detected:")
        print(render_diff(changes, args.aspect))

    if suggestion == "none":
        return 0
    if args.dry_run:
        if not args.json:
            print()
            print(f"DRY RUN: would bump {old_v} -> {next_v}")
        return 0

    chosen = suggestion if args.auto else _prompt(suggestion)
    if chosen is None:
        print("\naborted; no changes written")
        return 1

    old_str, new_str = apply_bump(curr, chosen)
    aspect_path.write_text(
        json.dumps(curr, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print()
    print(f"OK: {aspect_path.relative_to(workspace)} version {old_str} -> {new_str} "
          f"({chosen})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
