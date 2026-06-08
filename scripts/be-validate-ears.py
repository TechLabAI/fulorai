#!/usr/bin/env python3
"""be-validate-ears.py - validate EARS notation in service-spec markdown (D-111).

EARS (Easy Approach to Requirements Syntax) is the convention shipped in
templates/architecture/backend/standards/ears-notation.md.j2 (D-057, Tier
1.3). Five patterns are accepted; this script parses markdown files and
flags sentences that don't match exactly one of them.

Patterns:
  Ubiquitous       THE SYSTEM SHALL <response>
  Event-driven     WHEN <trigger>, THE SYSTEM SHALL <response>
  State-driven     WHILE <state>, THE SYSTEM SHALL <response>
  Optional         WHERE <feature>, THE SYSTEM SHALL <response>
  Unwanted         IF <undesired>, THEN THE SYSTEM SHALL <response>

Detection modes:

  default (heuristic) - any line containing `THE SYSTEM SHALL` is a
                       candidate. Backticks, list markers, and leading
                       whitespace are stripped before matching.
  --block-mode        - only validate lines inside <!-- ears-block --> ...
                       <!-- /ears-block --> sections; lines outside are
                       skipped. Suits projects that want explicit gating.

Usage:
    python scripts/be-validate-ears.py --file <path>
    python scripts/be-validate-ears.py --all-specs
    python scripts/be-validate-ears.py --all-specs --block-mode --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from cli_utils import force_utf8_stdio


# ── Pattern recognition ──────────────────────────────────────────────────────

_SHALL_PROBE = re.compile(r"\bTHE SYSTEM SHALL\b")
_SHALL_PROBE_LOWER = re.compile(r"\bthe system shall\b", re.IGNORECASE)
_LEADING_NOISE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|>\s+)?")
_BACKTICK_CONTENT = re.compile(r"`([^`]+)`")

PATTERNS = [
    ("unwanted",     re.compile(r"^IF\b.+?,?\s*THEN\s+THE SYSTEM SHALL(?:\s+NOT)?\b.+?$")),
    ("event-driven", re.compile(r"^WHEN\b.+?,\s*THE SYSTEM SHALL(?:\s+NOT)?\b.+?$")),
    ("state-driven", re.compile(r"^WHILE\b.+?,\s*THE SYSTEM SHALL(?:\s+NOT)?\b.+?$")),
    ("optional",     re.compile(r"^WHERE\b.+?,\s*THE SYSTEM SHALL(?:\s+NOT)?\b.+?$")),
    ("ubiquitous",   re.compile(r"^THE SYSTEM SHALL(?:\s+NOT)?\b.+?$")),
]


@dataclass
class Issue:
    path: Path
    line: int
    text: str
    severity: str  # "error" | "warning"
    message: str
    suggestion: str | None = None

    def render(self) -> str:
        sev = self.severity.upper()
        out = [f"  {self.path}:{self.line}  [{sev}] {self.message}"]
        if self.text:
            snippet = self.text.strip()
            if len(snippet) > 100:
                snippet = snippet[:97] + "..."
            out.append(f"    sentence: {snippet}")
        if self.suggestion:
            out.append(f"    suggestion: {self.suggestion}")
        return "\n".join(out)


def _strip_markdown(line: str) -> str:
    """Strip list markers + blockquote prefix + leading whitespace.

    Backticks are preserved here because the pattern regexes operate on the
    unwrapped sentence; the caller extracts backtick content separately
    when present.
    """
    return _LEADING_NOISE.sub("", line).rstrip()


def _candidate_sentences(line: str) -> list[str]:
    """Return EARS-candidate sentences pulled from a markdown line.

    A line may carry the EARS sentence as plain text or inside backticks
    (the workspace templates use backticks heavily). Both are returned —
    the caller validates each independently.
    """
    stripped = _strip_markdown(line)
    if not stripped:
        return []
    found = _BACKTICK_CONTENT.findall(stripped)
    if found:
        return [c.strip() for c in found if _SHALL_PROBE_LOWER.search(c)]
    if _SHALL_PROBE_LOWER.search(stripped):
        return [stripped]
    return []


def classify(sentence: str) -> tuple[str | None, str | None]:
    """Return (pattern_id, error_message). pattern_id None when no pattern
    matched; error_message describes the most likely fix.
    """
    s = sentence.strip()
    if not s:
        return None, None

    # Trigger-keyword detection (uppercase enforced — that's a separate check)
    upper = s.upper()
    head = upper.split(None, 1)[0] if upper else ""

    # Specific malformed shapes give better diagnostics than the generic
    # "doesn't match any pattern" message.
    if head == "IF" and "THEN" not in upper:
        return None, (
            "IF clause without THEN — Unwanted pattern requires "
            "'IF <condition>, THEN THE SYSTEM SHALL <response>'"
        )
    if head in ("WHEN", "WHILE", "WHERE") and "," not in s:
        return None, (
            f"{head} clause missing the comma before THE SYSTEM SHALL — "
            f"required by the {head}-pattern grammar"
        )

    for pat_id, regex in PATTERNS:
        if regex.match(s):
            return pat_id, None
    return None, "sentence doesn't match any of the 5 EARS patterns"


def _check_uppercase(sentence: str) -> str | None:
    """Return a warning when EARS keywords appear in non-uppercase, else None.

    Scoped to the SENTENCE-LEADING trigger word + the THE SYSTEM SHALL anchor.
    Free-form prose elsewhere (e.g. "when the consumer recovers") doesn't
    count — EARS only cares about the structural keywords at the head of
    each clause, not English vocabulary throughout.
    """
    lower_hit = _SHALL_PROBE_LOWER.search(sentence)
    upper_hit = _SHALL_PROBE.search(sentence)
    if lower_hit and not upper_hit:
        return "EARS keywords must be uppercase ('THE SYSTEM SHALL', not the lowercase form)"
    leading = sentence.lstrip().split(None, 1)[0] if sentence.strip() else ""
    if leading.lower() in {"when", "while", "where", "if"} and leading != leading.upper():
        return (
            f"leading trigger keyword {leading!r} must be uppercase "
            f"(e.g. {leading.upper()!r})"
        )
    # Unwanted pattern: THEN is the only second-position structural keyword.
    if leading.upper() == "IF":
        # Look for the first occurrence of `then` (case-insensitive) AFTER
        # the IF clause; only complain if it appears in lowercase.
        m = re.search(r",\s*(?P<then>then)\b\s+THE\s+SYSTEM", sentence, re.IGNORECASE)
        if m and m.group("then") != "THEN":
            return "the THEN connector must be uppercase ('IF ..., THEN THE SYSTEM SHALL ...')"
    return None


def _check_nested(sentence: str) -> str | None:
    """Flag nested conditionals like 'WHEN X, IF Y, THEN ...' — EARS forbids
    stacking. Authors should split into two requirements.

    Only counts UPPERCASE trigger words (case-sensitive) to avoid flagging
    English prose that happens to include the word "when" or "if".
    """
    triggers_seen = sum(1 for kw in ("WHEN", "WHILE", "WHERE", "IF")
                        if re.search(rf"\b{kw}\b", sentence))
    if triggers_seen > 1:
        return ("nested conditional — pick one trigger keyword per sentence "
                "and split if needed")
    return None


def _scan_blocks(text: str) -> list[tuple[int, int]]:
    """Return (start_line, end_line) ranges (1-indexed, inclusive) of every
    `<!-- ears-block -->` / `<!-- /ears-block -->` block."""
    out: list[tuple[int, int]] = []
    start: int | None = None
    for i, line in enumerate(text.splitlines(), start=1):
        if "<!-- ears-block -->" in line:
            start = i
        elif "<!-- /ears-block -->" in line and start is not None:
            out.append((start, i))
            start = None
    return out


def validate_file(path: Path, *, block_mode: bool, strict: bool) -> list[Issue]:
    """Return issues for one markdown file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [Issue(path=path, line=0, text="", severity="error",
                     message=f"cannot read file: {e}")]

    issues: list[Issue] = []
    block_ranges = _scan_blocks(text) if block_mode else None

    for lineno, line in enumerate(text.splitlines(), start=1):
        if block_ranges is not None and not any(
            start <= lineno <= end for start, end in block_ranges
        ):
            continue
        sentences = _candidate_sentences(line)
        if not sentences:
            continue
        for sentence in sentences:
            case_warn = _check_uppercase(sentence)
            if case_warn:
                issues.append(Issue(
                    path=path, line=lineno, text=sentence,
                    severity="error", message=case_warn,
                ))
                continue
            nested_warn = _check_nested(sentence)
            if nested_warn:
                issues.append(Issue(
                    path=path, line=lineno, text=sentence,
                    severity="error", message=nested_warn,
                    suggestion="rewrite as two sentences, one per trigger",
                ))
                continue
            pat, err = classify(sentence)
            if pat is None:
                issues.append(Issue(
                    path=path, line=lineno, text=sentence,
                    severity="error",
                    message=err or "EARS pattern not recognized",
                ))
                continue
            if strict and sentence.rstrip().endswith(".."):
                issues.append(Issue(
                    path=path, line=lineno, text=sentence,
                    severity="warning",
                    message="sentence ends with multiple dots — EARS style "
                            "uses a single period (or none)",
                ))
    return issues


