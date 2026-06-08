#!/usr/bin/env python3
"""knowledge-index.py — Validate artifact-identity frontmatter and generate reading-path index.

Subcommands
-----------
validate <dir>              Check all artifact_dependencies resolve to a known
                            artifact_name in the directory. Exit 2 on any broken
                            dependency. Warn about orphan artifacts (no dependents).
index <dir>                 Emit index.md with reading paths derived from the
                            dependency graph (Fast Path, Deep Path, Build Path).
next-seq <dir> <category>   Return the next free monotonic numeric prefix for
                            the given category (e.g. "03").

Follows R3 from CLAUDE.md:
  - argparse with subcommands
  - finds the knowledge dir from the explicit argument (no walk-up needed —
    the caller names the exact directory)
  - atomic writes (temp file + os.replace)
  - print "OK: <action>" on success; "error: <reason>" on failure (stderr)
  - exit 0 success, 1 user error, 2 validation failure

Pure stdlib — no PyYAML dependency.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from collections import defaultdict, deque
from pathlib import Path


# ── Frontmatter parser ────────────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> dict[str, str | list[str]] | None:
    """Parse YAML-style frontmatter between the first pair of --- delimiters.

    Supported value forms:
      key: scalar
      key: [item1, item2]          inline list
      key: item1, item2            comma-separated string → list[str]
      key:                         block list (items on subsequent indented lines)
        - item1
        - item2
      key: []                      explicit empty list

    Returns dict[str, str | list[str]] or None if no frontmatter block found.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return None

    result: dict[str, str | list[str]] = {}
    current_key: str | None = None
    current_list: list[str] | None = None

    for line in lines[1:end_idx]:
        if not line.strip():
            continue

        stripped = line.lstrip()

        # Block-list item
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            if current_key is not None and current_list is not None:
                current_list.append(item)
            continue

        # Non-list line: flush any pending block list
        if current_key is not None and current_list is not None:
            result[current_key] = current_list
            current_key = None
            current_list = None

        if ":" not in line:
            continue

        colon_idx = line.index(":")
        key = line[:colon_idx].strip()
        value = line[colon_idx + 1:].strip()

        if not value:
            current_key = key
            current_list = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            result[key] = [v.strip() for v in inner.split(",") if v.strip()] if inner else []
        elif "," in value and not value.startswith('"'):
            result[key] = [v.strip() for v in value.split(",") if v.strip()]
        else:
            result[key] = value

    # Flush trailing block list
    if current_key is not None and current_list is not None:
        result[current_key] = current_list

    return result


# ── Helpers ───────────────────────────────────────────────────────────────────

_EXCLUDED_SUBDIRS = {"_includes", "_meta"}


def _collect_artifacts(directory: Path) -> dict[str, dict]:
    """Walk directory for .md files with artifact_name frontmatter.

    Returns dict: artifact_name → {frontmatter fields..., "_path": Path}
    Skips files inside _includes/ and _meta/ subdirectories.
    Exits 1 on duplicate artifact_name.
    """
    artifacts: dict[str, dict] = {}

    for md_path in sorted(directory.rglob("*.md")):
        relative = md_path.relative_to(directory)
        # Skip excluded subdirectories
        if any(part in _EXCLUDED_SUBDIRS for part in relative.parts[:-1]):
            continue

        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {md_path}: {exc}", file=sys.stderr)
            sys.exit(1)

        fm = _parse_frontmatter(text)
        if fm is None or "artifact_name" not in fm:
            continue  # Not an artifact file — skip silently

        name = str(fm["artifact_name"])
        if name in artifacts:
            print(
                f"error: duplicate artifact_name '{name}' — "
                f"{md_path} conflicts with {artifacts[name]['_path']}",
                file=sys.stderr,
            )
            sys.exit(1)

        fm["_path"] = md_path
        artifacts[name] = fm

    return artifacts


