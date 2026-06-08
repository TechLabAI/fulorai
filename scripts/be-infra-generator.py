#!/usr/bin/env python3
"""
be-infra-generator.py — Generic infrastructure generator.

Gera sem IA:
  INFRA-001: GitHub Actions CI pipeline (matrix por serviço)
  INFRA-002: docker-compose.dev.yml + root settings.gradle.kts (multi-project)
  GWY-003:   routing config do API Gateway em application.yml

Uso:
    python scripts/be-infra-generator.py <TARGET>

Targets:
    ci          → INFRA-001: .github/workflows/ci.yml
    compose     → INFRA-002: docker/docker-compose.dev.yml
    root-gradle → INFRA-002: settings.gradle.kts (root multi-project)
    gateway     → GWY-003:   backend/services/<gateway>/src/main/resources/application.yml (rotas)
    all         → todos acima
    --dry-run   → exibe o conteúdo sem criar arquivos
"""

import argparse
import sys
import textwrap
from pathlib import Path

# Project context (loaded once at module import)
try:
    from be_context_helper import load_project_context
    _CTX = load_project_context()
except (ImportError, Exception):
    _CTX = None

PROJECT_NAME = _CTX.project_name if _CTX else "project"
PKG_BASE = _CTX.package_base if _CTX else "com.project"
NETWORK_NAME = f"{PROJECT_NAME}-net"
DB_NAME = PROJECT_NAME
DB_USER = PROJECT_NAME
DB_PASS = PROJECT_NAME
KEYCLOAK_REALM = PROJECT_NAME


ROOT = Path(__file__).resolve().parent.parent

# ── Catálogo de serviços (carregado dinamicamente do project-context.json) ────

def _build_services_from_context() -> list[dict]:
    """Build SERVICES list from project context modules registry.

    Maps module dict entries to the format used by infra generators:
      {"name": "<backend-service>", "port": <port>, "pkg": "<package-suffix>", "type": "<type>"}

    Module types are inferred from prefix conventions:
      - GWY → gateway (port 8080)
      - REG → registry (port 8761)
      - MIG → standard but with type="migrations" (no port; one-shot)
      - others → standard (port assigned by index starting at 8081)
    """
    if not _CTX or not _CTX.modules:
        # Fallback minimal set (so infra generator still works in workspace tests)
        return [
            {"name": f"{PROJECT_NAME}-api-gateway",      "port": 8080, "pkg": "gateway",  "type": "gateway"},
            {"name": f"{PROJECT_NAME}-service-registry", "port": 8761, "pkg": "registry", "type": "registry"},
        ]

    result = []
    standard_port = 8081
    for mod in _CTX.modules:
        prefix = mod.get("prefix", "")
        svc_name = mod.get("backendService") or f"{prefix.lower()}-service"
        pkg = prefix.lower()
        if prefix == "GWY":
            result.append({"name": svc_name, "port": 8080, "pkg": pkg, "type": "gateway"})
        elif prefix == "REG":
            result.append({"name": svc_name, "port": 8761, "pkg": pkg, "type": "registry"})
        elif prefix == "MIG":
            result.append({"name": svc_name, "port": 0, "pkg": pkg, "type": "migrations"})
        else:
            result.append({"name": svc_name, "port": standard_port, "pkg": pkg, "type": "standard"})
            standard_port += 1
    return result


SERVICES = _build_services_from_context()

STANDARD_SERVICES = [s for s in SERVICES if s["type"] == "standard"]



def _service_name(svc_type: str) -> str:
    """Find service name by type (gateway/registry/migrations) in SERVICES."""
    for s in SERVICES:
        if s["type"] == svc_type:
            return s["name"]
    return f"{PROJECT_NAME}-{svc_type}"


# ── INFRA-001: GitHub Actions CI ───────────────────────────────────────────────

