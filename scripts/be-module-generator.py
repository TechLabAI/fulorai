#!/usr/bin/env python3
"""
be-module-generator.py — Generic Spring Boot module scaffolder driven by project documentation.

Document-driven: aponta para o diretório de documentação da tool e deriva
toda a configuração a partir da estrutura de documentos (sempre a mesma).

Estrutura de docs esperada:
  docs/architecture/tools/<tool-name>/
  ├── setup-local.md                     ← porta HTTP, config de banco
  ├── <service-name>/
  │   ├── <service-name>-spec.md         ← frontmatter: service, bounded_context, project
  │   ├── contracts/
  │   │   ├── data-model.md              ← tabelas SQL → migration
  │   │   ├── api-contract.md            ← endpoints REST → controllers
  │   │   ├── event-contracts.md         ← eventos → producers/consumers
  │   │   └── hub-integration.md         ← FeignClients, Vertex AI, GCS
  │   └── tests/cucumber/*.feature       ← BDD features → step stubs
  ├── issues/XXX-NNN.md                  ← prefixo de issue (ex: RFM)
  └── adr/

Uso:
    python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec
    python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec --dry-run
    python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec --no-spec
    python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec --port 8090
    python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec --force

Chaining automático:
  --no-spec  → apenas scaffold base (sem migration, entidades, BDD)
  padrão     → scaffold + DDL + entidades + BDD (apenas para service_type=standard)

Service types suportados (campo `type` em generator-config.yml):
  standard  (padrão) → microserviço de domínio com JPA + Artemis + Feign + hexagonal completa
  gateway            → Spring Cloud Gateway reativo (WebFlux) — sem JPA/Artemis/Feign
  registry           → Eureka Server — stack mínima, sem Security/JPA

CLAUDE.md compliance:
  ✓ springCloudVersion = "2025.0.1"
  ✓ sem testcontainers:activemq → Artemis embedded nos testes
  ✓ BaseIntegrationTest sem @Container → singleton container pattern
"""

import argparse
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Project context (loaded once at module import; falls back to defaults if not found)
try:
    from be_context_helper import load_project_context
    _CTX = load_project_context()
except (ImportError, Exception):
    _CTX = None

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "backend" / "services"
PKG_BASE = _CTX.package_base if _CTX else "com.project"
PROJECT_NAME = _CTX.project_name if _CTX else "project"
PROJECT_DISPLAY = _CTX.project_display_name if _CTX else "Project"
KEYCLOAK_REALM = PROJECT_NAME  # used in issuer-uri default

# ── Hexagonal packages ────────────────────────────────────────────────────────

HEXAGONAL_PACKAGES = [
    "domain/model",
    "domain/service",
    "application/service",
    "application/port/in",
    "application/port/out",
    "api/controller",
    "api/dto",
    "api/exception",
    "infrastructure/clients",
    "infrastructure/config",
    "infrastructure/messaging/producer",
    "infrastructure/messaging/consumer",
    "infrastructure/persistence/entity",
    "infrastructure/persistence/repository",
    "infrastructure/persistence/adapter",
    "infrastructure/security",
]


# ── Metadata ──────────────────────────────────────────────────────────────────

@dataclass
class ToolMeta:
    service: str             # "reforma-map-service"
    package_suffix: str      # "reformamap"
    app_class: str           # "ReformaMapApplication"
    port: int                # 8090
    description: str
    docs_dir: Path           # docs/architecture/backend/services/rtc-service-spec (absolute)
    service_docs_dir: Path   # .../reforma-map/reforma-map-service (absolute)
    has_vertex_ai: bool
    has_gcs: bool
    issue_prefix: str        # "RFM"
    service_type: str = "standard"   # "standard" | "gateway" | "registry"
    extra_dependencies: list[str] = field(default_factory=list)
    profiles: list[dict] = field(default_factory=list)
    domain_aggregates: list[str] = field(default_factory=list)
    domain_entities: list[str] = field(default_factory=list)
    application_services: list[dict] = field(default_factory=list)  # [{name, operations}]
    enums: dict[str, list[str]] = field(default_factory=dict)
    published_events: list[str] = field(default_factory=list)
    feign_clients: list[dict] = field(default_factory=list)   # [{name, service, url_prop}]
    consumed_events: list[dict] = field(default_factory=list) # [{event, destination, consumer_class}]
    outbound_ports: list[str] = field(default_factory=list)   # ["TranscriptionSourcePort", ...]


# ── Discovery ─────────────────────────────────────────────────────────────────

_INFRA_SERVICES = (
    {_CTX.gateway_service, _CTX.registry_service, _CTX.migrations_service}
    if _CTX
    else {"project-api-gateway", "project-service-registry", "project-migrations"}
)


def discover_service_dir(docs_dir: Path) -> Path:
    """Resolve o diretório de specs do serviço.

    Padrão flat: docs_dir é o próprio serviço — termina em '-service'
      ou é um dos serviços de infra (api-gateway, service-registry, migrations).
    Padrão legacy (wrapper): docs_dir contém um subdir *-service.
    """
    if docs_dir.name.endswith("-service") or docs_dir.name in _INFRA_SERVICES:
        return docs_dir

    candidates = [d for d in docs_dir.iterdir() if d.is_dir() and d.name.endswith("-service")]
    if not candidates:
        raise ValueError(f"Nenhum diretório *-service encontrado em: {docs_dir}")
    if len(candidates) > 1:
        names = [c.name for c in candidates]
        raise ValueError(f"Múltiplos *-service encontrados: {names}. Use --service para especificar.")
    return candidates[0]


def parse_frontmatter(spec_file: Path) -> dict:
    """Extrai campos YAML-like do cabeçalho do spec (linhas key: value antes do primeiro ---)."""
    result = {}
    for line in spec_file.read_text(encoding="utf-8").splitlines():
        if line.strip() == "---":
            break
        m = re.match(r"^([\w_-]+):\s*(.+)$", line.strip())
        if m:
            result[m.group(1)] = m.group(2).strip()
    return result


_INFRA_PORTS = {
    5432, 5433,           # PostgreSQL
    61616,                # Artemis broker
    8161, 8162,           # Artemis web console
    8761,                 # Eureka (service-registry)
    8180,                 # Keycloak
    4317, 4318,           # OTel collector (gRPC, HTTP)
    9090, 9091,           # Prometheus
    3000,                 # Grafana
    8080,                 # api-gateway (porta de gateway, nao de microservico)
}

_PORT_HINTS = [
    # "responde em", "responder em", "respondem em" (qualquer conjugacao)
    re.compile(r"respond\w*\s+em\s+`?http://localhost:(\d{4,5})", re.IGNORECASE),
    re.compile(r"dispon[ií]vel\s+em\s+`?http://localhost:(\d{4,5})", re.IGNORECASE),
    re.compile(r"servi[cç]o\s+fica\s+em\s+`?http://localhost:(\d{4,5})", re.IGNORECASE),
    # "localhost:N/actuator/health" — convencao Spring Boot
    re.compile(r"localhost:(\d{4,5})/actuator/health", re.IGNORECASE),
]


def parse_port(setup_local: Path) -> int:
    """Extrai porta HTTP de setup-local.md.

    Estratégia em camadas:
      1. Padrões explícitos: "responde em http://localhost:N", "disponível em..."
      2. Primeira porta http://localhost:N/ que NÃO esteja em _INFRA_PORTS
      3. Fallback 8090

    O override via `generator-config.yml` (campo `port:`) tem precedência sobre tudo isso.
    """
    if not setup_local.exists():
        return 8090
    text = setup_local.read_text(encoding="utf-8")

    # Camada 1: padrões explícitos de "esta é a porta do serviço"
    for pattern in _PORT_HINTS:
        m = pattern.search(text)
        if m:
            candidate = int(m.group(1))
            if candidate not in _INFRA_PORTS:
                return candidate

    # Camada 2: primeira porta não-infra em qualquer URL localhost
    for m in re.finditer(r"localhost:(\d{4,5})", text):
        candidate = int(m.group(1))
        if candidate not in _INFRA_PORTS:
            return candidate

    return 8090


def parse_description(spec_file: Path) -> str:
    """Extrai primeira sentença da seção 1 do spec."""
    text = spec_file.read_text(encoding="utf-8")
    m = re.search(r"^#+\s*1\..+\n+((?:.+\n?)+)", text, re.MULTILINE)
    if m:
        para = m.group(1).strip().split("\n")[0]
        sentence = para.split(".")[0].strip()
        return sentence[:200]
    return f"Serviço de domínio {PROJECT_DISPLAY} tool."


def detect_external_deps(hub_integration_file: Path) -> tuple[bool, bool]:
    """Detecta uso de Vertex AI e/ou GCS a partir dos arquivos de contracts."""
    contracts_dir = hub_integration_file.parent
    texts = []
    for fname in ("hub-integration.md", "integration-contracts.md"):
        f = contracts_dir / fname
        if f.exists():
            texts.append(f.read_text(encoding="utf-8"))
    combined = "\n".join(texts)
    if not combined:
        return False, False
    has_vertex = bool(re.search(r"[Vv]ertex\s*AI|VertexAI|vertex[-_]ai|google-cloud-aiplatform", combined))
    has_gcs = bool(re.search(r"\bGCS\b|Google Cloud Storage|google-cloud-storage", combined, re.IGNORECASE))
    return has_vertex, has_gcs


def parse_issue_prefix(docs_dir: Path) -> str:
    """Detecta prefixo de issue a partir de issues/*.md.

    Procura nesta ordem:
      1. <docs_dir>/issues/             (layout legacy wrapper — ex: RFM-001.md → RFM)
      2. <ROOT>/docs/architecture/backend/issues/  (layout flat — ex: CAD-001.md → CAD)
    """
    issues_dir = docs_dir / "issues"
    if issues_dir.exists():
        for f in sorted(issues_dir.glob("*.md")):
            m = re.match(r"^([A-Z]{2,5})-\d+\.md$", f.name)
            if m:
                return m.group(1)

    global_issues = ROOT / "docs" / "architecture" / "backend" / "issues"
    if global_issues.exists():
        for f in sorted(global_issues.glob("*.md")):
            m = re.match(r"^([A-Z]{2,5})-\d+\.md$", f.name)
            if m:
                return m.group(1)

    return "TOOL"


