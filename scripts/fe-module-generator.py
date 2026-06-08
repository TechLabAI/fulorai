#!/usr/bin/env python3
"""fe-module-generator.py — Angular feature lib scaffolder for generated projects.

Gera a estrutura de uma feature lib Nx (Angular 18+ standalone + signals) a partir
do registro de módulos em project-context.json.

Uso:
    python scripts/fe-module-generator.py generate --module OVR --pattern P4
    python scripts/fe-module-generator.py generate --module LOS --pattern P1 --dry-run
    python scripts/fe-module-generator.py list

Padrões suportados:
    P1 — CRUD lista + filtros (mat-table + mat-select/chip)
    P2 — Tabs em painel (mat-tab-group)
    P4 — KPI dashboard + lista operacional (mat-card grid + mat-table)
    P6 — Kanban drag-and-drop (CDK drag-drop)

R3: argparse, atomic write, OK:/error:, exit 0/1/2.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

# ── Project context ────────────────────────────────────────────────────────────

def find_project_root(start: Path) -> Path:
    """Walk up from start looking for project-context.json."""
    current = start.resolve()
    for _ in range(8):
        if (current / "project-context.json").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise FileNotFoundError(
        "project-context.json not found. Run from inside the generated project "
        "or pass --project-root."
    )


def load_context(project_root: Path) -> dict:
    ctx_file = project_root / "project-context.json"
    try:
        return json.loads(ctx_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"project-context.json is not valid JSON: {exc}") from exc


# ── Name derivations ───────────────────────────────────────────────────────────

def kebab_to_pascal(kebab: str) -> str:
    return "".join(p.capitalize() for p in kebab.replace("_", "-").split("-"))


def derive_lib_name(module: dict) -> str:
    """Mirror the logic in new-project.py cmd_frontend_skeleton()."""
    lib_field = module.get("frontendLib")
    if lib_field:
        return lib_field[5:] if lib_field.startswith("libs/") else lib_field
    return (module.get("prefix") or "").lower()


def derive_names(lib: str) -> dict:
    """Derive all naming variants from lib (kebab) name."""
    pascal = kebab_to_pascal(lib)
    const = lib.upper().replace("-", "_")
    return {
        "lib": lib,
        "pascal": pascal,
        "const": const,
        "routes_const": f"{const}_ROUTES",
        "page_class": f"{pascal}PageComponent",
        "service_class": f"{pascal}Service",
        "page_slug": f"{lib}-page",
        "service_slug": f"{lib}.service",
    }


# ── File generators per pattern ────────────────────────────────────────────────

def gen_page_component(names: dict, display_name: str, pattern: str) -> str:
    lib = names["lib"]
    pascal = names["pascal"]
    page_class = names["page_class"]

    if pattern == "P1":
        return textwrap.dedent(f"""\
            import {{ ChangeDetectionStrategy, Component, signal }} from '@angular/core';

            @Component({{
              selector: '{lib}-page',
              standalone: true,
              imports: [],
              changeDetection: ChangeDetectionStrategy.OnPush,
              template: `
                <div class="{lib}-page">
                  <h1>{display_name}</h1>
                  <!-- P1: CRUD list + filters -->
                  <!-- TODO: add mat-table + mat-select filters (Angular Material) -->
                  <p>Carregando dados...</p>
                </div>
              `,
            }})
            export class {page_class} {{
              readonly items = signal<unknown[]>([]);
            }}
            """)

    if pattern == "P2":
        return textwrap.dedent(f"""\
            import {{ ChangeDetectionStrategy, Component, signal }} from '@angular/core';

            @Component({{
              selector: '{lib}-page',
              standalone: true,
              imports: [],
              changeDetection: ChangeDetectionStrategy.OnPush,
              template: `
                <div class="{lib}-page">
                  <h1>{display_name}</h1>
                  <!-- P2: tabs panel (mat-tab-group) -->
                  <!-- TODO: add MatTabsModule + tab content components -->
                  <nav>
                    @for (tab of tabs(); track tab.id) {{
                      <button (click)="activeTab.set(tab.id)">{{{{ tab.label }}}}</button>
                    }}
                  </nav>
                  <section>Tab: {{{{ activeTab() }}}}</section>
                </div>
              `,
            }})
            export class {page_class} {{
              readonly tabs = signal([
                {{ id: 'overview', label: 'Visão Geral' }},
                {{ id: 'details', label: 'Detalhes' }},
              ]);
              readonly activeTab = signal('overview');
            }}
            """)

    if pattern == "P4":
        return textwrap.dedent(f"""\
            import {{ ChangeDetectionStrategy, Component, signal }} from '@angular/core';

            interface KpiCard {{
              label: string;
              value: string | number;
              unit?: string;
            }}

            @Component({{
              selector: '{lib}-page',
              standalone: true,
              imports: [],
              changeDetection: ChangeDetectionStrategy.OnPush,
              template: `
                <div class="{lib}-page">
                  <h1>{display_name}</h1>
                  <!-- P4: KPI dashboard + operational list -->
                  <div class="kpi-grid">
                    @for (kpi of kpis(); track kpi.label) {{
                      <div class="kpi-card">
                        <span class="kpi-value">{{{{ kpi.value }}}}</span>
                        <span class="kpi-label">{{{{ kpi.label }}}}</span>
                      </div>
                    }}
                  </div>
                  <!-- TODO: add mat-table for operational list -->
                </div>
              `,
              styles: [`
                .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }}
                .kpi-card {{ padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; }}
                .kpi-value {{ font-size: 2rem; font-weight: 700; display: block; }}
              `],
            }})
            export class {page_class} {{
              readonly kpis = signal<KpiCard[]>([]);
            }}
            """)

    if pattern == "P6":
        return textwrap.dedent(f"""\
            import {{ ChangeDetectionStrategy, Component, signal }} from '@angular/core';
            import {{ CdkDragDrop, DragDropModule, moveItemInArray, transferArrayItem }} from '@angular/cdk/drag-drop';

            interface KanbanCard {{
              id: string;
              title: string;
            }}

            interface KanbanColumn {{
              id: string;
              label: string;
              cards: KanbanCard[];
            }}

            @Component({{
              selector: '{lib}-page',
              standalone: true,
              imports: [DragDropModule],
              changeDetection: ChangeDetectionStrategy.OnPush,
              template: `
                <div class="{lib}-page">
                  <h1>{display_name}</h1>
                  <!-- P6: Kanban board (CDK drag-drop) -->
                  <div class="kanban-board" cdkDropListGroup>
                    @for (col of columns(); track col.id) {{
                      <div class="kanban-column">
                        <h3>{{{{ col.label }}}}</h3>
                        <div cdkDropList [cdkDropListData]="col.cards" (cdkDropListDropped)="drop($event, col.id)" class="kanban-list">
                          @for (card of col.cards; track card.id) {{
                            <div cdkDrag class="kanban-card">{{{{ card.title }}}}</div>
                          }}
                        </div>
                      </div>
                    }}
                  </div>
                </div>
              `,
              styles: [`
                .kanban-board {{ display: flex; gap: 1rem; overflow-x: auto; }}
                .kanban-column {{ min-width: 240px; }}
                .kanban-list {{ min-height: 80px; }}
                .kanban-card {{ padding: 0.5rem; margin: 0.25rem 0; border: 1px solid #e5e7eb; border-radius: 0.25rem; cursor: grab; }}
              `],
            }})
            export class {page_class} {{
              readonly columns = signal<KanbanColumn[]>([
                {{ id: 'open', label: 'Aberto', cards: [] }},
                {{ id: 'doing', label: 'Em execução', cards: [] }},
                {{ id: 'done', label: 'Concluído', cards: [] }},
              ]);

              drop(event: CdkDragDrop<KanbanCard[]>, _columnId: string): void {{
                const cols = this.columns();
                if (event.previousContainer === event.container) {{
                  moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
                }} else {{
                  transferArrayItem(
                    event.previousContainer.data,
                    event.container.data,
                    event.previousIndex,
                    event.currentIndex,
                  );
                }}
                this.columns.set([...cols]);
              }}
            }}
            """)

    raise ValueError(f"Unsupported pattern: {pattern}")


def gen_service(names: dict, npm_scope: str) -> str:
    lib = names["lib"]
    pascal = names["pascal"]
    service_class = names["service_class"]
    return textwrap.dedent(f"""\
        import {{ Injectable, inject }} from '@angular/core';
        import {{ HttpClient }} from '@angular/common/http';
        import {{ Observable }} from 'rxjs';

        @Injectable({{ providedIn: 'root' }})
        export class {service_class} {{
          private readonly http = inject(HttpClient);

          // TODO: replace with real API base from environment config
          private readonly apiBase = '/api/{lib}';

          findAll(): Observable<unknown[]> {{
            return this.http.get<unknown[]>(this.apiBase);
          }}

          findById(id: string): Observable<unknown> {{
            return this.http.get<unknown>(`${{this.apiBase}}/${{id}}`);
          }}
        }}
        """)


def gen_routes(names: dict, npm_scope: str) -> str:
    lib = names["lib"]
    routes_const = names["routes_const"]
    page_slug = names["page_slug"]
    page_class = names["page_class"]
    return textwrap.dedent(f"""\
        import {{ Routes }} from '@angular/router';

        export const {routes_const}: Routes = [
          {{
            path: '',
            loadComponent: () =>
              import('./{page_slug}.component').then(c => c.{page_class}),
          }},
        ];
        """)


def gen_barrel(names: dict) -> str:
    routes_const = names["routes_const"]
    lib = names["lib"]
    return textwrap.dedent(f"""\
        export {{ {routes_const} }} from './lib/{lib}.routes';
        """)


# ── Atomic write ───────────────────────────────────────────────────────────────

def write_atomic(path: Path, content: str) -> None:
    """Write atomically via temp file + rename (R3)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


