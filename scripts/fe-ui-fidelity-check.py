#!/usr/bin/env python3
"""fe-ui-fidelity-check.py — Static fidelity gate for UI issues (D-309, D-315).

LAYER 3 script (D-315): deterministic, no AI.

Checks performed:
  1. No hardcoded hex colors (#RGB / #RRGGBB / rgba()) in SCSS files.
  2. No hardcoded spacing/sizing px values > 4px in SCSS files.
  3. ChangeDetectionStrategy.OnPush in every *.component.ts.
  4. standalone: true in every *.component.ts.
  5. CSS classes from contract.json hybrid.custom present in SCSS (warning).

Exit codes (R3):
  0 — all checks passed (no blocking failures, no warnings)
  1 — warnings only (no blocking failures)
  2 — one or more blocking failures

Usage:
    python scripts/fe-ui-fidelity-check.py check \\
        --issue LEAD-FE-001 \\
        --component-dir frontend/libs/lead/feature-lead-list/src/lib \\
        --contract docs/architecture/frontend/issues/LEAD-FE-001.contract.json \\
        --report

    python scripts/fe-ui-fidelity-check.py check \\
        --issue LEAD-FE-001 \\
        --component-dir frontend/libs/lead/feature-lead-list/src/lib

R3: argparse, atomic write (state.json), OK:/error:, exit 0/1/2.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ── Check patterns ─────────────────────────────────────────────────────────────

# Blocking: hardcoded hex colors in SCSS
_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b")
# Blocking: hardcoded rgb/rgba values
_RGB_COLOR = re.compile(r"\brgba?\s*\(")
# Blocking: hardcoded hsl values
_HSL_COLOR = re.compile(r"\bhsla?\s*\(")

# Blocking: hardcoded px values in spacing properties > 4px
_SPACING_PROP_PX = re.compile(
    r"(?:^|\s|;|{)(margin|padding|gap|row-gap|column-gap|"
    r"width|min-width|max-width|height|min-height|max-height|"
    r"top|right|bottom|left|inset)\s*:\s*[^;{]*?(\d+)px",
    re.IGNORECASE | re.MULTILINE,
)

# Angular component checks
_ON_PUSH = re.compile(r"ChangeDetectionStrategy\s*\.\s*OnPush")
_STANDALONE = re.compile(r"standalone\s*:\s*true")
_CSS_VAR_REMAINING = re.compile(r"var\s*\(\s*--[\w-]+\s*\)")


@dataclass
class CheckResult:
    passed: bool
    blocking: bool
    violations: list[str] = field(default_factory=list)


@dataclass
class FidelityReport:
    issue: str
    component_dir: str
    overall_passed: bool
    blocking_failures: int
    warning_count: int
    checks: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


# ── Checkers ──────────────────────────────────────────────────────────────────


def _check_scss_hardcoded_colors(scss_files: list[Path]) -> CheckResult:
    violations: list[str] = []
    for f in scss_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pattern, name in [(_HEX_COLOR, "hex"), (_RGB_COLOR, "rgb/rgba"), (_HSL_COLOR, "hsl/hsla")]:
            for m in pattern.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                violations.append(f"  {f.name}:{line_no} — hardcoded {name}: {m.group(0)!r}")
    return CheckResult(passed=not violations, blocking=True, violations=violations)


def _check_scss_hardcoded_spacing(scss_files: list[Path]) -> CheckResult:
    violations: list[str] = []
    for f in scss_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in _SPACING_PROP_PX.finditer(text):
            px_val = int(m.group(2))
            if px_val > 4:  # 1-4px fine (borders, outline)
                line_no = text.count("\n", 0, m.start()) + 1
                violations.append(
                    f"  {f.name}:{line_no} — hardcoded {m.group(1)}: {px_val}px"
                    " (use SCSS token)"
                )
    return CheckResult(passed=not violations, blocking=True, violations=violations)


def _check_unmapped_vars(scss_files: list[Path]) -> CheckResult:
    """Warn when ported SCSS still contains raw var(--xxx) references."""
    violations: list[str] = []
    for f in scss_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in _CSS_VAR_REMAINING.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            violations.append(f"  {f.name}:{line_no} — unmapped {m.group(0).strip()}")
    return CheckResult(passed=not violations, blocking=False, violations=violations)


def _check_ts_on_push(ts_files: list[Path]) -> CheckResult:
    violations: list[str] = []
    for f in ts_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if not _ON_PUSH.search(text):
            violations.append(f"  {f.name} — missing ChangeDetectionStrategy.OnPush")
    return CheckResult(passed=not violations, blocking=True, violations=violations)


def _check_ts_standalone(ts_files: list[Path]) -> CheckResult:
    violations: list[str] = []
    for f in ts_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if not _STANDALONE.search(text):
            violations.append(f"  {f.name} — missing standalone: true")
    return CheckResult(passed=not violations, blocking=True, violations=violations)


def _check_contract_classes(scss_files: list[Path], contract_path: Path | None) -> CheckResult:
    """Warn if CSS classes from hybrid.custom in contract.json are absent in SCSS."""
    if contract_path is None or not contract_path.exists():
        return CheckResult(passed=True, blocking=False, violations=[])

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    custom_classes = contract.get("hybrid", {}).get("custom", [])
    if not custom_classes:
        return CheckResult(passed=True, blocking=False, violations=[])

    # Merge all SCSS text
    all_scss = "\n".join(
        f.read_text(encoding="utf-8", errors="ignore") for f in scss_files
    )
    violations: list[str] = []
    for cls in custom_classes:
        # Remove qualifiers like "table+sort+paginate" → check just "table"
        slug = cls.split("+")[0].strip()
        if slug and slug not in all_scss:
            violations.append(f"  custom class .{slug} not found in SCSS (from contract hybrid.custom)")
    return CheckResult(passed=not violations, blocking=False, violations=violations)


# ── Main ──────────────────────────────────────────────────────────────────────


def check(issue: str, component_dir: Path, contract_path: Path | None, report: bool) -> int:
    if not component_dir.is_dir():
        print(f"error: component-dir not found: {component_dir}", file=sys.stderr)
        return 1

    scss_files = list(component_dir.rglob("*.scss")) + list(component_dir.rglob("*.css"))
    ts_files = [f for f in component_dir.rglob("*.component.ts")]

    if not scss_files and not ts_files:
        print(f"error: no SCSS or *.component.ts files found in: {component_dir}", file=sys.stderr)
        return 2

    results: dict[str, CheckResult] = {
        "noHardcodedColors": _check_scss_hardcoded_colors(scss_files),
        "noHardcodedSpacing": _check_scss_hardcoded_spacing(scss_files),
        "unmappedVars": _check_unmapped_vars(scss_files),
        "onPush": _check_ts_on_push(ts_files),
        "standalone": _check_ts_standalone(ts_files),
        "contractClasses": _check_contract_classes(scss_files, contract_path),
    }

    blocking_failures = sum(1 for r in results.values() if not r.passed and r.blocking)
    warnings = sum(1 for r in results.values() if not r.passed and not r.blocking)
    overall_passed = blocking_failures == 0

    fidelity = FidelityReport(
        issue=issue,
        component_dir=str(component_dir),
        overall_passed=overall_passed,
        blocking_failures=blocking_failures,
        warning_count=warnings,
        checks={k: {"passed": v.passed, "blocking": v.blocking, "violations": v.violations}
                for k, v in results.items()},
    )

    # Write state JSON atomically
    out_path = component_dir / f"{issue}.fidelity.json"
    tmp = out_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(fidelity.as_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(out_path)

    if overall_passed:
        status = "OK"
        detail = f"{warnings} warning(s)" if warnings else "clean"
    else:
        status = "FAIL"
        detail = f"{blocking_failures} blocking failure(s)"

    print(f"{'OK' if overall_passed else 'error'}: fidelity check {issue} — {status} ({detail})")
    print(f"  -> {out_path}")

    if report or not overall_passed or warnings:
        print(f"\nFidelity report — {issue}")
        for name, r in results.items():
            icon = "OK " if r.passed else ("ERR" if r.blocking else "WRN")
            print(f"  [{icon}] {name}")
            for v in r.violations:
                print(v)

    return 0 if blocking_failures == 0 and warnings == 0 else (2 if blocking_failures > 0 else 1)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fe-ui-fidelity-check",
        description="Static fidelity gate for Angular UI issues (D-309, D-315).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    chk = sub.add_parser("check", help="Run all fidelity checks for an issue")
    chk.add_argument("--issue", required=True, metavar="ISSUE_ID",
                     help="Issue ID (e.g. LEAD-FE-001)")
    chk.add_argument("--component-dir", required=True, metavar="DIR",
                     help="Angular component lib directory to scan (e.g. frontend/libs/lead/feature-lead-list/src/lib)")
    chk.add_argument("--contract", metavar="FILE", default=None,
                     help="Path to <ISSUE_ID>.contract.json (optional — enables class presence check)")
    chk.add_argument("--report", action="store_true",
                     help="Print full violation details even when passing")

    args = parser.parse_args()

    if args.command == "check":
        contract_path = Path(args.contract).resolve() if args.contract else None
        sys.exit(check(
            args.issue,
            Path(args.component_dir).resolve(),
            contract_path,
            args.report,
        ))


if __name__ == "__main__":
    main()