def gen_ci_workflow() -> str:
    service_names = [s["name"] for s in SERVICES]
    matrix = "\n          - ".join(service_names)

    return textwrap.dedent(f"""\
        # INFRA-001: CI pipeline
        # Executa build + test para cada serviço em paralelo (matrix strategy).
        # ArchUnit é executado como parte de ./gradlew test.

        name: CI

        on:
          push:
            branches: [ main, dev, "feature/**", "fix/**" ]
          pull_request:
            branches: [ main, dev ]

        jobs:
          build-and-test:
            name: Build & Test (${{{{ matrix.service }}}})
            runs-on: ubuntu-latest

            strategy:
              fail-fast: false
              matrix:
                service:
                  - {matrix}

            steps:
              - name: Checkout
                uses: actions/checkout@v4

              - name: Set up Java 21
                uses: actions/setup-java@v4
                with:
                  java-version: '21'
                  distribution: 'temurin'
                  cache: gradle

              - name: Grant execute permission for gradlew
                run: chmod +x backend/services/${{{{ matrix.service }}}}/gradlew || true

              - name: Build & test (standalone)
                working-directory: backend/services/${{{{ matrix.service }}}}
                run: ./gradlew test --no-daemon --info
                env:
                  SPRING_PROFILES_ACTIVE: default

              - name: Upload test results
                if: always()
                uses: actions/upload-artifact@v4
                with:
                  name: test-results-${{{{ matrix.service }}}}
                  path: backend/services/${{{{ matrix.service }}}}/build/reports/tests/

          architecture-check:
            name: ArchUnit (${{{{ matrix.service }}}})
            runs-on: ubuntu-latest
            needs: build-and-test

            strategy:
              fail-fast: true
              matrix:
                service:
                  - {matrix}

            steps:
              - name: Checkout
                uses: actions/checkout@v4

              - name: Set up Java 21
                uses: actions/setup-java@v4
                with:
                  java-version: '21'
                  distribution: 'temurin'
                  cache: gradle

              - name: Run ArchUnit rules
                working-directory: backend/services/${{{{ matrix.service }}}}
                run: ./gradlew test --tests "*.architecture.*" --no-daemon
                env:
                  SPRING_PROFILES_ACTIVE: default
    """)


# ── INFRA-002: docker-compose.dev.yml ─────────────────────────────────────────

