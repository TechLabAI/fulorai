#!/usr/bin/env python3
"""
be-bdd-generator.py — Gera infraestrutura de testes BDD (Cucumber) para um backend service.

Le os arquivos .feature do diretorio de spec do servico e:
  1. Copia os .feature para src/test/resources/features/<service>/
  2. Gera CucumberIT.java (runner de integracao Cucumber)
  3. Gera stubs de step definitions Java por feature file

Uso:
    python scripts/be-bdd-generator.py <SERVICE_NAME>
    python scripts/be-bdd-generator.py authorization-policy-service

    python scripts/be-bdd-generator.py --issue <ISSUE_ID>
    python scripts/be-bdd-generator.py --issue APS-011

Economia: elimina ~5.000-8.000 tokens de LLM por servico (stubs de steps).
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = ROOT / "docs" / "architecture" / "backend" / "services"
SERVICES_DIR = ROOT / "backend" / "services"
PLANS_DIR = ROOT / "docs" / "architecture" / "backend" / "plans"

# Project context (loaded once at module import)
try:
    from be_context_helper import load_project_context
    _CTX = load_project_context()
except (ImportError, Exception):
    _CTX = None


def _build_service_catalog() -> dict[str, str]:
    """Build SERVICE_CATALOG dynamically from project-context.json modules.

    Returns: dict mapping service_name → full Java package
      e.g. {"obras-service": "com.bosq.obr", "perdas-service": "com.bosq.prd", ...}
    """
    if not _CTX or not _CTX.modules:
        return {}
    pkg_base = _CTX.package_base
    catalog = {}
    for mod in _CTX.modules:
        prefix = mod.get("prefix", "")
        svc_name = mod.get("backendService") or f"{prefix.lower()}-service"
        catalog[svc_name] = f"{pkg_base}.{prefix.lower()}"
    return catalog


def _build_issue_prefix_to_service() -> dict[str, str]:
    """Map module prefix (e.g. 'OBR') to service name (e.g. 'obras-service').

    Built from project-context.json modules registry.
    """
    if not _CTX or not _CTX.modules:
        return {}
    result = {}
    for mod in _CTX.modules:
        prefix = mod.get("prefix", "")
        svc_name = mod.get("backendService") or f"{prefix.lower()}-service"
        if prefix:
            result[prefix] = svc_name
            # Also accept INT-<MOD> (integration) issues
            result[f"INT-{prefix}"] = svc_name
    # INFRA falls back to gateway
    if "GWY" in result:
        result["INFRA"] = result["GWY"]
    return result


SERVICE_CATALOG = _build_service_catalog()
ISSUE_PREFIX_TO_SERVICE = _build_issue_prefix_to_service()


def service_from_issue(issue_id: str) -> str | None:
    prefix = issue_id.split("-")[0].upper()
    return ISSUE_PREFIX_TO_SERVICE.get(prefix)


def service_from_plan(issue_id: str) -> str | None:
    plan_path = PLANS_DIR / f"plan-{issue_id}.md"
    if not plan_path.exists():
        return None
    text = plan_path.read_text(encoding="utf-8")
    m = re.search(r"\|\s*[Ss]ervi[çc]o\s*\|\s*([^\|]+)\|", text)
    if m:
        return m.group(1).strip()
    return None


# ── Feature file parsing ───────────────────────────────────────────────────────


def parse_feature_steps(feature_text: str) -> list:
    """Extract unique step text lines from a .feature file (Given/When/Then/And/But)."""
    steps = []
    seen = set()
    for line in feature_text.splitlines():
        s = line.strip()
        m = re.match(r"^(Given|When|Then|And|But)\s+(.+)$", s)
        if m:
            keyword, step_text = m.group(1), m.group(2)
            norm = (keyword, step_text)
            if norm not in seen:
                seen.add(norm)
                steps.append(norm)
    return steps


def feature_class_name(feature_file: Path) -> str:
    """Convert access-evaluation.feature -> AccessEvaluationSteps."""
    stem = feature_file.stem  # e.g. access-evaluation
    parts = stem.replace("-", "_").replace(" ", "_").split("_")
    return "".join(p.capitalize() for p in parts) + "Steps"


def step_method_name(keyword: str, text: str) -> str:
    """Turn a step text into a Java method name."""
    clean = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    words = clean.split()[:8]  # limit length
    return keyword.lower() + "".join(w.capitalize() for w in words)


def generate_step_definitions(feature_file: Path, package: str) -> str:
    """Generate a Java step definitions class for a .feature file."""
    feature_text = feature_file.read_text(encoding="utf-8")
    steps = parse_feature_steps(feature_text)
    class_name = feature_class_name(feature_file)

    # Derive the feature title
    title_match = re.search(r"^Feature:\s*(.+)$", feature_text, re.MULTILINE)
    feature_title = title_match.group(1).strip() if title_match else feature_file.stem

    method_lines = []
    used_names: dict[str, int] = {}
    for keyword, text in steps:
        annotation = {
            "Given": "@Given",
            "When": "@When",
            "Then": "@Then",
            "And": "@And",
            "But": "@But",
        }.get(keyword, "@And")
        base_name = step_method_name(keyword, text)
        # Deduplica: se nome ja foi usado, sufixa com _2, _3, ...
        # (acontece quando 2 steps diferentes truncados a 8 palavras dao mesmo nome).
        if base_name in used_names:
            used_names[base_name] += 1
            method_name = f"{base_name}_{used_names[base_name]}"
        else:
            used_names[base_name] = 1
            method_name = base_name
        # Use raw text in Cucumber Expression (no regex escaping needed)
        # Escape only Java string special chars: backslash and double-quote
        java_safe_text = text.replace("\\", "\\\\").replace('"', '\\"')
        method_lines.append(f'    {annotation}("{java_safe_text}")')
        method_lines.append(f"    public void {method_name}() {{")
        method_lines.append(f"        // TODO: implement step")
        method_lines.append(f"        throw new io.cucumber.java.PendingException();")
        method_lines.append(f"    }}")
        method_lines.append("")

    methods = "\n".join(method_lines)

    return f"""\
