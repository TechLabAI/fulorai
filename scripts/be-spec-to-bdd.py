#!/usr/bin/env python3
"""be-spec-to-bdd.py -- Generate executable BDD artifacts from EARS specs.

Reads EARS markdown (the same dialect parsed by
`scripts/be_spec_drift_lib/ears_parser.py`) and emits:

  <output-root>/src/test/resources/features/<module>.feature
  <output-root>/src/test/java/<pkg>/bdd/<Module>StepDefs.java
  <output-root>/src/test/resources/application-bdd.properties  (opt-in)
  <output-root>/src/test/java/<pkg>/bdd/CucumberSpringContext.java  (opt-in)

The generated step methods throw `io.cucumber.java.PendingException` so that
Cucumber classifies each scenario as *pending* until the team implements it
(D-214). Build-patch emission (D-215) prints a `dependencies { ... }` block
suitable for copy/paste into a service `build.gradle.kts`.

Pipeline position (D-218):

    /be-architect-specs MODULE
      -> /be-architect-specs-validate MODULE   # runs this script + gradle test
        -> /be-architect-scaffold MODULE

Stream: Pole Position v3 -- S10 (Gap 1: specs as executable artefact).
Decisions: D-214 (PendingException), D-215 (Cucumber 7.x stack),
D-216 (EARS->Gherkin keyword heuristic), D-217 (shared fixture).

Usage
-----
    python scripts/be-spec-to-bdd.py generate \\
        --module OBR \\
        --spec-root services/obras-service/spec \\
        --output-root services/obras-service \\
        --package com.bosq.obr

    # Print the Cucumber dependency patch:
    python scripts/be-spec-to-bdd.py emit-build-patch

Exit codes
----------
    0  generated successfully (or build-patch printed)
    1  user error (missing args, paths not found)
    2  validation failure (no EARS clauses found in spec-root)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# Reuse the permissive EARS parser (D-160). Falls back to a direct import
# path if invoked as a script from another cwd.
from be_spec_drift_lib.ears_parser import EarsClause, parse_ears, parse_ears_tree  # noqa: E402


# ---------------------------------------------------------------------------
# Gherkin model
# ---------------------------------------------------------------------------


@dataclass
class GherkinStep:
    keyword: str  # Given | When | Then | And
    text: str


@dataclass
class GherkinScenario:
    name: str
    steps: list[GherkinStep] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    source_clause: Optional[EarsClause] = None  # for diagnostics


# ---------------------------------------------------------------------------
# EARS -> Gherkin heuristics (D-216)
# ---------------------------------------------------------------------------


_HTTP_PREFIX_STATUS_RX = re.compile(
    r"\b(?:HTTP|status(?:\s+code)?|return(?:s|ed)?)\s+(\d{3})\b",
    re.IGNORECASE,
)
_STATUS_RX = re.compile(r"\b(\d{3})\b")
_VALID_HTTP_CODES = {
    "200", "201", "202", "204",
    "301", "302", "304",
    "400", "401", "403", "404", "405", "409", "410", "412", "415", "422", "429",
    "500", "502", "503", "504",
}
_VERB_PATH_RX = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\s+(`)?(/[A-Za-z0-9_\-/{}.:]+)`?",
    re.IGNORECASE,
)
_TOPIC_RX = re.compile(r"\btopic\s+`?([A-Za-z0-9_.\-]+)`?", re.IGNORECASE)
_EVENT_NAME_RX = re.compile(r"\bpublish\s+`?([A-Z][A-Za-z0-9]+)`?\s+event", re.IGNORECASE)
_ROLE_RX = re.compile(r"\brole[s]?\s+`?([A-Z][A-Z0-9_]+)`?", re.IGNORECASE)
_FIELD_BACKTICK_RX = re.compile(r"`([A-Za-z_][A-Za-z0-9_\.]*)`")


def _short(text: str, n: int = 60) -> str:
    """Return a one-line excerpt of `text`, truncated to `n` chars."""
    t = re.sub(r"\s+", " ", text).strip()
    return (t[: n - 1] + "...") if len(t) > n else t


def _detect_status(response: str) -> Optional[str]:
    """Find an HTTP status code in the clause response.

    Two-pass: first look for explicit `HTTP NNN` / `status NNN` / `return NNN`
    prefixes; only fall back to a bare 3-digit number if it appears in the
    known HTTP set. This avoids capturing `100` from "length <= 100 chars"
    (encountered in the SPEC-fixture event clause).
    """
    text = response or ""
    m = _HTTP_PREFIX_STATUS_RX.search(text)
    if m and m.group(1) in _VALID_HTTP_CODES:
        return m.group(1)
    for cand in _STATUS_RX.findall(text):
        if cand in _VALID_HTTP_CODES:
            return cand
    return None


def _detect_verb_path(response: str) -> Optional[tuple[str, str]]:
    m = _VERB_PATH_RX.search(response or "")
    if m:
        return m.group(1).upper(), m.group(3)
    return None


def _detect_topic(response: str) -> Optional[str]:
    m = _TOPIC_RX.search(response or "")
    return m.group(1) if m else None


def _detect_event_name(response: str) -> Optional[str]:
    m = _EVENT_NAME_RX.search(response or "")
    return m.group(1) if m else None


def _detect_role(text: str) -> Optional[str]:
    m = _ROLE_RX.search(text or "")
    return m.group(1) if m else None


def _detect_field(text: str) -> Optional[str]:
    """Pick the first backticked identifier that is *not* an HTTP code or topic name."""
    for cand in _FIELD_BACKTICK_RX.findall(text or ""):
        if cand.replace(".", "").isdigit():
            continue
        # Skip topic-like dotted identifiers (handled elsewhere)
        if "." in cand and not cand.endswith("Id"):
            continue
        return cand
    return None


_LOOSE_WHEN_THEN_RX = re.compile(
    r"^WHEN\s+(?P<trigger>.+?),\s+THEN\s+(?:the\s+system\s+)?SHALL\s+(?P<response>.+)$",
    re.IGNORECASE | re.DOTALL,
)


def _refine_loose(clause: EarsClause) -> EarsClause:
    """Detect WHEN..., THEN SHALL inside a loose clause and project it as event.

    The permissive ears_parser (D-160) does not match `WHEN X, THEN SHALL Y`
    because the `event` pattern there is `WHEN X, SHALL Y`. The fixture's
    clause 1 ("WHEN POST ..., THEN SHALL return HTTP 201") trips this. To
    avoid editing the shared parser, we re-classify here for the BDD use case.
    """
    if clause.pattern_type != "loose":
        return clause
    m = _LOOSE_WHEN_THEN_RX.match(clause.normalized_text)
    if not m:
        return clause
    return EarsClause(
        pattern_type="event",
        raw_text=clause.raw_text,
        normalized_text=clause.normalized_text,
        trigger=m.group("trigger").strip(),
        response=m.group("response").strip(),
        file=clause.file,
        line=clause.line,
        list_marker=clause.list_marker,
    )


def _scenario_name(clause: EarsClause) -> str:
    """Build a stable, human-readable scenario name for the clause."""
    response = (clause.response or clause.normalized_text or "").strip()
    status = _detect_status(response)

    if clause.pattern_type == "event":
        trigger = _short(clause.trigger or "", 40) or "event"
        if status:
            return f"Happy path -- {trigger} returns {status}"
        return f"Happy path -- {trigger}"

    if clause.pattern_type == "unwanted":
        trigger = _short(clause.trigger or "", 40) or "error path"
        if status:
            return f"Error path -- {trigger} returns {status}"
        return f"Error path -- {trigger}"

    if clause.pattern_type == "state":
        return f"Stateful -- {_short(clause.state or '', 40)}"

    if clause.pattern_type == "optional":
        return f"Feature flag -- {_short(clause.feature or '', 40)}"

    if clause.pattern_type == "ubiquitous":
        return f"Invariant -- {_short(response, 50)}"

    return f"Loose -- {_short(clause.normalized_text, 50)}"


def _clause_to_scenario(clause: EarsClause) -> GherkinScenario:
    """Map a single EarsClause to a Gherkin Scenario (D-216).

    The strategy is deterministic: detect well-known keywords in the clause
    response/trigger (HTTP status, verb+path, topic, role, field) and emit
    the corresponding Given/When/Then. Anything not matched falls through
    to a generic step labelled with the clause text so the team has a
    unique anchor in the step defs.
    """
    response = (clause.response or "").strip()
    trigger = (clause.trigger or "").strip()
    state = (clause.state or "").strip()
    feature = (clause.feature or "").strip()

    steps: list[GherkinStep] = []

    # ---- Given (precondition) ----
    if clause.pattern_type == "unwanted":
        status = _detect_status(response)
        role_in_trigger = _detect_role(trigger)
        field_in_trigger = _detect_field(trigger)
        if status == "401":
            steps.append(GherkinStep("Given", "no authentication token is provided"))
        elif status == "403" and role_in_trigger:
            steps.append(GherkinStep("Given", f"a JWT token without the {role_in_trigger} role"))
        elif status == "404":
            steps.append(GherkinStep("Given", "the target resource does not exist"))
        elif field_in_trigger and "blank" in trigger.lower():
            steps.append(GherkinStep("Given", f"the field {field_in_trigger} is blank"))
        elif field_in_trigger and "missing" in trigger.lower():
            steps.append(GherkinStep("Given", f"the field {field_in_trigger} is missing"))
        else:
            steps.append(GherkinStep("Given", f"the precondition {_short(trigger, 80)}"))
    elif clause.pattern_type == "event":
        steps.append(GherkinStep("Given", "an authenticated request with the required role"))
        steps.append(GherkinStep("And", f"the request payload satisfies {_short(trigger, 80)}"))
    elif clause.pattern_type == "state":
        steps.append(GherkinStep("Given", f"the system is in state {_short(state, 80)}"))
    elif clause.pattern_type == "optional":
        steps.append(GherkinStep("Given", f"the feature {_short(feature, 80)} is enabled"))
    else:
        steps.append(GherkinStep("Given", "an authenticated request with the required role"))

    # ---- When (action) ----
    verb_path = _detect_verb_path(response) or _detect_verb_path(trigger)
    if verb_path:
        verb, path = verb_path
        steps.append(GherkinStep("When", f"the client sends {verb} {path}"))
    else:
        steps.append(GherkinStep("When", f"the EARS clause is exercised: {_short(clause.normalized_text, 80)}"))

    # ---- Then (expected outcome) ----
    status = _detect_status(response)
    if status:
        steps.append(GherkinStep("Then", f"the response status is {status}"))

    event_name = _detect_event_name(response)
    topic = _detect_topic(response)
    if event_name and topic:
        steps.append(GherkinStep("And", f"event {event_name} is published on topic {topic}"))
    elif event_name:
        steps.append(GherkinStep("And", f"event {event_name} is published"))

    if "audit" in response.lower():
        steps.append(GherkinStep("And", "an audit log entry is emitted"))

    if "tenantcontextholder" in response.lower() or "tenantid" in response.lower():
        steps.append(GherkinStep("And", "the tenant context is resolved from the request"))

    # Fallback: every scenario MUST have at least one Then (otherwise the
    # Gherkin parser flags an incomplete scenario).
    if not any(s.keyword == "Then" for s in steps):
        steps.append(GherkinStep("Then", f"the system satisfies: {_short(response or clause.normalized_text, 80)}"))

    tags = [f"@ears-{clause.pattern_type}"]

    return GherkinScenario(
        name=_scenario_name(clause),
        steps=steps,
        tags=tags,
        source_clause=clause,
    )


# ---------------------------------------------------------------------------
# Gherkin emission
# ---------------------------------------------------------------------------


def _render_feature(module: str, scenarios: list[GherkinScenario], spec_files: list[Path]) -> str:
    sources = "\n".join(f"#   - {p}" for p in spec_files)
    lines: list[str] = []
    lines.append(f"# Generated by be-spec-to-bdd.py from EARS specs.")
    lines.append(f"# Module: {module}")
    lines.append(f"# Sources:")
    lines.append(sources)
    lines.append(f"# Edit step *implementations* freely. Re-running the generator")
    lines.append(f"# overwrites this .feature; commit it so drift is reviewable.")
    lines.append("")
    lines.append(f"Feature: {module} -- executable EARS specification")
    lines.append("")
    lines.append("  Background:")
    lines.append("    Given the application is up with the bdd profile")
    lines.append("")
    for sc in scenarios:
        for tag in sc.tags:
            lines.append(f"  {tag}")
        lines.append(f"  Scenario: {sc.name}")
        for step in sc.steps:
            lines.append(f"    {step.keyword} {step.text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Java step-defs emission
# ---------------------------------------------------------------------------


_JAVA_METHOD_SAFE_RX = re.compile(r"[^A-Za-z0-9 ]")


def _step_method_name(keyword: str, text: str, used: dict[str, int]) -> str:
    """Mirror the convention from `be-bdd-generator.py` (D-214 alignment)."""
    clean = _JAVA_METHOD_SAFE_RX.sub(" ", text)
    words = [w for w in clean.split() if w][:8]
    base = keyword.lower() + "".join(w.capitalize() for w in words)
    if base in used:
        used[base] += 1
        return f"{base}_{used[base]}"
    used[base] = 1
    return base


def _java_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _module_class_prefix(module: str) -> str:
    """`OBR` -> `Obr`, `auth-service` -> `AuthService`."""
    parts = re.split(r"[-_\s]+", module)
    return "".join(p.capitalize() for p in parts if p)


def _render_step_defs(module: str, package: str, scenarios: list[GherkinScenario]) -> str:
    seen: dict[tuple[str, str], None] = {}
    for sc in scenarios:
        for step in sc.steps:
            key = (step.keyword, step.text)
            if key not in seen:
                seen[key] = None
    # Background steps are emitted from the feature; include them here too
    # so the generated class is self-contained.
    background_steps = [("Given", "the application is up with the bdd profile")]
    for k in background_steps:
        seen.setdefault(k, None)

    used: dict[str, int] = {}
    method_blocks: list[str] = []
    for keyword, text in seen.keys():
        annotation_keyword = keyword if keyword in ("Given", "When", "Then", "And", "But") else "And"
        method_name = _step_method_name(annotation_keyword, text, used)
        safe_text = _java_escape(text)
        # Map "And"/"But" to the parent verb's annotation set -- Cucumber
        # accepts them as continuations, but the type-safe annotations live
        # under io.cucumber.java.en.{And,But}.
        method_blocks.append(
            f'    @{annotation_keyword}("{safe_text}")\n'
            f"    public void {method_name}() {{\n"
            f"        // D-214: pending until implemented.\n"
            f"        throw new io.cucumber.java.PendingException();\n"
            f"    }}"
        )

    methods = "\n\n".join(method_blocks)
    class_name = f"{_module_class_prefix(module)}StepDefs"

    return f"""package {package}.bdd;

