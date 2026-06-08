#!/usr/bin/env python3
"""
be-scaffold.py — Deterministic Java scaffold generator.

Parseia plan-<ISSUE_ID>.md e cria todos os arquivos listados na seção
"## 2. Arquivos a criar" com placeholders por camada.

Uso:
    python scripts/be-scaffold.py <ISSUE_ID>
    python scripts/be-scaffold.py APS-004

Economia: elimina ~10.000-20.000 tokens de LLM por issue.
"""

import re
import sys
from pathlib import Path

try:
    from be_context_helper import load_project_context
    _CTX = load_project_context()
except (ImportError, Exception):
    _CTX = None

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
ISSUES_DIR = ROOT / "docs" / "architecture" / "backend" / "issues"
PLANS_DIR = ROOT / "docs" / "architecture" / "backend" / "plans"
SERVICES_DIR = ROOT / "backend" / "services"
SPECS_DIR = ROOT / "docs" / "architecture" / "backend" / "services"

# ── Spec Context Parsing ───────────────────────────────────────────────────────


def find_spec_dir(service: str) -> Path | None:
    """Return the spec directory for a service, or None if not found."""
    candidate = SPECS_DIR / f"{service}-spec"
    return candidate if candidate.exists() else None


def parse_data_model(spec_dir: Path) -> dict:
    """Parse contracts/data-model.md → {table_name: [field_name, ...]}."""
    dm = spec_dir / "contracts" / "data-model.md"
    if not dm.exists():
        return {}
    tables = {}
    current = None
    for line in dm.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("### "):
            current = s[4:].strip()
            tables[current] = []
        elif s.startswith("- ") and current:
            field = s[2:].strip()
            # Skip description lines — must look like a plain snake_case identifier
            if re.match(r"^[a-z][a-z0-9_]*$", field):
                tables[current].append(field)
    return tables


def parse_api_contract(spec_dir: Path) -> list:
    """Parse contracts/api-contract.md → [{method, path, description}, ...]."""
    ac = spec_dir / "contracts" / "api-contract.md"
    if not ac.exists():
        return []
    endpoints = []
    for line in ac.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        m = re.match(r"^###\s+(GET|POST|PUT|PATCH|DELETE)\s+(/[\w/{}\-.,]+)", s)
        if m:
            endpoints.append({"method": m.group(1), "path": m.group(2), "description": ""})
        elif endpoints and s and not s.startswith("#") and not endpoints[-1]["description"]:
            endpoints[-1]["description"] = s
    return endpoints


def parse_event_contracts(spec_dir: Path) -> dict:
    """Parse contracts/event-contracts.md → {published: [...], consumed: [...]}."""
    ec = spec_dir / "contracts" / "event-contracts.md"
    if not ec.exists():
        return {"published": [], "consumed": []}
    result = {"published": [], "consumed": []}
    section = None
    for line in ec.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if "Eventos Publicados" in s:
            section = "published"
        elif "Eventos Consumidos" in s:
            section = "consumed"
        elif s.startswith("### ") and section:
            result[section].append(s[4:].strip())
    return result


def load_spec_context(service: str) -> dict:
    """Load the full spec context for a service. Returns empty context on failure."""
    empty = {"tables": {}, "endpoints": [], "events": {"published": [], "consumed": []}}
    spec_dir = find_spec_dir(service)
    if not spec_dir:
        return empty
    return {
        "tables": parse_data_model(spec_dir),
        "endpoints": parse_api_contract(spec_dir),
        "events": parse_event_contracts(spec_dir),
    }


# ── Field helpers ──────────────────────────────────────────────────────────────

def snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def field_java_type(field: str) -> str:
    """Return the Java type for a data-model field name."""
    if field.endswith("_at"):
        return "OffsetDateTime"
    if field.endswith("_id"):
        return "UUID"
    if field.endswith("_version"):
        return "Long"
    return "String"


JAVA_IMPORTS_FOR_TYPE = {
    "OffsetDateTime": "import java.time.OffsetDateTime;",
    "UUID": "import java.util.UUID;",
}


def find_best_table(class_name: str, tables: dict) -> str | None:
    """Find the best-matching table name for a Java class name."""
    if not tables:
        return None
    # Strip common suffixes
    clean = re.sub(r"(Entity|Jpa|Record)$", "", class_name)
    snake = to_snake_case(clean)
    if snake in tables:
        return snake
    # Partial match — longest table name that is a substring
    candidates = [t for t in tables if t in snake or snake in t]
    return max(candidates, key=len) if candidates else None