# ── Subcommands ────────────────────────────────────────────────────────────────

def cmd_generate(args: argparse.Namespace) -> int:
    project_root = (
        Path(args.project_root).resolve()
        if args.project_root
        else find_project_root(Path.cwd())
    )

    try:
        ctx = load_context(project_root)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    modules = (ctx.get("modules") or {}).get("registry") or []
    prefix_upper = args.module.upper()
    module = next((m for m in modules if m.get("prefix", "").upper() == prefix_upper), None)
    if module is None:
        known = [m.get("prefix", "") for m in modules]
        print(
            f"error: module '{args.module}' not found in project-context.modules.registry. "
            f"Known: {known}",
            file=sys.stderr,
        )
        return 1

    if not module.get("hasUi", True):
        print(
            f"error: module '{prefix_upper}' has hasUi=false — no frontend lib to generate.",
            file=sys.stderr,
        )
        return 2

    pattern = args.pattern.upper()
    if pattern not in ("P1", "P2", "P4", "P6"):
        print(f"error: unsupported pattern '{pattern}'. Choose P1, P2, P4 or P6.", file=sys.stderr)
        return 2

    lib = derive_lib_name(module)
    if not lib:
        print(f"error: could not derive lib name for module '{prefix_upper}'.", file=sys.stderr)
        return 1

    names = derive_names(lib)
    display_name = module.get("displayName") or lib

    fe = ctx.get("stack", {}).get("frontend", {})
    npm_scope = (fe.get("npmScope") or f"@{ctx['project']['name']}").lstrip("@")
    npm_scope_at = f"@{npm_scope}"

    libs_dir = project_root / "frontend" / "libs" / lib
    src_lib = libs_dir / "src" / "lib"

    files: list[tuple[Path, str]] = [
        (libs_dir / "src" / "index.ts", gen_barrel(names)),
        (src_lib / f"{lib}.routes.ts", gen_routes(names, npm_scope_at)),
        (src_lib / f"{names['page_slug']}.component.ts", gen_page_component(names, display_name, pattern)),
        (src_lib / f"{lib}.service.ts", gen_service(names, npm_scope_at)),
    ]

    if args.dry_run:
        print(f"[fe-module-generator] DRY RUN — module={prefix_upper}, lib={lib}, pattern={pattern}")
        for path, _ in files:
            rel = path.relative_to(project_root)
            print(f"  would write: {rel}")
        return 0

    created = skipped = 0
    for path, content in files:
        rel = path.relative_to(project_root)
        if path.exists() and not args.force:
            print(f"  [SKIP] {rel}")
            skipped += 1
            continue
        write_atomic(path, content)
        print(f"  [+] {rel}")
        created += 1

    print(f"\nOK: fe-module-generator {prefix_upper}/{pattern} — created {created}, skipped {skipped}")
    print(f"\nNext steps:")
    print(f"  1. Register '{npm_scope_at}/{lib}' in frontend/tsconfig.base.json paths (if not present)")
    print(f"  2. Check app.routes.ts includes the '{lib}' lazy route")
    print(f"  3. npx nx serve {ctx['project']['name']}-web")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    project_root = (
        Path(args.project_root).resolve()
        if args.project_root
        else find_project_root(Path.cwd())
    )

    try:
        ctx = load_context(project_root)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    modules = (ctx.get("modules") or {}).get("registry") or []
    ui_modules = [m for m in modules if m.get("hasUi", True) and not m.get("isInfrastructure")]

    if not ui_modules:
        print("No UI modules registered in project-context.json")
        return 0

    print(f"{'PREFIX':<8}  {'LIB':<30}  {'DISPLAY NAME'}")
    print("-" * 60)
    for m in ui_modules:
        lib = derive_lib_name(m)
        print(f"{m.get('prefix', ''):<8}  {lib:<30}  {m.get('displayName', '')}")

    return 0


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fe-module-generator",
        description="Angular feature lib scaffolder for techlab-architecture generated projects.",
    )
    parser.add_argument(
        "--project-root",
        metavar="PATH",
        help="Path to generated project root (default: walk up from cwd)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # generate subcommand
    gen = sub.add_parser("generate", help="Scaffold a feature lib for a registered module")
    gen.add_argument("--module", required=True, metavar="PREFIX",
                     help="Module prefix (3-5 uppercase letters, e.g. OVR)")
    gen.add_argument("--pattern", required=True, metavar="P1|P2|P4|P6",
                     help="UI pattern: P1=CRUD list, P2=tabs, P4=KPI dashboard, P6=kanban")
    gen.add_argument("--dry-run", action="store_true",
                     help="Print files that would be written without writing them")
    gen.add_argument("--force", action="store_true",
                     help="Overwrite existing files")

    # list subcommand
    lst = sub.add_parser("list", help="List UI modules from project-context.json")

    args = parser.parse_args()

    dispatch = {"generate": cmd_generate, "list": cmd_list}
    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(args))


if __name__ == "__main__":
    main()
