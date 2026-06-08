#!/usr/bin/env python3
"""Replay deferred gates from the architecture master-plan ledger.

P1 — D3 (docs/architecture/shared/workflow-improvements.md): gates that could not run
during scaffold (toolchain absent) are recorded in a consolidated "Ledger de gates
diferidos" table in the master-plan, each with its exact recovery command. This tool
reads that ledger, checks tool availability via `preflight.py`, runs the recovery
command for every gate whose tool is now present, and (with --update) rewrites the row
status. Gates whose tool is still absent stay `diferido` (reported, never silently dropped).

CLI:
    python scripts/be-gates-replay.py                      # BE master-plan, dry-run report
    python scripts/be-gates-replay.py --run                # actually run runnable gates
    python scripts/be-gates-replay.py --run --update       # run + rewrite row status
    python scripts/be-gates-replay.py --ledger <path.md>   # custom ledger file

Exit code: 0 if nothing failed; 1 if any executed gate failed.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from preflight import GATES, resolve_tool  # noqa: E402

LEDGER_HEADING = "## Ledger de gates diferidos"
BE_MASTER_PLAN = ROOT / "docs" / "architecture" / "backend" / "plans" / "architecture-master-plan.md"

_ROW = re.compile(r"^\|(.+)\|\s*$")


def _split_row(line: str) -> list[str]:
    # strip leading/trailing pipe, split, trim cells
    inner = line.strip()
    inner = inner[1:] if inner.startswith("|") else inner
    inner = inner[:-1] if inner.endswith("|") else inner
    return [c.strip() for c in inner.split("|")]


def parse_ledger(text: str) -> tuple[list[str], list[dict]]:
    """Return (header_cells, rows). Each row is a dict keyed by header cell name plus
    `_lineno` (index into the file's line list) for in-place rewrite."""
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.strip() == LEDGER_HEADING), None)
    if start is None:
        return [], []
    header: list[str] = []
    rows: list[dict] = []
    i = start + 1
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("## "):  # next section
            break
        if _ROW.match(ln):
            cells = _split_row(ln)
            if not header:
                header = cells
            elif set(cells) <= {"", "---", ":---", "---:", ":---:"} or all(set(c) <= {"-", ":"} for c in cells if c):
                pass  # separator row
            else:
                row = {header[j]: cells[j] for j in range(min(len(header), len(cells)))}
                row["_lineno"] = i
                rows.append(row)
        i += 1
    return header, rows


def _recover_cmd(row: dict) -> str:
    for k, v in row.items():
        if k.lower().startswith("comando"):
            return v.strip().strip("`")
    return ""


def _gate_name(row: dict) -> str:
    return row.get("Gate", "").strip()


def _status(row: dict) -> str:
    return row.get("Status", "").strip().lower()


def main(argv: list[str] | None = None) -> int:
    try:
        from cli_utils import force_utf8_stdio
        force_utf8_stdio()
    except Exception:
        pass

    parser = argparse.ArgumentParser(prog="be-gates-replay.py",
                                     description="Roda gates diferidos do ledger do master-plan.")
    parser.add_argument("--ledger", type=Path, default=BE_MASTER_PLAN,
                        help="Arquivo do master-plan com a seção 'Ledger de gates diferidos'.")
    parser.add_argument("--run", action="store_true",
                        help="Executa de fato os gates runnable (default: só reporta).")
    parser.add_argument("--update", action="store_true",
                        help="Reescreve o Status da linha (ok/fail) após executar (requer --run).")
    args = parser.parse_args(argv)

    ledger = args.ledger.resolve()
    if not ledger.is_file():
        print(f"[!] Ledger não encontrado: {ledger}")
        return 0

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(ROOT))
        except ValueError:
            return str(p)

    text = ledger.read_text(encoding="utf-8")
    header, rows = parse_ledger(text)
    if not header:
        print(f"[i] Nenhuma seção '{LEDGER_HEADING}' em {ledger.name} — nada a fazer.")
        return 0

    pending = [r for r in rows if _status(r) in ("diferido", "deferido", "pendente")]
    print(f"Ledger: {_rel(ledger)}")
    print(f"  {len(rows)} linha(s), {len(pending)} diferida(s)\n")
    if not pending:
        print("  Nada diferido — ledger limpo.")
        return 0

    lines = text.splitlines()
    failures = 0
    ran = 0
    for r in pending:
        gate = _gate_name(r)
        cmd = _recover_cmd(r)
        spec = GATES.get(gate, {})
        tool = spec.get("tool", "?")
        layer = spec.get("layer", "backend")
        available = resolve_tool(tool) is not None if tool != "?" else False

        if not available:
            print(f"  🚫 {gate:<18} mantido diferido — tool '{tool}' ausente")
            continue
        if not args.run:
            print(f"  ▶️  {gate:<18} runnable — {cmd}  (use --run para executar)")
            continue

        cwd = ROOT / ("frontend" if layer == "frontend" else "backend")
        print(f"  ▶️  {gate:<18} executando: {cmd}  (cwd={cwd.name})")
        try:
            proc = subprocess.run(cmd, shell=True, cwd=str(cwd),
                                  capture_output=True, text=True, timeout=600)
            ok = proc.returncode == 0
        except (subprocess.TimeoutExpired, OSError) as e:
            ok = False
            proc = None
            print(f"      erro de invocação: {e}")
        ran += 1
        if ok:
            print(f"      ✅ {gate} OK")
            new_status = "ok"
        else:
            failures += 1
            print(f"      ❌ {gate} FAIL")
            if proc is not None:
                tail = (proc.stdout or "")[-400:] + (proc.stderr or "")[-400:]
                for tl in tail.splitlines()[-6:]:
                    print(f"        {tl}")
            new_status = "fail"

        if args.update and "Status" in r:
            ln_idx = r["_lineno"]
            lines[ln_idx] = re.sub(r"(diferido|deferido|pendente)\s*\|?\s*$",
                                   f"{new_status} |", lines[ln_idx], flags=re.IGNORECASE)

    if args.run and args.update:
        ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\n  Ledger atualizado: {ran} gate(s) executado(s).")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