def filter_endpoints_for_controller(class_name: str, endpoints: list) -> list:
    """Filter api-contract endpoints that are relevant to this controller class."""
    if not endpoints:
        return []
    # Extract meaningful words from controller class name (PascalCase → words)
    words_raw = re.sub(r"Controller$", "", class_name)
    words = [w.lower() for w in re.findall(r"[A-Z][a-z0-9]*", words_raw)]
    if not words:
        return endpoints
    # Keep endpoints where ANY word appears in the path
    filtered = [ep for ep in endpoints if any(w in ep["path"].replace("-", "").replace("_", "") for w in words)]
    return filtered if filtered else endpoints


def build_entity_body(table_name: str, fields: list, issue_id: str) -> tuple:
    """Return (imports_block, fields_block) for a JPA entity."""
    if not fields:
        return "", f"    // TODO: add columns from data-model — see issue {issue_id}\n"

    # Identify the primary key field (first *_id field)
    pk = next((f for f in fields if f.endswith("_id")), None)
    other = [f for f in fields if f != pk]

    used_types = set()
    pk_block = ""
    if pk:
        pk_type = field_java_type(pk)
        used_types.add(pk_type)
        pk_block = (
            f"    @Id\n"
            f"    @GeneratedValue(strategy = GenerationType.UUID)\n"
            f"    @Column(name = \"{pk}\")\n"
            f"    private {pk_type} {snake_to_camel(pk)};\n"
        )

    lines = [pk_block] if pk_block else []
    for f in other:
        jtype = field_java_type(f)
        used_types.add(jtype)
        lines.append(f"    @Column(name = \"{f}\")\n    private {jtype} {snake_to_camel(f)};")

    imports = "\n".join(
        sorted(JAVA_IMPORTS_FOR_TYPE[t] for t in used_types if t in JAVA_IMPORTS_FOR_TYPE)
    )
    return imports, "\n\n".join(lines) + "\n"


def build_record_components(fields: list, issue_id: str) -> tuple:
    """Return (imports_block, components_str) for a Java record."""
    if not fields:
        return "", f"    // TODO: add fields from data-model — see issue {issue_id}\n    String placeholder"

    used_types = set()
    components = []
    for f in fields:
        jtype = field_java_type(f)
        used_types.add(jtype)
        components.append(f"    {jtype} {snake_to_camel(f)}")

    imports = "\n".join(
        sorted(JAVA_IMPORTS_FOR_TYPE[t] for t in used_types if t in JAVA_IMPORTS_FOR_TYPE)
    )
    return imports, ",\n".join(components)


def build_controller_methods(endpoints: list, issue_id: str) -> str:
    """Return stub methods for a controller given endpoint list."""
    if not endpoints:
        return f"    // TODO: implement endpoints — see issue {issue_id}\n"

    lines = []
    for ep in endpoints:
        method, path, desc = ep["method"], ep["path"], ep.get("description", "")
        path_vars = re.findall(r"\{(\w+)\}", path)
        # Build params
        if method in ("POST", "PUT", "PATCH"):
            params = "@Valid @RequestBody Object request"
            if path_vars:
                params += ", " + ", ".join(f"@PathVariable String {v}" for v in path_vars)
        elif method == "DELETE":
            params = ", ".join(f"@PathVariable String {v}" for v in path_vars) if path_vars else ""
        else:  # GET
            params = ", ".join(f"@PathVariable String {v}" for v in path_vars) if path_vars else ""
        return_type = "ResponseEntity<Void>" if method == "DELETE" else "ResponseEntity<?>"
        # Method name: methodVerb + last two meaningful path segments
        segs = [s for s in path.split("/") if s and not s.startswith("{")]
        method_name_parts = segs[-2:] if len(segs) >= 2 else segs
        method_name = method.lower() + "".join(s.replace("-", " ").title().replace(" ", "") for s in method_name_parts)
        annotation = {"GET": "GetMapping", "POST": "PostMapping", "PUT": "PutMapping",
                      "PATCH": "PatchMapping", "DELETE": "DeleteMapping"}.get(method, "RequestMapping")
        if desc:
            lines.append(f"    // {desc}")
        lines.append(f"    @{annotation}(\"{path}\")")
        lines.append(f"    public {return_type} {method_name}({params}) {{")
        lines.append(f"        // TODO: implement — see issue {issue_id}")
        lines.append(f"        throw new UnsupportedOperationException(\"Not implemented yet\");")
        lines.append(f"    }}")
        lines.append("")
    return "\n".join(lines)

