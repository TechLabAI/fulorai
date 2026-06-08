#!/usr/bin/env python3
"""be-pre-commit-check.py - pre-commit gating (D-115, automations D1).

Orchestrates the existing workspace validators against the set of files
about to be committed. Runs in <10s by invoking the validators only for
file classes that actually changed:

  templates/architecture/decisions/*.arch.json
      -> scripts/arch_decisions.py validate (structural, all aspects)

  templates/architecture/decisions/ OR templates/architecture/shared/
      -> scripts/be-check-orphans.py (workspace orphan detection)

  service-spec*.md AND/OR templates/sdd/service-spec/*.md.j2
      -> scripts/be-validate-ears.py --file <path> (per file)

Bypass: SKIP_HOOKS=1 env var OR git commit --no-verify.

Usage (from a git pre-commit hook):
    python scripts/be-pre-commit-check.py             # reads `git diff --cached`
    python scripts/be-pre-commit-check.py --staged-files a.md b.md  # explicit
    python scripts/be-pre-commit-check.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from cli_utils import force_utf8_stdio


def _workspace_root(start: Path) -> Path:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / "scripts" / "new-project.py").is_file() and (p / "templates").is_dir():
            return p
    sys.exit("error: could not locate workspace root from cwd")


def _staged_files(workspace: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=str(workspace),
            capture_output=True, text=True, check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        sys.exit(f"error: git diff --cached failed: {e}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def _run(cmd: list[str], workspace: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd, cwd=str(workspace), capture_output=True, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


def classify_changes(staged: list[str]) -> dict:
    """Bucket the staged file list into the three check-trigger categories."""
    arch_decisions = [
        f for f in staged
        if f.startswith("templates/architecture/decisions/")
        and f.endswith(".arch.json")
    ]
    arch_anywhere = [
        f for f in staged
        if f.startswith("templates/architecture/")
    ]
    service_specs = [
        f for f in staged
        if (
            (f.endswith("service-spec.md") or f.endswith("service-spec.md.j2"))
            or (
                f.startswith("templates/sdd/service-spec/")
                and (f.endswith(".md") or f.endswith(".md.j2"))
            )
        )
    ]
    return {
        "arch_decisions": arch_decisions,
        "arch_anywhere": arch_anywhere,
        "service_specs": service_specs,
    }


def run_checks(workspace: Path, staged: list[str], py: str | None = None) -> dict:
    """Run the pre-commit checks dictated by the staged file list.

    Returns a dict with `passed: bool`, `errors: list[str]`, and a per-check
    `details` block describing what ran and what each result was.
    """
    py = py or sys.executable
    buckets = classify_changes(staged)

    details: list[dict] = []
    errors: list[str] = []

    if buckets["arch_decisions"]:
        rc, out, err = _run(
            [py, "scripts/arch_decisions.py", "validate"], workspace
        )
        details.append({"name": "arch_decisions_validate", "ran": True,
                        "rc": rc, "stdout": out, "stderr": err,
                        "triggered_by": buckets["arch_decisions"]})
        if rc != 0:
            errors.append(f"arch_decisions validate failed (rc={rc}). "
                          f"See stderr above.")
    else:
        details.append({"name": "arch_decisions_validate", "ran": False,
                        "reason": "no decisions/*.arch.json staged"})

    if buckets["arch_anywhere"]:
        rc, out, err = _run(
            [py, "scripts/be-check-orphans.py"], workspace
        )
        details.append({"name": "be_check_orphans", "ran": True,
                        "rc": rc, "stdout": out, "stderr": err,
                        "triggered_by": buckets["arch_anywhere"]})
        if rc != 0:
            errors.append(f"be-check-orphans failed (rc={rc}). "
                          f"See stdout above.")
    else:
        details.append({"name": "be_check_orphans", "ran": False,
                        "reason": "no templates/architecture/ paths staged"})

    if buckets["service_specs"]:
        spec_errors: list[str] = []
        for spec in buckets["service_specs"]:
            rc, out, err = _run(
                [py, "scripts/be-validate-ears.py", "--file", spec],
                workspace,
            )
            if rc != 0:
                spec_errors.append(spec)
                errors.append(
                    f"be-validate-ears failed on {spec} (rc={rc}). "
                    f"Full output:\n{out}"
                )
        details.append({"name": "be_validate_ears", "ran": True,
                        "files": buckets["service_specs"],
                        "errors": spec_errors})
    else:
        details.append({"name": "be_validate_ears", "ran": False,
                        "reason": "no service-spec markdown staged"})

    return {
        "passed": not errors,
        "errors": errors,
        "details": details,
        "staged_files": staged,
    }


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    if os.environ.get("SKIP_HOOKS"):
        print("[pre-commit] SKIP_HOOKS set; bypassing checks", file=sys.stderr)
        return 0

    parser = argparse.ArgumentParser(
        prog="be-pre-commit-check.py",
        description="Run workspace validators on the about-to-commit file set (D-115).",
    )
    parser.add_argument("--workspace", type=Path, default=None,
                        help="Workspace root (default: walk up from cwd).")
    parser.add_argument("--staged-files", nargs="*", default=None,
                        help="Bypass `git diff --cached`; pass an explicit list.")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of human-readable text.")
    args = parser.parse_args(argv)

    workspace = _workspace_root(args.workspace or Path.cwd())
    staged = (
        args.staged_files
        if args.staged_files is not None
        else _staged_files(workspace)
    )

    if not staged:
        msg = "[pre-commit] no staged files; passing trivially."
        if args.json:
            print(json.dumps({"passed": True, "errors": [], "details": [],
                              "staged_files": []}, indent=2))
        else:
            print(msg)
        return 0

    report = run_checks(workspace, staged)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for d in report["details"]:
            if not d.get("ran"):
                continue
            print(f"--- {d['name']} ---")
            if "stdout" in d and d["stdout"]:
                print(d["stdout"].rstrip())
            if "stderr" in d and d["stderr"]:
                print(d["stderr"].rstrip(), file=sys.stderr)
        if report["errors"]:
            print()
            print("Pre-commit checks FAILED:")
            for e in report["errors"]:
                print(f"  - {e}")
            print()
            print("To bypass intentionally: SKIP_HOOKS=1 git commit ... "
                  "(or git commit --no-verify)")
        else:
            n_ran = sum(1 for d in report["details"] if d.get("ran"))
            print(f"[pre-commit] OK ({n_ran} check(s) ran; "
                  f"{len(staged)} file(s) staged).")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