import io.cucumber.java.en.And;
import io.cucumber.java.en.But;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import static org.springframework.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;

/**
 * Step definitions for {module} -- generated from EARS specs by be-spec-to-bdd.py.
 *
 * Every step starts as Cucumber-pending (D-214). Implement them progressively;
 * the build only validates that the class compiles, not that scenarios pass.
 *
 * Spring bootstrap lives in CucumberSpringContext (D-215). This class adds
 * MockMvc + a small JWT helper so step implementations can move past the
 * boilerplate. The helpers are unused (no-op) until the first step is fleshed
 * out -- safe to leave as-is while the scenarios stay pending.
 */
@AutoConfigureMockMvc
public class {class_name} {{

    @Autowired
    protected MockMvc mockMvc;

    /** Cached response between When/Then steps. */
    protected ResultActions lastResponse;

    /** JWT request post-processor for the given role (Spring Security test helper). */
    protected static org.springframework.test.web.servlet.request.RequestPostProcessor jwtWithRole(String role) {{
        return jwt().authorities(new org.springframework.security.core.authority.SimpleGrantedAuthority("ROLE_" + role));
    }}

{methods}
}}
"""


def _render_spring_context(package: str) -> str:
    return f"""package {package}.bdd;

import io.cucumber.spring.CucumberContextConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/**
 * Bootstraps the Spring context for Cucumber step definitions.
 * Generated by be-spec-to-bdd.py (D-215).
 */