def parse_generator_config(service_docs_dir: Path) -> dict:
    """Lê generator-config.yml se existir; retorna dict vazio se não existir."""
    config_file = service_docs_dir / "generator-config.yml"
    if not config_file.exists():
        return {}

    lines = config_file.read_text(encoding="utf-8").splitlines()
    result: dict = {
        "extra_dependencies": [],
        "profiles": [],
        "domain_aggregates": [],
        "domain_entities": [],
        "application_services": [],
        "enums": {},
        "published_events": [],
        "feign_clients": [],
        "consumed_events": [],
        "outbound_ports": [],
    }

    # State machine to track which section we're in
    section = None          # top-level key being parsed
    subsection = None       # e.g. "aggregates", "entities" under "domain"
    enum_name = None        # current enum being parsed
    current_svc: dict = {}  # current application_service entry being built
    current_feign: dict = {}
    current_consumed: dict = {}
    in_operations = False   # whether we're inside an operations list
    in_events_published = False

    for line in lines:
        stripped = line.strip()

        # Skip comments and blank lines
        if not stripped or stripped.startswith("#"):
            continue

        # Detect indentation depth
        indent = len(line) - len(line.lstrip())

        # Top-level keys (indent == 0)
        if indent == 0:
            section = None
            subsection = None
            enum_name = None
            in_operations = False
            in_events_published = False
            if current_svc:
                result["application_services"].append(current_svc)
                current_svc = {}
            if current_feign:
                result["feign_clients"].append(current_feign)
                current_feign = {}
            if current_consumed:
                result["consumed_events"].append(current_consumed)
                current_consumed = {}

            # Top-level scalars: service, port, db_name, db_user (key: value form)
            m_scalar = re.match(r"^([\w_-]+):\s+(.+)$", stripped)
            if m_scalar:
                key, val = m_scalar.group(1), m_scalar.group(2).strip().strip('"').strip("'")
                if key in ("service", "db_name", "db_user", "issue_prefix", "bounded_context"):
                    result[key] = val
                    continue
                if key == "type":
                    if val in ("standard", "gateway", "registry"):
                        result["service_type"] = val
                    continue
                if key == "port":
                    try:
                        result["port"] = int(val)
                    except ValueError:
                        pass
                    continue

            if stripped == "extra_dependencies:":
                section = "extra_dependencies"
            elif stripped == "profiles:":
                section = "profiles"
            elif stripped == "domain:":
                section = "domain"
            elif stripped == "application_services:":
                section = "application_services"
            elif stripped == "enums:":
                section = "enums"
            elif stripped == "events:":
                section = "events"
            elif stripped == "feign_clients:":
                section = "feign_clients"
            elif stripped == "consumed_events:":
                section = "consumed_events"
            elif stripped == "outbound_ports:":
                section = "outbound_ports"
            continue

        # Depth-2 items (indent == 2)
        if indent == 2:
            in_operations = False
            in_events_published = False

            if section == "extra_dependencies":
                m = re.match(r"^-\s+(.+)$", stripped)
                if m:
                    result["extra_dependencies"].append(m.group(1).strip('"').strip("'"))

            elif section == "outbound_ports":
                m = re.match(r"^-\s+(.+)$", stripped)
                if m:
                    result["outbound_ports"].append(m.group(1).strip('"').strip("'"))

            elif section == "profiles":
                m_name = re.match(r"^-\s+name:\s+(.+)$", stripped)
                m_role = re.match(r"^-?\s*role:\s+(.+)$", stripped)
                m_desc = re.match(r"^-?\s*description:\s+(.+)$", stripped)
                if m_name:
                    result["profiles"].append({"name": m_name.group(1), "role": "", "description": ""})
                elif m_role and result["profiles"]:
                    result["profiles"][-1]["role"] = m_role.group(1)
                elif m_desc and result["profiles"]:
                    result["profiles"][-1]["description"] = m_desc.group(1)

            elif section == "domain":
                if stripped == "aggregates:":
                    subsection = "aggregates"
                elif stripped == "entities:":
                    subsection = "entities"

            elif section == "application_services":
                m_name = re.match(r"^-\s+name:\s+(.+)$", stripped)
                if m_name:
                    if current_svc:
                        result["application_services"].append(current_svc)
                    current_svc = {"name": m_name.group(1), "operations": []}
                elif stripped == "operations:" and current_svc:
                    in_operations = True

            elif section == "enums":
                m_key = re.match(r"^(\w+):$", stripped)
                if m_key:
                    enum_name = m_key.group(1)
                    result["enums"][enum_name] = []

            elif section == "events":
                if stripped == "published:":
                    in_events_published = True

            elif section == "feign_clients":
                m = re.match(r"^-\s+name:\s+(.+)$", stripped)
                if m:
                    if current_feign:
                        result["feign_clients"].append(current_feign)
                    current_feign = {"name": m.group(1), "service": "", "url_prop": ""}
                m_svc = re.match(r"^-?\s*service:\s+(.+)$", stripped)
                m_url = re.match(r"^-?\s*url_prop:\s+(.+)$", stripped)
                if m_svc and current_feign:
                    current_feign["service"] = m_svc.group(1)
                if m_url and current_feign:
                    current_feign["url_prop"] = m_url.group(1)

            elif section == "consumed_events":
                m = re.match(r"^-\s+event:\s+(.+)$", stripped)
                if m:
                    if current_consumed:
                        result["consumed_events"].append(current_consumed)
                    current_consumed = {"event": m.group(1), "destination": "", "consumer_class": ""}
                m_dest = re.match(r"^-?\s*destination:\s+(.+)$", stripped)
                m_cls = re.match(r"^-?\s*consumer_class:\s+(.+)$", stripped)
                if m_dest and current_consumed:
                    current_consumed["destination"] = m_dest.group(1)
                if m_cls and current_consumed:
                    current_consumed["consumer_class"] = m_cls.group(1)

            continue

        # Depth-4+ items (indent >= 4)
        if indent >= 4:
            if section == "domain" and subsection == "aggregates":
                m = re.match(r"^-\s+(.+)$", stripped)
                if m:
                    result["domain_aggregates"].append(m.group(1).split('#')[0].strip())

            elif section == "domain" and subsection == "entities":
                m = re.match(r"^-\s+(.+)$", stripped)
                if m:
                    result["domain_entities"].append(m.group(1).split('#')[0].strip())

            elif section == "application_services":
                if stripped == "operations:" and current_svc:
                    in_operations = True
                elif in_operations:
                    m = re.match(r"^-\s+(.+)$", stripped)
                    if m:
                        current_svc["operations"].append(m.group(1).split('#')[0].strip())

            elif section == "enums" and enum_name:
                m = re.match(r"^-\s+(.+)$", stripped)
                if m:
                    result["enums"][enum_name].append(m.group(1).split('#')[0].strip())

            elif section == "events" and in_events_published:
                m = re.match(r"^-\s+(.+)$", stripped)
                if m:
                    result["published_events"].append(m.group(1).split('#')[0].strip())

            elif section == "consumed_events" and current_consumed:
                m_dest = re.match(r"^destination:\s+(.+)$", stripped)
                m_cls = re.match(r"^consumer_class:\s+(.+)$", stripped)
                if m_dest:
                    current_consumed["destination"] = m_dest.group(1)
                if m_cls:
                    current_consumed["consumer_class"] = m_cls.group(1)

    # Flush last entries
    if current_svc:
        result["application_services"].append(current_svc)
    if current_feign:
        result["feign_clients"].append(current_feign)
    if current_consumed:
        result["consumed_events"].append(current_consumed)

    return result


def to_pascal_case(kebab: str) -> str:
    return "".join(part.capitalize() for part in kebab.replace("_", "-").split("-"))


def derive_meta(docs_dir: Path, port_override: Optional[int] = None) -> ToolMeta:
    docs_dir = docs_dir.resolve()
    if not docs_dir.exists():
        raise ValueError(f"Diretório de docs não encontrado: {docs_dir}")

    service_docs_dir = discover_service_dir(docs_dir)
    service = service_docs_dir.name  # "reforma-map-service"

    spec_file = service_docs_dir / f"{service}-spec.md"
    if not spec_file.exists():
        raise ValueError(f"Spec file não encontrado: {spec_file}")

    frontmatter = parse_frontmatter(spec_file)

    gen_config = parse_generator_config(service_docs_dir)

    bounded_context = (
        frontmatter.get("bounded_context")
        or gen_config.get("bounded_context")
        or service.removesuffix("-service")
    )
    package_suffix = re.sub(r"[-_]", "", bounded_context).lower()

    service_base = service.removesuffix("-service")
    app_class = to_pascal_case(service_base) + "Application"

    port = port_override or parse_port(docs_dir / "setup-local.md")

    project_name = frontmatter.get("project", to_pascal_case(service_base))
    description = f"{project_name} — {parse_description(spec_file)}"

    has_vertex_ai, has_gcs = detect_external_deps(
        service_docs_dir / "contracts" / "hub-integration.md"
    )

    # Port from generator-config.yml overrides setup-local.md if not explicitly given by CLI
    if port_override is None and gen_config.get("port"):
        port = int(gen_config["port"])

    # Issue prefix: prefer explicit YAML field; fallback to scanning issues/*.md
    issue_prefix = gen_config.get("issue_prefix") or parse_issue_prefix(docs_dir)

    # Service type: standard (default) | gateway | registry. Affects build.gradle.kts,
    # application.yml, *Application.java, SecurityConfig, package layout, sub-generators.
    service_type = gen_config.get("service_type", "standard")

    return ToolMeta(
        service=service,
        package_suffix=package_suffix,
        app_class=app_class,
        port=port,
        description=description,
        docs_dir=docs_dir,
        service_docs_dir=service_docs_dir,
        has_vertex_ai=has_vertex_ai,
        has_gcs=has_gcs,
        issue_prefix=issue_prefix,
        service_type=service_type,
        extra_dependencies=gen_config.get("extra_dependencies", []),
        profiles=gen_config.get("profiles", []),
        domain_aggregates=gen_config.get("domain_aggregates", []),
        domain_entities=gen_config.get("domain_entities", []),
        application_services=gen_config.get("application_services", []),
        enums=gen_config.get("enums", {}),
        published_events=gen_config.get("published_events", []),
        feign_clients=gen_config.get("feign_clients", []),
        consumed_events=gen_config.get("consumed_events", []),
        outbound_ports=gen_config.get("outbound_ports", []),
    )


# ── File generators ───────────────────────────────────────────────────────────

def gen_settings_gradle(service: str) -> str:
    return f'rootProject.name = "{service}"\n'


def gen_build_gradle(meta: ToolMeta) -> str:
    """Dispatcher por service_type."""
    if meta.service_type == "gateway":
        return gen_build_gradle_gateway(meta)
    if meta.service_type == "registry":
        return gen_build_gradle_registry(meta)
    return gen_build_gradle_standard(meta)


