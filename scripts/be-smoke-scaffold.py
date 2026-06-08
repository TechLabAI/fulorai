#!/usr/bin/env python3
"""be-smoke-scaffold.py - validate a freshly-generated project (D-113, automations A4).

Takes the OUTPUT of `new-project.py bootstrap..frontend-skeleton` and runs
five checks. Designed to wrap the existing CI `smoke-test` job's
end-of-pipeline verification with something maintainable, AND to be
runnable locally after a manual pipeline run.

Checks:
  1. File counts per area vs tests/baseline.json (each area +/- tolerance)
  2. No unsubstituted `{{ var }}` or `{% block %}` artifacts in rendered
     output (frontend/* Angular bindings + templates/operational/ workspace
     templates are skipped intentionally)
  3. No obsolete references (`eerripe` outside _examples/, `TODO[lote-6a]`)
  4. Canonical required paths all present (from baseline.json)
  5. (optional, --full) Java compiles - `cd backend && gradlew compileJava`

Usage:
    python scripts/be-smoke-scaffold.py --target /tmp/smoke-bosq
    python scripts/be-smoke-scaffold.py --target /tmp/smoke-bosq --full
    python scripts/be-smoke-scaffold.py --target /tmp/smoke-bosq --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from cli_utils import force_utf8_stdio


_BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
    ".pdf", ".zip", ".jar", ".class",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".mp3", ".mp4", ".mov",
}

_SCAN_SKIP_PREFIXES = (
    ".git/",
    "frontend/apps/",
    "templates/operational/",
    "templates/architecture/",
    "scripts/",   # Python sources with f-string `{{ }}` escapes for generated Java
    "arch/decisions/",  # raw JSON with `{{ multi_tenancy_term }}` re-interpolated downstream
)

_OBSOLETE_ALLOW_DIRS = (
    "_examples/eerripe",
)

_JINJA_ARTIFACT_RE = re.compile(r"\{\{[^}]*\}\}|\{%[^%]*%\}")

# Default obsolete-ref patterns: EMPTY in normal mode (D-113).
#
# The plan original (A4) listed `eerripe` and `TODO[lote-6a]` as obsolete
# markers, but at the current state of the workspace:
#   - `eerripe` legitimately appears in `legacy.source: "eerripe"` config
#     entries and in `version: 1.0.0-eerripe-derived` strings that document
#     the framework's historical origin.
#   - `TODO[lote-6a]` is a stub marker the workspace ships intentionally
#     until Lote 6a (still pending) replaces the placeholders.
#
# Both should become real regressions only after their respective bumps
# land. The check kept its infrastructure ready (CheckResult + scan loop)
# so a future commit can populate _OBSOLETE_PATTERNS without touching the
# walker. `--obsolete-pattern <name>=<regex>` lets the CI pin a specific
# check ahead of that.
_OBSOLETE_PATTERNS: list[tuple[str, re.Pattern[str]]] = []


@dataclass
class CheckResult:
    name: str
    status: str
    details: list[str] = field(default_factory=list)

    def passed(self) -> bool:
        return self.status == "ok"


def _count_files(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for f in root.rglob("*") if f.is_file())


def check_file_counts(target: Path, baseline: dict) -> CheckResult:
    res = CheckResult(name="file_counts_per_area", status="ok")
    for area, spec in baseline.get("areas", {}).items():
        expected = spec.get("expected", 0)
        tolerance = spec.get("tolerance", 5)
        actual = _count_files(target / area)
        diff = abs(actual - expected)
        if diff > tolerance:
            res.status = "fail"
            res.details.append(
                f"{area}/: {actual} files (expected {expected} +/- {tolerance})"
            )
        else:
            res.details.append(f"{area}/: {actual} (within +/- {tolerance})")
    return res


def _walk_relevant(target: Path):
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(target).as_posix()
        if any(rel.startswith(p) for p in _SCAN_SKIP_PREFIXES):
            continue
        if path.suffix.lower() in _BINARY_SUFFIXES:
            continue
        try:
            yield rel, path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue


def _strip_fenced_blocks(text: str) -> str:
    """Replace contents inside triple-backtick fenced code blocks with empty
    lines so a regex sweep doesn't fire on documentation examples that
    legitimately show Jinja syntax (e.g. ears-notation.md teaching authors
    how to escape `{{ var }}`)."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def check_jinja_artifacts(target: Path) -> CheckResult:
    res = CheckResult(name="no_jinja_artifacts", status="ok")
    hits: list[str] = []
    for rel, text in _walk_relevant(target):
        if rel.endswith(".j2"):
            continue
        scan_text = _strip_fenced_blocks(text) if rel.endswith(".md") else text
        for m in _JINJA_ARTIFACT_RE.finditer(scan_text):
            hits.append(f"{rel}: {m.group(0)!r}")
            if len(hits) > 20:
                break
        if len(hits) > 20:
            break
    if hits:
        res.status = "fail"
        res.details = hits
    return res


