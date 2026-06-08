#!/usr/bin/env python3
"""fe-prototype-analyzer.py — HTML prototype analyzer → prototype-map.json.

Analisa um arquivo HTML de protótipo (single-file, React inline ou HTML puro)
e produz um prototype-map.json classificando cada tela nos padrões P1-P7 do
pipeline fe-feature-architect.

Padrões P1-P7 (conforme fe-feature-architect-from-prototype.md.j2):
    P1 — Generic CRUD (lista + filtros + modal)
    P2 — Tabs em modal/painel (masters com múltiplas abas)
    P3 — Lista expandível inline (nested expand)
    P4 — KPI + filtros + lista operacional (dashboard)
    P5 — Árvore hierárquica (MatTree)
    P6 — Kanban drag-and-drop
    P7 — Pipeline editor (custom renderer)

Estratégia (D-291): Python puro (re + html.parser) — determinístico, sem IA.
Detecta telas via id/data-section/class, classifica por presença de keywords
de componentes e marcadores visuais no HTML/JSX.

Uso:
    python scripts/fe-prototype-analyzer.py analyze \\
        --prototype design/prototype-bundle.html \\
        --output docs/architecture/frontend/prototype-map.json

    python scripts/fe-prototype-analyzer.py analyze \\
        --prototype design/prototype-bundle.html \\
        --report   # imprime resumo no stdout sem escrever arquivo

R3: argparse, atomic write, OK:/error:, exit 0/1/2.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ── Pattern classification rules ──────────────────────────────────────────────

# Each rule is (pattern_id, weight, list_of_keyword_patterns).
# The pattern with the highest weighted match wins.
# Keywords are matched case-insensitively against the raw HTML of the screen section.

_PATTERN_RULES: list[tuple[str, int, list[str]]] = [
    # P6 — Kanban drag-and-drop: highest priority (very distinctive)
    ("P6", 10, [
        r"kanban",
        r"drag.?drop|cdkDrag|DragDrop|useDrag|onDragEnd|draggable",
        r"board[^a-z]|lane[^a-z]|swimlane",
    ]),
    # P7 — Pipeline editor
    ("P7", 10, [
        r"pipeline.editor|pipe.?editor|flow.?editor",
        r"node.?graph|dag[^a-z]",
    ]),
    # P5 — Hierarchical tree
    ("P5", 8, [
        r"MatTree|treeControl|NestedTree|FlatTree|tree.?node|tree.?view",
        r"hierarchi|hierarqu",
        r"expand.?collapse|collaps.?expand",
    ]),
    # P4 — KPI dashboard (must come before P1 since dashboards often have tables too)
    ("P4", 6, [
        r"\bkpi\b|kpi.?card|kpi.?strip",
        r"pareto|histogram|chart|recharts|chartjs|apexchart|echarts",
        r"dashboard|cockpit|painel",
        r"metric[s]?|indicador",
    ]),
    # P2 — Tabs
    ("P2", 5, [
        r"MatTab|mat-tab|tab.?group|useTabs|tab.?panel|TabPanel|tab.?nav",
        r"tabIndex|activeTab|setActiveTab|selectedTab",
    ]),
    # P3 — Expandable list
    ("P3", 4, [
        r"accordion|collapse|expand|MatExpansion|expansion.?panel",
        r"toggle.?row|inline.?expand|row.?expand",
    ]),
    # P1 — Generic CRUD (fallback for table-based screens)
    ("P1", 2, [
        r"<table|mat.?table|MatTable|data.?table|list.?table",
        r"filter|filtrar|buscar|search",
        r"CRUD|criar|editar|excluir|create|edit|delete",
    ]),
]


def _score_pattern(html_fragment: str, rules: list[tuple[str, int, list[str]]]) -> str:
    """Return the best matching pattern ID for the HTML fragment."""
    lower = html_fragment.lower()
    scores: dict[str, int] = {}
    for pattern_id, weight, keywords in rules:
        hits = sum(1 for kw in keywords if re.search(kw, lower, re.IGNORECASE))
        if hits > 0:
            scores[pattern_id] = scores.get(pattern_id, 0) + hits * weight

    if not scores:
        return "P1"  # default fallback

    return max(scores, key=lambda k: scores[k])


# ── Screen extraction ─────────────────────────────────────────────────────────

@dataclass
class Screen:
    id: str
    label: str
    raw_html: str
    pattern: str = ""
    lib: str = ""
    components: list[str] = field(default_factory=list)


class _SectionExtractor(html.parser.HTMLParser):
    """Extracts top-level screen sections from HTML.

    Looks for elements matching any of:
      - <div id="section-*">
      - <div data-section="*">
      - <div class="screen *" id="*">
      - <section id="*">
    Also handles React JSX patterns via regex fallback.
    """

    def __init__(self) -> None:
        super().__init__()
        self.screens: list[Screen] = []
        self._stack: list[tuple[str, dict, int]] = []   # (tag, attrs, depth)
        self._depth = 0
        self._capturing: Screen | None = None
        self._capture_depth = 0
        self._buffer = ""

    def handle_starttag(self, tag: str, attrs_list: list) -> None:
        attrs = dict(attrs_list)
        self._depth += 1

        if self._capturing is not None:
            self._buffer += f"<{tag}>"
            self._stack.append((tag, attrs, self._depth))
            return

        el_id = attrs.get("id", "")
        data_section = attrs.get("data-section", "")
        el_class = attrs.get("class", "")

        is_screen = (
            (el_id.startswith("section-") and tag in ("div", "section"))
            or (data_section and tag in ("div", "section"))
            or (tag == "section" and el_id)
            or ("screen" in el_class.lower() and el_id)
        )

        if is_screen:
            raw_id = data_section or el_id
            label = _id_to_label(raw_id)
            screen = Screen(id=raw_id, label=label, raw_html="")
            self.screens.append(screen)
            self._capturing = screen
            self._capture_depth = self._depth

    def handle_endtag(self, tag: str) -> None:
        if self._capturing is not None:
            if self._depth == self._capture_depth:
                self._capturing.raw_html = self._buffer
                self._buffer = ""
                self._capturing = None
            else:
                self._buffer += f"</{tag}>"
        self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._capturing is not None:
            self._buffer += data


def _id_to_label(raw_id: str) -> str:
    """Convert 'section-loss-detail' → 'Loss Detail'."""
    cleaned = re.sub(r"^(section-|screen-|view-|page-)", "", raw_id, flags=re.IGNORECASE)
    return cleaned.replace("-", " ").replace("_", " ").title()


def _id_to_lib(raw_id: str) -> str:
    """Convert 'section-loss-detail' → 'feature-loss-detail'."""
    cleaned = re.sub(r"^(section-|screen-|view-|page-)", "", raw_id, flags=re.IGNORECASE)
    slug = re.sub(r"[^a-z0-9-]", "-", cleaned.lower()).strip("-")
    return f"feature-{slug}"


def _screen_id_from_filename(stem: str) -> str:
    """Strip leading NN- prefix: '03-screen-upload' → 'screen-upload'."""
    return re.sub(r"^\d+-", "", stem)


def _infer_components(lib: str, pattern: str) -> list[str]:
    """Infer a minimal component list from lib name + pattern."""
    pascal = "".join(p.capitalize() for p in lib.replace("_", "-").split("-"))
    comps = [f"{pascal}PageComponent"]
    if pattern in ("P1", "P4"):
        comps.append(f"{pascal}ListComponent")
    if pattern == "P2":
        comps.append(f"{pascal}TabsComponent")
    if pattern == "P6":
        comps.append(f"{pascal}KanbanComponent")
    if pattern in ("P1", "P4"):
        comps.append(f"{pascal}FilterBarComponent")
    return comps


# ── React JSX screen extraction (fallback) ────────────────────────────────────

def _extract_jsx_screens(html_text: str) -> list[Screen]:
    """Fallback: find React section identifiers in JSX / setSection() calls.

    Strategy (priority order):
    1. Explicit setSection('name') or setActiveScreen('name') calls — most reliable.
    2. section === 'name' / section == 'name' comparisons.
    3. Broad string literal search (last resort, heavily filtered).
    """
    screens: list[Screen] = []
    seen: set[str] = set()

    def _add(candidate: str) -> None:
        if candidate in seen:
            return
        # Skip obvious false positives:
        # CSS custom properties (--np, --np-rgb), React internals (__bundler_*)
        # Font names (woff2), boolean/null, numbers, too short/long
        if re.match(r"^--", candidate):
            return
        if re.match(r"^__", candidate):
            return
        if re.search(r"[A-Z]", candidate):  # camelCase / PascalCase → likely not a screen ID
            return
        if candidate in ("true", "false", "null", "undefined", "default", "none"):
            return
        if re.search(r"http|https|://|\.js|\.css|\.woff|\.png|\.svg", candidate):
            return
        if re.search(r"^\d", candidate):  # starts with digit
            return
        if len(candidate) < 2 or len(candidate) > 40:
            return
        if re.search(r"[/#@!%^&*+=<>?]", candidate):
            return
        seen.add(candidate)
        screens.append(Screen(id=candidate, label=_id_to_label(candidate), raw_html=""))

    # Pass 1 — screens/views object literal keys: const screens = { overview: ..., losses: ... }
    # BOSQ prototype pattern: `const screens = {\n    key:  <Component />,\n    ...}`
    # Cannot use [^}] because JSX expressions contain } — instead locate the declaration
    # and scan forward for indented "key:" lines (object properties at the root level).
    for decl_m in re.finditer(
        r"""(?:const|let|var)\s+(?:screens|views|sections|pages)\s*=\s*\{""",
        html_text, re.IGNORECASE,
    ):
        start = decl_m.end()
        chunk = html_text[start: start + 4000]
        # Normalize escaped newlines (\\n in the file = literal \n stored as 2 chars)
        chunk_norm = chunk.replace("\\n", "\n")
        for m in re.finditer(r"""^[ \t]{1,8}([a-z][a-z0-9_-]{1,39})\s*:""", chunk_norm, re.MULTILINE):
            _add(m.group(1).replace("_", "-"))

    # Pass 2 — setSection / setActiveSection / navigate calls
    if not screens:
        for m in re.finditer(
            r"""set(?:Section|ActiveSection|ActiveScreen|View|Page)\s*\(\s*['"]([^'"]{2,40})['"]\s*\)""",
            html_text, re.IGNORECASE,
        ):
            _add(m.group(1))

    # Pass 3 — section === 'name' comparison (React state matching)
    if not screens:
        for m in re.finditer(
            r"""(?:section|screen|view|page|activeSection)\s*===?\s*['"]([^'"]{2,40})['"]""",
            html_text, re.IGNORECASE,
        ):
            _add(m.group(1))

    # Pass 4 — useState('initialSection') — captures at least the first/default screen
    if not screens:
        for m in re.finditer(
            r"""useState\s*\(\s*['"]([a-z][a-z0-9-]{2,39})['"]\s*\)""",
            html_text,
        ):
            _add(m.group(1))

    return screens


# ── Asset blob extractor (UUID-based script bundles) ─────────────────────────

def _extract_asset_scripts(html_text: str) -> dict[str, str]:
    """Extract text/javascript or text/babel content from a bundled asset blob.

    Some single-file prototypes bundle all scripts as UUID-keyed entries in a JSON
    blob: {"<uuid>": {"mime": "text/javascript", "content": "..."}, ...}

    Returns a dict mapping UUID → decoded text content.
    """
    result: dict[str, str] = {}

    # Find the large JSON asset blob (usually in the first big <script> tag)
    for sc in re.finditer(r"<script[^>]*>(.*?)</script>", html_text, re.DOTALL | re.IGNORECASE):
        content = sc.group(1).strip()
        if not (content.startswith("{") and len(content) > 50000):
            continue
        try:
            blob = json.loads(content)
        except (json.JSONDecodeError, MemoryError):
            continue
        if not isinstance(blob, dict):
            continue

        for uid, entry in blob.items():
            if not isinstance(entry, dict):
                continue
            mime = (entry.get("mime") or entry.get("type") or "").lower()
            if "javascript" not in mime and "babel" not in mime and "tsx" not in mime:
                continue
            raw = entry.get("content") or entry.get("data") or entry.get("text") or ""
            if isinstance(raw, bytes):
                try:
                    raw = raw.decode("utf-8", errors="replace")
                except Exception:
                    continue
            if raw:
                result[uid] = raw

        if result:
            break

    return result


def _classify_from_asset_scripts(
    screen_id: str,
    asset_scripts: dict[str, str],
    inner_html: str,
) -> str:
    """Try to find the React component for screen_id in asset scripts and classify.

    Looks for the component definition in the concatenated asset script content.
    """
    pascal = "".join(p.capitalize() for p in screen_id.replace("-", "_").split("_"))
    comp_name = f"Screen{pascal}"

    for uid, code in asset_scripts.items():
        if comp_name not in code:
            continue
        # Found the script containing this component; classify its code
        m = re.search(
            rf"""(?:function\s+{re.escape(comp_name)}\s*\(|(?:const|let)\s+{re.escape(comp_name)}\s*=)""",
            code,
        )
        if m:
            fragment = code[m.start(): m.start() + 3000]
            return _score_pattern(fragment, _PATTERN_RULES)
        # Component referenced but not defined here — classify the whole file
        return _score_pattern(code, _PATTERN_RULES)

    return ""


# ── Name-based pattern hint ───────────────────────────────────────────────────

_NAME_PATTERN_HINTS: list[tuple[str, str]] = [
    # (regex to match screen id, pattern)
    # Use (?<![a-z])board to avoid matching "board" inside "dashboard".
    (r"kanban|(?<![a-z])board|opportunit|oportunid", "P6"),
    (r"overview|dashboard|home|cockpit|roi|kpi|analytics|analytic|metric|indicador|^\bai\b$|ia[_-]|ai[_-]|intelligence", "P4"),
    (r"detail|detalh|profile|perfil|view|modal|pdca|a3|form", "P2"),
    (r"setting|config|prefer|admin|manage|user|usuario", "P2"),
    (r"worksite|obra|workfront|frente|team|equip", "P4"),
    (r"tree|hierarqu|categori|taxonom", "P5"),
    (r"pipeline|flow|workflow|process", "P7"),
]


def _hint_pattern_from_name(screen_id: str) -> str:
    """Guess UI pattern from screen ID name when code analysis is unavailable."""
    sid = screen_id.lower()
    for pattern_re, pattern_id in _NAME_PATTERN_HINTS:
        if re.search(pattern_re, sid, re.IGNORECASE):
            return pattern_id
    return "P1"  # generic CRUD list as safe default


# ── JSX component body extractor ─────────────────────────────────────────────

def _extract_jsx_component_body(html_text: str, screen_id: str) -> str:
    """Try to extract the source body of the React component for a given screen ID.

    Looks for patterns like:
      function ScreenOverview(...)  {  ...  }
      const ScreenOverview = (...) =>  ...
    where the component name is derived from the screen ID ('overview' → 'ScreenOverview').

    Returns the source fragment or empty string if not found.
    Normalizes \\n escape sequences to real newlines for pattern matching.
    """
    pascal = "".join(p.capitalize() for p in screen_id.replace("-", "_").split("_"))
    comp_name = f"Screen{pascal}"

    # Normalize escaped newlines
    text = html_text.replace("\\n", "\n").replace("\\t", " ")

    # Find function or const component declaration
    m = re.search(
        rf"""(?:function\s+{re.escape(comp_name)}\s*\(|const\s+{re.escape(comp_name)}\s*=)""",
        text,
    )
    if not m:
        return ""

    # Extract ~3000 chars after the declaration start (enough for classification)
    start = m.start()
    return text[start: start + 3000]


# ── Main analysis ──────────────────────────────────────────────────────────────

def _unwrap_bundled_html(text: str) -> str:
    """If the HTML is a bundle wrapper (contains the real HTML as a JSON string),
    extract and return the inner HTML.

    Some single-file prototypes use a bundle format where the actual HTML is
    stored as a JSON string inside a <script> tag, e.g.:
      <script type="text/javascript">"<!DOCTYPE html>\\n<html>...</script>

    Returns the inner HTML if found, otherwise returns the original text.
    """
    # Look for a script tag whose content starts with a JSON string containing HTML
    m = re.search(
        r"""<script[^>]*>\s*"<!DOCTYPE html[^"]*(?:\\"|[^"])*"\s*</script>""",
        text, re.DOTALL | re.IGNORECASE,
    )
    if m:
        # Extract the JSON string value
        inner = m.group(0)
        str_m = re.search(r'"(<!DOCTYPE html.*)"', inner, re.DOTALL)
        if str_m:
            try:
                return json.loads('"' + str_m.group(1) + '"')
            except (json.JSONDecodeError, Exception):
                pass

    # Alternative: last <script> whose content is just a long JSON string
    scripts = list(re.finditer(r"""<script[^>]*>(.*?)</script>""", text, re.DOTALL | re.IGNORECASE))
    for sc in reversed(scripts):
        content = sc.group(1).strip()
        if content.startswith('"<!DOCTYPE html') or content.startswith('"<!doctype html'):
            try:
                return json.loads(content)
            except (json.JSONDecodeError, Exception):
                pass

    return text


def analyze_prototype(html_path: Path) -> dict:
    """Analyze HTML prototype, return prototype-map dict."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    # Unwrap bundle wrapper if present (D-291).
    # Also extract asset scripts from the bundle for component classification.
    asset_scripts = _extract_asset_scripts(text)
    text = _unwrap_bundled_html(text)

    # Try HTML-parser extraction first
    extractor = _SectionExtractor()
    try:
        extractor.feed(text)
    except Exception:
        pass  # tolerate malformed HTML

    screens = extractor.screens

    # Fallback to JSX/keyword extraction if nothing found
    if len(screens) < 2:
        screens = _extract_jsx_screens(text)

    # Classify each screen (priority: HTML fragment > asset scripts > JSX body > name hint)
    for screen in screens:
        pattern = ""
        if screen.raw_html:
            pattern = _score_pattern(screen.raw_html, _PATTERN_RULES)
        if not pattern and asset_scripts:
            pattern = _classify_from_asset_scripts(screen.id, asset_scripts, text)
        if not pattern:
            fragment = _extract_jsx_component_body(text, screen.id)
            if fragment:
                pattern = _score_pattern(fragment, _PATTERN_RULES)
        if not pattern:
            pattern = _hint_pattern_from_name(screen.id)
        screen.pattern = pattern
        screen.lib = _id_to_lib(screen.id)
        screen.components = _infer_components(screen.lib, screen.pattern)

    # Build output map
    pattern_summary: dict[str, int] = {}
    screen_entries = []
    for s in screens:
        pattern_summary[s.pattern] = pattern_summary.get(s.pattern, 0) + 1
        screen_entries.append({
            "id": s.id,
            "label": s.label,
            "pattern": s.pattern,
            "lib": s.lib,
            "components": s.components,
        })

    return {
        "source": str(html_path),
        "screensFound": len(screens),
        "screens": screen_entries,
        "patternSummary": pattern_summary,
    }


# ── Directory mode (D-292) ────────────────────────────────────────────────────

def analyze_directory(dir_path: Path) -> dict:
    """Analyze a modular frontend-reference directory → prototype-map dict.

    Processes files matching '*-screen-*.html' (e.g. 03-screen-upload.html).
    Files like 01-shell.html, 02-components.html and 00-tokens.css are ignored
    because they don't match the glob pattern — convention from /estagio-0-ui.

    The number of screens is determined dynamically from the directory contents.
    Screen IDs are derived from filenames (strip leading NN- prefix), so the
    result is independent of the HTML structure inside each file.

    Classification strategy: name-based hint ONLY.
    Full-file content scoring is avoided in directory mode because each file
    embeds a complete shell (sidebar + topbar + JS router) that contaminates
    the content signal — e.g. sidebar navigation containing "Dashboards" would
    score every screen as P4, and shared JS "board" identifiers would score as P6.
    The fe-feature-architect agent reads the actual HTML files and can override
    the pattern when it finds a stronger signal.
    """
    screen_files = sorted(dir_path.glob("*-screen-*.html"))
    screens: list[Screen] = []

    for f in screen_files:
        screen_id = _screen_id_from_filename(f.stem)
        pattern = _hint_pattern_from_name(screen_id)

        lib = _id_to_lib(screen_id)
        components = _infer_components(lib, pattern)
        screens.append(Screen(
            id=screen_id,
            label=_id_to_label(screen_id),
            raw_html="",
            pattern=pattern,
            lib=lib,
            components=components,
        ))

    pattern_summary: dict[str, int] = {}
    screen_entries = []
    for s in screens:
        pattern_summary[s.pattern] = pattern_summary.get(s.pattern, 0) + 1
        screen_entries.append({
            "id": s.id,
            "label": s.label,
            "pattern": s.pattern,
            "lib": s.lib,
            "components": s.components,
        })

    return {
        "source": str(dir_path),
        "mode": "directory",
        "screensFound": len(screens),
        "screens": screen_entries,
        "patternSummary": pattern_summary,
    }


# ── Subcommands ────────────────────────────────────────────────────────────────

def cmd_analyze(args: argparse.Namespace) -> int:
    html_path = Path(args.prototype).resolve()
    if not html_path.exists():
        print(f"error: path not found: {html_path}", file=sys.stderr)
        return 1

    try:
        if html_path.is_dir():
            result = analyze_directory(html_path)
        elif html_path.suffix.lower() == ".html":
            result = analyze_prototype(html_path)
        else:
            print(f"error: expected .html file or directory, got: {html_path.suffix}", file=sys.stderr)
            return 2
    except Exception as exc:
        print(f"error: analysis failed: {exc}", file=sys.stderr)
        return 1

    if args.report or not args.output:
        # Print summary to stdout
        print(f"\nPrototype: {result['source']}")
        print(f"Screens found: {result['screensFound']}")
        print(f"\nPattern summary: {result['patternSummary']}")
        print(f"\n{'ID':<30}  {'LABEL':<25}  {'PATTERN'}  {'LIB'}")
        print("-" * 90)
        for s in result["screens"]:
            print(f"{s['id']:<30}  {s['label']:<25}  {s['pattern']:<8}  {s['lib']}")

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(out_path.suffix + ".tmp")
        tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(out_path)
        print(f"\nOK: prototype-map written → {out_path}")

    return 0


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fe-prototype-analyzer",
        description="Analyze HTML prototype → prototype-map.json with P1-P7 pattern classification.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ana = sub.add_parser("analyze", help="Analyze an HTML prototype file")
    ana.add_argument(
        "--prototype", required=True, metavar="PATH",
        help="Path to the HTML prototype file",
    )
    ana.add_argument(
        "--output", metavar="PATH",
        help="Output path for prototype-map.json (default: print only)",
    )
    ana.add_argument(
        "--report", action="store_true",
        help="Always print summary to stdout (even when --output is set)",
    )

    args = parser.parse_args()

    dispatch = {"analyze": cmd_analyze}
    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(args))


if __name__ == "__main__":
    main()