def gen_build_gradle_gateway(meta: ToolMeta) -> str:
    """Spring Cloud Gateway reativo (WebFlux). Sem JPA, Artemis, Feign."""
    from be_context_helper import render_code_template
    return render_code_template("code/gradle/build-gateway.gradle.kts.j2", {"meta": meta})


def gen_build_gradle_registry(meta: ToolMeta) -> str:
    """Eureka Server. Stack mínima."""
    from be_context_helper import render_code_template
    return render_code_template("code/gradle/build-registry.gradle.kts.j2", {"meta": meta})


def gen_build_gradle_standard(meta: ToolMeta) -> str:
    # Buckets
    gcloud_bom_line = ""
    extra_impl_lines: list[str] = []
    extra_test_lines: list[str] = []

    declared_artifacts = {dep.split(":", 1)[0] + ":" + dep.split(":")[1] for dep in meta.extra_dependencies if ":" in dep}

    # Emit each declared extra_dependency in the right scope.
    # Heuristic: cucumber/wiremock/awaitility/junit/mockito/testcontainers go to testImplementation; rest to implementation.
    test_keywords = ("cucumber", "wiremock", "awaitility", "junit", "mockito", "testcontainers", "rest-assured")
    for dep in meta.extra_dependencies:
        is_test = any(kw in dep.lower() for kw in test_keywords)
        line = f'    {"testImplementation" if is_test else "implementation"}("{dep}")\n'
        (extra_test_lines if is_test else extra_impl_lines).append(line)

    # Decide if we need google-cloud BOM (for any com.google.cloud:* artifact without explicit version, or for fallback aiplatform).
    needs_gcloud_bom = meta.has_vertex_ai or meta.has_gcs or any(d.startswith("com.google.cloud:") for d in meta.extra_dependencies)
    if needs_gcloud_bom:
        gcloud_bom_line = '        mavenBom("com.google.cloud:libraries-bom:26.39.0")\n'

    # Fallback auto-add only when the user did NOT declare an explicit Vertex/GCS artifact.
    has_explicit_vertex = any("vertexai" in d.lower() or "google-cloud-aiplatform" in d.lower() for d in meta.extra_dependencies)
    has_explicit_gcs = any("google-cloud-storage" in d.lower() for d in meta.extra_dependencies)
    if meta.has_vertex_ai and not has_explicit_vertex:
        extra_impl_lines.append('    implementation("com.google.cloud:google-cloud-aiplatform")\n')
    if meta.has_gcs and not has_explicit_gcs:
        extra_impl_lines.append('    implementation("com.google.cloud:google-cloud-storage")\n')

    extra_impl_block = "".join(extra_impl_lines).rstrip("\n")
    extra_test_block = "".join(extra_test_lines).rstrip("\n")

    # If user declared their own cucumber/wiremock/awaitility deps, suppress the hardcoded BDD block
    user_declared_cucumber = any("cucumber" in d.lower() for d in meta.extra_dependencies)
    bdd_block = "" if user_declared_cucumber else (
        '    // BDD — Cucumber\n'
        '    testImplementation("io.cucumber:cucumber-junit-platform-engine:7.18.0")\n'
        '    testImplementation("io.cucumber:cucumber-java:7.18.0")\n'
        '    testImplementation("io.cucumber:cucumber-spring:7.18.0")\n'
        '    testImplementation("org.junit.platform:junit-platform-suite-api:1.10.3")'
    )

    extra_impl_section = (
        f"\n    // Extra dependencies (from generator-config.yml)\n{extra_impl_block}"
        if extra_impl_block else ""
    )
    extra_test_section = (
        f"\n    // Extra test dependencies (from generator-config.yml)\n{extra_test_block}"
        if extra_test_block else ""
    )

    from be_context_helper import render_code_template
    return render_code_template("code/gradle/build-standard.gradle.kts.j2", {
        "meta": meta,
        "gcloud_bom_line": gcloud_bom_line,
        "extra_impl_section": extra_impl_section,
        "extra_test_section": extra_test_section,
        "bdd_block": bdd_block,
    })


def gen_dockerfile(service: str, port: int) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/docker/Dockerfile.j2", {"service": service, "port": port})


def gen_readme(meta: ToolMeta) -> str:
    tool_name = meta.docs_dir.name
    spec_rel = meta.service_docs_dir.relative_to(ROOT) / f"{meta.service}-spec.md"
    from be_context_helper import render_code_template
    return render_code_template("code/markdown/service-readme.md.j2", {
        "meta": meta,
        "tool_name": tool_name,
        "spec_rel": str(spec_rel),
    })


def gen_application_main(pkg_full: str, app_class: str, service_type: str = "standard") -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/spring-application.java.j2", {
        "pkg_full": pkg_full,
        "app_class": app_class,
        "service_type": service_type,
    })


def gen_security_config(pkg_full: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/security-config.java.j2", {"pkg_full": pkg_full})


def gen_security_config_gateway(pkg_full: str) -> str:
    """WebFlux variant — Spring Cloud Gateway é reativo."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/security-config-gateway.java.j2", {"pkg_full": pkg_full})


def gen_webmvc_config(pkg_full: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/webmvc-config.java.j2", {"pkg_full": pkg_full})


def gen_correlation_interceptor(pkg_full: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/correlation-interceptor.java.j2", {"pkg_full": pkg_full})


def gen_global_exception_handler(pkg_full: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/global-exception-handler.java.j2", {"pkg_full": pkg_full})


def gen_coded_exception(pkg_full: str) -> str:
    """CodedException base — apps throw with a String code (D-069)."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/coded-exception.java.j2", {"pkg_full": pkg_full})


def gen_problem_detail_factory(pkg_full: str) -> str:
    """ProblemDetailFactory with the error-model catalogue baked (D-069).

    Bakes:
      - CODE_METADATA: every code → (category, http_status, title)
      - CATEGORY_METADATA: every category → (default_status, fe_action_hint)
      - type_uri_template (with project_name materialised)

    Graceful degrade: empty maps when error-model.arch.json is absent —
    factory still works, all codes map to the internal_error fallback.
    """
    from be_context_helper import render_code_template

    interp_vars = {
        "multi_tenancy_term": (_CTX.multi_tenancy_term if _CTX else "tenant"),
        "project_name": (_CTX.project_name if _CTX else "project"),
    }

    media_type = "application/problem+json"
    type_uri_template = f"https://{interp_vars['project_name']}.com/errors/{{code}}"
    categories: list[dict] = []
    flat_codes: list[dict] = []

    try:
        from arch_decisions import load_decision, interpolate_payload
        em = interpolate_payload(load_decision("error-model"), interp_vars)
        media_type = em.get("media_type") or media_type
        # type_uri_template already interpolated by interpolate_payload — but
        # the {code} placeholder is intentional and must survive.
        tut = em.get("type_uri_template")
        if isinstance(tut, str) and tut:
            type_uri_template = tut
        categories = [
            {
                "id": c.get("id"),
                "default_http_status": c.get("default_http_status"),
                "fe_action_hint": c.get("fe_action_hint", ""),
            }
            for c in (em.get("categories") or [])
        ]
        for module in (em.get("modules") or []):
            for e in (module.get("errors") or []):
                flat_codes.append({
                    "code": e.get("code"),
                    "category": e.get("category"),
                    "http_status": e.get("http_status"),
                    "title": e.get("title") or e.get("code"),
                })
    except (ImportError, FileNotFoundError):
        pass

    return render_code_template("code/java/problem-detail-factory.java.j2", {
        "pkg_full": pkg_full,
        "project_name": interp_vars["project_name"],
        "type_uri_template": type_uri_template,
        "media_type": media_type,
        "categories": categories,
        "flat_codes": flat_codes,
    })


def gen_package_info(pkg_full: str, subpkg: str) -> str:
    pkg = pkg_full + "." + subpkg.replace("/", ".")
    return f"/**\n * {subpkg} layer — hexagonal architecture.\n */\npackage {pkg};\n"


def gen_application_yml(meta: ToolMeta) -> str:
    """Dispatcher por service_type."""
    if meta.service_type == "gateway":
        return gen_application_yml_gateway(meta)
    if meta.service_type == "registry":
        return gen_application_yml_registry(meta)
    return gen_application_yml_standard(meta)


def gen_application_yml_gateway(meta: ToolMeta) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/yaml/application-gateway.yml.j2", {"meta": meta})


def gen_application_yml_registry(meta: ToolMeta) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/yaml/application-registry.yml.j2", {"meta": meta})


def gen_application_yml_standard(meta: ToolMeta) -> str:
    pkg_full = f"{PKG_BASE}.{meta.package_suffix}"
    from be_context_helper import render_code_template
    return render_code_template("code/yaml/application-standard.yml.j2", {
        "meta": meta,
        "pkg_full": pkg_full,
    })


def gen_application_default_yml(service_type: str = "standard") -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/yaml/application-default.yml.j2", {"service_type": service_type})


def gen_application_test_yml(service_type: str = "standard") -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/yaml/application-test.yml.j2", {"service_type": service_type})