def gen_docker_compose() -> str:
    service_blocks = []
    for svc in STANDARD_SERVICES:
        name = svc["name"]
        port = svc["port"]
        block = textwrap.dedent(f"""\
          {name}:
            build:
              context: ../backend/services/{name}
              dockerfile: Dockerfile
            ports:
              - "{port}:{port}"
            environment:
              SPRING_PROFILES_ACTIVE: default
              DB_URL: jdbc:postgresql://postgres:5432/{DB_NAME}
              DB_USER: {DB_USER}
              DB_PASS: {DB_PASS}
              KEYCLOAK_ISSUER_URI: http://keycloak:8180/realms/{KEYCLOAK_REALM}
              EUREKA_URI: http://{_service_name("registry")}:8761/eureka
            depends_on:
              postgres:
                condition: service_healthy
              activemq:
                condition: service_healthy
              {_service_name("registry")}:
                condition: service_started
            networks:
              - {NETWORK_NAME}
        """)
        service_blocks.append(block)

    svc_yaml = "\n".join(service_blocks)

    return textwrap.dedent(f"""\
        # INFRA-002: docker-compose.dev.yml (ambiente de desenvolvimento local)
        # Inclui: PostgreSQL 15, ActiveMQ Artemis, Keycloak, Eureka Registry e todos os serviços.
        #
        # Uso:
        #   docker compose -f docker/docker-compose.dev.yml up -d
        #   docker compose -f docker/docker-compose.dev.yml down -v

        services:

          # ── Infraestrutura ────────────────────────────────────────────────────

          postgres:
            image: postgres:16-alpine
            ports:
              - "5432:5432"
            environment:
              POSTGRES_DB: {DB_NAME}
              POSTGRES_USER: {DB_USER}
              POSTGRES_PASSWORD: {DB_PASS}
            volumes:
              - postgres-data:/var/lib/postgresql/data
              - ./init-scripts/postgres:/docker-entrypoint-initdb.d
            healthcheck:
              test: ["CMD-SHELL", "pg_isready -U {DB_USER} -d {DB_NAME}"]
              interval: 5s
              timeout: 5s
              retries: 10
            networks:
              - {NETWORK_NAME}

          activemq:
            image: apache/activemq-artemis:2.31.0
            ports:
              - "8161:8161"   # Web console
              - "61616:61616" # OpenWire / JMS
              - "5672:5672"   # AMQP
            environment:
              ARTEMIS_USER: artemis
              ARTEMIS_PASSWORD: artemis
            healthcheck:
              test: ["CMD", "curl", "-f", "http://localhost:8161/console"]
              interval: 10s
              timeout: 5s
              retries: 10
            networks:
              - {NETWORK_NAME}

          keycloak:
            image: quay.io/keycloak/keycloak:24.0
            command: start-dev
            ports:
              - "8180:8080"
            environment:
              KEYCLOAK_ADMIN: admin
              KEYCLOAK_ADMIN_PASSWORD: admin
              KC_DB: dev-file
            networks:
              - {NETWORK_NAME}

          # ── Service Registry ──────────────────────────────────────────────────

          {_service_name("registry")}:
            build:
              context: ../backend/services/{_service_name("registry")}
              dockerfile: Dockerfile
            ports:
              - "8761:8761"
            networks:
              - {NETWORK_NAME}

          # ── API Gateway ───────────────────────────────────────────────────────

          {_service_name("gateway")}:
            build:
              context: ../backend/services/{_service_name("gateway")}
              dockerfile: Dockerfile
            ports:
              - "8080:8080"
            environment:
              KEYCLOAK_ISSUER_URI: http://keycloak:8180/realms/{KEYCLOAK_REALM}
              EUREKA_URI: http://{_service_name("registry")}:8761/eureka
            depends_on:
              - {_service_name("registry")}
            networks:
              - {NETWORK_NAME}

          # ── Serviços de Domínio ───────────────────────────────────────────────

        {textwrap.indent(svc_yaml, '  ')}

        volumes:
          postgres-data:

        networks:
          {NETWORK_NAME}:
            driver: bridge
    """)


# ── INFRA-002: Root settings.gradle.kts (multi-project) ────────────────────────

def gen_root_settings_gradle() -> str:
    includes = "\n".join(
        f'include("services:java:{s["name"]}")'
        for s in SERVICES
    )

    return textwrap.dedent(f"""\
        // Root settings.gradle.kts (INFRA-002)
        // Define o build multi-projeto Gradle.
        // Cada subprojeto pode ser buildado standalone OU via raiz:
        //   ./gradlew :services:java:<example-service>:build

        rootProject.name = "be-{PROJECT_NAME}"

        pluginManagement {{
            repositories {{
                gradlePluginPortal()
                mavenCentral()
            }}
            plugins {{
                id("org.springframework.boot") version "3.5.11"
                id("io.spring.dependency-management") version "1.1.7"
            }}
        }}

        {includes}
    """)


# ── GWY-003: Gateway routing config ───────────────────────────────────────────

def gen_gateway_routing_yml() -> str:
    route_blocks = []
    for svc in STANDARD_SERVICES:
        name = svc["name"]
        port = svc["port"]
        # Convert service name to route prefix (e.g. identity-session-service → /api/v1/identity)
        prefix = name.replace("-service", "").replace("-capability", "")
        block = textwrap.dedent(f"""\
            - id: {name}
              uri: lb://{name}
              predicates:
                - Path=/api/v1/{prefix}/**
              filters:
                - StripPrefix=0
                - AddRequestHeader=X-Gateway-Service, {_service_name("gateway")}
        """)
        route_blocks.append(block)

    routes_yaml = "\n        ".join(route_blocks)

    return textwrap.dedent(f"""\
        # GWY-003: Routing configuration — {_service_name("gateway")}
        # Gerado por be-infra-generator.py — ajustar prefixos de path conforme a spec de cada serviço.
        #
        # Cada rota usa Eureka service discovery (lb://<service-name>).
        # CorrelationId é adicionado automaticamente pelo GatewayFilterFactory.

        spring:
          application:
            name: {_service_name("gateway")}
          cloud:
            gateway:
              default-filters:
                - AddRequestHeader=X-Gateway-Service, {_service_name("gateway")}
                - DedupeResponseHeader=Access-Control-Allow-Credentials Access-Control-Allow-Origin
              routes:
                {routes_yaml}
          security:
            oauth2:
              resourceserver:
                jwt:
                  issuer-uri: ${{KEYCLOAK_ISSUER_URI:http://localhost:8180/realms/{KEYCLOAK_REALM}}}

        server:
          port: 8080

        eureka:
          client:
            service-url:
              defaultZone: ${{EUREKA_URI:http://localhost:8761/eureka}}
          instance:
            prefer-ip-address: true

        management:
          endpoints:
            web:
              exposure:
                include: health,prometheus,gateway
          endpoint:
            health:
              show-details: always

        logging:
          pattern:
            console: "%d{{HH:mm:ss}} %-5level [%X{{correlationId}}] [%X{{tenantId}}] %logger{{36}} - %msg%n"
    """)


