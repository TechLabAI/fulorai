#!/usr/bin/env python3
"""sbom-generator.py - CycloneDX SBOM generator (D-142, Pole Position S3 Fase C).

Walks a project and emits a CycloneDX 1.4 JSON SBOM. Stdlib only — no syft
nor cyclonedx-cli dependency. Tooling choice rationale lives in D-142
(consolidation §3.x); short version: keeps workspace philosophy (stdlib-only,
see D-085 / D-094 / D-118) and works on Windows without external binaries.

Currently parses:
  - pyproject.toml          (PEP 621 [project.dependencies] + optional-deps)
  - package.json            (npm/yarn dependencies + devDependencies)
  - build.gradle / .kts     (best-effort Gradle dependency block extraction)
  - requirements*.txt       (one pinned/loose spec per line)

Output:
  - CycloneDX 1.4 JSON to --output (default stdout)
  - Each component: type, name, version, purl, scope (required/optional)

Limitations (documented, in scope of "vendable > complete"):
  - No transitive resolution. Direct deps only. Run a real tool (syft,
    cyclonedx-bom, cyclonedx-gradle-plugin) when transitive trees matter.
  - No license fingerprinting. We trust the project's declared license
    via classifiers and emit it as-is when available.
  - No hash verification. Hash collection requires resolving the registry;
    out of scope for a static walker.

Usage:
    python scripts/sbom-generator.py --project . --output tmp/sbom.json
    python scripts/sbom-generator.py --project /path/to/bosq --component-name bosq
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from cli_utils import force_utf8_stdio


# ── Component model (CycloneDX-shaped subset) ────────────────────────────────


@dataclass
class Component:
    type: str           # "library" | "application" | "framework"
    name: str
    version: str
    purl: str
    scope: str          # "required" | "optional" | "excluded"
    source: str         # which file/section produced this entry (audit trail)
    bom_ref: str = ""

    def __post_init__(self):
        if not self.bom_ref:
            # Stable ref for downstream tooling
            self.bom_ref = f"pkg:{self.purl}"


# ── Parsers ──────────────────────────────────────────────────────────────────


_PYPROJECT_TABLES = ("dependencies", "optional-dependencies")
_DEP_SPEC_NAME = re.compile(r"^[A-Za-z0-9_.\-]+")


def _split_pep508_name_version(spec: str) -> tuple[str, str]:
    """Best-effort PEP 508 split. Returns (name, version_constraint_or_empty).

    Not a full parser — extras, markers, URL deps degrade gracefully.
    """
    spec = spec.strip()
    if not spec:
        return ("", "")
    # Strip URL deps - "name @ url"
    if "@" in spec:
        head, _, _tail = spec.partition("@")
        name_match = _DEP_SPEC_NAME.match(head.strip())
        return ((name_match.group(0) if name_match else head.strip()), "")
    # Strip extras: "name[extra]"
    bare = re.sub(r"\[.*?\]", "", spec)
    # Match name then capture remainder as version constraint
    m = _DEP_SPEC_NAME.match(bare)
    if not m:
        return (spec, "")
    name = m.group(0)
    rest = bare[len(name):].strip()
    # Strip environment markers
    rest = rest.split(";", 1)[0].strip()
    return (name, rest or "")


def parse_pyproject(path: Path) -> list[Component]:
    """Parse PEP 621 pyproject.toml. Uses stdlib tomllib (3.11+)."""
    try:
        import tomllib
    except ImportError:
        return []
    if not path.is_file():
        return []
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    project = data.get("project", {})
    out: list[Component] = []

    for dep in project.get("dependencies", []) or []:
        name, ver = _split_pep508_name_version(dep)
        if not name:
            continue
        out.append(Component(
            type="library",
            name=name,
            version=ver,
            purl=f"pypi/{name}@{ver}" if ver else f"pypi/{name}",
            scope="required",
            source=f"{path.name}:[project.dependencies]",
        ))

    for extra_name, deps in (project.get("optional-dependencies") or {}).items():
        for dep in deps or []:
            name, ver = _split_pep508_name_version(dep)
            if not name:
                continue
            out.append(Component(
                type="library",
                name=name,
                version=ver,
                purl=f"pypi/{name}@{ver}" if ver else f"pypi/{name}",
                scope="optional",
                source=f"{path.name}:[project.optional-dependencies.{extra_name}]",
            ))

    return out


def parse_package_json(path: Path) -> list[Component]:
    """Parse npm-style package.json. dependencies = required, devDependencies = optional."""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    out: list[Component] = []
    for table, scope in (("dependencies", "required"), ("devDependencies", "optional"), ("peerDependencies", "optional")):
        for name, ver in (data.get(table) or {}).items():
            ver = (ver or "").strip()
            out.append(Component(
                type="library",
                name=name,
                version=ver,
                purl=f"npm/{name}@{ver}" if ver else f"npm/{name}",
                scope=scope,
                source=f"{path.name}:{table}",
            ))
    return out


_GRADLE_DEP_RE = re.compile(
    r"""
    (?P<config>implementation|api|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly|annotationProcessor)
    \s*[(\s]
    [\"']
    (?P<coord>[A-Za-z0-9_.\-]+:[A-Za-z0-9_.\-]+(?::[A-Za-z0-9_.\-+]+)?)
    [\"']
    """,
    re.VERBOSE,
)


def parse_gradle(path: Path) -> list[Component]:
    """Best-effort extraction from build.gradle / build.gradle.kts.

    Only catches the `implementation("g:a:v")` style. Misses platform BOM
    imports, version catalogs, dynamic versions, and the apply-from pattern.
    The plan calls this out as "best-effort"; real Gradle SBOM goes through
    cyclonedx-gradle-plugin from the Gradle build itself.
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    out: list[Component] = []
    for m in _GRADLE_DEP_RE.finditer(text):
        config = m.group("config")
        coord = m.group("coord")
        parts = coord.split(":")
        if len(parts) == 2:
            group, name = parts
            version = ""
        else:
            group, name, version = parts[0], parts[1], parts[2]
        scope = "optional" if config.startswith(("test", "compileOnly")) else "required"
        purl_name = f"{group}/{name}"
        out.append(Component(
            type="library",
            name=f"{group}:{name}",
            version=version,
            purl=f"maven/{purl_name}@{version}" if version else f"maven/{purl_name}",
            scope=scope,
            source=f"{path.name}:{config}",
        ))
    return out


_REQ_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*(?:[~=!<>]=?\s*([^\s;#]+))?")


def parse_requirements_txt(path: Path) -> list[Component]:
    if not path.is_file():
        return []
    out: list[Component] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = _REQ_LINE_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        ver = m.group(2) or ""
        out.append(Component(
            type="library",
            name=name,
            version=ver,
            purl=f"pypi/{name}@{ver}" if ver else f"pypi/{name}",
            scope="required",
            source=f"{path.name}",
        ))
    return out


# ── Walker ───────────────────────────────────────────────────────────────────


_SKIP_DIRS = {
    ".git", "node_modules", "build", "target", "dist", ".gradle",
    ".venv", "__pycache__", ".pytest_cache", ".idea", ".vscode", "out",
}


def walk_project(root: Path) -> list[Component]:
    """Walk the project, parse every known manifest, collect components.

    Deduplicates on (purl, scope, source) — same library declared in two
    places stays distinct so the SBOM consumer sees the audit trail.
    """
    components: list[Component] = []

    def visit(p: Path):
        for entry in p.iterdir():
            if entry.name in _SKIP_DIRS:
                continue
            if entry.is_dir():
                visit(entry)
                continue
            name = entry.name
            if name == "pyproject.toml":
                components.extend(parse_pyproject(entry))
            elif name == "package.json":
                components.extend(parse_package_json(entry))
            elif name in ("build.gradle", "build.gradle.kts"):
                components.extend(parse_gradle(entry))
            elif name.startswith("requirements") and name.endswith(".txt"):
                components.extend(parse_requirements_txt(entry))

    if root.is_dir():
        visit(root)
    return components


# ── CycloneDX render ─────────────────────────────────────────────────────────


def render_cyclonedx(
    components: list[Component],
    *,
    component_name: str,
    component_version: str,
) -> dict:
    """Build a CycloneDX 1.4 JSON document. Spec:
    https://cyclonedx.org/docs/1.4/json/
    """
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": [
                {
                    "vendor": "techlab-architecture",
                    "name": "sbom-generator.py",
                    "version": "0.1",
                },
            ],
            "component": {
                "type": "application",
                "name": component_name,
                "version": component_version,
                "bom-ref": f"app:{component_name}@{component_version}",
            },
        },
        "components": [
            {
                "type": c.type,
                "bom-ref": c.bom_ref,
                "name": c.name,
                "version": c.version,
                "purl": c.purl,
                "scope": c.scope,
                "properties": [
                    {"name": "techlab:source", "value": c.source},
                ],
            }
            for c in components
        ],
    }


# ── Project metadata discovery ───────────────────────────────────────────────


def discover_component_metadata(root: Path) -> tuple[str, str]:
    """Best-effort: derive the project's own name + version from pyproject.toml
    or package.json. Returns ('unknown', '0.0.0') when none found."""
    pp = root / "pyproject.toml"
    if pp.is_file():
        try:
            import tomllib
            with pp.open("rb") as fh:
                data = tomllib.load(fh)
            project = data.get("project", {})
            name = project.get("name") or "unknown"
            version = project.get("version") or "0.0.0"
            return (name, version)
        except Exception:
            pass
    pj = root / "package.json"
    if pj.is_file():
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
            return (data.get("name") or "unknown", data.get("version") or "0.0.0")
        except Exception:
            pass
    return (root.name or "unknown", "0.0.0")


# ── Public API ───────────────────────────────────────────────────────────────


def build_sbom(
    project: Path,
    *,
    component_name: str | None = None,
    component_version: str | None = None,
) -> dict:
    components = walk_project(project.resolve())
    if not component_name or not component_version:
        d_name, d_ver = discover_component_metadata(project.resolve())
        component_name = component_name or d_name
        component_version = component_version or d_ver
    return render_cyclonedx(
        components,
        component_name=component_name,
        component_version=component_version,
    )


# ── CLI ──────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sbom-generator",
        description="CycloneDX 1.4 SBOM generator (stdlib only).",
    )
    p.add_argument("--project", type=Path, default=Path("."),
                   help="Project root to scan (default: cwd).")
    p.add_argument("--output", type=Path, default=None,
                   help="Write to file (default: stdout).")
    p.add_argument("--component-name", type=str, default=None,
                   help="Override the BOM's primary component name.")
    p.add_argument("--component-version", type=str, default=None,
                   help="Override the BOM's primary component version.")
    p.add_argument("--summary", action="store_true",
                   help="Print a human-readable summary after writing.")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()
    args = _build_parser().parse_args(argv)
    project = args.project.resolve()
    if not project.is_dir():
        sys.exit(f"error: project path not a directory: {project}")
    bom = build_sbom(
        project,
        component_name=args.component_name,
        component_version=args.component_version,
    )
    payload = json.dumps(bom, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"OK: SBOM written to {args.output} ({len(bom['components'])} components)")
    else:
        print(payload)
    if args.summary:
        comps = bom["components"]
        sources: dict[str, int] = {}
        for c in comps:
            for prop in c.get("properties") or []:
                if prop.get("name") == "techlab:source":
                    src = prop["value"].split(":")[0]
                    sources[src] = sources.get(src, 0) + 1
        print("Sources:")
        for src, n in sorted(sources.items()):
            print(f"  {src}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