# ── Templates por camada ───────────────────────────────────────────────────────

TEMPLATES = {
    "domain/model": {
        "record": """\
package {package}.domain.model;

/**
 * Domain model — {class_name}.
 * Pure Java — zero Spring/JPA imports.
 *
 * @see plan-{issue_id}.md §2
 */
public record {class_name}(
    // TODO: add fields from spec — see issue {issue_id}
    String placeholder
) {{
    // TODO: add domain validations if needed
}}
""",
        "class": """\
package {package}.domain.model;

/**
 * Domain model — {class_name}.
 * Pure Java — zero Spring/JPA imports.
 *
 * @see plan-{issue_id}.md §2
 */
public class {class_name} {{

    // TODO: add fields from spec — see issue {issue_id}
    private String placeholder;

    public {class_name}() {{}}

    // TODO: add constructors, getters, domain behavior
}}
""",
    },
    "domain/service": """\
package {package}.domain.service;

import lombok.RequiredArgsConstructor;

/**
 * Domain service — {class_name}.
 * Pure business logic — zero Spring imports.
 *
 * @see plan-{issue_id}.md §6 (Acceptance Criteria)
 */
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: inject domain ports via constructor

    /**
     * TODO: implement — see issue {issue_id} Acceptance Criteria.
     */
    public Object execute(Object input) {{
        // TODO: implement
        throw new UnsupportedOperationException("Not implemented yet");
    }}
}}
""",
    "application/port/in": """\
package {package}.application.port.in;

/**
 * Input port (use case) — {class_name}.
 *
 * @see plan-{issue_id}.md §6
 */
public interface {class_name} {{

    // TODO: define use case method signature — see issue {issue_id}
    Object execute(Object command);
}}
""",
    "application/port/out": """\
package {package}.application.port.out;

import java.util.List;
import java.util.Optional;

/**
 * Output port (repository/client) — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
public interface {class_name} {{

    // TODO: define repository methods — see issue {issue_id}
}}
""",
    "application/service": """\
package {package}.application.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Application service (use case) — {class_name}.
 *
 * @see plan-{issue_id}.md §6 (Acceptance Criteria)
 */
@Service
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: inject ports via final fields

    @Transactional
    public Object execute(Object command) {{
        // TODO: TenantContextHolder.require(); — if tenant-scoped
        // TODO: implement — see issue {issue_id} Acceptance Criteria
        throw new UnsupportedOperationException("Not implemented yet");
    }}
}}
""",
    "infrastructure/persistence/entity": """\
package {package}.infrastructure.persistence.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

/**
 * JPA entity — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
@Entity
@Table(name = "{table_name}")
@Getter
@Setter
public class {class_name} {{

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    // TODO: add columns from domain model — see issue {issue_id}
}}
""",
    "infrastructure/persistence/repository": """\
package {package}.infrastructure.persistence.repository;

import {package}.infrastructure.persistence.entity.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * Spring Data JPA repository — {class_name}.
 */
@Repository
public interface {class_name} extends JpaRepository<{entity_name}, String> {{

    // TODO: add query methods as needed — see issue {issue_id}
}}
""",
    "infrastructure/persistence/adapter": """\
package {package}.infrastructure.persistence.adapter;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

/**
 * Persistence adapter — implements output port.
 *
 * @see plan-{issue_id}.md §2
 */
@Component
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: inject JPA repository

    // TODO: implement port methods — map domain <-> entity
    // throw new UnsupportedOperationException("Not implemented yet");
}}
""",
    "infrastructure/config": """\
package {package}.infrastructure.config;

import org.springframework.context.annotation.Configuration;

/**
 * Configuration — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
@Configuration
public class {class_name} {{

    // TODO: configure beans — see issue {issue_id}
}}
""",
    "infrastructure/security": """\
package {package}.infrastructure.security;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * Security / MDC interceptor — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
@Slf4j
@Component
public class {class_name} implements HandlerInterceptor {{

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {{
        // TODO: populate MDC (correlationId, tenantId, userId) — see issue {issue_id}
        return true;
    }}

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {{
        MDC.clear();
    }}
}}
""",
    "infrastructure/clients": """\
package {package}.infrastructure.clients;

import org.springframework.cloud.openfeign.FeignClient;

/**
 * Feign client — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
@FeignClient(name = "{feign_name}", url = "${{FEIGN_URL:http://localhost:8080}}")
public interface {class_name} {{

    // TODO: define Feign methods — see issue {issue_id}
}}
""",
    "infrastructure/messaging/producer": """\
package {package}.infrastructure.messaging.producer;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

/**
 * Event producer — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
@Component
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: inject KafkaTemplate<String, Object> (kafka) or JmsTemplate (artemis)
    // TODO: implement publish method — see issue {issue_id}
}}
""",
    "infrastructure/messaging/consumer": """\
package {package}.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * Event consumer — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: implement event consumer (@KafkaListener or @JmsListener) — see issue {issue_id}
}}
""",
    "api/controller": """\
package {package}.api.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

/**
 * REST controller — {class_name}.
 *
 * @see plan-{issue_id}.md §6 (Acceptance Criteria)
 */
@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: inject use case port

    // TODO: implement endpoints — see issue {issue_id}
}}
""",
    "api/dto": """\
package {package}.api.dto;

/**
 * DTO — {class_name}.
 *
 * @see plan-{issue_id}.md §2
 */
public record {class_name}(
    // TODO: add fields — see issue {issue_id}
    String placeholder
) {{}}
""",
    "api/exception": """\
package {package}.api.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * Exception handler — {class_name}.
 */
@RestControllerAdvice
public class {class_name} {{

    // TODO: add exception handlers — see issue {issue_id}
}}
""",
    "test/architecture": """\
package {package}.architecture;

import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition;

/**
 * ArchUnit rules — RULE-01 a RULE-08 (CLAUDE.md).
 * Executar: ./gradlew :{service}:test
 */
@AnalyzeClasses(packages = "{package}")
public class {class_name} {{

    // RULE-01: domain.* não importa org.springframework
    @ArchTest
    static final ArchRule rule01_domain_must_not_use_spring =
        ArchRuleDefinition.noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAPackage("org.springframework..");

    // RULE-02: domain.* não importa jakarta.persistence
    @ArchTest
    static final ArchRule rule02_domain_must_not_use_jpa =
        ArchRuleDefinition.noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAPackage("jakarta.persistence..");

    // RULE-04: api.* não depende de infrastructure.*
    @ArchTest
    static final ArchRule rule04_api_must_not_depend_on_infrastructure =
        ArchRuleDefinition.noClasses()
            .that().resideInAPackage("..api..")
            .should().dependOnClassesThat().resideInAPackage("..infrastructure..");

    // RULE-05: infrastructure.* não depende de api.*
    @ArchTest
    static final ArchRule rule05_infrastructure_must_not_depend_on_api =
        ArchRuleDefinition.noClasses()
            .that().resideInAPackage("..infrastructure..")
            .should().dependOnClassesThat().resideInAPackage("..api..");

    // RULE-06: @FeignClient apenas em infrastructure.clients
    @ArchTest
    static final ArchRule rule06_feign_only_in_clients =
        ArchRuleDefinition.noClasses()
            .that().resideOutsideOfPackage("..infrastructure.clients..")
            .and().areAnnotatedWith("org.springframework.cloud.openfeign.FeignClient")
            .should().exist();
}}
""",
    "test/integration/base": """\
package {package}.integration;

import org.junit.jupiter.api.Tag;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * Base class for integration tests.
 * Starts PostgreSQL 16-alpine via Testcontainers with container reuse.
 */
@Tag("integration")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@ActiveProfiles("test")
public abstract class {class_name} {{

    @Container
    static final PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName(TEST_DB)
            .withUsername("test")
            .withPassword("test")
            .withReuse(true);

    @DynamicPropertySource
    static void configureDataSource(DynamicPropertyRegistry registry) {{
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }}
}}
""",
    "test/integration/smoke": """\
package {package}.integration;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Smoke test — Spring context loads without errors.
 * @see issue {issue_id} — AC: ApplicationContext não é null
 */
class {class_name} extends BaseIntegrationTest {{

    @Autowired
    private ApplicationContext context;

    @Test
    void contextLoads() {{
        assertThat(context).isNotNull();
    }}
}}
""",
    "test/unit": """\
package {package}.unit;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;

/**
 * Unit tests — {class_name}.
 *
 * @see issue {issue_id} — Acceptance Criteria + Edge Cases
 */
@Tag("unit")
class {class_name} {{

    // TODO: setup mocks and SUT

    @Test
    void shouldSatisfyAcceptanceCriteria() {{
        // TODO: implement — see issue {issue_id} AC #1
    }}

    @Test
    void shouldHandleEdgeCases() {{
        // TODO: implement — see issue {issue_id} Edge Cases
    }}
}}
""",
}

