#!/usr/bin/env python3
"""Toolchain preflight for Journey OS scaffold/gates.

P1 — robustez de toolchain (docs/architecture/shared/workflow-improvements.md, A1/A2).

Detects which build tools are available in the environment BEFORE a command tries to
use them, so a missing tool produces an explicit "gate diferido + comando de recuperação"
up front, instead of a mid-run "command not found". This is the single source of truth
for the gate→tool mapping used by the scaffold scripts, the architecture autopilots, and
`be-gates-replay.py`.

CLI:
    python scripts/preflight.py                         # capability matrix (all known tools)
    python scripts/preflight.py --gates compileJava,architectureCheck --service wrks-service
    python scripts/preflight.py --json                  # machine-readable

Exit code: 0 always (preflight is informational — it never blocks; the caller decides).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_WIN = sys.platform == "win32"

# ── Gate → tool registry (single source of truth) ────────────────────────────────
# Each gate names the tool it needs and a recovery command template ({service}/{project}
# are filled in by the caller). `layer` groups gates for reporting.
GATES: dict[str, dict] = {
    "compileJava": {
        "tool": "gradle", "layer": "backend",
        "desc": "Compilação Java",
        "recover": './gradlew :{service}:compileJava',
    },
    "architectureCheck": {
        "tool": "gradle", "layer": "backend",
        "desc": "ArchUnit RULE-01..09",
        "recover": './gradlew :{service}:test --tests "*.architecture.*"',
    },
    "bddGate": {
        "tool": "gradle", "layer": "backend",
        "desc": "Cucumber BDD (specs-validate deferido)",
        "recover": './gradlew :{service}:test --tests "*CucumberIT*"',
    },
    "integrationTest": {
        "tool": "gradle", "layer": "backend",
        "desc": "Testcontainers (integration tests — também exige docker em runtime)",
        "recover": './gradlew :{service}:integrationTest',
    },
    "feChecks": {
        "tool": "nx", "layer": "frontend",
        "desc": "nx lint + test + build",
        "recover": 'npx nx run-many -t lint test build -p {project}',
    },
    "e2eValidate": {
        "tool": "nx", "layer": "frontend",
        "desc": "Playwright e2e (compile/list)",
        "recover": 'npx nx e2e {project}-e2e --list',
    },
}

# Tools the matrix reports on by default.
KNOWN_TOOLS = ["python", "java", "gradle", "docker", "node", "nx"]


def resolve_tool(tool: str) -> str | None:
    """Return the resolved path/handle for a tool, or None if absent.

    Special-cases the project's local wrappers (gradlew at backend/, nx in
    frontend/node_modules) before falling back to the system PATH.
    """
    if tool == "gradle":
        wrappers = ["backend/gradlew.bat", "gradlew.bat"] if _WIN else ["backend/gradlew", "gradlew"]
        for w in wrappers:
            if (ROOT / w).is_file():
                return str(ROOT / w)
        return shutil.which("gradle")
    if tool == "nx":
        local = ROOT / "frontend" / "node_modules" / ".bin" / ("nx.cmd" if _WIN else "nx")
        if local.is_file():
            return str(local)
        return shutil.which("npx")  # npx nx … fallback
    if tool == "python":
        return sys.executable or shutil.which("python")
    return shutil.which(tool)


def capability_matrix(tools: list[str] | None = None) -> dict[str, str | None]:
    return {t: resolve_tool(t) for t in (tools or KNOWN_TOOLS)}


def plan_gates(gate_names: list[str], service: str = "<service>",
               project: str = "<project>") -> list[dict]:
    """For each requested gate, report whether its tool is available and the recovery cmd."""
    out: list[dict] = []
    for name in gate_names:
        spec = GATES.get(name)
        if not spec:
            out.append({"gate": name, "known": False, "available": False,
                        "tool": "?", "recover": "", "status": "unknown-gate"})
            continue
        path = resolve_tool(spec["tool"])
        available = path is not None
        out.append({
            "gate": name,
            "known": True,
            "tool": spec["tool"],
            "tool_path": path,
            "desc": spec["desc"],
            "available": available,
            "recover": spec["recover"].format(service=service, project=project),
            "status": "runnable" if available else "diferido",
        })
    return out


def main(argv: list[str] | None = None) -> int:
    try:
        from cli_utils import force_utf8_stdio
        force_utf8_stdio()
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        prog="preflight.py",
        description="Detecta o toolchain disponível e planeja gates (runnable vs diferido).",
    )
    parser.add_argument("--gates", help="Lista de gates separada por vírgula "
                        f"(conhecidos: {', '.join(GATES)}).")
    parser.add_argument("--service", default="<service>", help="Serviço BE para o comando de recuperação.")
    parser.add_argument("--project", default="<project>", help="Projeto FE para o comando de recuperação.")
    parser.add_argument("--json", action="store_true", help="Saída JSON.")
    args = parser.parse_args(argv)

    matrix = capability_matrix()
    gate_plan = plan_gates([g.strip() for g in args.gates.split(",") if g.strip()],
                           args.service, args.project) if args.gates else []

    if args.json:
        print(json.dumps({"toolchain": matrix, "gates": gate_plan}, indent=2, ensure_ascii=False))
        return 0

    print("Toolchain preflight (Journey OS)")
    print("  Capability matrix:")
    for tool, path in matrix.items():
        mark = "✅" if path else "🚫"
        print(f"    {mark} {tool:<8} {path or 'ausente (não no PATH)'}")

    if gate_plan:
        print("\n  Gates:")
        for g in gate_plan:
            if not g["known"]:
                print(f"    ⚠️  {g['gate']:<18} gate desconhecido")
                continue
            mark = "✅" if g["available"] else "🚫"
            tag = "runnable" if g["available"] else "DIFERIDO"
            print(f"    {mark} {g['gate']:<18} [{tag}] needs {g['tool']} — {g['desc']}")
            if not g["available"]:
                print(f"        recuperar: {g['recover']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