package {package}.bdd.steps;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.And;
import io.cucumber.java.en.But;

/**
 * Step definitions — {feature_title}.
 * Feature: {feature_file.name}
 *
 * Generated by be-bdd-generator.py — implement each step.
 */
public class {class_name} {{

{methods}
}}
"""


def generate_cucumber_runner(package: str, service: str) -> str:
    """Generate a CucumberIT.java runner."""
    return f"""\
package {package}.bdd;

import io.cucumber.junit.platform.engine.Constants;
import org.junit.platform.suite.api.*;

/**
 * Cucumber integration test runner — {service}.
 *
 * Runs all .feature files in src/test/resources/features/.
 * Requires a running Spring context (Testcontainers via BaseIntegrationTest).
 */
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(
    key = Constants.GLUE_PROPERTY_NAME,
    value = "{package}.bdd"
)
@ConfigurationParameter(
    key = Constants.PLUGIN_PROPERTY_NAME,
    value = "pretty, html:build/reports/cucumber/cucumber-report.html"
)
public class CucumberIT {{}}
"""


def generate_cucumber_context(package: str) -> str:
    """Generate CucumberSpringContext.java to bootstrap Spring in BDD tests."""
    return f"""\
package {package}.bdd;

import io.cucumber.spring.CucumberContextConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/**
 * Bootstraps the Spring context for Cucumber step definitions.
 */
