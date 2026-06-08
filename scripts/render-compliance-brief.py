#!/usr/bin/env python3
"""render-compliance-brief.py - render Compliance Brief (D-144, S3 Fase F).

Wires the four S3 evidence sources into one Markdown brief:

  audit-log.py        -> §3 architectural decisions audit trail
  sbom-generator.py   -> §2 stack + SBOM
  ai-ops-report.py    -> §5 AI operations posture
  risk-register.md    -> §6 risk posture (workspace + project overlay)

Template: templates/operational/compliance-brief/compliance-brief.md.j2

Uses jinja2 (already a workspace dep — see pyproject.toml). Outputs to
stdout by default; `--output` to write a file (typical: docs/compliance-brief.md
under the project's own tree, or tmp/ for review pre-delivery).

Usage:
    python scripts/render-compliance-brief.py \\
        --project . \\
        --project-name techlab-architecture \\
        --client <id> \\
        --output tmp/brief.md

When --client is omitted, AI ops section is rendered without telemetry data
(template emits an "opt-in" message). When --client is set but the metrics
file is missing, same result — the brief stays honest.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from cli_utils import force_utf8_stdio


SCRIPTS = Path(__file__).resolve().parent


def _import(script_filename: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, SCRIPTS / script_filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def find_workspace(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "scripts").is_dir():
            return candidate
    sys.exit(f"error: workspace root not found from {start}")


# ── Risk register parsing (very light) ───────────────────────────────────────


_RISK_HEADER_RE = re.compile(r"^###\s+(R-\d{3})\s+[—-]\s+(.+)$", re.MULTILINE)


def parse_risk_register(workspace: Path) -> list[dict]:
    """Extract the H3 risk entries from docs/governance/risk-register.md.

    Returns a list of {id, title, status} for §6 summary. Full content stays
    in the file; brief only summarises (with a reference link).
    """
    rr = workspace / "docs" / "governance" / "risk-register.md"
    if not rr.is_file():
        return []
    text = rr.read_text(encoding="utf-8", errors="replace")
    risks: list[dict] = []
    matches = list(_RISK_HEADER_RE.finditer(text))
    for i, m in enumerate(matches):
        risk_id = m.group(1)
        title = m.group(2).strip()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end]
        status_match = re.search(r"\|\s*Status\s*\|\s*([^|]+?)\s*\|", body, re.IGNORECASE)
        status = status_match.group(1).strip() if status_match else "unknown"
        risks.append({"id": risk_id, "title": title, "status": status})
    return risks


# ── Top components helper ────────────────────────────────────────────────────


def select_top_required(components: list[dict], limit: int = 12) -> list[dict]:
    req = [c for c in components if c.get("scope") == "required"]
    req.sort(key=lambda c: c.get("name", ""))
    return req[:limit]


def select_sbom_sources(components: list[dict]) -> list[str]:
    sources: set[str] = set()
    for c in components:
        for prop in c.get("properties") or []:
            if prop.get("name") == "techlab:source":
                src = prop["value"].split(":")[0]
                sources.add(src)
    return sorted(sources)


# ── Lock SHA discovery ───────────────────────────────────────────────────────


def discover_lock_sha(project: Path) -> str | None:
    """Pull the workspace_version_sha (if present) from architecture.lock."""
    lock = project / "architecture.lock"
    if not lock.is_file():
        return None
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
        return data.get("workspace_sha") or data.get("workspaceSha") or data.get("sha")
    except (json.JSONDecodeError, OSError):
        return None


# ── Workspace version ────────────────────────────────────────────────────────


def workspace_version(workspace: Path) -> str:
    pp = workspace / "pyproject.toml"
    if not pp.is_file():
        return "unknown"
    try:
        import tomllib
        with pp.open("rb") as fh:
            data = tomllib.load(fh)
        return (data.get("project") or {}).get("version") or "unknown"
    except Exception:
        return "unknown"


# ── Main render ──────────────────────────────────────────────────────────────


def render_brief(args, workspace: Path) -> str:
    audit_mod = _import("audit-log.py", "audit_log")
    sbom_mod = _import("sbom-generator.py", "sbom_generator")
    ai_ops_mod = _import("ai-ops-report.py", "ai_ops_report")

    project_path = args.project.resolve()
    # Audit log: walk repo history of the workspace (or the project, if user
    # passed --project-as-repo). Default = workspace because the consolidation
    # doc lives there and D-NNN tracking is workspace-side.
    audit_repo = workspace if not args.project_as_repo else project_path
    audit_report = audit_mod.build_audit_report(audit_repo, last=args.audit_last)

    # SBOM: walks the project tree.
    sbom = sbom_mod.build_sbom(
        project_path,
        component_name=args.project_name,
        component_version=args.project_version,
    )

    # AI ops: telemetry for this project (if client id given and file exists).
    ai_ops_report = None
    ai_ops_path = None
    if args.client:
        ai_ops_path = ai_ops_mod.discover_metrics_file(workspace, args.client)
        ai_ops_report = ai_ops_mod.build_ai_ops_report(
            metrics_file=ai_ops_path,
            workspace=workspace,
            window_days=args.ai_ops_window,
        )

    workspace_risks = parse_risk_register(workspace)

    # Jinja render
    try:
        import jinja2
    except ImportError:
        sys.exit("error: jinja2 not installed. Run `pip install jinja2`. (workspace dep per pyproject.toml)")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(workspace / "templates" / "operational" / "compliance-brief")),
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template("compliance-brief.md.j2")

    sbom_components = sbom["components"]
    ai_ops_dict = None
    if ai_ops_report is not None:
        from dataclasses import asdict
        ai_ops_dict = asdict(ai_ops_report)

    audit_entries_dict = [
        # convert dataclass entries to dicts for the template
        {
            "short_sha": e.short_sha,
            "decision_ids": e.decision_ids,
            "subject": e.subject,
            "gpg_verified": e.gpg_verified,
        }
        for e in audit_report.entries[: args.recent_decisions]
    ]
    from dataclasses import asdict as _asdict
    audit_summary = _asdict(audit_report)

    context = {
        "project_name": args.project_name or sbom["metadata"]["component"]["name"],
        "project_version": args.project_version or sbom["metadata"]["component"]["version"],
        "project_description": args.project_description,
        "workspace_version": workspace_version(workspace),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": args.status or "DRAFT — for review with signing architect",
        "lock_sha": discover_lock_sha(project_path),
        "signing_architect": args.signing_architect,
        "signing_contact": args.signing_contact,
        "signing_key": args.signing_key,
        "architect_in_chief": args.architect_in_chief,
        "architect_contact": args.architect_contact,
        "security_contact": args.security_contact,
        "next_review_date": args.next_review,
        "stack_summary": args.stack_summary,
        # SBOM
        "sbom": sbom,
        "sbom_sources": select_sbom_sources(sbom_components),
        "sbom_top_required": select_top_required(sbom_components, args.sbom_top),
        "sbom_artifact_path": args.sbom_path,
        # Audit
        "audit": audit_summary,
        "recent_decisions": audit_entries_dict,
        "recent_decisions_count": len(audit_entries_dict),
        "audit_artifact_path": args.audit_path,
        # CI / quality
        "smoke_total": args.smoke_total,
        "smoke_status": args.smoke_status,
        "ci_workflow": args.ci_workflow,
        "ci_policies": None,  # template has sensible defaults
        # AI ops
        "ai_ops": ai_ops_dict,
        "ai_ops_artifact_path": str(ai_ops_path) if ai_ops_path else None,
        # Risk
        "workspace_risks": workspace_risks,
        "project_risks": None,  # caller injects via metadata file later
    }

    return tmpl.render(**context)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="render-compliance-brief",
        description="Render the Compliance Brief Markdown from S3 evidence sources.",
    )
    p.add_argument("--project", type=Path, default=Path("."),
                   help="Project to walk for SBOM + lock discovery (default: cwd).")
    p.add_argument("--project-name", type=str, default=None)
    p.add_argument("--project-version", type=str, default=None)
    p.add_argument("--project-description", type=str, default=None)
    p.add_argument("--project-as-repo", action="store_true",
                   help="Use --project as the git repo for audit-log (default: workspace).")
    p.add_argument("--workspace", type=Path, default=None)
    p.add_argument("--client", type=str, default=None,
                   help="Client id for AI ops telemetry lookup (clients/<id>/metrics.jsonl).")
    p.add_argument("--audit-last", type=int, default=30)
    p.add_argument("--audit-path", type=str, default=None)
    p.add_argument("--sbom-path", type=str, default=None)
    p.add_argument("--sbom-top", type=int, default=12)
    p.add_argument("--recent-decisions", type=int, default=10)
    p.add_argument("--ai-ops-window", type=int, default=30)
    p.add_argument("--smoke-total", type=str, default=None)
    p.add_argument("--smoke-status", type=str, default=None)
    p.add_argument("--ci-workflow", type=str, default=None)
    p.add_argument("--status", type=str, default=None)
    p.add_argument("--stack-summary", type=str, default=None)
    p.add_argument("--signing-architect", type=str, default=None)
    p.add_argument("--signing-contact", type=str, default=None)
    p.add_argument("--signing-key", type=str, default=None)
    p.add_argument("--architect-in-chief", type=str, default=None)
    p.add_argument("--architect-contact", type=str, default=None)
    p.add_argument("--security-contact", type=str, default=None)
    p.add_argument("--next-review", type=str, default=None)
    p.add_argument("--output", type=Path, default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    args = _build_parser().parse_args(argv)
    workspace = args.workspace.resolve() if args.workspace else find_workspace(Path.cwd().resolve())
    out = render_brief(args, workspace)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
        print(f"OK: Compliance Brief written to {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