def find_spec_files(root: Path) -> list[Path]:
    """Walk both workspace standards and rendered project specs.

    Catches:
      - templates/sdd/service-spec/*.md.j2 (workspace authoring templates)
      - docs/architecture/backend/services/*/service-spec.md (rendered)
      - docs/architecture/backend/services/*/spec/backend/*.md
      - docs/architecture/backend/services/*/contracts/*.md
    """
    candidates: list[Path] = []
    for sub in ("docs/architecture/backend/services",):
        base = root / sub
        if base.is_dir():
            candidates.extend(sorted(base.rglob("*.md")))
    tpl = root / "templates" / "sdd" / "service-spec"
    if tpl.is_dir():
        candidates.extend(sorted(tpl.rglob("*.md.j2")))
    return candidates


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="be-validate-ears.py",
        description="Validate EARS notation in service-spec markdown (D-111, A3).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/be-validate-ears.py --file docs/.../service-spec.md\n"
            "  python scripts/be-validate-ears.py --all-specs\n"
            "  python scripts/be-validate-ears.py --all-specs --block-mode --strict\n"
        ),
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--file", type=Path,
                        help="Validate one markdown file.")
    target.add_argument("--all-specs", action="store_true",
                        help="Walk docs/architecture/backend/services/ + "
                             "templates/sdd/service-spec/ and validate every "
                             "markdown (rendered + .md.j2 templates).")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="Root for --all-specs walk (default: cwd).")
    parser.add_argument("--block-mode", action="store_true",
                        help="Only validate lines inside <!-- ears-block --> "
                             "markers; ignore prose elsewhere.")
    parser.add_argument("--strict", action="store_true",
                        help="Also report style warnings (trailing-dot etc.).")
    args = parser.parse_args(argv)

    files = [args.file] if args.file else find_spec_files(args.root.resolve())
    if not files:
        print("(no markdown files matched the search)", file=sys.stderr)
        return 0

    all_issues: list[Issue] = []
    for f in files:
        all_issues.extend(validate_file(
            f, block_mode=args.block_mode, strict=args.strict,
        ))

    n_errors = sum(1 for i in all_issues if i.severity == "error")
    n_warnings = sum(1 for i in all_issues if i.severity == "warning")

    if all_issues:
        for issue in all_issues:
            print(issue.render())
        print()
        print(f"Result: {n_errors} error(s), {n_warnings} warning(s) "
              f"across {len(files)} file(s).")
        return 1 if n_errors else 0

    print(f"Result: 0 issues across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