@CucumberContextConfiguration
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("bdd")
public class CucumberSpringContext {{}}
"""


_APPLICATION_BDD_PROPERTIES = """\
# Generated by be-spec-to-bdd.py (D-215).
# Activated via @ActiveProfiles("bdd") in CucumberSpringContext.

spring.main.banner-mode=off
spring.jpa.hibernate.ddl-auto=create-drop
logging.level.root=WARN
logging.level.io.cucumber=INFO
"""


_BUILD_PATCH_TEMPLATE = (
    ROOT
    / "templates"
    / "operational"
    / "code"
    / "gradle"
    / "build-cucumber-bdd-patch.gradle.kts.j2"
)


def _load_build_patch(cucumber_version: str = "7.18.0") -> str:
    """Render the build-patch Jinja template into a plain kts snippet.

    The template uses one variable (`cucumber_version`) and a stripping Jinja
    header. To avoid pulling Jinja2 into this script's dependency surface, we
    inline a minimal renderer: strip the `{#- ... -#}` block, the `{%- set -%}`
    statement, and substitute `{{ cucumber_version }}` directly.
    """
    if not _BUILD_PATCH_TEMPLATE.exists():
        # Fallback so the CLI still works without the template (e.g. running
        # from a partial checkout).
        return (
            "    testImplementation(\"io.cucumber:cucumber-junit-platform-engine:"
            f"{cucumber_version}\")\n"
            "    testImplementation(\"io.cucumber:cucumber-java:"
            f"{cucumber_version}\")\n"
            "    testImplementation(\"io.cucumber:cucumber-spring:"
            f"{cucumber_version}\")\n"
        )
    text = _BUILD_PATCH_TEMPLATE.read_text(encoding="utf-8")
    # Strip Jinja comment block(s).
    text = re.sub(r"\{#-.*?-#\}\n?", "", text, flags=re.DOTALL)
    # Strip {%- set ... -%} statement(s).
    text = re.sub(r"\{%-?\s*set\s+[^%]+%\}\n?", "", text)
    # Substitute the one expected variable.
    text = text.replace("{{ cucumber_version }}", cucumber_version)
    return text.lstrip("\n")


# ---------------------------------------------------------------------------
# Spec discovery
# ---------------------------------------------------------------------------


def _discover_clauses(spec_root: Path) -> tuple[list[EarsClause], list[Path]]:
    """Collect EARS clauses + the markdown files they came from."""
    if spec_root.is_file():
        return parse_ears(spec_root), [spec_root]
    if not spec_root.is_dir():
        return [], []
    files: list[Path] = []
    clauses: list[EarsClause] = []
    for md in sorted(spec_root.rglob("*.md")):
        if md.is_file():
            found = parse_ears(md)
            if found:
                files.append(md.relative_to(spec_root.parent) if spec_root.parent in md.parents else md)
                clauses.extend(found)
    return clauses, files


# ---------------------------------------------------------------------------
# `generate` subcommand
# ---------------------------------------------------------------------------


def _cmd_generate(args: argparse.Namespace) -> int:
    module = args.module
    spec_root = Path(args.spec_root).resolve()
    output_root = Path(args.output_root).resolve()
    package = args.package or f"com.example.{module.lower()}"

    if not spec_root.exists():
        print(f"error: spec-root does not exist: {spec_root}", file=sys.stderr)
        return 1

    clauses, files = _discover_clauses(spec_root)
    if not clauses:
        print(f"error: no EARS clauses found under {spec_root}", file=sys.stderr)
        return 2

    scenarios = [_clause_to_scenario(_refine_loose(c)) for c in clauses]

    feature_dir = output_root / "src" / "test" / "resources" / "features"
    feature_dir.mkdir(parents=True, exist_ok=True)
    feature_path = feature_dir / f"{module.lower()}.feature"
    feature_path.write_text(_render_feature(module, scenarios, files), encoding="utf-8")

    pkg_path = package.replace(".", "/")
    java_dir = output_root / "src" / "test" / "java" / pkg_path / "bdd"
    java_dir.mkdir(parents=True, exist_ok=True)
    step_defs_path = java_dir / f"{_module_class_prefix(module)}StepDefs.java"
    step_defs_path.write_text(_render_step_defs(module, package, scenarios), encoding="utf-8")

    written = [feature_path, step_defs_path]

    if args.emit_spring_context:
        spring_path = java_dir / "CucumberSpringContext.java"
        spring_path.write_text(_render_spring_context(package), encoding="utf-8")
        written.append(spring_path)

        props_dir = output_root / "src" / "test" / "resources"
        props_dir.mkdir(parents=True, exist_ok=True)
        props_path = props_dir / "application-bdd.properties"
        props_path.write_text(_APPLICATION_BDD_PROPERTIES, encoding="utf-8")
        written.append(props_path)

    print(f"OK: be-spec-to-bdd generate {module}")
    print(f"     {len(clauses)} EARS clause(s) -> {len(scenarios)} scenario(s)")
    for w in written:
        try:
            rel = w.relative_to(output_root)
            print(f"     wrote {rel}")
        except ValueError:
            print(f"     wrote {w}")
    return 0


def _cmd_emit_build_patch(args: argparse.Namespace) -> int:
    print(_load_build_patch(args.cucumber_version), end="")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="be-spec-to-bdd",
        description="Generate executable BDD artefacts (Gherkin + Java step stubs) from EARS specs.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="generate .feature + step defs for a module")
    g.add_argument("--module", "-m", required=True, help="module short name (e.g. OBR)")
    g.add_argument(
        "--spec-root",
        required=True,
        help="path to the spec markdown file or directory containing EARS specs",
    )
    g.add_argument(
        "--output-root",
        required=True,
        help="path to the service root where src/test/{resources,java}/... will be written",
    )
    g.add_argument(
        "--package",
        default=None,
        help="Java package base for step defs (default: com.example.<module-lower>)",
    )
    g.add_argument(
        "--emit-spring-context",
        action="store_true",
        help="also emit CucumberSpringContext.java + application-bdd.properties",
    )
    g.set_defaults(func=_cmd_generate)

    bp = sub.add_parser(
        "emit-build-patch",
        help="print a build.gradle.kts dependency patch (Cucumber 7.x)",
    )
    bp.add_argument(
        "--cucumber-version",
        default="7.18.0",
        help="Cucumber version pin (default 7.18.0, matches be-module-generator.py)",
    )
    bp.set_defaults(func=_cmd_emit_build_patch)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
