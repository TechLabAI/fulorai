#!/usr/bin/env python3
"""be-architect-upgrade.py — re-apply workspace architecture safely.

Reads ``architecture.lock``, classifies each aspect (via lockfile.classify_aspect),
and for each evolved aspect either previews or applies a safe upgrade:

- **synced** → no action.
- **source_changed** (workspace evolved, output unchanged locally) → safe
  upgrade. Re-render the template and overwrite the output. Update the lock.
- **locally_modified** (output edited, source unchanged) → no upgrade needed.
  Don't touch the file. Update the lock's ``output_sha`` to reflect the new
  local content so future drift-checks don't keep flagging it.
- **drifted** (both differ) → DO NOT auto-upgrade. Print the diff so the
  human can manually merge. The lock stays as-is for this aspect.
- **source_missing** → cannot upgrade; warn.
- **output_missing** → re-render to restore the file.

Default mode is **dry-run** (preview the plan). Use ``--apply`` to actually
execute. The implementation NEVER overwrites a locally-modified file without
explicit human action (this is the safety invariant from the evolution plan).

Usage:
    python scripts/be-architect-upgrade.py [--workspace PATH] [--apply] [--verbose]

Exit codes:
    0 — completed (whether dry-run or apply)
    1 — drifted aspects detected (require human review)
    2 — usage error (lock not found, workspace not found, schema mismatch)
"""
from __future__ import annotations

import argparse
import difflib
import io
import os
import sys
from pathlib import Path
from typing import Any

# Resolve sibling imports regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Force UTF-8 stdout for cross-platform safety (Windows cp1252 console chokes
# on non-ASCII characters that appear in template content).
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from lockfile import (  # noqa: E402
    LOCK_FILENAME,
    build_lock,
    classify_aspect,
    read_lock,
    sha256_of_file,
    write_lock,
)
from render import load_context_vars, render_template  # noqa: E402


# ── Workspace + project resolution (mirrors drift-check) ─────────────────────


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


# ── Plan + actions ───────────────────────────────────────────────────────────


def make_plan(
    lock: dict[str, Any],
    workspace: Path,
    project_root: Path,
) -> list[dict[str, Any]]:
    """Classify each aspect and decide the action."""
    plan: list[dict[str, Any]] = []
    for key, entry in lock["aspects"].items():
        c = classify_aspect(key, entry, workspace, project_root)
        state = c["state"]
        if state == "synced":
            action = "skip"
        elif state == "source_changed":
            action = "re-render"
        elif state == "output_missing":
            action = "re-render-restore"
        elif state == "locally_modified":
            action = "preserve-local"
        elif state == "drifted":
            action = "needs-review"
        elif state == "source_missing":
            action = "warn-source-missing"
        else:
            action = "unknown"
        plan.append({**c, "action": action})
    return plan


def render_diff(old: str, new: str, path_label: str, max_lines: int = 40) -> list[str]:
    """Unified diff, truncated at `max_lines` to keep previews readable."""
    diff = list(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"{path_label} (current)",
        tofile=f"{path_label} (workspace)",
        n=3,
    ))
    if len(diff) <= max_lines:
        return diff
    head = diff[:max_lines]
    head.append(f"  ... ({len(diff) - max_lines} more diff lines truncated; use --verbose to see all)\n")
    return head


def apply_plan(
    plan: list[dict[str, Any]],
    workspace: Path,
    project_root: Path,
    template_vars: dict[str, Any],
    apply: bool,
    verbose: bool,
) -> tuple[int, int, int]:
    """Execute (or preview) the plan. Returns (n_applied, n_skipped, n_review)."""
    applied = skipped = review = 0
    for item in plan:
        action = item["action"]
        if action == "skip":
            skipped += 1
            continue

        rel_out = item["aspect"].split("/architecture/", 1)[-1] if "/architecture/" in item["aspect"] else item["aspect"]

        if action in ("re-render", "re-render-restore"):
            output_path = project_root / item["output"]
            # D-061: decision JSON files are pinned as verbatim copies, not
            # Jinja-rendered.
            # D-074: overridden decisions have composite source; re-derive
            # via build_merged_decision_content (workspace base + project
            # overrides + dynamic ctx-derived overrides).
            source_str = item["source"].replace("\\", "/")
            is_decision = "architecture/decisions/" in source_str
            is_composite = " + " in item["source"]
            try:
                if is_composite:
                    from lockfile import build_merged_decision_content
                    new_content = build_merged_decision_content(
                        item, workspace, project_root)
                    if new_content is None:
                        raise FileNotFoundError(
                            "could not rebuild merged content (workspace/"
                            "override file missing)")
                elif is_decision:
                    source_path = workspace / item["source"]
                    new_content = source_path.read_text(encoding="utf-8")
                else:
                    source_path = workspace / item["source"]
                    new_content = render_template(source_path, template_vars, postprocess=True)
            except Exception as e:
                print(f"  [error] re-render failed for {rel_out}: {e}")
                review += 1
                continue
            old_content = output_path.read_text(encoding="utf-8") if output_path.is_file() else ""
            print(f"  [upgrade] {rel_out}  ({action})")
            if verbose:
                for line in render_diff(old_content, new_content, rel_out, max_lines=10_000):
                    sys.stdout.write(line)
            else:
                preview_lines = render_diff(old_content, new_content, rel_out, max_lines=20)
                for line in preview_lines:
                    sys.stdout.write("    " + line)
            if apply:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(new_content, encoding="utf-8")
                applied += 1
            else:
                applied += 1  # would-be-applied
        elif action == "preserve-local":
            print(f"  [preserve-local] {rel_out}  (you edited locally; workspace unchanged — lock entry kept as-was)")
            skipped += 1
        elif action == "needs-review":
            print(f"  [DRIFTED] {rel_out}  (workspace evolved AND you edited locally — manual merge required)")
            if verbose:
                source_path = workspace / item["source"]
                output_path = project_root / item["output"]
                is_decision = "architecture/decisions/" in item["source"].replace("\\", "/")
                try:
                    if is_decision:
                        new_content = source_path.read_text(encoding="utf-8")
                    else:
                        new_content = render_template(source_path, template_vars, postprocess=True)
                    old_content = output_path.read_text(encoding="utf-8")
                    for line in render_diff(old_content, new_content, rel_out, max_lines=10_000):
                        sys.stdout.write("    " + line)
                except Exception as e:
                    print(f"    [error] could not render workspace version: {e}")
            review += 1
        elif action == "warn-source-missing":
            print(f"  [orphan] {rel_out}  (source template was removed from workspace; consider deleting locally)")
            review += 1
        else:
            print(f"  [unknown] {rel_out}  state={item['state']}")
            review += 1
    return applied, skipped, review


