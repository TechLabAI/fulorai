#!/usr/bin/env python3
"""backlog-gen.py -- deterministic issue generator (D-318).

The ONE issue generator (be / fe / fe-feature). The agent decides WHAT issues
exist (the manifest); this script does the mechanical, deterministic part:
continuous numbering, the canonical skeleton with ``TODO[agent]`` markers for
the judgment fields, issues-map update, and (prototype mode) the
``<ISSUE>.contract.json`` + ``raw/`` copy. ``fe-ui-issue-gen`` (D-311) is this
script's ``--from-prototype-map`` mode -- not a separate tool.

The line (R5): script writes numbering + structure + map; the agent fills
Outcome / Approach / Acceptance / Dependencies (the ``TODO[agent]`` slots).

Inputs (at least one):
    --manifest <json>            explicit list of issue descriptors
    --from-prototype-map <json>  derive descriptors from a prototype-map.json

Manifest entry: {title, kind?, priority?, slug?, module?, targetFiles?[],
                 pattern?, contract?{}, raw?{html,css}}

R3: argparse subcommand, root walk-up, atomic write, OK:/error:, exit 0/1/2.
Exit 2 == numbering conflict (file exists) without --force, or bad input.

Usage:
    python scripts/backlog-gen.py gen --layer fe --module lead --manifest items.json
    python scripts/backlog-gen.py gen --from-prototype-map prototype-map.json --module lead --dry-run
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import sys
from pathlib import Path

try:
    from cli_utils import force_utf8_stdio
    from issue_state import LAYER_PROFILES, atomic_write, find_root
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cli_utils import force_utf8_stdio
    from issue_state import LAYER_PROFILES, atomic_write, find_root


_VALID_KINDS = {"FE", "INT", "BE"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def read_tenant_term(root: Path) -> str:
    ctx = root / "project-context.json"
    try:
        data = json.loads(ctx.read_text(encoding="utf-8"))
        return (data.get("multiTenancy", {}) or {}).get("term", "tenant")
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "tenant"


def default_kind(layer: str) -> str:
    return "BE" if layer == "be" else "FE"


def issue_id(module: str, kind: str, n: int) -> str:
    mod = module.upper()
    return f"{mod}-{n:03d}" if kind == "BE" else f"{mod}-{kind}-{n:03d}"


def id_pattern(module: str, kind: str) -> re.Pattern:
    mod = re.escape(module.upper())
    return re.compile(rf"^{mod}-(\d+)\.md$") if kind == "BE" else \
        re.compile(rf"^{mod}-{kind}-(\d+)\.md$")


def next_number(output_dir: Path, module: str, kind: str) -> int:
    mx = 0
    pat = id_pattern(module, kind)
    if output_dir.is_dir():
        for f in output_dir.glob("*.md"):
            m = pat.match(f.name)
            if m:
                mx = max(mx, int(m.group(1)))
    return mx + 1


# ── Skeleton rendering ─────────────────────────────────────────────────────────

def _checklist_lines(target_files: list[str], checklist_label: str) -> list[str]:
    lines = [f"- [ ] implementar `{f}`" for f in target_files]
    lines.append(f"- [ ] TODO[agent]: itens adicionais de {checklist_label}")
    return lines


def render_issue(issue: str, entry: dict, layer: str, tenant: str, date: str) -> str:
    title = entry.get("title", issue)
    priority = entry.get("priority", "P3")
    targets = entry.get("targetFiles", []) or []

    if layer == "be":
        checklist = _checklist_lines(targets, "escopo")
        accept = ["- [ ] TODO[agent]: criterio de aceite verificavel"]
        n = len(checklist) + len(accept)
        body = [
            f"# {issue} -- {title}", "",
            f"**Status:** INTACT -- gerado {date}",
            "**Maturidade:** 0 -- Inicial",
            f"**Done/Total:** 0/{n} itens", "",
            "## Contexto", "TODO[agent]: contexto e objetivo da issue.", "",
            "## Escopo", *checklist, "",
            "## Criterios de aceite", *accept, "",
            "## Dependencias", "TODO[agent]: issues/endpoints dependentes ou \"Nenhuma\".", "",
            "## Estimativa", "S", "",
            "## Prioridade", priority, "",
        ]
        return "\n".join(body), n

    # fe / int
    checklist = _checklist_lines(targets, "implementacao")
    accept = ["- [ ] TODO[agent]: criterio de aceite verificavel"]
    n = len(checklist) + len(accept)
    tcap = tenant.capitalize()
    body = [
        f"# {issue} -- {title}", "",
        f"**Status:** INTACT -- gerado {date}",
        "**Maturidade:** 0 -- Inicial",
        f"**Done/Total:** 0/{n} itens", "",
        "## Outcome", "TODO[agent]: o que esta issue entrega, em uma frase.", "",
        "## Approach (execution path)", "TODO[agent]: caminho de execucao.", "",
        "## Implementation checklist (by layer/file)", *checklist, "",
        "## Acceptance criteria", *accept, "",
        "## Dependencies", "TODO[agent]: issues/endpoints dependentes ou \"Nenhuma\".", "",
        f"## {tcap}-context impact", f"TODO[agent]: impacto multi-{tenant} ou \"Nenhum\".", "",
    ]
    if entry.get("contract") or entry.get("pattern"):
        body += _contract_section(issue, entry)
    body += ["## Prioridade", priority, ""]
    return "\n".join(body), n


def _contract_section(issue: str, entry: dict, tenant: str = "tenant") -> list[str]:
    c = entry.get("contract", {}) or {}
    pattern = entry.get("pattern") or c.get("pattern", "?")
    raw = c.get("raw") or {}
    hybrid = c.get("hybrid") or {}
    tokens = c.get("tokens") or []
    component_tree = c.get("componentTree") or []
    da = c.get("dataAccess") or {}
    lines = [
        "## Contrato de Fidelidade UI",
        "",
        f"**Padrao:** {pattern}  ",
        f"**Contrato (dado):** `{issue}.contract.json`",
        "",
    ]
    if c.get("ngComponent"):
        lines.append(f"**Componente alvo:** `{c['ngComponent']}`  ")
    if c.get("ngRoute"):
        lines.append(f"**Rota:** `{c['ngRoute']}`  ")
    if raw.get("html"):
        lines.append(f"**Fonte visual:** `{raw['html']}`{' + `' + raw['css'] + '`' if raw.get('css') else ''}  ")
    lines.append("")
    if hybrid:
        lines += [
            "### Split híbrido (Material × custom)",
            "",
            "| Elemento | Alvo | Critério |",
            "|---|---|---|",
        ]
        for elem in hybrid.get("material", []):
            lines.append(f"| {elem} | **Material** | A11y/behaviour |")
        for elem in hybrid.get("custom", []):
            lines.append(f"| {elem} | **Custom** + tokens | Identidade visual |")
        lines.append("")
    if tokens:
        preview = tokens[:8]
        extra = f" (+{len(tokens) - 8} mais)" if len(tokens) > 8 else ""
        lines += [
            "### Tokens da tela",
            "",
            f"`{'`, `'.join(preview)}`{extra}",
            "",
        ]
    if component_tree:
        lines += [
            "### Árvore de componentes",
            "",
            *[f"- `{c}`" for c in component_tree],
            "",
        ]
    if da:
        lines += [
            "### Data-access (das SPECs — não inventar)",
            "",
            f"- Facade: `{da.get('facade', 'TODO[agent]')}`",
            f"- Spec ref: `{da.get('spec', 'TODO[agent]')}`",
            "- `isMock: true` enquanto o BE não existir",
            "",
        ]
    lines += [
        "### Critérios de aceite de fidelidade",
        "",
        "- [ ] Paridade visual com `raw/` — zero desvio de layout perceptível",
        "- [ ] Zero cor/spacing hardcoded (todo valor via token SCSS)",
        "- [ ] `OnPush` + `standalone` em todos os componentes",
        "- [ ] A11y: ARIA roles, foco por teclado, contraste AA",
        f"- [ ] Multi-{tenant}: componente isolado por {tenant} via interceptor",
        "",
    ]
    return lines


# ── Manifest assembly ──────────────────────────────────────────────────────────

def manifest_from_prototype_map(
    map_path: Path,
    fallback_module: str | None,
    filter_module: str | None = None,
) -> list[dict]:
    data = json.loads(map_path.read_text(encoding="utf-8"))
    entries: list[dict] = []
    for s in data.get("screens", []):
        module = s.get("module") or fallback_module
        if not module:
            raise ValueError(f"screen {s.get('id')!r} sem 'module' e sem --module de fallback")
        # D-311: filter_module restricts generation to one module at a time.
        if filter_module and module.lower() != filter_module.lower():
            continue
        # Build raw dict from D-308 enriched fields (sourceHtml/sourceCss) or legacy raw key.
        raw_html = s.get("sourceHtml", "")
        raw_css = s.get("sourceCss", "")
        raw = {"html": raw_html, "css": raw_css} if raw_html else (s.get("raw") or {})
        entries.append({
            "title": s.get("label") or s.get("id"),
            "kind": "FE",
            "slug": s.get("id"),
            "module": module,
            "pattern": s.get("pattern"),
            "targetFiles": [],
            "contract": {
                "pattern": s.get("pattern"),
                "ngComponent": s.get("ngComponent") or "",
                "ngSelector": s.get("ngSelector") or "",
                "ngRoute": s.get("ngRoute") or "",
                "componentTree": s.get("components", []),
                "tokens": s.get("tokens", []),
                "hybrid": s.get("hybrid", {}),
                "lib": s.get("lib") or "",
                "raw": {"html": f"raw/{raw_html}", "css": f"raw/{raw_css}"} if raw_html else {},
                "dataAccess": {"facade": "TODO[agent]", "spec": "TODO[agent]: SPEC-04#resource"},
            },
            "raw": raw,
        })
    return entries


def load_manifest(args) -> list[dict]:
    if args.manifest:
        data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else data.get("issues", [])
    elif args.from_prototype_map:
        filter_mod = getattr(args, "filter_module", None) or args.module
        entries = manifest_from_prototype_map(
            Path(args.from_prototype_map),
            args.module,
            filter_module=filter_mod,
        )
    else:
        raise ValueError("informe --manifest ou --from-prototype-map")
    if not entries:
        raise ValueError("manifest vazio (nenhuma tela encontrada para o modulo especificado)")
    return entries


# ── issues-map ───────────────────────────────────────────────────────────────

def update_issues_map(map_file: Path, rows: list[tuple[str, str, str, str]]) -> str:
    header = (
        f"# Issues Map -- {map_file.parent.name}\n\n"
        "| Issue | Title | Kind | Priority | Status |\n"
        "|---|---|---|---|---|\n"
    )
    existing = map_file.read_text(encoding="utf-8") if map_file.is_file() else header
    if "| Issue | Title |" not in existing:
        existing = header + existing
    appended = "".join(f"| {i} | {t} | {k} | {p} | INTACT |\n" for i, t, k, p in rows)
    return existing.rstrip("\n") + "\n" + appended


# ── Subcommand ───────────────────────────────────────────────────────────────

def cmd_gen(args) -> int:
    root = find_root(args.root)
    layer = args.layer or "fe"
    tenant = read_tenant_term(root)
    date = _dt.date.today().isoformat()

    try:
        entries = load_manifest(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir) if args.output_dir else root / LAYER_PROFILES[layer]["issue_dir"]

    # Plan everything first (numbering + conflict detection) before writing.
    counters: dict[tuple[str, str], int] = {}
    planned: list[dict] = []
    conflicts: list[str] = []
    for entry in entries:
        module = entry.get("module") or args.module
        if not module:
            print("error: entry sem 'module' e sem --module", file=sys.stderr)
            return 2
        kind = (entry.get("kind") or default_kind(layer)).upper()
        if kind not in _VALID_KINDS:
            print(f"error: kind invalido: {kind}", file=sys.stderr)
            return 2
        key = (module.upper(), kind)
        if key not in counters:
            counters[key] = next_number(out_dir, module, kind)
        n = counters[key]
        counters[key] += 1
        iid = issue_id(module, kind, n)
        issue_path = out_dir / f"{iid}.md"
        if issue_path.exists() and not args.force:
            conflicts.append(str(issue_path.name))
        content, _ = render_issue(iid, entry, layer, tenant, date)
        planned.append({"id": iid, "path": issue_path, "content": content,
                        "entry": entry, "module": module, "kind": kind,
                        "priority": entry.get("priority", "P3"),
                        "title": entry.get("title", iid)})

    if conflicts and not args.force:
        print(f"error: conflito de numeracao (arquivos existem; use --force): {', '.join(conflicts)}",
              file=sys.stderr)
        return 2

    if args.dry_run:
        for p in planned:
            print(f"[dry-run] {p['path'].relative_to(root)} ({p['kind']} {p['priority']})")
        print(f"OK: dry-run -- {len(planned)} issue(s) seriam geradas em {out_dir.relative_to(root)}")
        return 0

    # Write issues + contract.json + raw/
    rows = []
    for p in planned:
        atomic_write(p["path"], p["content"].rstrip("\n") + "\n")
        rows.append((p["id"], p["title"], p["kind"], p["priority"]))
        entry = p["entry"]
        if entry.get("contract"):
            contract = {"issue": p["id"], "screen": entry.get("slug"), **entry["contract"]}
            atomic_write(p["path"].with_name(f"{p['id']}.contract.json"),
                         json.dumps(contract, indent=2, ensure_ascii=False) + "\n")
        if entry.get("raw") and args.prototype_root:
            _copy_raw(entry, p["module"], root, Path(args.prototype_root))

    map_file = Path(args.issues_map) if args.issues_map else out_dir / "issues-map.md"
    atomic_write(map_file, update_issues_map(map_file, rows))

    if args.report:
        for p in planned:
            print(f"  {p['id']}  {p['kind']:<3} {p['priority']}  {p['title']}")

    print(f"OK: {len(planned)} issue(s) geradas em {out_dir.relative_to(root)}; "
          f"issues-map atualizado ({map_file.name})")
    return 0


def _copy_raw(entry: dict, module: str, root: Path, proto_root: Path) -> None:
    slug = entry.get("slug", "screen")
    dest = root / "docs/architecture/frontend/prototypes" / module / slug / "raw"
    for key in ("html", "css"):
        src_rel = (entry.get("raw") or {}).get(key)
        if not src_rel:
            continue
        src = proto_root / src_rel
        if src.is_file():
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest / Path(src_rel).name)


def main() -> None:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="backlog-gen",
        description="Deterministic issue generator (D-318).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("gen", help="generate issues from a manifest / prototype-map")
    g.add_argument("--layer", choices=sorted(LAYER_PROFILES), default="fe")
    g.add_argument("--module", metavar="MOD", help="fallback module when entries omit it")
    g.add_argument("--manifest", metavar="PATH", help="JSON list of issue descriptors")
    g.add_argument("--from-prototype-map", metavar="PATH", help="derive issues from a prototype-map.json")
    g.add_argument("--filter-module", metavar="MOD", help="(prototype-map mode) only emit screens for this module slug")
    g.add_argument("--output-dir", metavar="PATH", help="issues dir (default: layout-resolved)")
    g.add_argument("--issues-map", metavar="PATH", help="issues-map.md path (default: <issues-dir>/issues-map.md)")
    g.add_argument("--prototype-root", metavar="PATH", help="root to resolve raw/ source files")
    g.add_argument("--root", metavar="PATH")
    g.add_argument("--force", action="store_true", help="overwrite existing issue files")
    g.add_argument("--dry-run", action="store_true", help="list what would be generated")
    g.add_argument("--report", action="store_true")
    g.set_defaults(func=cmd_gen)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