@CucumberContextConfiguration
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
public class CucumberSpringContext {{}}
"""


# ── Main ───────────────────────────────────────────────────────────────────────


def run(service: str, force: bool = False,
        spec_dir_override: str = None, package_override: str = None) -> None:
    if package_override:
        package = package_override
    else:
        package = SERVICE_CATALOG.get(service)
        if not package:
            print(f"[!] Unknown service: {service}")
            print(f"    Known services: {', '.join(SERVICE_CATALOG)}")
            print(f"    For tool services use --package <full.package.name>")
            sys.exit(1)

    # Spec features dir
    if spec_dir_override:
        spec_features = Path(spec_dir_override) / "tests" / "cucumber"
    else:
        spec_features = SPECS_DIR / f"{service}-spec" / "tests" / "cucumber"
    if not spec_features.exists():
        print(f"[!] No BDD features found at: {spec_features}")
        sys.exit(1)

    feature_files = list(spec_features.glob("*.feature"))
    if not feature_files:
        print(f"[!] No .feature files in: {spec_features}")
        sys.exit(1)

    service_root = SERVICES_DIR / service
    if not service_root.exists():
        print(f"[!] Service directory not found: {service_root}")
        print(f"    Run scaffold for *-001 issue first.")
        sys.exit(1)

    pkg_path = package.replace(".", "/")

    # Target directories
    features_dest = service_root / "src" / "test" / "resources" / "features"
    steps_dest = service_root / "src" / "test" / "java" / pkg_path / "bdd" / "steps"
    runner_dest = service_root / "src" / "test" / "java" / pkg_path / "bdd"

    features_dest.mkdir(parents=True, exist_ok=True)
    steps_dest.mkdir(parents=True, exist_ok=True)
    runner_dest.mkdir(parents=True, exist_ok=True)

    print(f"[+] BDD generator — {service}")
    print(f"    Package:  {package}")
    print(f"    Features: {len(feature_files)} found in spec")
    print()

    # 1. Copy feature files
    print("[+] Copying .feature files:")
    for feat in feature_files:
        dest = features_dest / feat.name
        if dest.exists() and not force:
            print(f"    [>] {feat.name} (already exists)")
        else:
            shutil.copy2(feat, dest)
            print(f"    [+] features/{feat.name}")

    print()

    # 2. Generate step definition stubs
    print("[+] Generating step definition stubs:")
    for feat in feature_files:
        class_name = feature_class_name(feat)
        dest = steps_dest / f"{class_name}.java"
        if dest.exists() and not force:
            print(f"    [>] steps/{class_name}.java (already exists)")
        else:
            content = generate_step_definitions(feat, package)
            dest.write_text(content, encoding="utf-8")
            print(f"    [+] steps/{class_name}.java")

    print()

    # 3. Generate CucumberIT runner
    runner_file = runner_dest / "CucumberIT.java"
    if runner_file.exists() and not force:
        print(f"    [>] CucumberIT.java (already exists)")
    else:
        runner_file.write_text(generate_cucumber_runner(package, service), encoding="utf-8")
        print(f"    [+] CucumberIT.java")

    # 4. Generate CucumberSpringContext
    context_file = runner_dest / "CucumberSpringContext.java"
    if context_file.exists() and not force:
        print(f"    [>] CucumberSpringContext.java (already exists)")
    else:
        context_file.write_text(generate_cucumber_context(package), encoding="utf-8")
        print(f"    [+] CucumberSpringContext.java")

    print()
    print(f"[+] BDD setup completo para {service}")
    print()
    print("    Proximos passos:")
    print(f"    1. Implementar os steps em: src/test/java/{pkg_path}/bdd/steps/")
    print(f"    2. Rodar: ./gradlew :{service}:integrationTest")
    print(f"    3. Relatorio: build/reports/cucumber/cucumber-report.html")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="be-bdd-generator.py",
        description="Gera infraestrutura de testes BDD (Cucumber) para um backend service.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/be-bdd-generator.py authorization-policy-service\n"
            "  python scripts/be-bdd-generator.py --issue APS-011\n"
            "  python scripts/be-bdd-generator.py <service> "
            "--spec-dir <path> --package <pkg>\n"
        ),
    )
    parser.add_argument(
        "service",
        nargs="?",
        help="Service name (e.g. authorization-policy-service). "
             "Mutually exclusive with --issue.",
    )
    parser.add_argument(
        "--issue",
        metavar="ISSUE_ID",
        help="Resolve the service from a plan/issue prefix instead of "
             "passing the service name directly.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .feature copies, step stubs, and runners.",
    )
    parser.add_argument(
        "--spec-dir",
        metavar="PATH",
        help="Override the default SPECS_DIR/<service>-spec lookup "
             "(useful for tool services living outside docs/architecture).",
    )
    parser.add_argument(
        "--package",
        metavar="PKG",
        help="Override the SERVICE_CATALOG Java package lookup.",
    )
    return parser


def main():
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()

    parser = _build_parser()
    args = parser.parse_args()

    # D-088: enforce mutual exclusivity post-parse. argparse's
    # mutually_exclusive_group + nargs="?" interacts awkwardly with
    # boolean intent (a missing positional and a missing --issue both
    # look like "not provided"), so a manual check is clearer.
    if bool(args.service) == bool(args.issue):
        parser.error(
            "provide exactly one of: <service> positional OR --issue <ISSUE_ID>"
        )

    if args.issue:
        service = service_from_plan(args.issue) or service_from_issue(args.issue)
        if not service:
            print(f"[!] Could not resolve service for issue: {args.issue}")
            sys.exit(1)
        print(f"[+] Resolved service from {args.issue}: {service}")
    else:
        service = args.service

    run(
        service,
        force=args.force,
        spec_dir_override=args.spec_dir,
        package_override=args.package,
    )


if __name__ == "__main__":
    main()

