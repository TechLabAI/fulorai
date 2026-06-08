#!/usr/bin/env python3
"""be-arch-migration.py - generate a migration plan for an aspect bump (D-117, B4).

When an aspect bump REMOVES items (roles, permission codes, error codes,
event names, etc.), the code in registered client projects may still
reference them. This script:

  1. Diffs the aspect between two refs (default: HEAD vs working tree)
     via the same logic D-116 uses for bump suggestion.
  2. Collects every "removed" item with its canonical id.
  3. Greps the target project tree for quoted occurrences of each id in
     source files (Java/Kotlin/TS/Python/Markdown by default).
  4. For each removed item, suggests the lexically closest surviving
     item via difflib (Levenshtein-like ratio).
  5. Emits a markdown migration plan listing file/line/snippet of every
     hit, plus suggested replacements.

The script generates a plan for a HUMAN to execute. It NEVER modifies
target code automatically (per plan's E3-rejected boundary).

Usage:
    python scripts/be-arch-migration.py --aspect rbac --project /repos/bosq
    python scripts/be-arch-migration.py --aspect rbac --from v0.4.0 --project /repos/bosq
    python scripts/be-arch-migration.py --aspect rbac --project /repos/bosq --out /tmp/plan.md
"""

from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from cli_utils import force_utf8_stdio


_DEFAULT_SOURCE_GLOBS = (
    "*.java", "*.kt", "*.ts", "*.tsx", "*.js", "*.py", "*.md",
)
_SKIP_DIRS = {".git", "node_modules", "build", "target", "dist", ".gradle",
              ".venv", "__pycache__"}
_ID_KEYS = ("id", "code", "prefix", "name")


def _workspace_root(start: Path) -> Path:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / "scripts" / "new-project.py").is_file() and (p / "templates").is_dir():
            return p
    sys.exit("error: could not locate workspace root from cwd")


def _aspect_path(workspace: Path, aspect: str) -> Path:
    return workspace / "templates" / "architecture" / "decisions" / f"{aspect}.arch.json"


