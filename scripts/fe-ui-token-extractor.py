#!/usr/bin/env python3
"""fe-ui-token-extractor.py — Extract CSS custom properties → SCSS tokens + catalog.

LAYER 3 script (D-315): deterministic, no AI. Takes the prototype design system
files (00-tokens.css, shell.css, 02-components.html) and produces:

  1. ui-tokens-map.json      — CSS var → SCSS token name + category mapping.
  2. ui-tokens.scss          — SCSS partial with all tokens ($token-name: var(--xxx)).
  3. components-catalog.md   — Inventory of shell primitives and their hybrid
                               classification suggestion (Material vs custom, D-309).

These outputs are consumed by the `fe-ui-tokens` command (the agent reads the
catalog and decides borderline Material/custom splits).

Usage:
    python scripts/fe-ui-token-extractor.py extract \\
        --prototype frontend/design-reference \\
        --output docs/architecture/frontend/ui-design-system

    python scripts/fe-ui-token-extractor.py extract \\
        --prototype frontend/design-reference \\
        --output docs/architecture/frontend/ui-design-system \\
        --report

R3: argparse, atomic write, OK:/error:, exit 0/1/2.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── Token category detection ──────────────────────────────────────────────────

_CATEGORY_RULES: list[tuple[str, str]] = [
    (r"--color|--bg|--text|--border|--icon|--surface|--overlay|--on-", "color"),
    (r"--font|--type|--text-size|--line-height|--letter-spacing|--font-weight", "typography"),
    (r"--space|--gap|--padding|--margin|--inset", "spacing"),
    (r"--radius|--rounded", "radius"),
    (r"--shadow|--elevation|--ring", "shadow"),
    (r"--transition|--duration|--ease|--motion", "motion"),
    (r"--sidebar|--topbar|--drawer|--shell|--density", "layout"),
    (r"--z-|--z-index", "z-index"),
]

# Primitives from shell.css that are likely Material candidates (D-309)
_MATERIAL_CANDIDATES: list[str] = [
    "dialog", "modal", "tooltip", "snackbar", "toast", "menu", "select",
    "datepicker", "autocomplete", "chip", "checkbox", "radio", "toggle",
    "form-field", "input", "textarea", "progress", "spinner",
    "table", "sort", "paginator",
]

_CUSTOM_KEEP: list[str] = [
    "sidebar", "topbar", "tab", "btn", "button", "card", "badge",
    "ai-drawer", "score", "kpi", "kanban", "builder", "canvas",
    "breadcrumb", "avatar", "status-dot",
]


def _categorize_token(name: str) -> str:
    """Return the semantic category for a CSS custom property name."""
    for pattern, category in _CATEGORY_RULES:
        if re.search(pattern, name, re.IGNORECASE):
            return category
    return "misc"


def _to_scss_name(css_var: str) -> str:
    """Convert --color-primary-500 → $color-primary-500."""
    slug = css_var.lstrip("-")
    return f"${slug}"


def _to_scss_theme_pair(css_var: str, light_val: str, dark_val: str | None) -> str:
    """Emit a SCSS variable forwarding to the CSS var with optional dark note."""
    scss_name = _to_scss_name(css_var)
    comment = f"  // dark: {dark_val}" if dark_val else ""
    return f"{scss_name}: var({css_var});{comment}"


# ── CSS parser helpers ────────────────────────────────────────────────────────


def _parse_css_vars(css_text: str) -> dict[str, dict[str, str]]:
    """Extract CSS custom properties and their values.

    Returns {var_name: {"light": value, "dark": value_or_empty}}.
    Handles both :root { --x: val } and [data-theme="dark"] { --x: val }.
    """
    tokens: dict[str, dict[str, str]] = {}

    # Light values from :root or bare selector
    for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}\n]+)", css_text):
        name, val = m.group(1).strip(), m.group(2).strip()
        tokens.setdefault(name, {"light": "", "dark": ""})
        tokens[name]["light"] = val

    # Dark overrides inside [data-theme="dark"] or .dark blocks
    dark_block = re.search(
        r'\[data-theme=["\']dark["\']\]\s*\{([^}]+)\}|\.dark\s*\{([^}]+)\}',
        css_text, re.DOTALL | re.IGNORECASE,
    )
    if dark_block:
        block = dark_block.group(1) or dark_block.group(2) or ""
        for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}\n]+)", block):
            name, val = m.group(1).strip(), m.group(2).strip()
            tokens.setdefault(name, {"light": "", "dark": ""})
            tokens[name]["dark"] = val

    return tokens


def _extract_class_names(css_text: str) -> list[str]:
    """Extract unique CSS class names from a stylesheet."""
    classes = re.findall(r"\.([\w-]+)\s*(?:\{|,)", css_text)
    # Deduplicate, preserve order
    seen: set[str] = set()
    result: list[str] = []
    for c in classes:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result


def _extract_html_components(html_text: str) -> list[str]:
    """Extract component class hints from HTML (class= attributes)."""
    raw = re.findall(r'class="([^"]+)"', html_text)
    classes: set[str] = set()
    for group in raw:
        for cls in group.split():
            classes.add(cls)
    return sorted(classes)


# ── Hybrid classification for primitives ─────────────────────────────────────


def _classify_primitive(class_name: str) -> str:
    """Return 'material', 'custom', or 'review' for a CSS class name."""
    lower = class_name.lower()
    for mat in _MATERIAL_CANDIDATES:
        if mat in lower:
            return "material"
    for cust in _CUSTOM_KEEP:
        if cust in lower:
            return "custom"
    return "review"


# ── Main extraction logic ─────────────────────────────────────────────────────


def extract(prototype_dir: Path, output_dir: Path, report: bool) -> int:
    tokens_css = prototype_dir / "00-tokens.css"
    shell_css = prototype_dir / "shell.css"
    components_html = prototype_dir / "02-components.html"

    missing = [f for f in [tokens_css, shell_css] if not f.exists()]
    if missing:
        for f in missing:
            print(f"error: required file not found: {f}", file=sys.stderr)
        return 1

    # Parse tokens
    tokens_text = tokens_css.read_text(encoding="utf-8", errors="ignore")
    css_vars = _parse_css_vars(tokens_text)

    # Augment with shell.css vars (may define layout tokens)
    if shell_css.exists():
        shell_text = shell_css.read_text(encoding="utf-8", errors="ignore")
        for name, vals in _parse_css_vars(shell_text).items():
            if name not in css_vars:
                css_vars[name] = vals

    # Build token map
    token_map: list[dict] = []
    for name, vals in sorted(css_vars.items()):
        category = _categorize_token(name)
        scss_name = _to_scss_name(name)
        token_map.append({
            "cssVar": name,
            "scssName": scss_name,
            "category": category,
            "lightValue": vals["light"],
            "darkValue": vals.get("dark", ""),
        })

    if report:
        print(f"\nToken extraction: {prototype_dir}")
        print(f"Tokens found: {len(token_map)}")
        cats: dict[str, int] = {}
        for t in token_map:
            cats[t["category"]] = cats.get(t["category"], 0) + 1
        print(f"By category: {cats}")

    # Build SCSS partial
    scss_lines: list[str] = [
        "// Auto-generated by fe-ui-token-extractor.py — do not edit manually.",
        "// Source: 00-tokens.css + shell.css from the design prototype.",
        "// Re-generate: python scripts/fe-ui-token-extractor.py extract ...",
        "",
    ]
    by_category: dict[str, list[dict]] = {}
    for t in token_map:
        by_category.setdefault(t["category"], []).append(t)

    for cat in ["color", "typography", "spacing", "radius", "shadow", "layout", "motion", "z-index", "misc"]:
        group = by_category.get(cat, [])
        if not group:
            continue
        scss_lines.append(f"// ── {cat.capitalize()} ────────────────────────────────────────────────────")
        for t in group:
            dark_comment = f"  // dark: {t['darkValue']}" if t["darkValue"] else ""
            scss_lines.append(f"{t['scssName']}: var({t['cssVar']});{dark_comment}")
        scss_lines.append("")

    scss_content = "\n".join(scss_lines)

    # Components catalog from shell.css classes + 02-components.html
    shell_classes = _extract_class_names(shell_text) if shell_css.exists() else []
    html_classes: list[str] = []
    if components_html.exists():
        html_text = components_html.read_text(encoding="utf-8", errors="ignore")
        html_classes = _extract_html_components(html_text)

    all_primitives = sorted(set(shell_classes + html_classes))

    catalog_lines: list[str] = [
        "# UI Components Catalog",
        "",
        "> Auto-generated by `fe-ui-token-extractor.py`.",
        "> Review `material` / `custom` column — agent may override per-screen.",
        "",
        "## Primitives (shell.css + 02-components.html)",
        "",
        "| Class | Hybrid Classification | Notes |",
        "|---|---|---|",
    ]
    material_list: list[str] = []
    custom_list: list[str] = []
    review_list: list[str] = []
    for cls in all_primitives:
        verdict = _classify_primitive(cls)
        notes = ""
        if verdict == "material":
            notes = "→ use Material component + token theming"
            material_list.append(cls)
        elif verdict == "custom":
            notes = "→ keep CSS custom implementation"
            custom_list.append(cls)
        else:
            notes = "**review** — decide Material or custom"
            review_list.append(cls)
        catalog_lines.append(f"| `.{cls}` | {verdict} | {notes} |")

    catalog_lines += [
        "",
        "## Summary",
        "",
        f"- Material candidates: {len(material_list)}",
        f"- Custom (keep): {len(custom_list)}",
        f"- Needs agent review: {len(review_list)}",
        "",
        "## Tokens by category",
        "",
        "| Category | Count |",
        "|---|---|",
    ]
    for cat, group in sorted(by_category.items()):
        catalog_lines.append(f"| {cat} | {len(group)} |")

    catalog_content = "\n".join(catalog_lines) + "\n"

    if report:
        print(f"\nPrimitives found: {len(all_primitives)}")
        print(f"  material={len(material_list)}, custom={len(custom_list)}, review={len(review_list)}")

    # Write outputs atomically
    output_dir.mkdir(parents=True, exist_ok=True)

    map_path = output_dir / "ui-tokens-map.json"
    tmp = map_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(token_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(map_path)

    scss_path = output_dir / "ui-tokens.scss"
    tmp_scss = scss_path.with_suffix(".scss.tmp")
    tmp_scss.write_text(scss_content, encoding="utf-8")
    tmp_scss.replace(scss_path)

    cat_path = output_dir / "components-catalog.md"
    tmp_cat = cat_path.with_suffix(".md.tmp")
    tmp_cat.write_text(catalog_content, encoding="utf-8")
    tmp_cat.replace(cat_path)

    print(f"OK: extracted {len(token_map)} tokens, {len(all_primitives)} primitives")
    print(f"    -> {map_path}")
    print(f"    -> {scss_path}")
    print(f"    -> {cat_path}")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fe-ui-token-extractor",
        description="Extract CSS tokens and primitives from the design prototype → SCSS + catalog.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ext_p = sub.add_parser("extract", help="Run extraction on a prototype directory")
    ext_p.add_argument(
        "--prototype", required=True, metavar="DIR",
        help="Path to the vendored prototype directory (frontend/design-reference)",
    )
    ext_p.add_argument(
        "--output", required=True, metavar="DIR",
        help="Output directory for ui-tokens-map.json, ui-tokens.scss, components-catalog.md",
    )
    ext_p.add_argument(
        "--report", action="store_true",
        help="Print summary to stdout in addition to writing files",
    )

    args = parser.parse_args()

    if args.command == "extract":
        prototype_dir = Path(args.prototype).resolve()
        if not prototype_dir.is_dir():
            print(f"error: prototype path is not a directory: {prototype_dir}", file=sys.stderr)
            sys.exit(2)
        sys.exit(extract(prototype_dir, Path(args.output).resolve(), args.report))


if __name__ == "__main__":
    main()
