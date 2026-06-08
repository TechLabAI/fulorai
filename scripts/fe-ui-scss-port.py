#!/usr/bin/env python3
"""fe-ui-scss-port.py — Port a screen CSS file to Angular component SCSS.

LAYER 3 script (D-315): deterministic, no AI. Takes a screen's CSS from
`raw/` and produces a `*.component.scss` with all `var(--xxx)` replaced by
SCSS token references from `ui-tokens-map.json`.

The agent handles judgment (template HTML bindings, signals, facade wiring).
This script handles the mechanical CSS-to-SCSS token port.

Usage:
    python scripts/fe-ui-scss-port.py port \\
        --raw docs/architecture/frontend/issues/raw/lead-list.css \\
        --token-map docs/architecture/frontend/ui-design-system/ui-tokens-map.json \\
        --output frontend/libs/lead/feature-lead-list/src/lib/lead-list.component.scss

    python scripts/fe-ui-scss-port.py port \\
        --raw ... --token-map ... --output ... --report

R3: argparse, atomic write, OK:/error:, exit 0/1/2.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Spacing property names where a bare px value likely signals a hardcoded token
_SPACING_PROPS = frozenset([
    "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
    "gap", "row-gap", "column-gap",
    "width", "min-width", "max-width",
    "height", "min-height", "max-height",
    "top", "right", "bottom", "left",
    "inset", "inset-block", "inset-inline",
])

# px values <= this are typically fine (borders, outlines) — not flagged
_PX_TINY_THRESHOLD = 4


def _build_token_index(token_map: list[dict]) -> dict[str, str]:
    """Return {cssVar: scssName} from ui-tokens-map.json."""
    return {entry["cssVar"]: entry["scssName"] for entry in token_map}


def _replace_css_vars(css_text: str, index: dict[str, str]) -> tuple[str, list[str], list[str]]:
    """Replace var(--xxx) occurrences; return (ported_css, replaced, unmapped)."""
    replaced: list[str] = []
    unmapped: list[str] = []

    def _sub(m: re.Match) -> str:
        var_name = m.group(1).strip()
        if var_name in index:
            replaced.append(var_name)
            return index[var_name]
        unmapped.append(var_name)
        return m.group(0)  # leave as-is

    ported = re.sub(r"var\(\s*(--[\w-]+)\s*\)", _sub, css_text)
    return ported, replaced, unmapped


def _wrap_host(scss_text: str) -> str:
    """Wrap SCSS content in :host { } for Angular component encapsulation."""
    # Already wrapped? Leave it.
    if scss_text.lstrip().startswith(":host"):
        return scss_text
    # Indent each line by 2 spaces inside :host
    indented = "\n".join("  " + line if line.strip() else line for line in scss_text.splitlines())
    return f":host {{\n{indented}\n}}\n"


def _detect_unmapped_warnings(css_text: str, unmapped: list[str]) -> list[str]:
    """Return warning lines for unmapped var() usages with usage context."""
    warnings: list[str] = []
    for var_name in sorted(set(unmapped)):
        count = css_text.count(var_name)
        warnings.append(f"  unmapped: {var_name} ({count} usage(s))")
    return warnings


def port(raw_css: Path, token_map_path: Path, output: Path, report: bool) -> int:
    if not raw_css.exists():
        print(f"error: raw CSS not found: {raw_css}", file=sys.stderr)
        return 1
    if not token_map_path.exists():
        print(f"error: token map not found: {token_map_path}", file=sys.stderr)
        return 1

    token_map = json.loads(token_map_path.read_text(encoding="utf-8"))
    index = _build_token_index(token_map)

    css_text = raw_css.read_text(encoding="utf-8", errors="ignore")
    ported, replaced, unmapped = _replace_css_vars(css_text, index)
    scss_out = _wrap_host(ported)

    # Write atomically
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(".scss.tmp")
    tmp.write_text(scss_out, encoding="utf-8")
    tmp.replace(output)

    print(f"OK: ported {raw_css.name} -> {output} "
          f"({len(set(replaced))} var replaced, {len(set(unmapped))} unmapped)")

    if report or unmapped:
        print(f"  replaced: {len(set(replaced))} unique CSS vars -> SCSS tokens")
        for w in _detect_unmapped_warnings(css_text, unmapped):
            print(w)
        if unmapped:
            print("  NOTE: unmapped vars kept as var(--xxx) — agent should review")

    return 0 if not unmapped else 1


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fe-ui-scss-port",
        description="Port screen CSS to Angular component SCSS using token map.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    port_p = sub.add_parser("port", help="Port a raw CSS screen file to component SCSS")
    port_p.add_argument(
        "--raw", required=True, metavar="FILE",
        help="Path to the raw screen CSS file (e.g. raw/lead-list.css)",
    )
    port_p.add_argument(
        "--token-map", required=True, metavar="FILE",
        help="Path to ui-tokens-map.json (from fe-ui-token-extractor.py)",
    )
    port_p.add_argument(
        "--output", required=True, metavar="FILE",
        help="Output path for *.component.scss",
    )
    port_p.add_argument(
        "--report", action="store_true",
        help="Print detailed replacement summary even when all vars are mapped",
    )

    args = parser.parse_args()

    if args.command == "port":
        sys.exit(port(
            Path(args.raw).resolve(),
            Path(args.token_map).resolve(),
            Path(args.output).resolve(),
            args.report,
        ))


if __name__ == "__main__":
    main()