def gen_architecture_test(pkg_full: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/architecture-test.java.j2", {"pkg_full": pkg_full})


def gen_cross_aspect_arch_test(pkg_full: str) -> str:
    """CrossAspectArchTest.java (D-067) — bakes the decision catalogues into
    static Sets so ArchUnit rules can validate code against permission-
    catalogue / entity-scope / events without parsing JSON at test time.

    Gracefully degrades when an aspect file is missing: rules guard on
    `if (CATALOGUE.isEmpty()) return;` so a project without the snapshot
    still compiles and runs the tests as no-ops.
    """
    from be_context_helper import render_code_template

    interp_vars = {
        "multi_tenancy_term": (_CTX.multi_tenancy_term if _CTX else "tenant"),
        "project_name": (_CTX.project_name if _CTX else "project"),
    }

    permission_codes: list[str] = []
    filter_names: list[str] = []
    event_destinations: list[str] = []
    have_any = False

    try:
        from arch_decisions import (
            load_decision, interpolate_payload, all_permissions,
            entity_scope_entries_for_table, all_event_names,
        )
    except ImportError:
        from arch_decisions import (
            load_decision, interpolate_payload, all_permissions,
            all_event_names,
        )
        entity_scope_entries_for_table = None  # type: ignore

    try:
        pc = interpolate_payload(load_decision("permission-catalogue"), interp_vars)
        permission_codes = sorted(all_permissions(pc))
        have_any = have_any or bool(permission_codes)
    except FileNotFoundError:
        pass

    try:
        es = interpolate_payload(load_decision("entity-scope"), interp_vars)
        # Flatten every scopes[tipo][*].filter_name; dedup.
        names: set[str] = set()
        for tipo, entries in (es.get("scopes") or {}).items():
            for e in entries:
                fn = e.get("filter_name")
                if isinstance(fn, str) and fn:
                    names.add(fn)
        filter_names = sorted(names)
        have_any = have_any or bool(filter_names)
    except FileNotFoundError:
        pass

    try:
        ev = interpolate_payload(load_decision("events"), interp_vars)
        event_destinations = sorted(all_event_names(ev))
        have_any = have_any or bool(event_destinations)
    except FileNotFoundError:
        pass

    return render_code_template("code/java/cross-aspect-arch-test.java.j2", {
        "pkg_full": pkg_full,
        "permission_codes": permission_codes,
        "filter_names": filter_names,
        "event_destinations": event_destinations,
        "have_decisions": have_any,
    })


def gen_base_integration_test(pkg_full: str, service_type: str = "standard") -> str:
    """Singleton container pattern — sem @Container/@Testcontainers (CLAUDE.md compliance).

    Para gateway/registry, retorna variante sem Testcontainers (serviços de infra
    não persistem estado, não há DataSource para configurar).
    """
    from be_context_helper import render_code_template
    return render_code_template("code/java/base-integration-test.java.j2", {
        "pkg_full": pkg_full,
        "service_type": service_type,
    })


def gen_init_schema_sql(meta: ToolMeta) -> str:
    """Schema SQL executado pelo Testcontainers antes dos testes de integração.
    D-068 Phase 2: prepends CREATE EXTENSION IF NOT EXISTS for each extension
    declared in persistence.arch.json, so tests fail fast if an extension
    expected in production is missing.
    """
    from be_context_helper import render_code_template
    persistence_extensions: list[dict] = []
    try:
        from arch_decisions import load_decision
        persistence = load_decision("persistence")
        persistence_extensions = persistence.get("extensions_required") or []
    except (ImportError, FileNotFoundError):
        pass
    return render_code_template("code/sql/init-schema.sql.j2", {
        "meta": meta,
        "persistence_extensions": persistence_extensions,
    })


def gen_context_loads_it(pkg_full: str, service: str, issue_prefix: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/context-loads-it.java.j2", {"pkg_full": pkg_full, "service": service, "issue_prefix": issue_prefix})


def gen_docker_compose(meta: ToolMeta) -> str:
    """docker-compose.yml — infraestrutura local (PostgreSQL 16 + ActiveMQ Classic 5.18)."""
    db_name = f"{meta.package_suffix}_dev"
    db_user = meta.package_suffix
    db_pass = f"{meta.package_suffix}_dev_pass"
    from be_context_helper import render_code_template
    return render_code_template("code/yaml/docker-compose.yml.j2", {
        "meta": meta,
        "db_name": db_name,
        "db_user": db_user,
        "db_pass": db_pass,
    })


def gen_application_local_yml(meta: ToolMeta) -> str:
    """application-local.yml — profile local com mocks de plataforma."""
    db_name = f"{meta.package_suffix}_dev"
    db_user = meta.package_suffix
    db_pass = f"{meta.package_suffix}_dev_pass"
    pkg_full = f"{PKG_BASE}.{meta.package_suffix}"

    # Derive primary role: prefer meta.profiles[0]['role'] if available (safe access),
    # otherwise derive from service name (e.g. "<tool>-service" -> "<TOOL>_OPERATOR" — generic fallback)
    profiles_list = getattr(meta, 'profiles', [])
    primary_role = None
    if profiles_list and isinstance(profiles_list, list) and len(profiles_list) > 0:
        first = profiles_list[0]
        primary_role = first.get('role', None) if isinstance(first, dict) else None

    if not primary_role:
        # Derive from service name: "<tool>-service" -> "<TOOL>_OPERATOR"
        # Override via generator-config.yml profiles[0].role
        base = meta.service.removesuffix("-service")
        primary_role = base.upper().replace("-", "_") + "_OPERATOR"

    from be_context_helper import render_code_template
    return render_code_template("code/yaml/application-local.yml.j2", {
        "meta": meta,
        "db_name": db_name,
        "db_user": db_user,
        "db_pass": db_pass,
        "pkg_full": pkg_full,
        "primary_role": primary_role,
    })


def gen_init_db_sql(meta: ToolMeta) -> str:
    """scripts/init-db.sql — inicializa schemas de tenant para desenvolvimento local."""
    db_user = meta.package_suffix
    from be_context_helper import render_code_template
    return render_code_template("code/sql/init-db.sql.j2", {
        "meta": meta,
        "db_user": db_user,
    })


def gen_domain_service_config(pkg_full: str) -> str:
    """DomainServiceConfig — obrigatório pelo CLAUDE.md: domain services são POJOs e devem ser @Bean."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/domain-service-config.java.j2", {"pkg_full": pkg_full})


def gen_feign_client_config(pkg_full: str) -> str:
    """FeignClientConfig — 3 RequestInterceptors: correlationId, tenantId, auth bearer propagation."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/feign-client-config.java.j2", {"pkg_full": pkg_full})


def gen_vertex_ai_config(pkg_full: str) -> str:
    """VertexAiConfig — VertexAI + GenerativeModel beans (Google Cloud Vertex AI SDK)."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/vertex-ai-config.java.j2", {"pkg_full": pkg_full})


def _event_name_to_constant(event_name: str, project_name: str) -> str:
    """Convert 'bosq.cadastro.cliente.criado' → 'CADASTRO_CLIENTE_CRIADO'.

    Strips the project_name prefix (if present) and the leading dot, then
    converts dots/hyphens to underscores and uppercases. For IAM-style names
    where the project prefix is the only segment before the entity
    (`bosq.sessao.criada`), the constant becomes `SESSAO_CRIADA`.
    """
    name = event_name
    prefix = project_name + "."
    if name.startswith(prefix):
        name = name[len(prefix):]
    return name.replace(".", "_").replace("-", "_").upper()


_ENVELOPE_FIELD_TO_JAVA: dict[str, str] = {
    # Catalogue type → Java type. Falls back to Object for unknown shapes.
    "uuid": "UUID",
    "string": "String",
    "ISO-8601": "OffsetDateTime",
    "object": "Map<String, Object>",
    "{service, instance, version}": "Map<String, Object>",
    "{usuarioId, papel}": "Map<String, Object>",
}


def gen_event_destinations(pkg_full: str) -> str:
    """EventDestinations.java — compile-time constants from events.arch.json (D-070)."""
    from be_context_helper import render_code_template

    interp_vars = {
        "multi_tenancy_term": (_CTX.multi_tenancy_term if _CTX else "tenant"),
        "project_name": (_CTX.project_name if _CTX else "project"),
    }
    project_name = interp_vars["project_name"]

    destinations: list[dict] = []
    try:
        from arch_decisions import load_decision, interpolate_payload
        ev = interpolate_payload(load_decision("events"), interp_vars)
        for module in (ev.get("modules") or []):
            for e in (module.get("events") or []):
                name = e.get("name")
                if not isinstance(name, str) or not name:
                    continue
                destinations.append({
                    "constant_name": _event_name_to_constant(name, project_name),
                    "value": name,
                    "payload_data": e.get("payload_data", ""),
                })
    except (ImportError, FileNotFoundError):
        pass
    return render_code_template("code/java/event-destinations.java.j2", {
        "pkg_full": pkg_full,
        "destinations": destinations,
    })


def gen_event_envelope(pkg_full: str) -> str:
    """EventEnvelope.java — record from events.envelope.payload_fields (D-070)."""
    from be_context_helper import render_code_template

    interp_vars = {
        "multi_tenancy_term": (_CTX.multi_tenancy_term if _CTX else "tenant"),
        "project_name": (_CTX.project_name if _CTX else "project"),
    }

    fields: list[dict] = []
    try:
        from arch_decisions import load_decision, interpolate_payload
        ev = interpolate_payload(load_decision("events"), interp_vars)
        for f in (ev.get("envelope") or {}).get("payload_fields") or []:
            name = f.get("name")
            if not isinstance(name, str) or not name:
                continue
            ftype = f.get("type", "string")
            java_type = _ENVELOPE_FIELD_TO_JAVA.get(ftype, "Object")
            # camelCase the field name. Catalogue already uses camelCase, but
            # be defensive.
            java_name = name[0].lower() + name[1:] if name else name
            fields.append({
                "java_name": java_name,
                "java_type": java_type,
                "required": bool(f.get("required")),
                "description": f.get("description", ""),
            })
    except (ImportError, FileNotFoundError):
        pass

    if not fields:
        # Minimal fallback so the record still compiles.
        fields = [{
            "java_name": "data",
            "java_type": "Map<String, Object>",
            "required": True,
            "description": "(no events.arch.json pinned at generation time)",
        }]

    return render_code_template("code/java/event-envelope.java.j2", {
        "pkg_full": pkg_full,
        "fields": fields,
    })


def gen_processed_event(pkg_full: str) -> str:
    """ProcessedEvent.java — idempotency JPA entity (D-070).

    Reads table + key_field from events.idempotency. Defaults to
    'processed_events' + 'event_id' when no catalogue is pinned.
    """
    from be_context_helper import render_code_template

    table_name = "processed_events"
    key_field = "event_id"
    try:
        from arch_decisions import load_decision
        ev = load_decision("events")
        idem = ev.get("idempotency") or {}
        table_name = idem.get("table") or table_name
        key_field = idem.get("key_field") or key_field
    except (ImportError, FileNotFoundError):
        pass

    return render_code_template("code/java/processed-event.java.j2", {
        "pkg_full": pkg_full,
        "table_name": table_name,
        "key_field": key_field,
    })


def gen_processed_event_repository(pkg_full: str) -> str:
    """ProcessedEventRepository.java — Spring Data JPA repo (D-070)."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/processed-event-repository.java.j2",
                                {"pkg_full": pkg_full})


def gen_artemis_config(pkg_full: str) -> str:
    """ArtemisConfig — JMS listener factory + DLQ wiring + Jackson MessageConverter."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/artemis-config.java.j2", {"pkg_full": pkg_full})


def gen_audit_action_annotation(pkg_full: str) -> str:
    """@AuditAction marker annotation (D-059, Phase 2). Lives under shared/audit."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/audit-action-annotation.java.j2", {"pkg_full": pkg_full})


def gen_audit_aspect(pkg_full: str) -> str:
    """AuditAspect — intercepts @AuditAction methods, emits slf4j audit log (D-059)."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/audit-aspect.java.j2", {"pkg_full": pkg_full})


def gen_data_scope_record(pkg_full: str) -> str:
    """DataScope record — tipo (e.g. VENDEDOR) + valores. Derived from rbac.arch.json (D-059)."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/data-scope.java.j2", {"pkg_full": pkg_full})