# ── Parser ─────────────────────────────────────────────────────────────────────


def parse_plan(plan_path: Path) -> dict:
    """Parse plan-<ID>.md and extract identity + files to create."""
    text = plan_path.read_text(encoding="utf-8")

    # Extract identity table
    identity = {}
    identity_match = re.search(r"## 1\. Identidade\s*\n\n\|[^\n]+\n\|[^\n]+\n((?:\|[^\n]+\n)+)", text)
    if identity_match:
        for line in identity_match.group(1).strip().split("\n"):
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2:
                identity[cols[0].lower()] = cols[1]

    # Extract files table
    files = []
    files_match = re.search(
        r"## 2\. Arquivos a criar\s*\n\n\|[^\n]+\n\|[^\n]+\n((?:\|[^\n]+\n)+)", text
    )
    if files_match:
        for line in files_match.group(1).strip().split("\n"):
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 4 and not cols[0].startswith("..."):
                files.append({
                    "path": cols[0].strip("`"),
                    "type": cols[1].strip("`"),
                    "layer": cols[2].strip("`"),
                    "description": cols[3],
                })

    return {
        "issue_id": identity.get("issue id", "UNKNOWN"),
        "service": identity.get("serviço", identity.get("service", "")),
        "package_base": identity.get("package base", ""),
        "gradle_project": identity.get("gradle project path", identity.get("gradle project", "")),
        "files": files,
    }


