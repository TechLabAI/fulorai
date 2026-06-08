#!/usr/bin/env python3
"""ai-ops-report.py - aggregate AI Operations telemetry (D-143, Pole Position S3 Fase D).

Consumes the JSON-lines metrics file produced by techlab.py
(`TECHLAB_METRICS_FILE`, D-119) and emits an aggregated report covering:

  - invocation counts per command
  - wall-clock totals + percentiles (p50, p95)
  - exit-code distribution (success vs failure)
  - token totals (when populated externally; see D-119 placeholder)
  - estimated USD cost (when --pricing supplied)
  - time-window scoping (--window-days)

Privacy policy (D-143):
  - opt-in via env var TECHLAB_METRICS_FILE; absence -> nothing written.
  - file lives locally under clients/<id>/metrics.jsonl by default.
  - no PII fields collected. `args` are commit-style arg lists, not file
    contents nor prompts. If `args` contains paths, they remain local-only.
  - reporter is read-only; never mutates the source file.

Usage:
    python scripts/ai-ops-report.py --client bosq
    python scripts/ai-ops-report.py --metrics-file clients/bosq/metrics.jsonl --window-days 90
    python scripts/ai-ops-report.py --client bosq --format json

Stdlib only. Coordinates with S1 Fase A (D-119 / D-120).
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

from cli_utils import force_utf8_stdio


# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_PRICING = {
    # USD per million tokens, default = 0.0 (no estimation)
    # Caller can pass --pricing to override.
    "input": 0.0,
    "output": 0.0,
}


# ── Data ─────────────────────────────────────────────────────────────────────


@dataclass
class CommandStats:
    command: str
    invocations: int = 0
    total_elapsed_s: float = 0.0
    p50_s: float = 0.0
    p95_s: float = 0.0
    max_s: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    total_tokens: int = 0


@dataclass
class Report:
    source: str
    workspace: str
    window_days: int | None
    generated_at: str
    span_start: str | None
    span_end: str | None
    total_invocations: int
    distinct_commands: int
    overall_success_rate: float
    overall_total_elapsed_s: float
    overall_total_tokens: int
    estimated_cost_usd: float
    per_command: list[CommandStats] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# ── Reading ──────────────────────────────────────────────────────────────────


def discover_metrics_file(workspace: Path, client_id: str) -> Path:
    """Default location per D-119: clients/<id>/metrics.jsonl."""
    return workspace / "clients" / client_id / "metrics.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSON-lines file. Skip empty / malformed lines silently —
    metrics writer is best-effort (D-119 swallows OSError); reader stays
    forgiving so a partial line at the end doesn't lose the whole report."""
    if not path.is_file():
        return []
    records: list[dict] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            records.append(obj)
    return records


# ── Filtering ────────────────────────────────────────────────────────────────


def parse_record_ts(rec: dict) -> datetime | None:
    """Parse the ISO-8601 UTC timestamp written by D-119 (`%Y-%m-%dT%H:%M:%SZ`)."""
    ts = rec.get("timestamp")
    if not isinstance(ts, str):
        return None
    # Try the strict D-119 format first; fall back to fromisoformat for
    # forward compatibility if anyone migrates to a richer format.
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def filter_window(records: list[dict], window_days: int | None, now: datetime | None = None) -> list[dict]:
    """Keep records within the last `window_days`. None = no filter."""
    if window_days is None or window_days <= 0:
        return records
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=window_days)
    out: list[dict] = []
    for r in records:
        ts = parse_record_ts(r)
        if ts is None or ts >= cutoff:
            out.append(r)
    return out


# ── Aggregation ──────────────────────────────────────────────────────────────


