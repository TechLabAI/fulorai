#!/usr/bin/env python3
"""install-hooks.py - install hooks/pre-commit into .git/hooks/ (D-115).

Copies the versioned shim at `hooks/pre-commit` into `.git/hooks/pre-commit`
and marks it executable. Idempotent; reports what it did so the operator
can verify.

Usage:
    python scripts/install-hooks.py
    python scripts/install-hooks.py --workspace /path/to/repo
    python scripts/install-hooks.py --force      # overwrite existing
    python scripts/install-hooks.py --uninstall
"""

from __future__ import annotations

import argparse
import shutil
import stat
import sys
from pathlib import Path

from cli_utils import force_utf8_stdio


def _workspace_root(explicit: Path | None) -> Path:
    if explicit:
        return explicit.resolve()
    cur = Path.cwd().resolve()
    for p in [cur, *cur.parents]:
        if (p / "scripts" / "new-project.py").is_file() and (p / ".git").exists():
            return p
    sys.exit(
        "error: could not locate a workspace + git checkout from cwd. "
        "Pass --workspace explicitly."
    )


def install(workspace: Path, *, force: bool) -> int:
    src = workspace / "hooks" / "pre-commit"
    dst = workspace / ".git" / "hooks" / "pre-commit"

    if not src.is_file():
        sys.exit(f"error: source hook not found at {src}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        # Check whether the existing hook is identical to ours; if so, exit ok.
        if dst.read_bytes() == src.read_bytes():
            print(f"OK: {dst.relative_to(workspace)} already installed (identical)")
            return 0
        print(f"FAIL: {dst.relative_to(workspace)} exists and differs; "
              f"re-run with --force to overwrite", file=sys.stderr)
        return 1

    shutil.copyfile(src, dst)
    mode = dst.stat().st_mode
    dst.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"OK: installed {src.relative_to(workspace)} -> "
          f"{dst.relative_to(workspace)} (executable)")
    return 0


def uninstall(workspace: Path) -> int:
    dst = workspace / ".git" / "hooks" / "pre-commit"
    if not dst.exists():
        print(f"OK: no hook at {dst.relative_to(workspace)} (already uninstalled)")
        return 0
    dst.unlink()
    print(f"OK: removed {dst.relative_to(workspace)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="install-hooks.py",
        description="Install or remove the workspace pre-commit hook (D-115).",
    )
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Workspace root (default: walk up from cwd).")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--force", action="store_true",
                      help="Overwrite an existing .git/hooks/pre-commit.")
    mode.add_argument("--uninstall", action="store_true",
                      help="Remove the installed hook.")
    args = parser.parse_args(argv)

    workspace = _workspace_root(args.workspace)
    if args.uninstall:
        return uninstall(workspace)
    return install(workspace, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