def detect_layer(file_path: str) -> str:
    """Detect the template layer from the file path."""
    path_lower = file_path.lower()

    # Resource files
    ext = Path(file_path).suffix.lower()
    if ext in (".yml", ".yaml", ".sql", ".feature", ".xml"):
        return f"resource/{ext.lstrip('.')}"

    # Test files
    if "/test/" in path_lower:
        if "architecturetest" in path_lower or "architecture/" in path_lower:
            return "test/architecture"
        if "baseintegration" in path_lower:
            return "test/integration/base"
        if "contextloads" in path_lower or "smoketest" in path_lower:
            return "test/integration/smoke"
        return "test/unit"

    layer_patterns = [
        ("domain/model", ["domain/model/"]),
        ("domain/service", ["domain/service/"]),
        ("application/port/in", ["application/port/in/", "port/in/"]),
        ("application/port/out", ["application/port/out/", "port/out/"]),
        ("application/service", ["application/service/"]),
        ("infrastructure/persistence/entity", ["persistence/entity/"]),
        ("infrastructure/persistence/repository", ["persistence/repository/"]),
        ("infrastructure/persistence/adapter", ["persistence/adapter/"]),
        ("infrastructure/clients", ["infrastructure/clients/"]),
        ("infrastructure/messaging/producer", ["messaging/producer/"]),
        ("infrastructure/messaging/consumer", ["messaging/consumer/"]),
        ("infrastructure/config", ["infrastructure/config/"]),
        ("infrastructure/security", ["infrastructure/security/"]),
        ("api/controller", ["api/controller/"]),
        ("api/dto", ["api/dto/"]),
        ("api/exception", ["api/exception/"]),
    ]

    for layer, patterns in layer_patterns:
        for pattern in patterns:
            if pattern in path_lower:
                return layer

    return "unknown"


def class_name_from_path(file_path: str) -> str:
    """Extract class name from file path."""
    return Path(file_path).stem


def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case for table names."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