# ── Orquestrador ───────────────────────────────────────────────────────────────

TARGETS = {
    "ci": {
        "path": ROOT / ".github" / "workflows" / "ci.yml",
        "gen": gen_ci_workflow,
        "desc": "INFRA-001: GitHub Actions CI pipeline",
    },
    "compose": {
        "path": ROOT / "docker" / "docker-compose.dev.yml",
        "gen": gen_docker_compose,
        "desc": "INFRA-002: docker-compose.dev.yml",
    },
    "root-gradle": {
        "path": ROOT / "settings.gradle.kts",
        "gen": gen_root_settings_gradle,
        "desc": "INFRA-002: root settings.gradle.kts (multi-project)",
    },
    "gateway": {
        "path": ROOT / "backend" / "services" / _service_name("gateway") / "src" / "main" / "resources" / "application.yml",
        "gen": gen_gateway_routing_yml,
        "desc": "GWY-003: gateway routing config",
    },
}


def write_target(key: str, dry_run: bool) -> None:
    target = TARGETS[key]
    path: Path = target["path"]
    content: str = target["gen"]()

    status = "EXISTS" if path.exists() else "NEW"
    print(f"\n  [{status}] {target['desc']}")
    print(f"         {path.relative_to(ROOT)}")

    if dry_run:
        print()
        print(textwrap.indent(content[:800] + ("..." if len(content) > 800 else ""), "    "))
        return

    if path.exists():
        print("  [SKIP] Pulado (ja existe). Use --force para sobrescrever.")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("  [OK]   Criado.")


def _build_parser() -> argparse.ArgumentParser:
    choices = list(TARGETS.keys()) + ["all"]
    parser = argparse.ArgumentParser(
        prog="be-infra-generator.py",
        description="Generic infrastructure generator (CI, compose, root gradle, gateway).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/be-infra-generator.py ci\n"
            "  python scripts/be-infra-generator.py compose root-gradle --dry-run\n"
            "  python scripts/be-infra-generator.py all --force\n"
        ),
    )
    parser.add_argument(
        "targets",
        nargs="+",
        choices=choices,
        metavar="TARGET",
        help=f"One or more targets to generate. Options: "
             f"{', '.join(choices)}. 'all' expands to every target.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated content without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files.",
    )
    return parser


def main():
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()

    parser = _build_parser()
    args = parser.parse_args()

    # D-090: expand "all" to every target while preserving order/dedup.
    if "all" in args.targets:
        target_keys = list(TARGETS.keys())
    else:
        # Preserve user order; dedup conservatively.
        seen: set[str] = set()
        target_keys = [t for t in args.targets if not (t in seen or seen.add(t))]

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}be-infra-generator.py")
    print(f"  Targets: {', '.join(target_keys)}")

    for key in target_keys:
        # --force: remove existing file so write_target creates it.
        if args.force and TARGETS[key]["path"].exists() and not args.dry_run:
            TARGETS[key]["path"].unlink()
        write_target(key, args.dry_run)

    print()


if __name__ == "__main__":
    main()
