#!/usr/bin/env python3
"""techlab.py - unified CLI for techlab-architecture workspace (D-118, automations F1).

Dispatches to the per-script CLIs that already exist in scripts/. Each
subcommand resolves its target script via importlib + swaps sys.argv
before invoking the script's main(). No subprocess overhead; shares the
Python startup. Stdlib only (no Click dep).

Install:
    pip install -e .                # makes `techlab` available globally
    # ...or just run via:
    python scripts/techlab.py <command> [args...]

Usage:
    techlab --help                  # show grouped command list
    techlab <command> --help        # delegates to the script's --help
    techlab new-project bootstrap --target ~/dev/bosq
    techlab arch-bump --aspect rbac --dry-run
    techlab impact --all-aspects
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from cli_utils import force_utf8_stdio


SCRIPTS_DIR = Path(__file__).resolve().parent


# ── Command catalog ──────────────────────────────────────────────────────────
#
# Mapping: subcommand-name -> (script-filename, one-line-summary, group)
# Groups: "lifecycle", "architecture", "codegen", "workflow"

COMMAND_MAP: dict[str, tuple[str, str, str]] = {
    # Project lifecycle
    "new-project":       ("new-project.py",          "orchestrate project bootstrap..frontend-skeleton", "lifecycle"),
    "context":           ("context.py",              "CRUD on project-context.json", "lifecycle"),
    "checklist":         ("checklist.py",            "manage project-checklist.md", "lifecycle"),
    "journal":           ("journal.py",              "append project-journal.md", "lifecycle"),
    "sync-techlab-ai":   ("sync-techlab-ai.py",      "docs-only sync of pinned techlab-ai snapshot", "lifecycle"),
    "ingest-discovery":  ("ingest_discovery.py",     "Pre-0 ingestion from BA artifacts (D-073)", "lifecycle"),

    # Architecture management
    "validate-arch":     ("arch_decisions.py",       "structural + cross-validation of *.arch.json", "architecture"),
    "validate-ears":     ("be-validate-ears.py",     "EARS notation in service-specs (D-111)", "architecture"),
    "check-orphans":     ("be-check-orphans.py",     "workspace orphan-files detector (D-112)", "architecture"),
    "impact":            ("impact_analysis.py",      "workspace-side impact analysis (D-096..D-110)", "architecture"),
    "drift-check":       ("be-architect-drift-check.py", "project-side drift detector", "architecture"),
    "upgrade":           ("be-architect-upgrade.py", "apply workspace evolution to a project", "architecture"),
    "arch-bump":         ("be-arch-bump.py",         "semver bump suggester for an aspect (D-116)", "architecture"),
    "arch-migration":    ("be-arch-migration.py",    "migration plan for an aspect change (D-117)", "architecture"),
    "migrate-deps":      ("be-migrate-arch-deps.py", "inject arch_dependencies frontmatter (D-109)", "architecture"),

    # Code generation
    "entity-gen":        ("be-entity-generator.py",  "generate domain/JPA/controllers from SQL+spec", "codegen"),
    "module-gen":        ("be-module-generator.py",  "generate Spring Boot module", "codegen"),
    "bdd-gen":           ("be-bdd-generator.py",     "generate Cucumber BDD infrastructure", "codegen"),
    "migration-gen":     ("be-migration-generator.py", "generate Flyway V1 from data-model.md", "codegen"),
    "infra-gen":         ("be-infra-generator.py",   "CI + docker-compose + gateway config", "codegen"),
    "scaffold":          ("be-scaffold.py",          "scaffold files from plan-<ISSUE_ID>.md", "codegen"),
    "render":            ("render.py",               "generic Jinja renderer", "codegen"),
    "file-guard":        ("be-file-guard.py",        "atomic file creation guard", "codegen"),

    # Smoke + dev workflow
    "smoke-scaffold":    ("be-smoke-scaffold.py",    "validate a generated project (D-113)", "workflow"),
    "install-hooks":     ("install-hooks.py",        "install pre-commit hook (D-115)", "workflow"),
    "pre-commit":        ("be-pre-commit-check.py",  "run pre-commit checks on staged files (D-115)", "workflow"),
}

GROUP_TITLES = {
    "lifecycle":     "Project lifecycle",
    "architecture":  "Architecture management",
    "codegen":       "Code generation",
    "workflow":      "Smoke + dev workflow",
}
GROUP_ORDER = ["lifecycle", "architecture", "codegen", "workflow"]


# ── Dispatch ─────────────────────────────────────────────────────────────────


def _load_script(script_filename: str):
    """Load a sibling script via importlib. Registers in sys.modules so
    dataclass introspection works on Python 3.12+ (lesson from D-085, D-111)."""
    path = SCRIPTS_DIR / script_filename
    if not path.is_file():
        sys.exit(f"error: target script not found: {path}")
    module_name = script_filename.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _record_metric(cmd: str, argv: list[str], elapsed: float, rc: int) -> None:
    """Append one JSON-lines record to TECHLAB_METRICS_FILE when set (D-119).

    Failures are silently swallowed — metrics must never block real work.
    File format: one JSON object per line so it's append-safe and
    machine-readable without loading the whole file.

    To activate: set env var TECHLAB_METRICS_FILE=/path/to/metrics.jsonl
    before invoking techlab.  A sensible default is
    clients/<project-id>/metrics.jsonl.

    Fields:
        command       - techlab subcommand name
        args          - remaining argv passed to the subcommand
        elapsed_s     - wall-clock seconds (float, 3 decimal places)
        exit_code     - return code from the subcommand
        timestamp     - ISO-8601 UTC
        claude_tokens - placeholder; populate externally from API logs (D-119)
    """
    metrics_file = os.environ.get("TECHLAB_METRICS_FILE")
    if not metrics_file:
        return
    record = {
        "command": cmd,
        "args": list(argv),
        "elapsed_s": round(elapsed, 3),
        "exit_code": rc,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "claude_tokens": 0,
    }
    try:
        p = Path(metrics_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass


def dispatch(cmd: str, argv: list[str]) -> int:
    """Run the target script's main() with argv. Every workspace script
    reads sys.argv inside its own argparse parser, so we temporarily swap
    sys.argv. SystemExit (raised by argparse on error/--help) is surfaced
    as the return code."""
    if cmd not in COMMAND_MAP:
        sys.exit(f"error: unknown command {cmd!r}. Run 'techlab --help' for the catalog.")

    script_filename, _summary, _group = COMMAND_MAP[cmd]
    mod = _load_script(script_filename)
    if not hasattr(mod, "main"):
        sys.exit(f"error: {script_filename} has no main() function")

    saved_argv = sys.argv
    t0 = time.perf_counter()
    try:
        sys.argv = [script_filename] + list(argv)
        try:
            rc = mod.main()
        except SystemExit as e:
            if e.code is None:
                rc = 0
            elif isinstance(e.code, int):
                rc = e.code
            else:
                # sys.exit("message") -> non-zero
                print(str(e.code), file=sys.stderr)
                rc = 1
        else:
            rc = rc if isinstance(rc, int) else 0
    finally:
        sys.argv = saved_argv
        _record_metric(cmd, argv, time.perf_counter() - t0, rc)  # D-119
    return rc


# ── Help ─────────────────────────────────────────────────────────────────────


def _render_catalog() -> str:
    lines = [
        "techlab — unified CLI for the techlab-architecture workspace",
        "",
        "Usage:",
        "  techlab <command> [args...]",
        "  techlab <command> --help          (delegates to the target script)",
        "",
    ]
    for group in GROUP_ORDER:
        cmds = [(name, summary) for name, (_, summary, g) in COMMAND_MAP.items() if g == group]
        if not cmds:
            continue
        lines.append(f"{GROUP_TITLES[group]}:")
        for name, summary in cmds:
            lines.append(f"  {name:<22s} {summary}")
        lines.append("")
    lines.append("Run 'techlab --list' for a flat list with the underlying script name.")
    return "\n".join(lines)


def _render_list() -> str:
    """Flat machine-readable list: <subcommand>  <script-filename>."""
    return "\n".join(
        f"{name:<22s} {script}"
        for name, (script, _summary, _group) in COMMAND_MAP.items()
    )


# ── Entry point ──────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    raw = list(sys.argv[1:] if argv is None else argv)

    if not raw or raw[0] in ("-h", "--help"):
        print(_render_catalog())
        return 0
    if raw[0] == "--list":
        print(_render_list())
        return 0
    if raw[0] == "--version":
        print("techlab 0.4.0")  # mirrors pyproject.toml version
        return 0

    cmd = raw[0]
    remainder = raw[1:]
    return dispatch(cmd, remainder)


if __name__ == "__main__":
    sys.exit(main())