def gen_access_context_holder(pkg_full: str) -> str:
    """AccessContextHolder — ThreadLocal carrying the current user's permissions + dataScope (D-059)."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/access-context-holder.java.j2", {"pkg_full": pkg_full})


def gen_data_scope_filter_aspect(pkg_full: str) -> str:
    """DataScopeFilterAspect — activates Hibernate filters per request based on
    AccessContextHolder.requireDataScope() (D-059). Branches per tipo are
    derived from entity-scope.arch.json so each entity contributes its own
    enableFilter call (D-062).
    """
    from be_context_helper import render_code_template
    try:
        from arch_decisions import load_decision
        rbac = load_decision("rbac")
        scope_types = (rbac.get("data_scope") or {}).get("types") or []
    except FileNotFoundError:
        scope_types = []

    # Build {tipo: [{filter_name, param, kind}, ...]} from entity-scope.
    # Skip EMPRESA_COMPLETA / any tipo without entities — those need no
    # filters since they mean "no restriction".
    entity_scope_filters: dict[str, list[dict]] = {}
    try:
        from arch_decisions import load_decision
        entity_scope = load_decision("entity-scope")
        for tipo, entries in (entity_scope.get("scopes") or {}).items():
            entity_scope_filters[tipo] = [
                {"filter_name": e["filter_name"], "param": e["param"],
                 "kind": e.get("kind", "scalar")}
                for e in entries
            ]
    except FileNotFoundError:
        # No entity-scope pinned — aspect renders with no branches, every
        # restricted scope hits the "no filter wiring" warning path.
        pass

    return render_code_template("code/java/data-scope-filter-aspect.java.j2", {
        "pkg_full": pkg_full,
        "scope_types": scope_types,
        "entity_scope_filters": entity_scope_filters,
    })


def gen_tenant_context_holder(pkg_full: str) -> str:
    """TenantContextHolder — ThreadLocal + MDC binding for tenant-id propagation."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/tenant-context-holder.java.j2", {"pkg_full": pkg_full})


def gen_tenant_context_filter(pkg_full: str) -> str:
    """TenantContextFilter — extract tenantId from JWT and bind to TenantContextHolder."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/tenant-context-filter.java.j2", {"pkg_full": pkg_full})


def _multi_tenancy_phase2_active() -> tuple[bool, str, str]:
    """Decide whether Phase 2 multi-tenancy code should be emitted.

    Returns (active, hibernate_strategy, tenant_global_schema). active is True
    only when the project's multiTenancy.isolationStrategy is one of the
    Hibernate-MULTI_TENANT strategies declared in multi-tenancy.arch.json
    (D-071 Fase 1 only ships schema-per-tenant — other strategies would
    require different impls).
    """
    try:
        from arch_decisions import (
            load_decision, multi_tenancy_isolation_strategy,
        )
        mt = load_decision("multi-tenancy")
    except (ImportError, FileNotFoundError):
        return (False, "", "")
    if _CTX is None:
        return (False, "", "")
    raw_ctx = _CTX.raw or {}
    strategy_id = (raw_ctx.get("multiTenancy") or {}).get("isolationStrategy") or ""
    if strategy_id != "schema-per-tenant":
        # Fase 1 only ships schema-per-tenant; other strategies require
        # different impls (DataSource-per-tenant, RLS, ...) — out of scope.
        return (False, "", "")
    strat = multi_tenancy_isolation_strategy(strategy_id, mt)
    if not strat:
        return (False, "", "")
    return (
        True,
        strat.get("hibernate_strategy") or "SCHEMA",
        _CTX.global_schema or "global",
    )


def gen_multi_tenant_connection_provider(pkg_full: str) -> str:
    """MultiTenantConnectionProvider — Hibernate schema-switching hook (D-071)."""
    from be_context_helper import render_code_template
    _, _, tenant_global_schema = _multi_tenancy_phase2_active()
    return render_code_template("code/java/multi-tenant-connection-provider.java.j2", {
        "pkg_full": pkg_full,
        "tenant_global_schema": tenant_global_schema or "global",
    })


def gen_tenant_identifier_resolver(pkg_full: str) -> str:
    """TenantIdentifierResolver — reads from TenantContextHolder (D-071)."""
    from be_context_helper import render_code_template
    _, _, tenant_global_schema = _multi_tenancy_phase2_active()
    return render_code_template("code/java/tenant-identifier-resolver.java.j2", {
        "pkg_full": pkg_full,
        "tenant_global_schema": tenant_global_schema or "global",
    })


def gen_hibernate_multi_tenancy_config(pkg_full: str) -> str:
    """HibernateMultiTenancyConfig — wires Hibernate multi-tenancy beans (D-071)."""
    from be_context_helper import render_code_template
    _, hibernate_strategy, _ = _multi_tenancy_phase2_active()
    return render_code_template("code/java/hibernate-multi-tenancy-config.java.j2", {
        "pkg_full": pkg_full,
        "hibernate_strategy": hibernate_strategy or "SCHEMA",
    })


def gen_mdc_context_restorer(pkg_full: str) -> str:
    """MdcContextRestorer — restore correlationId/tenantId on JMS consumer thread from message headers."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/mdc-context-restorer.java.j2", {"pkg_full": pkg_full})


# ── P3: domain generators (from generator-config.yml) ────────────────────────

def gen_enum_class(pkg_full: str, enum_name: str, values: list[str]) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/enum-class.java.j2", {
        "pkg_full": pkg_full,
        "enum_name": enum_name,
        "values": values,
    })


def gen_use_case_interface(pkg_full: str, svc_name: str, operations: list[str]) -> str:
    iface_name = svc_name.replace("Service", "UseCase")
    from be_context_helper import render_code_template
    return render_code_template("code/java/use-case-interface.java.j2", {
        "pkg_full": pkg_full,
        "iface_name": iface_name,
        "operations": operations,
    })


def gen_application_service_stub(pkg_full: str, svc_name: str, operations: list[str]) -> str:
    iface_name = svc_name.replace("Service", "UseCase")
    from be_context_helper import render_code_template
    return render_code_template("code/java/application-service-stub.java.j2", {
        "pkg_full": pkg_full,
        "svc_name": svc_name,
        "iface_name": iface_name,
        "operations": operations,
    })


def gen_event_producer(pkg_full: str, event_fqn: str) -> str:
    """event_fqn: 'ReformaMap.AssessmentCreated' → class AssessmentCreatedProducer."""
    parts = event_fqn.split(".")
    event_simple = parts[-1]          # AssessmentCreated
    destination = event_fqn           # ReformaMap.AssessmentCreated (JMS destination)
    class_name = f"{event_simple}Producer"
    from be_context_helper import render_code_template
    return render_code_template("code/java/event-producer.java.j2", {
        "pkg_full": pkg_full,
        "class_name": class_name,
        "destination": destination,
    })


# ── P3+: full hexagonal stubs from generator-config.yml ──────────────────────

def _svc_to_kebab(svc_name: str) -> str:
    """AssessmentService → assessment, ModuleExecutionService → module-execution."""
    base = svc_name.replace("Service", "")
    return re.sub(r'(?<!^)(?=[A-Z])', '-', base).lower()


def _http_verb(op: str) -> str:
    if any(op.startswith(p) for p in ("create", "register", "open", "start", "request", "generate", "consolidate", "submit", "add")):
        return "Post"
    if any(op.startswith(p) for p in ("get", "list", "find")):
        return "Get"
    if any(op.startswith(p) for p in ("delete", "cancel", "revoke", "remove")):
        return "Delete"
    return "Put"


def gen_controller(pkg_full: str, svc_name: str, ops: list[str], tool_name: str) -> str:
    controller_name = svc_name.replace("Service", "Controller")
    iface_name = svc_name.replace("Service", "UseCase")
    field_name = iface_name[0].lower() + iface_name[1:]
    kebab = _svc_to_kebab(svc_name)
    # Stub path; dev deve refinar conforme contracts/api-contract.md (TODO no controller)
    base_path = f"/{tool_name}/{kebab}"

    # D-059 (Tier 2.1 Phase 2): derive @PreAuthorize permission code + optional
    # @AuditAction from rbac.arch.json. D-060 (Phase 1.5) adds the permission
    # catalogue for HARD validation of derived codes. Falls back to no
    # annotation when no decisions are pinned, so this generator stays usable
    # before /new-project P2 lands the snapshot in a project.
    try:
        from arch_decisions import (
            load_decision, resolve_module_prefix, resolve_permission,
            resolve_audit_action, interpolate_payload, all_permissions,
            expand_bundle,
        )
        rbac = load_decision("rbac")
        # D-078: pass project-context.modules.registry so resolve_module_prefix
        # consults the project's actual module declarations before falling
        # back to the workspace's hardcoded BOSQ-ERP map.
        project_modules = (_CTX.modules if _CTX else None)
        module_prefix = resolve_module_prefix(
            pkg_full.split(".")[-1], modules=project_modules)
        audit_required = (rbac.get("enforcement") or {}).get("audit_required") or []
    except FileNotFoundError:
        print(f"[gen_controller] WARN: no rbac.arch.json found — skipping @PreAuthorize derivation for {controller_name}", file=sys.stderr)
        rbac = None
        module_prefix = pkg_full.split(".")[-1][:3].lower()
        audit_required = []

    # Try the catalogue (D-060). Absent catalogue → fall back to soft hint
    # against rbac kind:list bundles only (Phase 2 behaviour).
    # D-077: track `catalogue_loaded` as a sentinel so an EMPTY catalogue
    # (loaded but with no permissions yet — common right after D-074
    # discovery override) still triggers hard validation. The previous
    # `if catalogue_codes:` guard was falsy for empty sets, silently
    # bypassing validation.
    catalogue = None
    catalogue_loaded = False
    catalogue_codes: set[str] = set()
    granted_codes: set[str] = set()
    if rbac is not None:
        try:
            catalogue = load_decision("permission-catalogue")
            catalogue_loaded = True
            # Interpolate `{{ multi_tenancy_term }}` placeholders so codes
            # match what the generator produces (literal). Use project context
            # if available; fall back to the legacy 'tenant' default otherwise.
            interp_vars = {
                "multi_tenancy_term": (_CTX.multi_tenancy_term if _CTX else "tenant"),
            }
            catalogue = interpolate_payload(catalogue, interp_vars)
            catalogue_codes = all_permissions(catalogue)
            # Union of every code granted by every role's bundle — used to
            # warn when no role currently grants the derived permission.
            interp_rbac = interpolate_payload(rbac, interp_vars)
            for role in interp_rbac.get("roles", []):
                granted_codes |= expand_bundle(role.get("permission_bundle") or {}, catalogue)
        except FileNotFoundError:
            print(f"[gen_controller] hint: no permission-catalogue.arch.json — skipping hard validation for {controller_name}", file=sys.stderr)

    methods_ops = []
    unknown_verbs: list[str] = []
    unknown_perms: list[str] = []
    for op in ops:
        verb = _http_verb(op)
        ann = f"@{verb}Mapping"
        if verb == "Get" and op.startswith("get"):
            ann = "@GetMapping(\"/{id}\")"
        elif verb == "Put":
            ann = f"@PutMapping(\"/{{id}}/{op}\")"

        permission = resolve_permission(op, module_prefix, kebab) if rbac else None
        audit_action = resolve_audit_action(op, kebab, audit_required) if rbac else None
        if rbac and permission is None:
            # Verb didn't map to any action in _OP_VERB_TO_ACTION. Aggregate
            # for a single error report after the loop.
            unknown_verbs.append(op)
        elif permission and catalogue_loaded:
            if permission not in catalogue_codes:
                unknown_perms.append(f"{op} → {permission}")
            elif granted_codes and permission not in granted_codes:
                print(f"[gen_controller] hint: '{permission}' declared in catalogue but granted to NO role", file=sys.stderr)

        methods_ops.append({
            "annotation": ann,
            "op": op,
            "permission": permission,
            "audit_action": audit_action,
        })

    if unknown_verbs or unknown_perms:
        msg = [f"[gen_controller] {controller_name}: cannot resolve security annotations for these ops:"]
        if unknown_verbs:
            msg.append(f"  unknown verb prefix (not in arch_decisions._OP_VERB_TO_ACTION):")
            msg.extend(f"    - {op}" for op in unknown_verbs)
        if unknown_perms:
            msg.append(f"  permission not declared in permission-catalogue.arch.json:")
            msg.extend(f"    - {p}" for p in unknown_perms)
        msg.append(
            f"Fix: either add the verb to arch_decisions._OP_VERB_TO_ACTION, "
            f"add the missing permission under "
            f"modules[prefix={module_prefix!r}].permissions in the catalogue, "
            f"or rename the op so it follows the canonical verb vocabulary."
        )
        raise ValueError("\n".join(msg))

    from be_context_helper import render_code_template
    return render_code_template("code/java/controller.java.j2", {
        "pkg_full": pkg_full,
        "iface_name": iface_name,
        "controller_name": controller_name,
        "field_name": field_name,
        "base_path": base_path,
        "methods_ops": methods_ops,
    })