def _as_list(value: str | list[str] | None) -> list[str]:
    """Normalize a frontmatter field value to list[str], filtering empty strings."""
    if not value:
        return []
    if isinstance(value, list):
        return [v for v in value if v]
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _seq_num(artifact_name: str) -> int:
    """Extract the leading numeric sequence from an artifact_name.

    'knowledge-02-index-design' → 2
    'playbook-10-build'        → 10
    'charter-purpose'          → 999 (no numeric segment → sort last)
    """
    for part in artifact_name.split("-"):
        if part.isdigit():
            return int(part)
    return 999


def _atomic_write(path: Path, content: str) -> None:
    """Write content atomically using a temp file + os.replace."""
    parent = path.parent
    fd, tmp = tempfile.mkstemp(prefix=".ki-", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


# ── Subcommand: validate ──────────────────────────────────────────────────────

def cmd_validate(args: argparse.Namespace) -> int:
    """Check all artifact_dependencies resolve; warn on orphan artifacts."""
    directory = Path(args.dir).resolve()
    if not directory.is_dir():
        print(f"error: directory not found: {directory}", file=sys.stderr)
        return 1

    artifacts = _collect_artifacts(directory)
    if not artifacts:
        print("OK: validate — 0 artifacts found (nothing to validate)")
        return 0

    known: set[str] = set(artifacts)
    errors: list[str] = []

    for name, meta in artifacts.items():
        for dep in _as_list(meta.get("artifact_dependencies")):
            if dep not in known:
                errors.append(f"  '{name}' → unresolved dependency '{dep}'")

    if errors:
        print(
            f"error: {len(errors)} unresolved dependency(ies) in {directory}:",
            file=sys.stderr,
        )
        for msg in errors:
            print(msg, file=sys.stderr)
        return 2

    # Detect orphans: artifacts that no other artifact depends on
    depended_on: set[str] = set()
    for meta in artifacts.values():
        depended_on.update(_as_list(meta.get("artifact_dependencies")))
    orphans = [n for n in known if n not in depended_on]
    for name in sorted(orphans):
        print(f"warning: orphan artifact (no dependents): '{name}'", file=sys.stderr)

    print(
        f"OK: validate — {len(artifacts)} artifact(s), "
        f"0 broken dependencies, {len(orphans)} orphan(s)"
    )
    return 0


# ── Subcommand: index ─────────────────────────────────────────────────────────

_CATEGORY_ORDER = ["knowledge", "playbook", "template", "charter"]


def _topological_sort(artifacts: dict[str, dict]) -> list[str]:
    """Return artifact names in topological order (dependencies before dependents).

    Uses Kahn's algorithm. Cycles are broken by alphabetical ordering of the
    remaining nodes (appended at end).
    """
    in_degree: dict[str, int] = {n: 0 for n in artifacts}
    dependents: dict[str, list[str]] = defaultdict(list)

    for name, meta in artifacts.items():
        for dep in _as_list(meta.get("artifact_dependencies")):
            if dep in artifacts:
                in_degree[name] += 1
                dependents[dep].append(name)

    queue: deque[str] = deque(sorted(n for n, d in in_degree.items() if d == 0))
    order: list[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for child in sorted(dependents[node]):
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    # Handle any cycle remnants
    remaining = sorted(n for n in artifacts if n not in set(order))
    order.extend(remaining)
    return order


def cmd_index(args: argparse.Namespace) -> int:
    """Emit index.md with Fast Path, Deep Path, and Build Path reading paths."""
    directory = Path(args.dir).resolve()
    if not directory.is_dir():
        print(f"error: directory not found: {directory}", file=sys.stderr)
        return 1

    artifacts = _collect_artifacts(directory)
    if not artifacts:
        print("OK: index — 0 artifacts found; no index.md generated")
        return 0

    # Fast Path: knowledge-category artifacts ordered by sequence number
    fast_path = sorted(
        (n for n, m in artifacts.items() if m.get("artifact_category") == "knowledge"),
        key=_seq_num,
    )

    # Deep Path: all artifacts ordered by category priority then sequence number
    def _deep_key(name: str) -> tuple[int, int]:
        cat = artifacts[name].get("artifact_category", "")
        cat_rank = _CATEGORY_ORDER.index(cat) if cat in _CATEGORY_ORDER else len(_CATEGORY_ORDER)
        return (cat_rank, _seq_num(name))

    deep_path = sorted(artifacts, key=_deep_key)

    # Build Path: topological order (dependencies before dependents)
    build_path = _topological_sort(artifacts)

    def _item_line(name: str) -> str:
        meta = artifacts[name]
        role = meta.get("artifact_role", "")
        rel = meta["_path"].relative_to(directory).as_posix()
        return f"- [`{rel}`]({rel}) — {role}" if role else f"- `{rel}`"

    lines: list[str] = [
        "# Knowledge Index",
        "",
        f"> Generated from {len(artifacts)} artifact(s) in `{directory.name}/`.",
        "",
        "## Reading Paths",
        "",
        "### Fast Path",
        "",
        "Quickest entry into core concepts — knowledge artifacts in sequence order.",
        "",
    ]
    lines.extend(_item_line(n) for n in fast_path)

    lines += [
        "",
        "### Deep Path",
        "",
        "All artifacts in category + sequence order for comprehensive coverage.",
        "",
    ]
    lines.extend(_item_line(n) for n in deep_path)

    lines += [
        "",
        "### Build Path",
        "",
        "Dependency-first ordering — safe sequence to build the full body of knowledge.",
        "",
    ]
    lines.extend(_item_line(n) for n in build_path)
    lines.append("")

    content = "\n".join(lines)
    out_path = directory / "index.md"
    _atomic_write(out_path, content)

    print(
        f"OK: index — wrote {out_path} "
        f"({len(fast_path)} fast, {len(deep_path)} deep, {len(build_path)} build)"
    )
    return 0


# ── Subcommand: next-seq ──────────────────────────────────────────────────────

_VALID_CATEGORIES = frozenset(_CATEGORY_ORDER)


def cmd_next_seq(args: argparse.Namespace) -> int:
    """Return the next free monotonic numeric prefix (zero-padded to 2 digits)."""
    directory = Path(args.dir).resolve()
    if not directory.is_dir():
        print(f"error: directory not found: {directory}", file=sys.stderr)
        return 1

    category = args.category
    if category not in _VALID_CATEGORIES:
        print(
            f"error: unknown category '{category}'. "
            f"Valid: {', '.join(sorted(_VALID_CATEGORIES))}",
            file=sys.stderr,
        )
        return 1

    artifacts = _collect_artifacts(directory)

    nums = [
        _seq_num(n)
        for n, m in artifacts.items()
        if m.get("artifact_category") == category and _seq_num(n) < 999
    ]
    next_num = max(nums, default=0) + 1
    print(f"{next_num:02d}")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge-index.py",
        description=(
            "Validate artifact-identity frontmatter and generate "
            "reading-path index for a knowledge artifact directory."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser(
        "validate",
        help="Check all artifact_dependencies resolve; warn on orphans (exit 2 on failure)",
    )
    p_val.add_argument("dir", help="Knowledge directory to validate")
    p_val.set_defaults(func=cmd_validate)

    p_idx = sub.add_parser(
        "index",
        help="Emit index.md with Fast / Deep / Build reading paths",
    )
    p_idx.add_argument("dir", help="Knowledge directory to index")
    p_idx.set_defaults(func=cmd_index)

    p_seq = sub.add_parser(
        "next-seq",
        help="Return next free monotonic numeric prefix for an artifact category",
    )
    p_seq.add_argument("dir", help="Knowledge directory to scan")
    p_seq.add_argument(
        "category",
        choices=sorted(_VALID_CATEGORIES),
        help="Artifact category to count",
    )
    p_seq.set_defaults(func=cmd_next_seq)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