def refresh_lock(
    plan: list[dict[str, Any]],
    workspace: Path,
    project_root: Path,
    original_lock: dict[str, Any],
) -> dict[str, Any]:
    """Build a new lock with updated SHAs reflecting the post-apply state.

    Per-action policy:
    - ``warn-source-missing``: drop from lock (source no longer exists).
    - ``needs-review`` (drifted) and ``preserve-local`` (locally_modified):
      KEEP the original entry untouched so the local edit (or unresolved
      conflict) stays visible to future drift-checks. CRITICAL FOR SAFETY:
      if we recomputed output_sha for a locally-modified aspect, future
      workspace evolutions would be classified as ``source_changed``
      ("safe to overwrite") and ``--apply`` would silently destroy the
      user's edit.
    - any other action (``skip`` (synced), ``re-render``, ``re-render-restore``):
      recompute current SHAs — this is the new baseline for future drift
      detection.
    """
    new_aspects: dict[str, dict[str, str]] = {}
    for item in plan:
        key = item["aspect"]
        action = item["action"]
        original_entry = original_lock["aspects"].get(key, {})

        if action == "warn-source-missing":
            # Drop orphaned aspect (source template removed from workspace).
            continue
        if action in ("needs-review", "preserve-local"):
            # Preserve original entry — conflict not yet resolved OR local
            # edit must remain detectable for safety.
            new_aspects[key] = {k: v for k, v in original_entry.items() if k != "_state"}
            continue

        source_path = workspace / item["source"]
        output_path = project_root / item["output"]
        if not source_path.is_file() or not output_path.is_file():
            new_aspects[key] = {k: v for k, v in original_entry.items() if k != "_state"}
            continue
        new_aspects[key] = {
            "source": item["source"],
            "source_sha": sha256_of_file(source_path),
            "output": item["output"],
            "output_sha": sha256_of_file(output_path),
        }
    return build_lock(workspace, project_root, new_aspects)


# ── CLI ──────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-architect-upgrade.py",
        description="Re-apply workspace architecture safely (preserves local edits).",
    )
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Path to the techlab-architecture workspace.")
    parser.add_argument("--project-root", type=Path, default=None,
                        help="Path to the generated project (default: walk up to find architecture.lock).")
    parser.add_argument("--apply", action="store_true",
                        help="Actually write the upgrades (default is dry-run preview).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show full diffs and per-file detail.")
    args = parser.parse_args(argv)

    workspace = find_workspace(args.workspace)
    project_root = find_project_root(args.project_root)
    try:
        lock = read_lock(project_root)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"error: {e}")

    template_vars = load_context_vars(project_root)

    print(f"Architecture upgrade plan")
    print(f"  Workspace:     {workspace}")
    print(f"  Project root:  {project_root}")
    print(f"  Mode:          {'APPLY' if args.apply else 'dry-run (use --apply to execute)'}")
    print()

    plan = make_plan(lock, workspace, project_root)
    applied, skipped, review = apply_plan(
        plan, workspace, project_root, template_vars, apply=args.apply, verbose=args.verbose,
    )

    print()
    print("Summary:")
    label = "applied" if args.apply else "would apply"
    print(f"  {label:24s} {applied}")
    print(f"  {'skipped (synced or local)':24s} {skipped}")
    print(f"  {'needs review':24s} {review}")

    if args.apply and applied > 0:
        new_lock = refresh_lock(plan, workspace, project_root, lock)
        path = write_lock(project_root, new_lock)
        print()
        print(f"  Wrote {path.name} (new arch {new_lock['architecture']['version']}, "
              f"{len(new_lock['aspects'])} aspect(s))")

    if review > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