_RESOURCE_STUBS = {
    "yml":     "# TODO: configure — see plan-{issue_id}.md §2\n# Description: {description}\n",
    "yaml":    "# TODO: configure — see plan-{issue_id}.md §2\n# Description: {description}\n",
    "sql":     "-- TODO: implement migration — see plan-{issue_id}.md §2\n-- Description: {description}\n",
    "feature": "# TODO: write Gherkin scenarios — see plan-{issue_id}.md §6\n# Feature: {description}\n",
    "xml":     "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!-- TODO: configure — see plan-{issue_id}.md §2 -->\n",
}


def generate_file(plan: dict, file_info: dict, spec_ctx: dict | None = None) -> str:
    """Generate file content from template, enriched with spec context where available."""
    layer = detect_layer(file_info["path"])
    class_name = class_name_from_path(file_info["path"])
    file_type = file_info.get("type", "class")
    issue_id = plan["issue_id"]
    package = plan["package_base"]
    ctx = spec_ctx or {"tables": {}, "endpoints": [], "events": {"published": [], "consumed": []}}

    # ── Resource files (yml, sql, feature, xml) ────────────────────────────────
    if layer.startswith("resource/"):
        ext = layer.split("/")[1]
        if ext == "sql":
            return _generate_sql_stub(plan, file_info, ctx)
        stub = _RESOURCE_STUBS.get(ext, "# TODO: see plan-{issue_id}.md §2\n")
        return stub.format(
            issue_id=issue_id,
            description=file_info.get("description", class_name_from_path(file_info["path"])),
        )

    # ── JPA Entity — inject real fields from data-model ────────────────────────
    if layer == "infrastructure/persistence/entity":
        table_name = find_best_table(class_name, ctx["tables"]) or to_snake_case(class_name.replace("Entity", ""))
        fields = ctx["tables"].get(table_name, [])
        extra_imports, fields_block = build_entity_body(table_name, fields, issue_id)
        imports_block = "import jakarta.persistence.*;\nimport lombok.Getter;\nimport lombok.Setter;"
        if extra_imports:
            imports_block += "\n" + extra_imports
        return f"""\
package {package}.infrastructure.persistence.entity;

{imports_block}

/**
 * JPA entity — {class_name}.
 * Table: {table_name}
 *
 * @see plan-{issue_id}.md §2
 */
@Entity
@Table(name = "{table_name}")
@Getter
@Setter
public class {class_name} {{

{fields_block}
}}
"""

    # ── Domain Model — inject real fields from data-model ──────────────────────
    if layer == "domain/model":
        table_name = find_best_table(class_name, ctx["tables"])
        if table_name and ctx["tables"].get(table_name):
            fields = ctx["tables"][table_name]
            extra_imports, components = build_record_components(fields, issue_id)
            imports_block = extra_imports + "\n" if extra_imports else ""
            if file_type == "record":
                return f"""\
package {package}.domain.model;

{imports_block}/**
 * Domain model — {class_name}.
 * Pure Java — zero Spring/JPA imports.
 *
 * @see plan-{issue_id}.md §2
 */
public record {class_name}(
{components}
) {{
    // TODO: add domain validations if needed
}}
"""
            else:
                # class variant
                field_lines = []
                for field in fields:
                    jtype = field_java_type(field)
                    field_lines.append(f"    private {jtype} {snake_to_camel(field)};")
                fields_str = "\n".join(field_lines)
                return f"""\
package {package}.domain.model;

{imports_block}/**
 * Domain model — {class_name}.
 * Pure Java — zero Spring/JPA imports.
 *
 * @see plan-{issue_id}.md §2
 */
public class {class_name} {{

{fields_str}

    public {class_name}() {{}}

    // TODO: add constructors, getters, domain behavior
}}
"""
        # Fall through to generic template when no matching table found

    # ── REST Controller — inject real endpoints ────────────────────────────────
    if layer == "api/controller":
        relevant = filter_endpoints_for_controller(class_name, ctx["endpoints"])
        methods_block = build_controller_methods(relevant, issue_id)
        return f"""\
package {package}.api.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

/**
 * REST controller — {class_name}.
 *
 * @see plan-{issue_id}.md §6 (Acceptance Criteria)
 */
@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: inject use case port

{methods_block}
}}
"""

    # ── Messaging Producer — inject published event names ─────────────────────
    if layer == "infrastructure/messaging/producer":
        published = ctx["events"].get("published", [])
        dest_hints = ("\n    // Destinations: " + ", ".join(published)) if published else ""
        broker = _CTX.events_broker if _CTX else "artemis"
        if broker == "kafka":
            return f"""\
package {package}.infrastructure.messaging.producer;

import lombok.RequiredArgsConstructor;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

/**
 * Kafka producer — {class_name}.{dest_hints}
 *
 * @see plan-{issue_id}.md §2
 */
@Component
@RequiredArgsConstructor
public class {class_name} {{

    private final KafkaTemplate<String, Object> kafkaTemplate;

    // TODO: implement publish method — see issue {issue_id}
    // TODO: topics: {", ".join(published) if published else "configure in application.yml"}
}}
"""
        return f"""\
package {package}.infrastructure.messaging.producer;

import lombok.RequiredArgsConstructor;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.stereotype.Component;

/**
 * JMS producer — {class_name}.{dest_hints}
 *
 * @see plan-{issue_id}.md §2
 */
@Component
@RequiredArgsConstructor
public class {class_name} {{

    private final JmsTemplate jmsTemplate;

    // TODO: implement publish method — see issue {issue_id}
    // TODO: destinations: {", ".join(published) if published else "configure in application.yml"}
}}
"""

    # ── Messaging Consumer — inject consumed event names ───────────────────────
    if layer == "infrastructure/messaging/consumer":
        consumed = ctx["events"].get("consumed", [])
        dest_hints = ("\n    // Listens to: " + ", ".join(consumed)) if consumed else ""
        broker = _CTX.events_broker if _CTX else "artemis"
        project_name = _CTX.project_name if _CTX else "project"
        if broker == "kafka":
            return f"""\
package {package}.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka consumer — {class_name}.{dest_hints}
 *
 * @see plan-{issue_id}.md §2
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: events consumed: {", ".join(consumed) if consumed else "configure in application.yml"}
    // @KafkaListener(topics = "topic_name", groupId = "{project_name}-consumer")
    // public void handle(String payload) {{ ... }}
}}
"""
        return f"""\
package {package}.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

/**
 * JMS consumer — {class_name}.{dest_hints}
 *
 * @see plan-{issue_id}.md §2
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {class_name} {{

    // TODO: events consumed: {", ".join(consumed) if consumed else "configure in application.yml"}
    // @JmsListener(destination = "${{jms.destination.QUEUE_NAME}}")
    // public void handle(Object event) {{ ... }}
}}
"""

    # ── Generic templates (fallback) ───────────────────────────────────────────
    template = TEMPLATES.get(layer)
    if template is None:
        return f"// TODO: scaffold for layer '{layer}' — see plan-{issue_id}.md\n"

    if isinstance(template, dict):
        template = template.get(file_type, template.get("class", list(template.values())[0]))

    service_name = plan.get("service", "")
    vars = {
        "package": package,
        "class_name": class_name,
        "issue_id": issue_id,
        "service": service_name,
        "table_name": to_snake_case(class_name.replace("Entity", "")),
        "entity_name": class_name.replace("JpaRepository", "Entity").replace("Repository", "Entity"),
        "feign_name": to_snake_case(class_name.replace("Client", "")),
    }
    return template.format(**vars)