def check_obsolete_refs(target: Path,
                        patterns: list[tuple[str, re.Pattern[str]]] | None = None
                        ) -> CheckResult:
    """Scan for obsolete-ref patterns. With no patterns, returns "skipped"
    so the empty default doesn't masquerade as a passing check."""
    effective = patterns if patterns is not None else _OBSOLETE_PATTERNS
    res = CheckResult(name="no_obsolete_refs", status="ok")
    if not effective:
        res.status = "skipped"
        res.details = ["no obsolete-ref patterns configured (see _OBSOLETE_PATTERNS)"]
        return res
    hits: list[str] = []
    for rel, text in _walk_relevant(target):
        if any(allow in rel for allow in _OBSOLETE_ALLOW_DIRS):
            continue
        for label, pattern in effective:
            if pattern.search(text):
                hits.append(f"{rel}: {label}")
                if len(hits) > 20:
                    break
        if len(hits) > 20:
            break
    if hits:
        res.status = "fail"
        res.details = hits
    return res


def check_canonical_paths(target: Path, baseline: dict) -> CheckResult:
    res = CheckResult(name="canonical_paths_present", status="ok")
    missing: list[str] = []
    for rel in baseline.get("required_paths", []):
        if not (target / rel).exists():
            missing.append(rel)
    if missing:
        res.status = "fail"
        res.details = [f"missing: {p}" for p in missing]
    else:
        res.details = [
            f"all {len(baseline.get('required_paths', []))} required paths present"
        ]
    return res


def check_java_compile(target: Path) -> CheckResult:
    res = CheckResult(name="java_compiles", status="ok")
    backend = target / "backend"
    if not backend.is_dir():
        res.status = "skipped"
        res.details = ["backend/ directory not present"]
        return res
    wrapper = backend / ("gradlew.bat" if sys.platform == "win32" else "gradlew")
    if not wrapper.is_file():
        res.status = "skipped"
        res.details = ["gradlew wrapper not present (backend not fully scaffolded)"]
        return res
    try:
        proc = subprocess.run(
            [str(wrapper), "compileJava", "--no-daemon", "-q"],
            cwd=str(backend),
            capture_output=True, text=True, timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        res.status = "fail"
        res.details = [f"gradlew invocation error: {e}"]
        return res
    if proc.returncode != 0:
        res.status = "fail"
        res.details = [proc.stdout[-500:], proc.stderr[-500:]]
    return res


def load_baseline(baseline_path: Path) -> dict:
    return json.loads(baseline_path.read_text(encoding="utf-8"))


def run_all(target: Path, baseline: dict, *, full: bool,
            obsolete_patterns: list[tuple[str, re.Pattern[str]]] | None = None
            ) -> list[CheckResult]:
    out = [
        check_file_counts(target, baseline),
        check_jinja_artifacts(target),
        check_obsolete_refs(target, obsolete_patterns),
        check_canonical_paths(target, baseline),
    ]
    if full:
        out.append(check_java_compile(target))
    return out


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-smoke-scaffold.py",
        description="Validate a freshly-generated project tree (D-113, automations A4).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Run new-project.py bootstrap..frontend-skeleton first, then point "
            "this script at the target.\n"
            "Exit codes: 0 = all green, 1 = at least one check failed.\n"
        ),
    )
    parser.add_argument("--target", type=Path, required=True,
                        help="Path to the generated project root.")
    parser.add_argument("--baseline", type=Path, default=None,
                        help="Override tests/baseline.json (default: workspace tests/).")
    parser.add_argument("--full", action="store_true",
                        help="Also run java_compiles (gradlew compileJava in backend/).")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of human-readable text.")
    parser.add_argument("--obsolete-pattern", action="append", default=[],
                        metavar="NAME=REGEX",
                        help="Append an obsolete-ref pattern. Repeatable. "
                             "Default patterns are empty; pass this flag "
                             "(or extend _OBSOLETE_PATTERNS in the script) "
                             "to enable the check.")
    args = parser.parse_args(argv)

    target = args.target.resolve()
    if not target.is_dir():
        sys.exit(f"error: --target {target} is not a directory")

    if args.baseline:
        baseline_path = args.baseline
    else:
        workspace = Path(__file__).resolve().parent.parent
        baseline_path = workspace / "tests" / "baseline.json"
    if not baseline_path.is_file():
        sys.exit(f"error: baseline file not found: {baseline_path}")
    baseline = load_baseline(baseline_path)

    extra_patterns: list[tuple[str, re.Pattern[str]]] = []
    for raw in args.obsolete_pattern:
        if "=" not in raw:
            sys.exit(f"error: --obsolete-pattern {raw!r} must be NAME=REGEX")
        name, _, regex = raw.partition("=")
        try:
            compiled = re.compile(regex)
        except re.error as exc:
            sys.exit(f"error: --obsolete-pattern {name!r} regex invalid: {exc}")
        extra_patterns.append((name, compiled))

    results = run_all(target, baseline, full=args.full,
                      obsolete_patterns=extra_patterns or None)
    n_fail = sum(1 for r in results if r.status == "fail")
    n_skip = sum(1 for r in results if r.status == "skipped")
    n_ok = sum(1 for r in results if r.status == "ok")

    if args.json:
        print(json.dumps({
            "target": str(target),
            "results": [
                {"name": r.name, "status": r.status, "details": r.details}
                for r in results
            ],
        }, indent=2))
    else:
        print(f"be-smoke-scaffold - {target}")
        for r in results:
            tag = {"ok": "OK", "fail": "FAIL", "skipped": "SKIP"}[r.status]
            print(f"  [{tag:4s}] {r.name}")
            for d in r.details:
                print(f"           {d}")
        print()
        print(f"Result: {n_ok} ok, {n_fail} fail, {n_skip} skipped.")

    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