def _load_bump_module(workspace: Path):
    """Reuse be-arch-bump's diff_aspect via importlib."""
    spec = importlib.util.spec_from_file_location(
        "be_arch_bump", workspace / "scripts" / "be-arch-bump.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("be_arch_bump", mod)
    spec.loader.exec_module(mod)
    return mod


def _git_show(workspace: Path, rel_path: str, ref: str) -> str | None:
    try:
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


def _id_value_from_dict(item: dict) -> str | None:
    """Return the canonical id VALUE (not the key=value formatted string
    that be-arch-bump uses internally) so it can be used for code grep."""
    for key in _ID_KEYS:
        if key in item and isinstance(item[key], (str, int)):
            return str(item[key])
    return None


def collect_removed_items(prev: dict, curr: dict, workspace: Path) -> list[dict]:
    """Identify items removed between two payloads. Returns a list of
    ``{path, id, source_value}`` where ``source_value`` is the literal
    string to grep for in code (id stripped of `key=` prefix)."""
    bump = _load_bump_module(workspace)
    changes = bump.diff_aspect(prev, curr)
    out: list[dict] = []
    for c in changes:
        if c["kind"] != "removed":
            continue
        # be-arch-bump returns id in "key=value" format when items have a
        # canonical key, or repr(scalar) when positional. Unwrap.
        raw_id = c.get("id")
        if raw_id is None:
            continue
        if "=" in raw_id and raw_id.split("=", 1)[1].startswith(("'", '"')):
            # "code='SYS_ADMIN'" -> "SYS_ADMIN"
            try:
                source_value = raw_id.split("=", 1)[1].strip("'\"")
            except IndexError:
                source_value = raw_id
        else:
            # Positional list item, was repr'd: "'CREATE'"
            try:
                source_value = raw_id.strip("'\"")
            except AttributeError:
                source_value = str(raw_id)
        out.append({
            "path": c["path"],
            "id": raw_id,
            "source_value": source_value,
        })
    return out


def collect_surviving_ids(payload: dict) -> dict[str, list[str]]:
    """Walk the payload and bucket surviving ids by their list path.
    Used by the closest-match heuristic to suggest replacements within
    the same list. Returns ``{path: [id_value, ...]}``."""
    out: dict[str, list[str]] = {}

    def walk(node, path: str):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            ids_here: list[str] = []
            for item in node:
                if isinstance(item, dict):
                    val = _id_value_from_dict(item)
                    if val:
                        ids_here.append(val)
                elif isinstance(item, str):
                    ids_here.append(item)
            if ids_here:
                out[path] = ids_here

    walk(payload, "")
    return out


def closest_match(target: str, candidates: list[str]) -> str | None:
    """Return the lexically closest surviving id or None when none plausible.
    Threshold tuned conservatively — better no suggestion than a misleading one."""
    matches = difflib.get_close_matches(target, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None


def _iter_source_files(project: Path, globs: tuple[str, ...]):
    for entry in project.rglob("*"):
        if not entry.is_file():
            continue
        if any(part in _SKIP_DIRS for part in entry.parts):
            continue
        if not any(entry.match(g) for g in globs):
            continue
        yield entry


def grep_quoted_literal(project: Path, value: str,
                       globs: tuple[str, ...] = _DEFAULT_SOURCE_GLOBS
                       ) -> list[dict]:
    """Return ``[{file, line, snippet}, ...]`` of every occurrence of
    ``value`` enclosed in either single or double quotes inside source
    files. Quotes anchor the match so we don't false-positive on
    arbitrary substrings (e.g. 'SYS_ADMIN' won't match the word
    SYSTEMADMINISTRATOR)."""
    # Quoted literal: `'value'` OR `"value"`
    escaped = re.escape(value)
    pat = re.compile(rf"['\"]{escaped}['\"]")
    hits: list[dict] = []
    for path in _iter_source_files(project, globs):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pat.search(line):
                hits.append({
                    "file": str(path.relative_to(project)).replace("\\", "/"),
                    "line": lineno,
                    "snippet": line.strip()[:160],
                })
    return hits


def build_plan(
    aspect: str,
    prev_version: str,
    curr_version: str,
    project: Path,
    removed: list[dict],
    surviving_by_list: dict[str, list[str]],
    source_globs: tuple[str, ...] = _DEFAULT_SOURCE_GLOBS,
) -> dict:
    """Cross-reference removed items against the target project's source.
    Returns a structured report including suggested replacements."""
    sections: list[dict] = []
    total_hits = 0
    for r in removed:
        list_path = r["path"]
        survivors = surviving_by_list.get(list_path, [])
        suggestion = closest_match(r["source_value"], survivors)
        hits = grep_quoted_literal(project, r["source_value"], source_globs)
        total_hits += len(hits)
        sections.append({
            "list_path": list_path,
            "removed_id": r["source_value"],
            "raw_id": r["id"],
            "hits": hits,
            "suggested_replacement": suggestion,
        })
    return {
        "aspect": aspect,
        "from_version": prev_version,
        "to_version": curr_version,
        "project": str(project),
        "generated_on": date.today().isoformat(),
        "total_removed": len(removed),
        "total_hits": total_hits,
        "sections": sections,
    }


def render_markdown(plan: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Migration plan — {plan['aspect']} "
                 f"{plan['from_version']} → {plan['to_version']}")
    lines.append("")
    lines.append(f"> Generated by `be-arch-migration.py` on "
                 f"{plan['generated_on']}.  ")
    lines.append(f"> Target project: `{plan['project']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- {plan['total_removed']} removed item(s) checked.")
    lines.append(f"- {plan['total_hits']} usage(s) found across the project.")
    n_with_suggestion = sum(
        1 for s in plan["sections"] if s["suggested_replacement"]
    )
    lines.append(f"- {n_with_suggestion} suggested replacement(s) "
                 f"(heuristic; verify before applying).")
    lines.append("")
    if not plan["sections"]:
        lines.append("No removed items detected — nothing to migrate.")
        return "\n".join(lines) + "\n"

    lines.append("## Removed items requiring attention")
    lines.append("")
    for section in plan["sections"]:
        lines.append(f"### `{section['removed_id']}` "
                     f"(removed from `{section['list_path']}`)")
        lines.append("")
        if section["hits"]:
            lines.append(f"Found {len(section['hits'])} usage(s):")
            lines.append("")
            for hit in section["hits"]:
                lines.append(f"- `{hit['file']}:{hit['line']}`")
                lines.append(f"  - `{hit['snippet']}`")
            lines.append("")
        else:
            lines.append("No source usages found — safe to bump.")
            lines.append("")
        if section["suggested_replacement"]:
            lines.append(f"**Suggested replacement:** "
                         f"`{section['suggested_replacement']}` "
                         f"(closest surviving id; **verify manually**).")
        else:
            lines.append("**Suggested replacement:** _none found_ — "
                         "redesign required, or drop usage entirely.")
        lines.append("")
        lines.append("**Action:** review each usage above, replace or remove, "
                     "then re-run `/be-architect-drift-check`.")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-arch-migration.py",
        description="Generate a migration plan for an aspect bump (D-117, automations B4).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--aspect", required=True,
                        help="Aspect name (e.g. rbac, permission-catalogue).")
    parser.add_argument("--from", dest="from_ref", default="HEAD",
                        help="Git ref containing the OLD aspect payload (default: HEAD).")
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Workspace root (default: walk up from cwd).")
    parser.add_argument("--project", type=Path, required=True,
                        help="Path to the client project to scan.")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output markdown file (default: stdout).")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON report instead of markdown.")
    parser.add_argument("--globs", default=",".join(_DEFAULT_SOURCE_GLOBS),
                        help="Comma-separated file globs to scan "
                             "(default: java/kt/ts/tsx/js/py/md).")
    args = parser.parse_args(argv)

    workspace = _workspace_root(args.workspace or Path.cwd())
    project = args.project.resolve()
    if not project.is_dir():
        sys.exit(f"error: --project {project} is not a directory")

    aspect_path = _aspect_path(workspace, args.aspect)
    if not aspect_path.is_file():
        sys.exit(f"error: aspect file not found: {aspect_path}")

    curr_text = aspect_path.read_text(encoding="utf-8")
    curr = json.loads(curr_text)
    rel = str(aspect_path.relative_to(workspace)).replace("\\", "/")
    prev_text = _git_show(workspace, rel, args.from_ref)
    if prev_text is None:
        sys.exit(
            f"error: cannot read {rel} at git ref {args.from_ref!r}. "
            f"Is the file tracked there? Pass --from <other-ref>."
        )
    prev = json.loads(prev_text)

    removed = collect_removed_items(prev, curr, workspace)
    surviving = collect_surviving_ids(curr)
    globs = tuple(g.strip() for g in args.globs.split(",") if g.strip())

    plan = build_plan(
        args.aspect,
        prev.get("version", "?"),
        curr.get("version", "?"),
        project, removed, surviving, globs,
    )

    if args.json:
        output = json.dumps(plan, indent=2)
    else:
        output = render_markdown(plan)

    if args.out:
        args.out.write_text(output, encoding="utf-8")
        print(f"OK: wrote migration plan to {args.out}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