def _generate_sql_stub(plan: dict, file_info: dict, ctx: dict) -> str:
    """Generate a SQL migration stub with table structure hints from data-model."""
    tables = ctx.get("tables", {})
    desc = file_info.get("description", "")
    issue_id = plan["issue_id"]

    header = f"-- Migration stub generated for {issue_id}\n-- Description: {desc}\n"
    if not tables:
        return header + "-- TODO: implement migration — see plan-{}.md §2\n".format(issue_id)

    lines = [header, "-- Data model summary (implement with be-migration-generator.py):"]
    for table, fields in tables.items():
        lines.append(f"-- Table: {table} ({', '.join(fields[:5])}{'...' if len(fields) > 5 else ''})")
    lines.append("")
    lines.append("-- TODO: run: python scripts/be-migration-generator.py " + plan.get("service", "<service>"))
    lines.append("-- to generate the full CREATE TABLE statements\n")
    return "\n".join(lines)


def resolve_file_path(plan: dict, relative_path: str) -> Path:
    """Resolve relative path from plan to absolute path.

    Handles three path conventions found in plans:
      1. Paths starting with 'src/'           → prepend service root
      2. Java source relative to package dir  → prepend src/main/java/<pkg_path>/
      3. Resource files (.yml, .sql, etc.)    → prepend src/main/resources/
      4. Test files starting with 'java/'     → prepend src/test/
      5. Root config files (settings.gradle)  → service root only
    """
    service = plan["service"]
    service_root = SERVICES_DIR / service
    pkg_path = plan["package_base"].replace(".", "/")

    # Already absolute-style from service root
    if relative_path.startswith("src/"):
        return service_root / relative_path

    # Test source files (from "Testes" table: java/.../Foo.java)
    if relative_path.startswith("java/"):
        return service_root / "src" / "test" / relative_path

    # Test resource files (resources/application-test.yml)
    if relative_path.startswith("resources/") and "test" in relative_path.lower():
        return service_root / "src" / "test" / relative_path

    # Resource files by extension
    ext = Path(relative_path).suffix.lower()
    if ext in (".yml", ".yaml", ".sql", ".feature", ".xml", ".properties"):
        return service_root / "src" / "main" / "resources" / relative_path

    # Java source files relative to package root
    if ext == ".java":
        return service_root / "src" / "main" / "java" / pkg_path / relative_path

    # Root-level config files (build.gradle.kts, Dockerfile, README.md, etc.)
    return service_root / relative_path