def gen_request_record(pkg_full: str, name: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/request-record.java.j2", {"pkg_full": pkg_full, "name": name})


def gen_response_record(pkg_full: str, name: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/response-record.java.j2", {"pkg_full": pkg_full, "name": name})


def gen_aggregate_model(pkg_full: str, name: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/aggregate-model.java.j2", {"pkg_full": pkg_full, "name": name})


def gen_entity_model(pkg_full: str, name: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/entity-model.java.j2", {"pkg_full": pkg_full, "name": name})


def gen_domain_service_pojo(pkg_full: str, aggregate: str) -> str:
    svc_name = f"{aggregate}DomainService"
    from be_context_helper import render_code_template
    return render_code_template("code/java/domain-service-pojo.java.j2", {
        "pkg_full": pkg_full,
        "aggregate": aggregate,
        "svc_name": svc_name,
    })


def gen_outbound_port_stub(pkg_full: str, port_name: str) -> str:
    """Stub interface for outbound ports declared in generator-config.yml outbound_ports."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/outbound-port-stub.java.j2", {"pkg_full": pkg_full, "port_name": port_name})


def gen_repository_port(pkg_full: str, aggregate: str) -> str:
    port_name = f"{aggregate}RepositoryPort"
    model_import = f"{pkg_full}.domain.model.{aggregate}"
    from be_context_helper import render_code_template
    return render_code_template("code/java/repository-port.java.j2", {
        "pkg_full": pkg_full,
        "aggregate": aggregate,
        "port_name": port_name,
        "model_import": model_import,
    })


def gen_feign_client_stub(pkg_full: str, fc: dict) -> str:
    name = fc["name"]           # TenantContextFeignClient
    service = fc["service"]     # tenant-context-service
    url_prop = fc["url_prop"]   # services.tenant-context-service.url
    from be_context_helper import render_code_template
    return render_code_template("code/java/feign-client-stub.java.j2", {
        "pkg_full": pkg_full,
        "name": name,
        "service": service,
        "url_prop": url_prop,
    })


def gen_jms_consumer(pkg_full: str, consumed: dict) -> str:
    cls = consumed["consumer_class"]
    dest = consumed["destination"]
    event = consumed["event"]
    from be_context_helper import render_code_template
    return render_code_template("code/java/jms-consumer.java.j2", {
        "pkg_full": pkg_full,
        "cls": cls,
        "dest": dest,
        "event": event,
    })


def gen_jpa_entity(pkg_full: str, name: str) -> str:
    table = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    id_col = f"{table}_id"
    from be_context_helper import render_code_template
    return render_code_template("code/java/jpa-entity.java.j2", {
        "pkg_full": pkg_full,
        "name": name,
        "table": table,
        "id_col": id_col,
    })


def gen_jpa_repository(pkg_full: str, name: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/jpa-repository.java.j2", {"pkg_full": pkg_full, "name": name})


def gen_persistence_adapter(pkg_full: str, name: str) -> str:
    from be_context_helper import render_code_template
    return render_code_template("code/java/persistence-adapter.java.j2", {
        "pkg_full": pkg_full,
        "name": name,
    })


def gen_domain_service_config_full(pkg_full: str, aggregates: list[str]) -> str:
    """DomainServiceConfig with @Bean per domain service aggregate."""
    from be_context_helper import render_code_template
    return render_code_template("code/java/domain-service-config-full.java.j2", {
        "pkg_full": pkg_full,
        "aggregates": aggregates,
    })


# ── Manifest builder ──────────────────────────────────────────────────────────

def build_file_manifest(meta: ToolMeta) -> list[tuple[Path, str]]:
    if meta.service_type in ("gateway", "registry"):
        return _build_file_manifest_infra(meta)
    return _build_file_manifest_standard(meta)


def _build_file_manifest_infra(meta: ToolMeta) -> list[tuple[Path, str]]:
    """Manifesto reduzido para gateway/registry: sem JPA, sem messaging, sem domain."""
    svc_root = SERVICES_DIR / meta.service
    pkg_full = f"{PKG_BASE}.{meta.package_suffix}"
    pkg_path = pkg_full.replace(".", "/")

    main_java = svc_root / "src" / "main" / "java" / pkg_path
    main_res = svc_root / "src" / "main" / "resources"
    test_java = svc_root / "src" / "test" / "java" / pkg_path
    test_res = svc_root / "src" / "test" / "resources"

    files: list[tuple[Path, str]] = []

    files.append((svc_root / "settings.gradle.kts", gen_settings_gradle(meta.service)))
    files.append((svc_root / "build.gradle.kts", gen_build_gradle(meta)))
    files.append((svc_root / "Dockerfile", gen_dockerfile(meta.service, meta.port)))
    files.append((svc_root / "README.md", gen_readme(meta)))

    files.append((main_java / f"{meta.app_class}.java",
                  gen_application_main(pkg_full, meta.app_class, meta.service_type)))

    # Gateway tem JWT/OAuth2 Resource Server (WebFlux); Registry não tem Security
    if meta.service_type == "gateway":
        files.append((main_java / "infrastructure" / "config" / "SecurityConfig.java",
                      gen_security_config_gateway(pkg_full)))

    files.append((main_res / "application.yml", gen_application_yml(meta)))
    files.append((main_res / "application-default.yml",
                  gen_application_default_yml(meta.service_type)))

    files.append((test_java / "architecture" / "ArchitectureTest.java",
                  gen_architecture_test(pkg_full)))
    # D-067: cross-aspect ArchUnit tests with baked decision catalogues.
    # Only emitted for standard services — gateway/registry don't have
    # controllers/entities/producers to validate against.
    if meta.service_type == "standard":
        files.append((test_java / "architecture" / "CrossAspectArchTest.java",
                      gen_cross_aspect_arch_test(pkg_full)))
    files.append((test_java / "integration" / "BaseIntegrationTest.java",
                  gen_base_integration_test(pkg_full, meta.service_type)))
    files.append((test_java / "integration" / "ApplicationContextLoadsIT.java",
                  gen_context_loads_it(pkg_full, meta.service, meta.issue_prefix)))
    files.append((test_res / "application-test.yml",
                  gen_application_test_yml(meta.service_type)))
    # gateway/registry have no domain/api/infrastructure classes — allow empty ArchUnit rules
    files.append((test_res / "archunit.properties",
                  "archRule.failOnEmptyShould=false\n"))

    return files


def _build_file_manifest_standard(meta: ToolMeta) -> list[tuple[Path, str]]:
    svc_root = SERVICES_DIR / meta.service
    pkg_full = f"{PKG_BASE}.{meta.package_suffix}"
    pkg_path = pkg_full.replace(".", "/")

    main_java = svc_root / "src" / "main" / "java" / pkg_path
    main_res = svc_root / "src" / "main" / "resources"
    test_java = svc_root / "src" / "test" / "java" / pkg_path
    test_res = svc_root / "src" / "test" / "resources"

    files: list[tuple[Path, str]] = []

    # ── Root ────────────────────────────────────────────────────────────────────
    files.append((svc_root / "settings.gradle.kts", gen_settings_gradle(meta.service)))
    files.append((svc_root / "build.gradle.kts", gen_build_gradle(meta)))
    files.append((svc_root / "Dockerfile", gen_dockerfile(meta.service, meta.port)))
    files.append((svc_root / "README.md", gen_readme(meta)))
    files.append((svc_root / "docker-compose.yml", gen_docker_compose(meta)))
    files.append((svc_root / "scripts" / "init-db.sql", gen_init_db_sql(meta)))

    # ── Main application class ──────────────────────────────────────────────────
    files.append((main_java / f"{meta.app_class}.java",
                  gen_application_main(pkg_full, meta.app_class, meta.service_type)))

    # ── Infrastructure boilerplate ──────────────────────────────────────────────
    files.append((main_java / "infrastructure" / "config" / "SecurityConfig.java",
                  gen_security_config(pkg_full)))
    files.append((main_java / "infrastructure" / "config" / "WebMvcConfig.java",
                  gen_webmvc_config(pkg_full)))
    if meta.domain_aggregates:
        files.append((main_java / "infrastructure" / "config" / "DomainServiceConfig.java",
                      gen_domain_service_config_full(pkg_full, meta.domain_aggregates)))
    else:
        files.append((main_java / "infrastructure" / "config" / "DomainServiceConfig.java",
                      gen_domain_service_config(pkg_full)))
    files.append((main_java / "infrastructure" / "config" / "FeignClientConfig.java",
                  gen_feign_client_config(pkg_full)))
    files.append((main_java / "infrastructure" / "security" / "CorrelationIdInterceptor.java",
                  gen_correlation_interceptor(pkg_full)))
    files.append((main_java / "infrastructure" / "security" / "TenantContextHolder.java",
                  gen_tenant_context_holder(pkg_full)))
    files.append((main_java / "infrastructure" / "security" / "TenantContextFilter.java",
                  gen_tenant_context_filter(pkg_full)))
    # D-071: multi-tenancy Phase 2 — schema-per-tenant Hibernate wiring.
    # Emitted ONLY when the project picked schema-per-tenant strategy.
    mt_active, _, _ = _multi_tenancy_phase2_active()
    if mt_active:
        files.append((main_java / "infrastructure" / "security" / "MultiTenantConnectionProvider.java",
                      gen_multi_tenant_connection_provider(pkg_full)))
        files.append((main_java / "infrastructure" / "security" / "TenantIdentifierResolver.java",
                      gen_tenant_identifier_resolver(pkg_full)))
        files.append((main_java / "infrastructure" / "config" / "HibernateMultiTenancyConfig.java",
                      gen_hibernate_multi_tenancy_config(pkg_full)))
    # D-059 (Tier 2.1 Phase 2): audit annotation + aspect, data-scope holder
    # + filter aspect. Packages match shared/rbac/{enforcement,data-scope}.md.
    files.append((main_java / "shared" / "audit" / "AuditAction.java",
                  gen_audit_action_annotation(pkg_full)))
    files.append((main_java / "shared" / "audit" / "AuditAspect.java",
                  gen_audit_aspect(pkg_full)))
    files.append((main_java / "shared" / "security" / "DataScope.java",
                  gen_data_scope_record(pkg_full)))
    files.append((main_java / "shared" / "security" / "AccessContextHolder.java",
                  gen_access_context_holder(pkg_full)))
    files.append((main_java / "shared" / "security" / "DataScopeFilterAspect.java",
                  gen_data_scope_filter_aspect(pkg_full)))
    files.append((main_java / "api" / "exception" / "GlobalExceptionHandler.java",
                  gen_global_exception_handler(pkg_full)))
    # D-069: error-model Phase 2 — CodedException base + ProblemDetailFactory
    # with the catalogue baked. Apps throw CodedException("cad.cliente.duplicado")
    # and the handler resolves it via the factory.
    files.append((main_java / "shared" / "error" / "CodedException.java",
                  gen_coded_exception(pkg_full)))
    files.append((main_java / "shared" / "error" / "ProblemDetailFactory.java",
                  gen_problem_detail_factory(pkg_full)))

    # Vertex AI config (only if tool declares Vertex usage in contracts/extra_dependencies)
    if meta.has_vertex_ai:
        files.append((main_java / "infrastructure" / "config" / "VertexAiConfig.java",
                      gen_vertex_ai_config(pkg_full)))

    # Artemis JMS config + MDC restorer (only if messaging is used)
    has_messaging = bool(meta.published_events) or bool(meta.consumed_events)
    if has_messaging:
        files.append((main_java / "infrastructure" / "config" / "ArtemisConfig.java",
                      gen_artemis_config(pkg_full)))
        files.append((main_java / "infrastructure" / "messaging" / "MdcContextRestorer.java",
                      gen_mdc_context_restorer(pkg_full)))
        # D-070: events Phase 2 — EventDestinations (constants), EventEnvelope
        # (record), ProcessedEvent (idempotency JPA entity + repository).
        files.append((main_java / "shared" / "messaging" / "EventDestinations.java",
                      gen_event_destinations(pkg_full)))
        files.append((main_java / "shared" / "messaging" / "EventEnvelope.java",
                      gen_event_envelope(pkg_full)))
        files.append((main_java / "infrastructure" / "persistence" / "entity" / "ProcessedEvent.java",
                      gen_processed_event(pkg_full)))
        files.append((main_java / "infrastructure" / "persistence" / "repository" / "ProcessedEventRepository.java",
                      gen_processed_event_repository(pkg_full)))

    # ── Resources ───────────────────────────────────────────────────────────────
    files.append((main_res / "application.yml", gen_application_yml(meta)))
    files.append((main_res / "application-default.yml", gen_application_default_yml()))
    files.append((main_res / "application-local.yml", gen_application_local_yml(meta)))

    # ── Tests ───────────────────────────────────────────────────────────────────
    files.append((test_java / "architecture" / "ArchitectureTest.java",
                  gen_architecture_test(pkg_full)))
    # D-067: cross-aspect ArchUnit tests with baked decision catalogues.
    # Only emitted for standard services — gateway/registry don't have
    # controllers/entities/producers to validate against.
    if meta.service_type == "standard":
        files.append((test_java / "architecture" / "CrossAspectArchTest.java",
                      gen_cross_aspect_arch_test(pkg_full)))
    files.append((test_java / "integration" / "BaseIntegrationTest.java",
                  gen_base_integration_test(pkg_full)))
    files.append((test_java / "integration" / "ApplicationContextLoadsIT.java",
                  gen_context_loads_it(pkg_full, meta.service, meta.issue_prefix)))
    files.append((test_res / "application-test.yml", gen_application_test_yml()))
    files.append((test_res / "init-schema.sql", gen_init_schema_sql(meta)))

    # ── Domain enums ────────────────────────────────────────────────────────────
    for enum_name, values in meta.enums.items():
        files.append((main_java / "domain" / "model" / f"{enum_name}.java",
                      gen_enum_class(pkg_full, enum_name, values)))

    # ── Domain models (aggregates + entities) ───────────────────────────────────
    for agg in meta.domain_aggregates:
        files.append((main_java / "domain" / "model" / f"{agg}.java",
                      gen_aggregate_model(pkg_full, agg)))

    for ent in meta.domain_entities:
        files.append((main_java / "domain" / "model" / f"{ent}.java",
                      gen_entity_model(pkg_full, ent)))

    # ── Domain services (pure POJOs) ────────────────────────────────────────────
    for agg in meta.domain_aggregates:
        files.append((main_java / "domain" / "service" / f"{agg}DomainService.java",
                      gen_domain_service_pojo(pkg_full, agg)))

    # ── Application use cases + services ────────────────────────────────────────
    for svc in meta.application_services:
        svc_name = svc["name"]
        ops = svc.get("operations", [])
        iface_name = svc_name.replace("Service", "UseCase")
        files.append((main_java / "application" / "port" / "in" / f"{iface_name}.java",
                      gen_use_case_interface(pkg_full, svc_name, ops)))
        files.append((main_java / "application" / "service" / f"{svc_name}.java",
                      gen_application_service_stub(pkg_full, svc_name, ops)))
        files.append((main_java / "api" / "controller" / f"{svc_name.replace('Service', 'Controller')}.java",
                      gen_controller(pkg_full, svc_name, ops, meta.docs_dir.name)))
        domain_name = svc_name.replace("Service", "")
        files.append((main_java / "api" / "dto" / f"{domain_name}Request.java",
                      gen_request_record(pkg_full, domain_name)))
        files.append((main_java / "api" / "dto" / f"{domain_name}Response.java",
                      gen_response_record(pkg_full, domain_name)))

    # ── Outbound ports (repository interfaces) ──────────────────────────────────
    all_domain_types = meta.domain_aggregates + meta.domain_entities
    for name in all_domain_types:
        files.append((main_java / "application" / "port" / "out" / f"{name}RepositoryPort.java",
                      gen_repository_port(pkg_full, name)))

    # ── Outbound ports (declared in generator-config.yml: outbound_ports) ───────
    for port_name in meta.outbound_ports:
        files.append((main_java / "application" / "port" / "out" / f"{port_name}.java",
                      gen_outbound_port_stub(pkg_full, port_name)))

    # ── JMS event producers ──────────────────────────────────────────────────────
    for event_fqn in meta.published_events:
        event_simple = event_fqn.split(".")[-1]
        files.append((main_java / "infrastructure" / "messaging" / "producer" / f"{event_simple}Producer.java",
                      gen_event_producer(pkg_full, event_fqn)))

    # ── JMS consumers ────────────────────────────────────────────────────────────
    for consumed in meta.consumed_events:
        cls = consumed.get("consumer_class", "")
        if cls:
            files.append((main_java / "infrastructure" / "messaging" / "consumer" / f"{cls}.java",
                          gen_jms_consumer(pkg_full, consumed)))

    # ── FeignClient stubs ────────────────────────────────────────────────────────
    for fc in meta.feign_clients:
        fc_name = fc.get("name", "")
        if fc_name:
            files.append((main_java / "infrastructure" / "clients" / f"{fc_name}.java",
                          gen_feign_client_stub(pkg_full, fc)))

    # ── JPA layer (entity, repo, adapter) ───────────────────────────────────────
    for name in all_domain_types:
        files.append((main_java / "infrastructure" / "persistence" / "entity" / f"{name}JpaEntity.java",
                      gen_jpa_entity(pkg_full, name)))
        files.append((main_java / "infrastructure" / "persistence" / "repository" / f"{name}JpaRepository.java",
                      gen_jpa_repository(pkg_full, name)))
        files.append((main_java / "infrastructure" / "persistence" / "adapter" / f"{name}RepositoryAdapter.java",
                      gen_persistence_adapter(pkg_full, name)))

    return files


# ── Sub-generators ────────────────────────────────────────────────────────────

def _validate_config_vs_sql(meta: ToolMeta, sql_path: Path) -> None:
    """B1 gate: reporta divergência entre agregados declarados no generator-config.yml
    e as tabelas do V1 SQL. Informativo (não aborta) — torna a deriva visível em vez
    de silenciosa. Normaliza removendo underscores/case (base_conhecimento ~ BaseConhecimento)."""
    def _norm(s: str) -> str:
        return s.replace("_", "").lower()

    declared = meta.domain_aggregates + meta.domain_entities
    if not declared:
        return
    sql_text = sql_path.read_text(encoding="utf-8")
    tables = re.findall(
        r"CREATE TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\w+\.)?(\w+)",
        sql_text, re.IGNORECASE)
    # ProcessedEvent (idempotência) é infra do framework — não é agregado de domínio.
    table_norms = {_norm(t) for t in tables} - {_norm("processed_event")}
    declared_norms = {_norm(d) for d in declared}

    missing_table = [d for d in declared if _norm(d) not in table_norms]
    missing_decl = [t for t in tables if _norm(t) not in declared_norms
                    and _norm(t) != _norm("processed_event")]

    if missing_table or missing_decl:
        print(f"\n  [GATE config↔SQL] divergência detectada para {meta.service}:")
        if missing_table:
            print(f"    [WARN] agregado(s) declarado(s) em generator-config.yml sem tabela no V1 SQL: "
                  f"{', '.join(missing_table)}")
            print(f"           → o entity-gen não terá DDL p/ esses agregados; a layer base "
                  f"(stub) permanece, mas confira se o data-model.md cobre o agregado.")
        if missing_decl:
            print(f"    [INFO] tabela(s) no V1 SQL sem agregado declarado em generator-config.yml: "
                  f"{', '.join(missing_decl)}")
            print(f"           → o entity-gen vai gerar a layer completa p/ essas tabelas "
                  f"(sem layer base canônica concorrente).")
    else:
        print(f"\n  [GATE config↔SQL] OK — {len(declared_norms)} agregado(s) declarado(s) "
              f"alinhado(s) com as tabelas do V1 SQL.")


def _invoke_subgen(label: str, cmd: list[str], echo_prefixes: tuple[str, ...],
                   continue_on_error: bool) -> None:
    """Run a chained sub-generator. A3 (workflow-improvements.md): FAIL-FAST por padrão —
    se o sub-gerador retorna != 0, aborta o scaffold (em vez de só [WARN] e seguir com um
    scaffold parcial silencioso). `--continue-on-error` restaura o comportamento tolerante."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        s = line.strip()
        if any(s.startswith(p) for p in echo_prefixes):
            print(f"         {s}")
    if result.returncode != 0:
        for line in result.stderr.splitlines()[:8]:
            print(f"         {line}")
        msg = f"{label} retornou {result.returncode}"
        if continue_on_error:
            print(f"  [WARN] {msg} — continuando (--continue-on-error); scaffold pode ficar parcial.")
        else:
            print(f"  [ERRO] {msg}. Abortando o scaffold (A3 fail-fast).")
            print(f"         Corrija a causa, ou use --continue-on-error para tolerar e seguir parcial.")
            sys.exit(1)


def run_subgenerators(meta: ToolMeta, dry_run: bool, force: bool = False,
                      continue_on_error: bool = False) -> None:
    """Chama migration, entity e BDD generators com --spec-dir apontando para docs da tool.

    Pulado para gateway/registry: esses serviços não têm domínio próprio (sem JPA,
    sem aggregates, sem migrations). Migration/entity/bdd não se aplicam.
    """
    if meta.service_type in ("gateway", "registry"):
        if not dry_run:
            print(f"  [INFO] service_type={meta.service_type} — pulando migration/entity/bdd generators")
        return

    scripts = ROOT / "scripts"
    spec_dir = str(meta.service_docs_dir)
    pkg_full = f"{PKG_BASE}.{meta.package_suffix}"

    # 1. Migration: gera DDL real a partir de data-model.md
    dm = meta.service_docs_dir / "contracts" / "data-model.md"
    if dm.exists():
        cmd = [sys.executable, str(scripts / "be-migration-generator.py"),
               meta.service, "--spec-dir", spec_dir, "--force"]
        if dry_run:
            print(f"  [DRY] be-migration-generator.py {meta.service} --spec-dir <tool-docs>")
        else:
            print(f"\n  [SPEC] Gerando DDL para {meta.service}...")
            _invoke_subgen("migration-generator", cmd, ("[",), continue_on_error)
    else:
        if not dry_run:
            print(f"  [INFO] data-model.md não encontrado — migration placeholder mantido")

    # 2. Entity: gera JPA entities, ports, adapters, controllers
    sql_path = (SERVICES_DIR / meta.service / "src" / "main" / "resources"
                / "db" / "migration" / "V1__create_initial_schema.sql")

    # B1 gate (docs/architecture/shared/workflow-improvements.md): validar
    # config↔SQL ANTES de encadear o entity-generator. Reporta divergência entre
    # os agregados declarados em generator-config.yml e as tabelas do V1 SQL, em
    # vez de deixar a divergência passar silenciosa (que antes virava layer
    # duplicada / órfã). Informativo — não aborta o scaffold.
    if sql_path.exists():
        _validate_config_vs_sql(meta, sql_path)

    if sql_path.exists() and "CREATE TABLE" in sql_path.read_text(encoding="utf-8").upper():
        cmd = [sys.executable, str(scripts / "be-entity-generator.py"),
               meta.service, "--spec-dir", spec_dir, "--package", pkg_full,
               *(["--force"] if force else [])]
        if dry_run:
            print(f"  [DRY] be-entity-generator.py {meta.service} --spec-dir <tool-docs>")
        else:
            print(f"\n  [SPEC] Gerando entidades JPA, ports, adapters e controllers...")
            _invoke_subgen("entity-generator", cmd,
                           ("[+]", "[>]", "[=]", "Use cases", "Tables:", "Package:"), continue_on_error)
    else:
        if not dry_run:
            print(f"  [INFO] V1 SQL sem DDL real — entity generation pulada")

    # 3. BDD: copia .feature + gera step stubs
    features_dir = meta.service_docs_dir / "tests" / "cucumber"
    if features_dir.exists() and list(features_dir.glob("*.feature")):
        cmd = [sys.executable, str(scripts / "be-bdd-generator.py"),
               meta.service, "--spec-dir", spec_dir, "--package", pkg_full]
        if dry_run:
            print(f"  [DRY] be-bdd-generator.py {meta.service} --spec-dir <tool-docs>")
        else:
            print(f"\n  [SPEC] Copiando features e gerando step stubs...")
            _invoke_subgen("bdd-generator", cmd, ("[",), continue_on_error)
    else:
        if not dry_run:
            print(f"  [INFO] Nenhum .feature encontrado em tests/cucumber")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()
    parser = argparse.ArgumentParser(
        description="Gera projeto Spring Boot para project tool a partir da documentação.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Exemplos:
              python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec
              python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec --dry-run
              python scripts/be-module-generator.py --docs docs/architecture/backend/services/rtc-service-spec --port 8090 --force
        """),
    )
    parser.add_argument("--docs", required=True,
                        help="Diretório de docs da tool (relativo à raiz do projeto ou absoluto)")
    parser.add_argument("--port", type=int,
                        help="Porta HTTP (padrão: detectado do setup-local.md, fallback 8090)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que seria gerado sem criar arquivos")
    parser.add_argument("--no-spec", action="store_true",
                        help="Apenas scaffold base (sem migration, entidades, BDD)")
    parser.add_argument("--force", action="store_true",
                        help="Sobrescreve arquivos existentes")
    parser.add_argument("--continue-on-error", action="store_true",
                        help="Tolera falha de sub-gerador (migration/entity/bdd) e segue com "
                             "scaffold parcial. Padrão: fail-fast (aborta no primeiro erro).")
    args = parser.parse_args()

    docs_path = Path(args.docs)
    if not docs_path.is_absolute():
        docs_path = ROOT / docs_path

    print(f"\n[be-module-generator] Lendo docs: {docs_path}")

    try:
        meta = derive_meta(docs_path, args.port)
    except ValueError as e:
        print(f"\n[ERRO] {e}")
        sys.exit(1)

    pkg_full = f"{PKG_BASE}.{meta.package_suffix}"
    svc_root = SERVICES_DIR / meta.service

    print(f"[be-module-generator] Serviço     : {meta.service}")
    print(f"[be-module-generator] Tipo        : {meta.service_type}")
    print(f"[be-module-generator] Pacote      : {pkg_full}")
    print(f"[be-module-generator] App class   : {meta.app_class}")
    print(f"[be-module-generator] Porta       : {meta.port}")
    print(f"[be-module-generator] Issue prefix: {meta.issue_prefix}")
    print(f"[be-module-generator] Vertex AI   : {meta.has_vertex_ai}")
    print(f"[be-module-generator] GCS         : {meta.has_gcs}")
    print(f"[be-module-generator] Output      : {svc_root.relative_to(ROOT)}")
    print()

    files = build_file_manifest(meta)

    created = skipped = 0
    for path, content in files:
        rel = path.relative_to(ROOT)
        if args.dry_run:
            print(f"  [DRY] {rel}")
            continue
        if path.exists() and not args.force:
            print(f"  [SKIP] {rel}")
            skipped += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"  [+] {rel}")
        created += 1

    if not args.dry_run:
        print(f"\n  Criados: {created}  |  Pulados: {skipped}")

    if not args.no_spec:
        run_subgenerators(meta, dry_run=args.dry_run, force=args.force,
                          continue_on_error=args.continue_on_error)

    if not args.dry_run:
        print(f"\n[be-module-generator] Scaffold completo. Próximos passos:")
        print(f"  1. Adicionar :{meta.service} ao settings.gradle.kts da raiz")

        # A1/A2 (workflow-improvements.md): preflight de toolchain ANTES de sugerir
        # gates Gradle. Se o toolchain estiver ausente, os gates são marcados como
        # DIFERIDOS com o comando de recuperação — em vez de o usuário descobrir o
        # "command not found" só ao rodar. Registre os diferidos no ledger do
        # master-plan e rode `python scripts/be-gates-replay.py` quando houver toolchain.
        try:
            from preflight import plan_gates  # type: ignore
            gp = plan_gates(["compileJava", "architectureCheck"], service=meta.service)
            deferred = [g for g in gp if not g["available"]]
            if deferred:
                print(f"  2. ⚠️  Toolchain ausente — gates pós-scaffold DIFERIDOS "
                      f"(tool '{deferred[0]['tool']}' não encontrado):")
                for g in gp:
                    print(f"        - {g['gate']}: {g['recover']}")
                print(f"     Registre no ledger do master-plan e rode depois: "
                      f"python scripts/be-gates-replay.py --run --update")
            else:
                print(f"  2. ./gradlew :{meta.service}:build")
                print(f"  3. ./gradlew :{meta.service}:architectureCheck")
        except Exception:
            print(f"  2. ./gradlew :{meta.service}:build")
            print(f"  3. ./gradlew :{meta.service}:architectureCheck")

        if meta.service_type == "standard":
            print(f"  4. Implementar cases de uso em application/service/")
        elif meta.service_type == "gateway":
            print(f"  4. Definir rotas em src/main/resources/application.yml (spring.cloud.gateway.routes)")
        else:  # registry
            print(f"  4. Subir o registry PRIMEIRO; demais serviços dependem dele para descoberta")


if __name__ == "__main__":
    main()