def _percentile(values: list[float], p: float) -> float:
    """Linear-interpolation percentile (matches numpy.percentile default)."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] + (s[c] - s[f]) * (k - f)


def aggregate(records: list[dict]) -> dict[str, CommandStats]:
    by_cmd: dict[str, list[dict]] = {}
    for r in records:
        cmd = r.get("command") or "<unknown>"
        by_cmd.setdefault(cmd, []).append(r)

    stats_by_cmd: dict[str, CommandStats] = {}
    for cmd, group in by_cmd.items():
        elapsed = [float(r.get("elapsed_s") or 0) for r in group]
        tokens = [int(r.get("claude_tokens") or 0) for r in group]
        successes = sum(1 for r in group if (r.get("exit_code") or 0) == 0)
        failures = len(group) - successes
        stats_by_cmd[cmd] = CommandStats(
            command=cmd,
            invocations=len(group),
            total_elapsed_s=round(sum(elapsed), 3),
            p50_s=round(_percentile(elapsed, 0.50), 3),
            p95_s=round(_percentile(elapsed, 0.95), 3),
            max_s=round(max(elapsed) if elapsed else 0.0, 3),
            success_count=successes,
            failure_count=failures,
            total_tokens=sum(tokens),
        )
    return stats_by_cmd


def compute_estimated_cost(total_tokens: int, pricing: dict[str, float]) -> float:
    """Estimate USD given total tokens and per-million pricing.

    D-119 stores a single `claude_tokens` field (not input/output split).
    Use the input rate as the simpler default; doc the limit in the report.
    """
    return round((total_tokens / 1_000_000.0) * pricing.get("input", 0.0), 4)


# ── Report build ─────────────────────────────────────────────────────────────


def build_report(
    records: list[dict],
    *,
    source: str,
    workspace: Path,
    window_days: int | None,
    pricing: dict[str, float] | None = None,
) -> Report:
    pricing = pricing or DEFAULT_PRICING
    timestamps = [parse_record_ts(r) for r in records]
    timestamps = [t for t in timestamps if t is not None]
    span_start = min(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ") if timestamps else None
    span_end = max(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ") if timestamps else None

    per_cmd = aggregate(records)
    overall_elapsed = round(sum(s.total_elapsed_s for s in per_cmd.values()), 3)
    overall_tokens = sum(s.total_tokens for s in per_cmd.values())
    total = sum(s.invocations for s in per_cmd.values())
    success = sum(s.success_count for s in per_cmd.values())
    success_rate = round((success / total) if total else 0.0, 4)

    notes = []
    if overall_tokens == 0 and total > 0:
        notes.append(
            "claude_tokens=0 across all records. "
            "D-119 ships the field as placeholder; populate from Claude Code session logs."
        )
    if not records:
        notes.append("No metrics records found in window. Check TECHLAB_METRICS_FILE was set.")

    return Report(
        source=source,
        workspace=str(workspace),
        window_days=window_days,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        span_start=span_start,
        span_end=span_end,
        total_invocations=total,
        distinct_commands=len(per_cmd),
        overall_success_rate=success_rate,
        overall_total_elapsed_s=overall_elapsed,
        overall_total_tokens=overall_tokens,
        estimated_cost_usd=compute_estimated_cost(overall_tokens, pricing),
        per_command=sorted(per_cmd.values(), key=lambda s: s.invocations, reverse=True),
        notes=notes,
    )


# ── Rendering ────────────────────────────────────────────────────────────────


def render_json(report: Report) -> str:
    return json.dumps(asdict(report), indent=2, ensure_ascii=False)


def render_markdown(report: Report) -> str:
    lines: list[str] = []
    lines.append("# AI Operations report")
    lines.append("")
    lines.append(f"> **Source:** `{report.source}`")
    lines.append(f"> **Workspace:** `{report.workspace}`")
    win = f"last {report.window_days} days" if report.window_days else "all-time"
    lines.append(f"> **Window:** {win}")
    lines.append(f"> **Generated:** {report.generated_at}")
    if report.span_start and report.span_end:
        lines.append(f"> **Span:** {report.span_start} to {report.span_end}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Invocations:** {report.total_invocations}")
    lines.append(f"- **Distinct commands:** {report.distinct_commands}")
    pct = report.overall_success_rate * 100
    lines.append(f"- **Success rate:** {pct:.1f}%")
    lines.append(f"- **Wall-clock total:** {report.overall_total_elapsed_s:.3f}s")
    lines.append(f"- **Tokens total:** {report.overall_total_tokens}")
    if report.estimated_cost_usd > 0:
        lines.append(f"- **Estimated cost:** USD {report.estimated_cost_usd:.4f}")
    lines.append("")
    if report.notes:
        lines.append("## Notes")
        lines.append("")
        for n in report.notes:
            lines.append(f"- {n}")
        lines.append("")
    lines.append("## Per command")
    lines.append("")
    if not report.per_command:
        lines.append("_No commands in window._")
        return "\n".join(lines) + "\n"
    lines.append("| Command | Invocations | p50 (s) | p95 (s) | Max (s) | Total (s) | Success | Failures | Tokens |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for s in report.per_command:
        lines.append(
            f"| {s.command} | {s.invocations} | {s.p50_s:.3f} | {s.p95_s:.3f} | "
            f"{s.max_s:.3f} | {s.total_elapsed_s:.3f} | {s.success_count} | "
            f"{s.failure_count} | {s.total_tokens} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


# ── Public API ───────────────────────────────────────────────────────────────


def build_ai_ops_report(
    *,
    metrics_file: Path,
    workspace: Path,
    window_days: int | None = 30,
    pricing: dict[str, float] | None = None,
) -> Report:
    records = read_jsonl(metrics_file)
    filtered = filter_window(records, window_days)
    return build_report(
        filtered,
        source=str(metrics_file),
        workspace=workspace,
        window_days=window_days,
        pricing=pricing,
    )


# ── CLI ──────────────────────────────────────────────────────────────────────


def find_workspace(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "scripts").is_dir():
            return candidate
    sys.exit(f"error: workspace root not found from {start}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ai-ops-report",
        description="Aggregate AI Operations telemetry from TECHLAB_METRICS_FILE jsonl.",
    )
    src = p.add_mutually_exclusive_group()
    src.add_argument("--client", type=str, help="Client id; reads clients/<id>/metrics.jsonl.")
    src.add_argument("--metrics-file", type=Path, help="Explicit path to a metrics.jsonl file.")
    p.add_argument("--workspace", type=Path, default=None)
    p.add_argument("--window-days", type=int, default=30,
                   help="Window in days (default 30). Use 0 for all-time.")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--pricing-input", type=float, default=0.0,
                   help="USD per 1M input tokens. Default 0 (no cost estimation).")
    p.add_argument("--pricing-output", type=float, default=0.0,
                   help="USD per 1M output tokens. Default 0 (token field is single-counter today).")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    args = _build_parser().parse_args(argv)
    workspace = args.workspace.resolve() if args.workspace else find_workspace(Path.cwd().resolve())
    if args.metrics_file:
        metrics_file = args.metrics_file.resolve()
    elif args.client:
        metrics_file = discover_metrics_file(workspace, args.client)
    else:
        sys.exit("error: provide --client or --metrics-file")
    window = None if args.window_days == 0 else args.window_days
    pricing = {"input": args.pricing_input, "output": args.pricing_output}
    report = build_ai_ops_report(
        metrics_file=metrics_file,
        workspace=workspace,
        window_days=window,
        pricing=pricing,
    )
    payload = render_json(report) if args.format == "json" else render_markdown(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"OK: AI ops report written to {args.output} ({report.total_invocations} invocations)")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