_USAGE = (
    "Usage: python scripts/be-scaffold.py <ISSUE_ID>\n"
    "Example: python scripts/be-scaffold.py APS-004\n"
    "\n"
    "Le plan-<ISSUE_ID>.md em docs/architecture/backend/plans/ e cria os\n"
    "arquivos listados na secao '## 2. Arquivos a criar'. Nao aceita flags -\n"
    "o primeiro argumento DEVE ser um ISSUE_ID (ex: APS-004, OBR-012)."
)


def main():
    from cli_utils import force_utf8_stdio, require_positional_argv
    force_utf8_stdio()

    # D-087: same argv hardening as be-file-guard (D-086). Previously
    # `be-scaffold.py --help` tried to read `plan---help.md`.
    issue_id = require_positional_argv(
        sys.argv, usage=_USAGE, doc=__doc__, prog="be-scaffold.py"
    )
    plan_path = PLANS_DIR / f"plan-{issue_id}.md"

    if not plan_path.exists():
        print(f"[!] Plan not found: {plan_path}")
        print(f"    Run the planner first: /project:be-planner {issue_id}")
        sys.exit(1)

    print(f"[+] Reading plan: {plan_path.name}")
    plan = parse_plan(plan_path)

    if not plan["files"]:
        print("[!] No files found in '## 2. Arquivos a criar'. Check the plan format.")
        sys.exit(1)

    print(f"    Service: {plan['service']}")
    print(f"    Package: {plan['package_base']}")
    print(f"    Files:   {len(plan['files'])}")

    # Load spec context for enriched scaffolding
    spec_ctx = load_spec_context(plan["service"])
    spec_dir = find_spec_dir(plan["service"])
    if spec_dir:
        tables_found = len(spec_ctx["tables"])
        endpoints_found = len(spec_ctx["endpoints"])
        events_pub = len(spec_ctx["events"]["published"])
        events_con = len(spec_ctx["events"]["consumed"])
        print(f"    Spec:    {spec_dir.name} ({tables_found} tables, {endpoints_found} endpoints, "
              f"{events_pub} pub / {events_con} cons events)")
    else:
        print(f"    Spec:    not found — using generic placeholders")
    print()

    created = []
    skipped = []

    for file_info in plan["files"]:
        rel_path = file_info["path"]
        abs_path = resolve_file_path(plan, rel_path)

        if abs_path.exists():
            skipped.append(rel_path)
            print(f"   [>] {rel_path} (already exists)")
            continue

        content = generate_file(plan, file_info, spec_ctx)
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(content, encoding="utf-8")
        created.append(rel_path)
        print(f"   [+] {rel_path}")

    print()
    print(f"[+] Scaffold completo para {issue_id}:")
    print(f"    Criados:  {len(created)}")
    print(f"    Pulados:  {len(skipped)} (ja existiam)")
    print()

    if created:
        for f in created:
            print(f"    + {f}")
        print()

    print(f"[>] Proximo passo: implementar logica com ISSUE_ID={issue_id}")


if __name__ == "__main__":
    main()

