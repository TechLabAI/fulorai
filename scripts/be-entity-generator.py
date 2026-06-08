#!/usr/bin/env python3
"""
be-entity-generator.py — Gera domain, persistencia, controllers e DTOs a partir do SQL e spec.

Le V1__create_initial_schema.sql + api-contract.md + spec.md + event-contracts.md e produz:

  Por tabela (SQL):
    1. domain/model/<Name>.java                                (record puro — zero Spring/JPA)
    2. domain/service/<Name>DomainService.java                 (stub puro — zero Spring/JPA)
    3. infrastructure/persistence/entity/<Name>Entity.java     (@Entity com @Column reais)
    4. infrastructure/persistence/repository/<Name>Repository  (Spring Data JPA)
    5. application/port/out/<Name>Port.java                    (interface de saida)
    6. infrastructure/persistence/adapter/<Name>JpaAdapter     (stub implements Port)

  Por endpoint (api-contract.md):
    7. api/controller/<Group>Controller.java                   (@RestController agrupado)
    8. api/dto/<Name>Request.java / <Name>Response.java        (records de contrato)

  Por use case (spec §8):
    9. application/port/in/<UseCaseName>.java                  (interface de entrada)
   10. application/service/<UseCaseName→Service>.java          (@Service stub)

  Por integracao interna (spec §11):
   11. infrastructure/clients/<ServicePascal>Client.java       (@FeignClient stub)

  Por evento publicado (event-contracts.md):
   12. infrastructure/messaging/producer/<EventPascal>Producer (@Component + JmsTemplate)

  Por evento consumido (event-contracts.md):
   13. infrastructure/messaging/consumer/<EventPascal>Consumer (@JmsListener stub)

  Cleanup:
   14. Remove package-info.java de pacotes que ja possuem classes reais

Uso:
    python scripts/be-entity-generator.py <SERVICE_NAME>
    python scripts/be-entity-generator.py --force identity-session-service
    python scripts/be-entity-generator.py --dry-run all
    python scripts/be-entity-generator.py --no-usecases --no-controllers audit-trace-capability
    python scripts/be-entity-generator.py --no-domain-services --no-clients --no-messaging <SVC>

Economia: elimina ~20.000-35.000 tokens de LLM por servico.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Project context (loaded once; defaults applied when the script runs outside
# a project — e.g. workspace-side smoke tests).
try:
    from be_context_helper import load_project_context
    _CTX = load_project_context()
except (ImportError, Exception):
    _CTX = None

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "backend" / "services"
SPECS_DIR = ROOT / "docs" / "architecture" / "backend" / "services"

PKG_BASE = _CTX.package_base if _CTX else "com.project"


# ── Generation overrides (D-092) ──────────────────────────────────────────────
#
# Previously three module-level globals (_SPEC_DIR_OVERRIDE,
# _PACKAGE_OVERRIDE, _AGGREGATE_NAME_OVERRIDE) were mutated from main()
# and read deep in the call stack. Refactored into a `GenerationOverrides`
# dataclass that flows explicitly through each helper as an optional
# parameter — keeps the workspace tool single-threaded but makes the data
# flow visible (no spooky-action-at-a-distance) and the script unit-testable
# without monkey-patching module globals.
@dataclass
class GenerationOverrides:
    """Per-invocation overrides that flow through generate_for_service."""
    spec_dir: Path | None = None
    aggregate_names: dict[str, str] = field(default_factory=dict)


def _get_spec_dir(service: str, overrides: GenerationOverrides | None = None) -> Path:
    """Resolve spec directory: override for tool services, standard path for platform services."""
    if overrides and overrides.spec_dir is not None:
        return overrides.spec_dir
    return SPECS_DIR / f"{service}-spec"


# ── Service catalog ─────────────────────────────────────────────────────────────

SERVICE_PACKAGES = {
    "identity-session-service":         "identity",
    "authorization-policy-service":     "authorization",
    "tenant-context-service":           "tenantcontext",
    "hub-administration-service":       "administration",
    "tool-catalog-entitlement-service": "toolcatalog",
    "audit-trace-capability":           "audit",
    "hub-api-gateway":                  "gateway",
    "hub-service-registry":             "registry",
    "hermes-service":                   "hermes",
}


def _resolve_service_package_suffix(service: str, ctx) -> str | None:
    """D-079: derive Java package suffix for a service name.

    Resolution order:
      1. Legacy hardcoded `SERVICE_PACKAGES` (above; covers the hub-platform
         services this script was originally written for).
      2. Project-context.modules.registry convention: split service name
         on "-", treat first token as module prefix (lowercase); match
         against `modules[*].prefix.lower()`. If found, use the module's
         `packageSuffix` (if declared, D-078) or fall back to `prefix.lower()`.

    Examples:
      "ops-obras-service" + modules.registry has OPS → "ops"
      "loss-classification-service" + LOSS → "loss"
      "kaizen-pdca-service" + KAI with packageSuffix="kaizen" → "kaizen"

    Returns None when no resolution rule applies. Caller's error message
    points the user at modules.registry edit OR --package override.
    """
    if service in SERVICE_PACKAGES:
        return SERVICE_PACKAGES[service]
    if not ctx or not getattr(ctx, "modules", None):
        return None
    head = service.split("-", 1)[0].lower()
    for m in ctx.modules:
        if (m.get("prefix") or "").lower() == head:
            return (m.get("packageSuffix") or "").lower() or head
    return None

# ── SQL type → Java type ───────────────────────────────────────────────────────

_SQL_TO_JAVA: dict[str, tuple[str, str | None]] = {
    "UUID":        ("UUID",           "java.util.UUID"),
    "TIMESTAMPTZ": ("OffsetDateTime", "java.time.OffsetDateTime"),
    "TIMESTAMP":   ("OffsetDateTime", "java.time.OffsetDateTime"),
    "BIGINT":      ("Long",           None),
    "INTEGER":     ("Integer",        None),
    "INT":         ("Integer",        None),
    "SMALLINT":    ("Integer",        None),
    "BOOLEAN":     ("Boolean",        None),
    "BOOL":        ("Boolean",        None),
    "JSONB":       ("String",         None),
    "TEXT":        ("String",         None),
    "VARCHAR":     ("String",         None),
    "CHAR":        ("String",         None),
    "NUMERIC":     ("java.math.BigDecimal", "java.math.BigDecimal"),
    "DECIMAL":     ("java.math.BigDecimal", "java.math.BigDecimal"),
}


def _persistence_type_lookup(sql_type: str) -> tuple[str, str | None] | None:
    """D-068 Phase 2: look up the catalogue's full sql_type match.

    persistence.column_types declares full forms like 'NUMERIC(15,2)' with
    java_type. Exact match (case-insensitive, whitespace-tolerant) wins over
    the legacy precision-stripped dict. Returns None when no exact match
    OR no catalogue pinned — caller falls back to _SQL_TO_JAVA.
    """
    try:
        from arch_decisions import load_decision
        persistence = load_decision("persistence")
    except (ImportError, FileNotFoundError):
        return None
    target = sql_type.replace(" ", "").upper()
    for ct in persistence.get("column_types", []):
        catalogue_type = (ct.get("sql_type") or "").replace(" ", "").upper()
        if catalogue_type == target:
            jtype = ct.get("java_type") or ""
            if not jtype:
                continue
            # Java type may be FQN ('java.math.BigDecimal') or short ('String').
            short = jtype.rsplit(".", 1)[-1]
            fqn = jtype if "." in jtype else None
            return (short, fqn)
    return None


def java_type(sql_type: str) -> tuple[str, str | None]:
    """Return (java_short_type, import_fqn_or_None) for a SQL type.

    Resolution order (D-068 Phase 2):
      1. persistence.column_types — exact match on full sql_type (catches
         the canonical types: NUMERIC(15,2) → monetary, etc.).
      2. _SQL_TO_JAVA — base type lookup (strips precision).
      3. Fallback to ('String', None).
    """
    catalogue = _persistence_type_lookup(sql_type)
    if catalogue is not None:
        return catalogue
    base = re.sub(r"\(\d+(?:,\s*\d+)?\)", "", sql_type).upper()
    return _SQL_TO_JAVA.get(base, ("String", None))


# ── Naming helpers ─────────────────────────────────────────────────────────────

def to_pascal(snake: str) -> str:
    return "".join(p.capitalize() for p in snake.split("_"))


def to_camel(snake: str) -> str:
    parts = snake.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


# ── Aggregate name overrides (populated from generator-config.yml) ─────────────


def _normalize(name: str) -> str:
    return name.replace("_", "").lower()


def resolve_class_name(
    table_name: str, overrides: GenerationOverrides | None = None
) -> str:
    """Return PascalCase class name, preferring exact aggregate names from config over to_pascal()."""
    if overrides:
        return overrides.aggregate_names.get(_normalize(table_name), to_pascal(table_name))
    return to_pascal(table_name)


def _load_aggregate_overrides(spec_dir: Path) -> dict[str, str]:
    config_file = spec_dir / "generator-config.yml"
    if not config_file.exists():
        return {}
    overrides: dict[str, str] = {}
    in_domain = False
    in_list = False
    for line in config_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            in_domain = stripped.startswith("domain:")
            in_list = False
        elif in_domain and indent == 2:
            in_list = stripped in ("aggregates:", "entities:")
        elif in_domain and in_list and indent == 4 and stripped.startswith("- "):
            name = stripped[2:].strip()
            if name:
                overrides[_normalize(name)] = name
    return overrides


# ── SQL parser ─────────────────────────────────────────────────────────────────

def parse_sql_tables(sql_text: str) -> list[dict]:
    """Extrai tabelas de DDL Postgres. Aceita CREATE TABLE com ou sem IF NOT EXISTS.

    Reconhece:
      - CREATE TABLE name (...)
      - CREATE TABLE IF NOT EXISTS name (...)
      - CREATE TABLE schema.name (...)
      - PK inline (`coluna ... PRIMARY KEY`) ou via CONSTRAINT
      - Constraints inline (UNIQUE, CHECK, FOREIGN KEY) — ignoradas em colunas
    """
    tables = []
    pattern = re.compile(
        r"CREATE TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:(\w+)\.)?(\w+)\s*\((.*?)\)\s*;",
        re.DOTALL | re.IGNORECASE,
        )
    # Reservas SQL que NÃO são nomes de coluna (aparecem como primeira palavra
    # em linhas de constraint sem prefixo CONSTRAINT — ex.: `UNIQUE (col)`,
    # `CHECK (...)`, `FOREIGN KEY (...)`, `PRIMARY KEY (...)`).
    _CONSTRAINT_KEYWORDS = {"PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "EXCLUDE"}

    for m in pattern.finditer(sql_text):
        schema = m.group(1) or "public"
        table_name = m.group(2)
        body = m.group(3)
        # PK via CONSTRAINT explícita ou via PRIMARY KEY (col)
        pk_match = re.search(
            r"CONSTRAINT\s+\w+\s+PRIMARY\s+KEY\s*\((\w+)\)", body, re.IGNORECASE
        )
        if not pk_match:
            pk_match = re.search(r"^\s*PRIMARY\s+KEY\s*\((\w+)\)", body, re.IGNORECASE | re.MULTILINE)
        pk_col = pk_match.group(1).strip() if pk_match else None
        # PK inline (`coluna_id UUID PRIMARY KEY ...`)
        if not pk_col:
            inline_pk = re.search(r"^\s*(\w+)\s+\w+.*?\bPRIMARY\s+KEY\b", body, re.IGNORECASE | re.MULTILINE)
            if inline_pk:
                pk_col = inline_pk.group(1)

        columns = []
        constraint_depth = 0
        for line in body.splitlines():
            line = line.strip().rstrip(",")
            if not line:
                continue
            # Skip content nested inside multi-line constraint bodies (e.g. EXCLUDE USING gist (...))
            if constraint_depth > 0:
                constraint_depth += line.count("(") - line.count(")")
                if constraint_depth < 0:
                    constraint_depth = 0
                continue
            # Pula linhas de constraint (CONSTRAINT ..., UNIQUE ..., CHECK ..., FOREIGN KEY ..., PRIMARY KEY ...)
            if re.match(r"^\s*CONSTRAINT\b", line, re.IGNORECASE):
                constraint_depth = max(0, line.count("(") - line.count(")"))
                continue
            first_word = line.split()[0].upper() if line.split() else ""
            if first_word in _CONSTRAINT_KEYWORDS:
                constraint_depth = max(0, line.count("(") - line.count(")"))
                continue
            col_m = re.match(r"^(\w+)\s+(\w+(?:\(\d+(?:,\s*\d+)?\))?)(.*)", line)
            if not col_m:
                continue
            col_name = col_m.group(1)
            raw_type = col_m.group(2).upper()
            rest = col_m.group(3).upper()
            is_pk = col_name == pk_col
            nullable = "NOT NULL" not in rest and not is_pk
            columns.append({"name": col_name, "sql_type": raw_type, "nullable": nullable, "is_pk": is_pk})
        if columns:
            tables.append({"schema": schema, "table_name": table_name, "pk_col": pk_col, "columns": columns})
    return tables


# ── Smart findBy method generator ─────────────────────────────────────────────

def smart_query_methods(
    table: dict, pkg: str, overrides: GenerationOverrides | None = None
) -> tuple[list[str], bool]:
    cols = {c["name"] for c in table["columns"]}
    methods = []
    cls = resolve_class_name(table["table_name"], overrides)
    has_list = False
    if "tenant_id" in cols:
        methods.append(f"    List<{cls}Entity> findByTenantId(UUID tenantId);")
        has_list = True
    status_cols = [c["name"] for c in table["columns"] if c["name"].endswith("_status")]
    for sc in status_cols[:2]:
        methods.append(f"    List<{cls}Entity> findBy{to_pascal(sc)}(String {to_camel(sc)});")
        has_list = True
    for uid in ["user_id", "actor_user_id", "invited_by_user_id"]:
        if uid in cols:
            methods.append(f"    List<{cls}Entity> findBy{to_pascal(uid)}(UUID {to_camel(uid)});")
            has_list = True
            break
    if "correlation_id" in cols:
        methods.append(f"    List<{cls}Entity> findByCorrelationId(UUID correlationId);")
        has_list = True
    if "session_id" in cols and table["table_name"] != "hub_session":
        methods.append(f"    List<{cls}Entity> findBySessionId(UUID sessionId);")
        has_list = True
    return methods, has_list


def port_out_methods(table: dict, cls: str) -> list[str]:
    cols = {c["name"] for c in table["columns"]}
    methods = [
        f"    {cls} save({cls} domain);",
        f"    Optional<{cls}> findById(UUID id);",
    ]
    if "tenant_id" in cols:
        methods.append(f"    List<{cls}> findByTenantId(UUID tenantId);")
    methods.append(f"    void deleteById(UUID id);")
    return methods


# ── Persistence code generators ────────────────────────────────────────────────

def gen_domain_record(
    table: dict, pkg: str, overrides: GenerationOverrides | None = None
) -> str:
    cls = resolve_class_name(table["table_name"], overrides)
    imports_set: set[str] = set()
    components: list[str] = []
    for col in table["columns"]:
        jtype, imp = java_type(col["sql_type"])
        if imp:
            imports_set.add(f"import {imp};")
        components.append(f"    {jtype} {to_camel(col['name'])}")
    imports_block = "\n".join(sorted(imports_set))
    if imports_block:
        imports_block += "\n\n"
    comp_str = ",\n".join(components)
    return f"""\
package {pkg}.domain.model;

{imports_block}/**
 * Domain model — {cls}.
 * Pure Java record — zero Spring/JPA imports (RULE-01/02).
 * Source: V1__create_initial_schema.sql :: {table["table_name"]}
 * Generated by be-entity-generator.py.
 */
public record {cls}(
{comp_str}
) {{
    // TODO: add domain validations / compact constructor if needed
}}
"""


def _entity_scope_filter_blocks(table_name: str, columns: list[dict]) -> tuple[str, str, set[str]]:
    """Return (filter_def_block, filter_block, extra_imports) for this table.

    Looks up table in entity-scope.arch.json (D-062). Emits one @FilterDef +
    @Filter pair per scope tipo the table participates in. Returns empty
    strings + empty set when entity-scope isn't pinned or the table isn't
    listed (most entities aren't data-scoped).

    Soft validation: when an entry references a column not present on the
    table, prints a warning to stderr and skips that entry — emitting a
    @Filter against a non-existent column would compile but fail at runtime.
    """
    try:
        from arch_decisions import load_decision, entity_scope_entries_for_table
    except ImportError:
        return "", "", set()
    try:
        entity_scope = load_decision("entity-scope")
    except FileNotFoundError:
        return "", "", set()

    rows = entity_scope_entries_for_table(entity_scope, table_name)
    if not rows:
        return "", "", set()

    col_names = {c["name"] for c in columns}
    valid_rows: list[dict] = []
    for r in rows:
        if r["column"] not in col_names:
            print(f"[be-entity-generator] WARN: entity-scope entry "
                  f"{r['filter_name']!r} references column {r['column']!r} "
                  f"absent on table {table_name!r} — skipping",
                  file=sys.stderr)
            continue
        valid_rows.append(r)
    if not valid_rows:
        return "", "", set()

    extra_imports = {
        "import org.hibernate.annotations.Filter;",
        "import org.hibernate.annotations.FilterDef;",
        "import org.hibernate.annotations.Filters;",
        "import org.hibernate.annotations.FilterDefs;",
        "import org.hibernate.annotations.ParamDef;",
    }

    def_lines: list[str] = []
    use_lines: list[str] = []
    for r in valid_rows:
        is_list = r.get("kind") == "list"
        # Both scalar and list use UUID at the param level; the difference is
        # whether Hibernate sees one value (setParameter) or many
        # (setParameterList) — driven by the aspect, not declared here.
        param_type = "java.util.UUID"
        def_lines.append(
            f'@FilterDef(name = "{r["filter_name"]}", '
            f'parameters = @ParamDef(name = "{r["param"]}", type = {param_type}.class))'
        )
        op = "IN (:" + r["param"] + ")" if is_list else "= :" + r["param"]
        use_lines.append(
            f'@Filter(name = "{r["filter_name"]}", condition = "{r["column"]} {op}")'
        )

    if len(def_lines) == 1:
        # Single scope — class-level annotation, flush left.
        filter_def_block = def_lines[0]
        filter_block = use_lines[0]
    else:
        # Multiple scopes — wrap in @FilterDefs / @Filters with one entry per
        # line, indented 4 spaces inside the braces.
        filter_def_block = (
            "@FilterDefs({\n"
            + ",\n".join("    " + l for l in def_lines)
            + "\n})"
        )
        filter_block = (
            "@Filters({\n"
            + ",\n".join("    " + l for l in use_lines)
            + "\n})"
        )
    return filter_def_block, filter_block, extra_imports


def _check_audit_completeness(table_name: str, col_names: set[str]) -> None:
    """D-068 Phase 2: warn when a table declares SOME audit columns but
    misses others. Heuristic: if any of the 4 names from
    persistence.audit_columns appears, all 4 should appear (otherwise the
    table is partly-audited, which is almost always a DDL bug).
    """
    try:
        from arch_decisions import load_decision, audit_column_names
        persistence = load_decision("persistence")
    except (ImportError, FileNotFoundError):
        return
    audit = audit_column_names(persistence)
    declared = [v for v in audit.values() if v in col_names]
    if 0 < len(declared) < 4:
        missing = [v for v in audit.values() if v not in col_names]
        print(
            f"[be-entity-generator] WARN: table {table_name!r} has SOME audit "
            f"columns ({declared!r}) but is missing {missing!r} — "
            f"persistence.arch.json declares all 4 should appear together on "
            f"root aggregates",
            file=sys.stderr,
        )


def gen_jpa_entity(
    table: dict, pkg: str, overrides: GenerationOverrides | None = None
) -> str:
    cls = resolve_class_name(table["table_name"], overrides)
    table_name = table["table_name"]
    schema = table["schema"] if table["schema"] not in ("public", None) else None
    _check_audit_completeness(table_name, {c["name"] for c in table["columns"]})
    imports_set: set[str] = {"import jakarta.persistence.*;", "import lombok.Getter;",
                             "import lombok.Setter;", "import lombok.NoArgsConstructor;"}
    field_lines: list[str] = []
    for col in table["columns"]:
        jtype, imp = java_type(col["sql_type"])
        if imp:
            imports_set.add(f"import {imp};")
        camel = to_camel(col["name"])
        if col["is_pk"]:
            field_lines.append(f"    @Id\n    @GeneratedValue(strategy = GenerationType.UUID)")
            field_lines.append(f'    @Column(name = "{col["name"]}", nullable = false, updatable = false)')
            field_lines.append(f"    private {jtype} {camel};\n")
        else:
            ann = f'    @Column(name = "{col["name"]}"'
            if not col["nullable"]:
                ann += ", nullable = false"
            size_m = re.search(r"\((\d+)\)", col["sql_type"])
            if size_m and jtype == "String" and int(size_m.group(1)) < 255:
                ann += f", length = {size_m.group(1)}"
            ann += ")"
            field_lines.append(ann)
            field_lines.append(f"    private {jtype} {camel};\n")
    table_ann = f'@Table(name = "{table_name}"'
    if schema:
        table_ann += f', schema = "{schema}"'
    table_ann += ")"

    # D-062: emit @FilterDef + @Filter from entity-scope.arch.json when this
    # table participates in any data-scope tipo. Imports adjusted accordingly.
    filter_def_block, filter_block, extra_imports = _entity_scope_filter_blocks(
        table_name, table["columns"]
    )
    imports_set |= extra_imports
    scope_annotations = ""
    if filter_def_block:
        scope_annotations = f"{filter_def_block}\n{filter_block}\n"

    # B2 (workflow-improvements.md): layout via Jinja2 template; column/import logic stays here.
    from be_context_helper import render_code_template
    return render_code_template("code/java/eg-entity.java.j2", {
        "pkg": pkg,
        "cls": cls,
        "schema_table": f'{table["schema"]}.{table_name}',
        "imports_block": chr(10).join(sorted(imports_set)),
        "table_ann": table_ann,
        "scope_annotations": scope_annotations,
        "fields_block": chr(10).join(field_lines),
    })


def gen_jpa_repository(
    table: dict, pkg: str, overrides: GenerationOverrides | None = None
) -> str:
    cls = resolve_class_name(table["table_name"], overrides)
    extra_methods, needs_list = smart_query_methods(table, pkg, overrides)
    methods_block = "\n".join(extra_methods)
    if methods_block:
        methods_block = "\n" + methods_block + "\n"
    list_import = "import java.util.List;\n" if needs_list else ""
    from be_context_helper import render_code_template
    return render_code_template("code/java/eg-repository.java.j2", {
        "pkg": pkg, "cls": cls, "list_import": list_import, "methods_block": methods_block,
    })


def gen_port_out(
    table: dict, pkg: str, overrides: GenerationOverrides | None = None
) -> str:
    cls = resolve_class_name(table["table_name"], overrides)
    methods_str = "\n".join(port_out_methods(table, cls))
    from be_context_helper import render_code_template
    return render_code_template("code/java/eg-port-out.java.j2", {
        "pkg": pkg, "cls": cls, "methods_str": methods_str,
    })


def gen_jpa_adapter(
    table: dict, pkg: str, overrides: GenerationOverrides | None = None
) -> str:
    cls = resolve_class_name(table["table_name"], overrides)
    cols = {c["name"] for c in table["columns"]}
    extra = ""
    if "tenant_id" in cols:
        extra = f"""
    @Override
    public List<{cls}> findByTenantId(UUID tenantId) {{
        return repository.findByTenantId(tenantId).stream().map(this::toDomain).toList();
    }}
"""
    from be_context_helper import render_code_template
    return render_code_template("code/java/eg-adapter.java.j2", {
        "pkg": pkg, "cls": cls, "extra": extra,
        "pk_getter": to_pascal(table["pk_col"] or "id"),
    })


# ── Use case (port/in) generator from spec §8 ─────────────────────────────────

def parse_use_cases_from_spec(
    service: str, overrides: GenerationOverrides | None = None
) -> list[str]:
    spec_dir = _get_spec_dir(service, overrides)
    spec_files = list(spec_dir.glob("*.spec.md"))
    if not spec_files:
        return []
    text = spec_files[0].read_text(encoding="utf-8")
    section_match = re.search(r"##\s*8\.\s*Casos de Uso.*?\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    if not section_match:
        return []
    names = re.findall(r"`([A-Z][A-Za-z0-9]+UseCase)`", section_match.group(1))
    return list(dict.fromkeys(names))


def gen_use_case_port_in(use_case_name: str, pkg: str) -> str:
    cmd = use_case_name.replace("UseCase", "Command")
    result = use_case_name.replace("UseCase", "Result")
    return f"""\
package {pkg}.application.port.in;

/**
 * Input port — {use_case_name}.
 * Generated by be-entity-generator.py from spec.md §8.
 * TODO: replace Object with {cmd} / {result}.
 */
public interface {use_case_name} {{
    Object execute(Object command);
}}
"""


def gen_use_case_service(use_case_name: str, pkg: str) -> str:
    """Generate the @Service stub that implements a port/in use case interface."""
    svc_class = use_case_name.replace("UseCase", "Service")
    return f"""\
package {pkg}.application.service;

import {pkg}.application.port.in.{use_case_name};
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Application service — {svc_class}.
 * Implements {use_case_name}.
 * Generated by be-entity-generator.py from spec.md §8.
 * TODO: inject ports, add @Transactional and implement logic — see 02b-be-logic.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class {svc_class} implements {use_case_name} {{

    @Override
    public Object execute(Object command) {{
        // TODO: implement — replace Object with proper command/result types
        throw new UnsupportedOperationException("{svc_class} not implemented — see 02b-be-logic");
    }}
}}
"""


# ── Domain service generator ─────────────────────────────────────────────────

def gen_domain_service(
    table: dict, pkg: str, overrides: GenerationOverrides | None = None
) -> str:
    cls = resolve_class_name(table["table_name"], overrides)
    camel = cls[0].lower() + cls[1:]
    return f"""\
package {pkg}.domain.service;

import {pkg}.domain.model.{cls};

/**
 * Domain service — {cls}DomainService.
 * Pure domain logic for {cls} aggregate.
 * Zero Spring/JPA imports (RULE-01/02). Instantiated by application services.
 * Generated by be-entity-generator.py.
 * TODO: implement domain invariants and business rules — see 02b-be-logic.
 */
public class {cls}DomainService {{

    // TODO: add domain operations — validation, state transitions, invariant checks.
    // Example:
    // public void validate({cls} {camel}) {{
    //     // enforce domain rules
    // }}
}}
"""


# ── Feign client generators ──────────────────────────────────────────────────

def parse_integrations_from_spec(
    service: str, overrides: GenerationOverrides | None = None
) -> list[dict]:
    """Parse spec §11 'Integrações Internas' → [{service, operations[]}]."""
    spec_dir = _get_spec_dir(service, overrides)
    spec_files = list(spec_dir.glob("*.spec.md"))
    if not spec_files:
        return []
    text = spec_files[0].read_text(encoding="utf-8")
    sec_m = re.search(r"##\s*11\.", text)
    if not sec_m:
        return []
    section_start = sec_m.start()
    next_m = re.search(r"\n##\s+\d+\.", text[section_start + 5:])
    section_end = section_start + 5 + next_m.start() if next_m else len(text)
    section = text[section_start:section_end]

    integrations = []
    for m in re.finditer(
        r"###\s+\d+\.\d+\s+`([^`]+)`\s*\n(.*?)(?=\n###\s+\d|\Z)", section, re.DOTALL
    ):
        dep_service = m.group(1).strip()
        ops_raw = [ln.strip()[2:].strip() for ln in m.group(2).splitlines()
                   if ln.strip().startswith("-")]
        ops = [re.sub(r"[^\x00-\x7F]", "", op).strip() for op in ops_raw]
        ops = [op for op in ops if 3 < len(op) < 100]
        integrations.append({"service": dep_service, "operations": ops[:6]})
    return integrations


def gen_feign_client(dep_service: str, operations: list[str], pkg: str) -> str:
    cls = to_pascal(dep_service.replace("-", "_")) + "Client"
    ops_block = "\n".join(f"    // TODO: {op}" for op in operations)
    if ops_block:
        ops_block = "\n" + ops_block + "\n"
    return f"""\
package {pkg}.infrastructure.clients;

import org.springframework.cloud.openfeign.FeignClient;

/**
 * Feign client — {cls}.
 * Internal integration with {dep_service}.
 * Generated by be-entity-generator.py from spec.md §11.
 * TODO: add method signatures — see 02b-be-logic.
 */
@FeignClient(name = "{dep_service}")
public interface {cls} {{{ops_block}
}}
"""


# ── Messaging generators ─────────────────────────────────────────────────────

def parse_event_contracts(
    service: str, overrides: GenerationOverrides | None = None
) -> tuple[list[str], list[dict]]:
    """Parse event-contracts.md → (published_names, [{name, description}] consumed)."""
    ec = _get_spec_dir(service, overrides) / "contracts" / "event-contracts.md"
    if not ec.exists():
        return [], []
    text = ec.read_text(encoding="utf-8")

    published: list[str] = []
    consumed: list[dict] = []

    pub_m = re.search(r"##\s*Eventos Publicados[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    if pub_m:
        published = list(dict.fromkeys(re.findall(r"###\s+(\w+)", pub_m.group(0))))

    con_m = re.search(r"##\s*Eventos Consumidos[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    if con_m:
        section = con_m.group(0)
        named = list(dict.fromkeys(re.findall(r"###\s+(\w+)", section)))
        for name in named:
            dm = re.search(
                rf"###\s+{re.escape(name)}\s*\n(.+?)(?=\n###|\n##|\Z)", section, re.DOTALL
            )
            desc = ""
            if dm:
                first = dm.group(1).strip().split("\n")[0]
                desc = re.sub(r"[^\x00-\x7F]", "", first).strip(" .-*")
            consumed.append({"name": name, "description": desc})

    return published, consumed


def gen_event_producer(event_name: str, pkg: str) -> str:
    cls = to_pascal(event_name) + "Producer"
    broker = _CTX.events_broker if _CTX else "artemis"
    if broker == "kafka":
        return f"""\
package {pkg}.infrastructure.messaging.producer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

/**
 * Kafka producer — {cls}.
 * Topic: {event_name}
 * Generated by be-entity-generator.py from event-contracts.md.
 * TODO: replace Object with proper event payload type — see 02b-be-logic.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {cls} {{

    private static final String TOPIC = "{event_name}";
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publish(Object event) {{
        log.info("Publishing {{}} to topic {{}}", event.getClass().getSimpleName(), TOPIC);
        kafkaTemplate.send(TOPIC, event);
    }}
}}
"""
    return f"""\
package {pkg}.infrastructure.messaging.producer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.stereotype.Component;

/**
 * JMS producer — {cls}.
 * Destination: {event_name}
 * Generated by be-entity-generator.py from event-contracts.md.
 * TODO: replace Object with proper event payload type — see 02b-be-logic.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {cls} {{

    private static final String DESTINATION = "{event_name}";
    private final JmsTemplate jmsTemplate;

    public void publish(Object event) {{
        log.info("Publishing {{}} to {{}}", event.getClass().getSimpleName(), DESTINATION);
        jmsTemplate.convertAndSend(DESTINATION, event);
    }}
}}
"""


def gen_event_consumer(event_name: str, description: str, pkg: str) -> str:
    cls = to_pascal(event_name) + "Consumer"
    todo = f"// TODO: {description}" if description else "// TODO: implement handler — see 02b-be-logic"
    broker = _CTX.events_broker if _CTX else "artemis"
    project_name = _CTX.project_name if _CTX else "project"
    if broker == "kafka":
        return f"""\
package {pkg}.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka consumer — {cls}.
 * Topic: {event_name}
 * Generated by be-entity-generator.py from event-contracts.md.
 * TODO: implement handler logic — see 02b-be-logic.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {cls} {{

    @KafkaListener(topics = "{event_name}", groupId = "{project_name}-consumer")
    public void handle(String payload) {{
        {todo}
        throw new UnsupportedOperationException("{cls} not implemented — see 02b-be-logic");
    }}
}}
"""
    return f"""\
package {pkg}.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

/**
 * JMS consumer — {cls}.
 * Listens to: {event_name}
 * Generated by be-entity-generator.py from event-contracts.md.
 * TODO: implement handler logic — see 02b-be-logic.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {cls} {{

    @JmsListener(destination = "{event_name}")
    public void handle(Object event) {{
        {todo}
        throw new UnsupportedOperationException("{cls} not implemented — see 02b-be-logic");
    }}
}}
"""


def gen_generic_consumer(service: str, pkg: str) -> str:
    """Generic consumer for services that consume events by category (e.g. audit-trace)."""
    svc_pascal = to_pascal(service.replace("-", "_"))
    cls = f"{svc_pascal}EventConsumer"
    broker = _CTX.events_broker if _CTX else "artemis"
    project_name = _CTX.project_name if _CTX else "project"
    if broker == "kafka":
        listener_import = "import org.springframework.kafka.annotation.KafkaListener;"
        listener_example = f"// @KafkaListener(topics = \"event_topic\", groupId = \"{project_name}-consumer\")"
        consumer_type = "Kafka"
        todo_annotation = "add @KafkaListener"
    else:
        listener_import = "import org.springframework.jms.annotation.JmsListener;"
        listener_example = "// @JmsListener(destination = \"user_logged_in\")"
        consumer_type = "JMS"
        todo_annotation = "add @JmsListener"
    return f"""\
package {pkg}.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
{listener_import}
import org.springframework.stereotype.Component;

/**
 * Generic {consumer_type} consumer — {cls}.
 * Ingests events from all source services.
 * Generated by be-entity-generator.py from event-contracts.md.
 * TODO: {todo_annotation} methods per event type and implement persistence — see 02b-be-logic.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class {cls} {{

    // TODO: define specific listener methods per event type.
    // Event categories to handle:
    //   session events, context events, access events,
    //   catalog events, administrative events, edge technical events.
    // Example:
    {listener_example}
    // public void handleUserLoggedIn(Object event) {{ ... }}
}}
"""


# ── API contract parser + controller/DTO generators ────────────────────────────

def _compute_prefix_suffix(path: str) -> tuple[str, str]:
    """Split path into (prefix, suffix) at the first path variable.

    Strategy: walk segments after /api/v1/ and stop **before** the first
    ``{...}`` variable.  This produces natural resource-level grouping:

    - ``/api/v1/admin/tenants``                → prefix ``/api/v1/admin/tenants``, suffix ````
    - ``/api/v1/admin/tenants/{tenantId}/disable`` → prefix ``/api/v1/admin/tenants``, suffix ``/{tenantId}/disable``
    - ``/api/v1/roles``                        → prefix ``/api/v1/roles``, suffix ````
    - ``/api/v1/roles/{roleId}``               → prefix ``/api/v1/roles``, suffix ``/{roleId}``
    """
    segs = path.split("/")
    prefix_parts: list[str] = []
    for s in segs:
        if s.startswith("{"):
            break
        prefix_parts.append(s)
    prefix = "/".join(prefix_parts)
    suffix = path[len(prefix):] if len(prefix) < len(path) else ""
    return prefix, suffix


def _merge_singleton_groups(groups: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Merge single-endpoint groups that share a deep parent path.

    Only singletons whose parent has ≥ 3 non-empty segments (e.g.
    ``/api/v1/admin``, ``/api/v1/tools``, ``/api/v1/session``) are candidates.
    Shallow singletons (parent = ``/api/v1``) stay as their own controller.

    When singletons share a deep parent *and* a multi-endpoint sibling group
    exists under the same parent, all of them are promoted to the parent level
    with recalculated suffixes.
    """
    merged: dict[str, list[dict]] = {}
    singletons: list[tuple[str, dict]] = []

    for prefix, eps in groups.items():
        if len(eps) == 1:
            singletons.append((prefix, eps[0]))
        else:
            merged[prefix] = list(eps)

    # Bucket singletons by parent — only deep parents
    by_parent: dict[str, list[tuple[str, dict]]] = {}
    for prefix, ep in singletons:
        parent = prefix.rsplit("/", 1)[0]
        parent_depth = len([s for s in parent.split("/") if s])
        if parent_depth >= 3:                           # api/v1/something = 3
            by_parent.setdefault(parent, []).append((prefix, ep))
        else:
            merged[prefix] = [ep]                       # too shallow → own controller

    for parent, singleton_list in by_parent.items():
        # Collect all sibling multi-endpoint groups under this parent
        sibling_keys = [k for k in merged if k.rsplit("/", 1)[0] == parent]

        if len(singleton_list) >= 2:
            # Multiple singletons → merge into one controller at parent level
            new_group: list[dict] = []
            for _prefix, ep in singleton_list:
                ep["path_suffix"] = ep["path"][len(parent):]
                new_group.append(ep)
            merged[parent] = new_group
        elif sibling_keys:
            # Lone singleton but has sibling groups — keep as own controller
            # (absorbing into a sibling would break method naming)
            prefix, ep = singleton_list[0]
            merged[prefix] = [ep]
        else:
            # Lone singleton with no siblings — keep as its own controller
            prefix, ep = singleton_list[0]
            merged[prefix] = [ep]

    return merged


def parse_api_contract(
    service: str, overrides: GenerationOverrides | None = None
) -> list[dict]:
    contract = _get_spec_dir(service, overrides) / "contracts" / "api-contract.md"
    if not contract.exists():
        return []
    text = contract.read_text(encoding="utf-8")
    endpoints = []
    for m in re.finditer(r"###\s+(GET|POST|PUT|DELETE|PATCH)\s+(/\S+)\s*\n(.+?)(?=\n###|\n##|\Z)", text, re.DOTALL):
        method, path = m.group(1).upper(), m.group(2).strip()
        desc = m.group(3).strip().split("\n")[0].strip()
        prefix, suffix = _compute_prefix_suffix(path)
        endpoints.append({"method": method, "path": path, "description": desc,
                          "path_prefix": prefix, "path_suffix": suffix})
    return endpoints


def parse_dto_fields_from_spec(
    service: str, overrides: GenerationOverrides | None = None
) -> dict[str, list[dict]]:
    spec_files = list((_get_spec_dir(service, overrides)).glob("*.spec.md"))
    if not spec_files:
        return {}
    text = spec_files[0].read_text(encoding="utf-8")
    sec = re.search(r"##\s*10\.\s*Contratos.*?\n(.*?)(?=\n##\s(?!#)|\Z)", text, re.DOTALL)
    if not sec:
        return {}
    result, key, fields = {}, None, []
    for line in sec.group(1).splitlines():
        sm = re.match(r"###\s*\d+\.\d+\s+(.+)", line)
        if sm:
            if key and fields:
                result[key] = fields
            key, fields = sm.group(1).strip(), []
            continue
        fm = re.match(r"^-\s+(\w+)(.*)", line.strip())
        if fm and key:
            fname = fm.group(1).strip()
            if " " in fname or len(fname) < 3:
                continue
            fields.append({"name": fname, "optional": "opcional" in fm.group(2).lower()})
    if key and fields:
        result[key] = fields
    return result


def _guess_dto_type(name: str) -> str:
    lower = name.lower()
    if lower.endswith("id") and lower != "id":
        return "UUID"
    if lower.endswith("at") or "timestamp" in lower:
        return "OffsetDateTime"
    if lower.startswith("is") or lower.startswith("has"):
        return "Boolean"
    return "String"


def _dto_imports(fields: list[dict]) -> str:
    imps = set()
    for f in fields:
        t = _guess_dto_type(f["name"])
        if t == "UUID":
            imps.add("import java.util.UUID;")
        elif t == "OffsetDateTime":
            imps.add("import java.time.OffsetDateTime;")
    block = "\n".join(sorted(imps))
    return block + "\n\n" if block else ""


def gen_dto_record(dto_name: str, fields: list[dict], pkg: str, kind: str) -> str:
    imports = _dto_imports(fields)
    comps = ",\n".join(f"    {_guess_dto_type(f['name'])} {f['name']}" for f in fields)
    return f"""\
package {pkg}.api.dto;

{imports}/**
 * {kind} DTO — {dto_name}.
 * Generated by be-entity-generator.py from spec.md §10.
 */
public record {dto_name}(
{comps}
) {{}}
"""


def _method_name(method: str, suffix: str) -> str:
    """Generate a REST-semantic handler method name.

    Examples:
        GET  + ""            → list
        POST + ""            → create
        GET  + "/{roleId}"   → getByRoleId
        PUT  + "/{roleId}"   → updateByRoleId
        DELETE + "/{entId}"  → deleteByEntId
        POST + "/evaluate"   → evaluate
        POST + "/{id}/disable" → disableById
        GET  + "/search"     → search
    """
    # ── 1. No suffix — root of the resource ───────────────────────────────────
    if not suffix or suffix == "/":
        return {
            "GET": "list", "POST": "create", "PUT": "replaceAll",
            "DELETE": "deleteAll", "PATCH": "updateAll",
        }.get(method, method.lower())

    # ── 2. Suffix is just a path variable: /{id} ──────────────────────────────
    id_match = re.match(r"^/\{(\w+)\}$", suffix)
    if id_match:
        var = id_match.group(1)
        pascal_var = var[0].upper() + var[1:]
        return {
            "GET": f"getBy{pascal_var}", "PUT": f"updateBy{pascal_var}",
            "DELETE": f"deleteBy{pascal_var}", "PATCH": f"patchBy{pascal_var}",
        }.get(method, f"{method.lower()}By{pascal_var}")

    # ── 3. Suffix ends with a named action after a variable: /{id}/disable ────
    action_match = re.match(r"^/\{\w+\}/([a-z][\w-]*)$", suffix)
    if action_match:
        action = action_match.group(1).replace("-", "_")
        parts = action.split("_")
        camel = parts[0] + "".join(p.capitalize() for p in parts[1:])
        var = re.search(r"\{(\w+)\}", suffix).group(1)
        return f"{camel}By{var[0].upper()}{var[1:]}"

    # ── 4. Named suffix without variables: /evaluate, /search ─────────────────
    if "{" not in suffix:
        clean = suffix.strip("/").replace("/", "_").replace("-", "_")
        parts = clean.split("_")
        camel = parts[0] + "".join(p.capitalize() for p in parts[1:])
        return camel

    # ── 5. Fallback — general suffix with mixed segments ──────────────────────
    clean = re.sub(r"\{(\w+)\}", r"by_\1", suffix).strip("/").replace("/", "_").replace("-", "_")
    parts = clean.split("_")
    camel = parts[0] + "".join(p[0].upper() + p[1:] for p in parts[1:])
    return method.lower() + camel[0].upper() + camel[1:]


def _spring_ann(method: str) -> str:
    return {"GET": "@GetMapping", "POST": "@PostMapping", "PUT": "@PutMapping",
            "DELETE": "@DeleteMapping", "PATCH": "@PatchMapping"}.get(method, "@RequestMapping")


def _to_field(class_name: str) -> str:
    """PascalCase → camelCase field name."""
    return class_name[0].lower() + class_name[1:]


def _words(text: str) -> list[str]:
    """Split PascalCase/camelCase/kebab-case/snake_case into lowercase words."""
    # Insert space before uppercase sequences, then split on non-alpha
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    spaced = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", spaced)
    return [w.lower() for w in re.split(r"[\W_]+", spaced) if w]


def _match_use_case(handler_name: str, ctrl_name: str, ep_path: str,
                    use_cases: list[str]) -> str | None:
    """Score use cases against an endpoint and return the best match.

    Scoring:
    - +2 per use-case word found in the combined token set (handler + ctrl + path)
    - +3 bonus when the handler name starts with the same verb as the use case
      (e.g. handler='start' and use case starts with 'Start')
    Returns None when no use case scores > 0.
    """
    if not use_cases:
        return None

    path_tokens = {p.lower() for p in re.split(r"[/{}\-]", ep_path) if p}
    all_tokens = (set(_words(ctrl_name.replace("Controller", "")))
                  | set(_words(handler_name))
                  | path_tokens)

    best_score, best_uc = -1, None
    for uc in use_cases:
        uc_words = _words(uc.replace("UseCase", ""))
        score = sum(2 for w in uc_words if w in all_tokens)
        # Bonus: handler verb matches the first word of the use case (strongest signal)
        if uc_words and handler_name.lower().startswith(uc_words[0]):
            score += 3
        # Bonus: handler name exactly matches any word inside the use case
        # (e.g. 'refresh' handler matches 'refresh' inside ValidateRefreshHandleUseCase)
        if handler_name.lower() in uc_words[1:]:
            score += 4
        # Bonus: any non-handler path token matches a non-verb word of the use case
        path_only_tokens = all_tokens - set(_words(handler_name))
        if any(t in uc_words[1:] for t in path_only_tokens):
            score += 1
        if score > best_score:
            best_score, best_uc = score, uc

    return best_uc if best_score > 0 else None


def gen_controller(ctrl_name: str, base_path: str, endpoints: list[dict],
                   pkg: str, use_cases: list[str] | None = None) -> str:
    use_cases = use_cases or []

    imports = {"import lombok.RequiredArgsConstructor;", "import lombok.extern.slf4j.Slf4j;",
               "import org.springframework.http.ResponseEntity;",
               "import org.springframework.web.bind.annotation.*;"}
    if any(e["method"] in ("POST", "PUT", "PATCH") for e in endpoints):
        imports.add("import jakarta.validation.Valid;")

    # ── Match each endpoint to a use case ────────────────────────────────────
    handler_to_uc: dict[str, str] = {}
    for ep in endpoints:
        handler = _method_name(ep["method"], ep["path_suffix"])
        uc = _match_use_case(handler, ctrl_name, ep["path"], use_cases)
        if uc:
            handler_to_uc[handler] = uc

    # Unique use cases needed by this controller (in insertion order)
    unique_ucs = list(dict.fromkeys(handler_to_uc.values()))
    for uc in unique_ucs:
        imports.add(f"import {pkg}.application.port.in.{uc};")

    # ── Field declarations ────────────────────────────────────────────────────
    fields_block = ""
    if unique_ucs:
        fields_block = "\n" + "\n".join(
            f"    private final {uc} {_to_field(uc)};" for uc in unique_ucs
        ) + "\n"

    # ── Handler methods ───────────────────────────────────────────────────────
    handlers = []
    for ep in endpoints:
        method, suffix = ep["method"], ep["path_suffix"]
        handler = _method_name(method, suffix)
        ann = _spring_ann(method)
        params = [f"@PathVariable String {p}" for p in re.findall(r"\{(\w+)\}", suffix)]
        if method in ("POST", "PUT", "PATCH"):
            params.append("@Valid @RequestBody Object request")
        path_str = f'("{suffix}")' if suffix else ""

        uc = handler_to_uc.get(handler)
        has_body = method in ("POST", "PUT", "PATCH")
        if uc:
            field = _to_field(uc)
            arg = "request" if has_body else "null"
            body = f"return ResponseEntity.ok({field}.execute({arg}));"
        else:
            body = ('// TODO: delegate to use case port/in — see 02b-be-logic\n'
                    '        throw new UnsupportedOperationException("Not implemented");')

        handlers.append(f"""\
    /** {method} {ep['path']} — {ep['description']} */
    {ann}{path_str}
    public ResponseEntity<?> {handler}({", ".join(params)}) {{
        {body}
    }}""")

    return f"""\
package {pkg}.api.controller;

{chr(10).join(sorted(imports))}

/**
 * REST controller — {ctrl_name}. Base path: {base_path}
 * Generated by be-entity-generator.py from api-contract.md.
 */
@Slf4j
@RestController
@RequestMapping("{base_path}")
@RequiredArgsConstructor
public class {ctrl_name} {{{fields_block}
{chr(10) + chr(10).join(handlers)}
}}
"""


# ── Package-info cleanup ──────────────────────────────────────────────────────

def cleanup_package_info(service_root: Path, pkg_path: str, dry_run: bool) -> int:
    """Remove package-info.java from any package that has at least one real .java file."""
    main_java = service_root / "src" / "main" / "java" / pkg_path
    removed = 0
    for pkg_info in sorted(main_java.rglob("package-info.java")):
        real = [f for f in pkg_info.parent.glob("*.java") if f.name != "package-info.java"]
        if real:
            rel = pkg_info.relative_to(service_root)
            if not dry_run:
                pkg_info.unlink()
            removed += 1
            print(f"{'  [DRY]  ' if dry_run else '    [-] '}{rel}")
    return removed


# ── Main orchestrator ──────────────────────────────────────────────────────────

def generate_for_service(service: str, dry_run: bool = False, force: bool = False,
                         with_use_cases: bool = True, with_controllers: bool = True,
                         with_domain_services: bool = True, with_clients: bool = True,
                         with_messaging: bool = True,
                         allow_duplicate_layer: bool = False,
                         overrides: GenerationOverrides | None = None) -> dict:
    # D-079: project-context-aware lookup before falling back to legacy map.
    pkg_suffix = _resolve_service_package_suffix(service, _CTX)
    if not pkg_suffix:
        print(f"  [!] Unknown service: {service}")
        print(f"      Resolution attempted:")
        print(f"        1. SERVICE_PACKAGES (legacy) — not found")
        if _CTX and getattr(_CTX, "modules", None):
            prefixes = [m.get("prefix") for m in _CTX.modules if m.get("prefix")]
            head = service.split("-", 1)[0].lower()
            print(f"        2. project-context.modules.registry — "
                  f"first-token '{head}' not in {prefixes}")
        else:
            print(f"        2. project-context.modules.registry — "
                  f"not available")
        print(f"      Fix: rename the service to start with a declared "
              f"module prefix (e.g. 'ops-<X>-service' for OPS module), "
              f"OR pass --package <full.package>, OR add the service to "
              f"SERVICE_PACKAGES in this script.")
        return {"created": 0, "skipped": 0, "errors": 1}

    pkg = f"{PKG_BASE}.{pkg_suffix}"
    pkg_path = pkg.replace(".", "/")
    service_root = SERVICES_DIR / service
    main_java = service_root / "src" / "main" / "java" / pkg_path

    if not service_root.exists():
        print(f"  [!] Service directory not found: {service_root}")
        return {"created": 0, "skipped": 0, "errors": 1}

    sql_path = service_root / "src" / "main" / "resources" / "db" / "migration" / "V1__create_initial_schema.sql"
    if not sql_path.exists():
        print(f"  [!] V1 SQL not found — run be-migration-generator.py first")
        return {"created": 0, "skipped": 0, "errors": 1}

    tables = parse_sql_tables(sql_path.read_text(encoding="utf-8"))
    if not tables:
        print(f"  [!] No CREATE TABLE found in {sql_path.name}")
        return {"created": 0, "skipped": 0, "errors": 1}

    created, skipped = [], []

    def _write(path: Path, content: str):
        rel = path.relative_to(service_root)
        # On Windows (case-insensitive FS) a file with different case may exist
        existing = path if path.exists() else None
        if existing is None and path.parent.exists():
            for p in path.parent.iterdir():
                if p.name.lower() == path.name.lower() and p.name != path.name:
                    existing = p
                    break
        if existing and not force:
            skipped.append(rel)
            print(f"    [>] {rel}")
        else:
            if not dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                if existing and existing.name != path.name:
                    # Two-step rename to fix case on Windows case-insensitive FS
                    tmp = existing.parent / f"_tmp_{existing.name}"
                    existing.rename(tmp)
                    tmp.rename(path)
                path.write_text(content, encoding="utf-8")
            created.append(rel)
            print(f"{'  [DRY]  ' if dry_run else '    [+] '}{rel}")

    print(f"\n  {'[DRY] ' if dry_run else ''}Entity generator — {service}")
    print(f"  Package: {pkg}")
    print(f"  Tables:  {len(tables)} ({', '.join(t['table_name'] for t in tables)})")

    # B1 (docs/architecture/shared/workflow-improvements.md): the module-generator
    # base layer (*JpaEntity / *JpaRepository / *RepositoryPort / *RepositoryAdapter)
    # is the CANONICAL persistence layer for standard services. When it already
    # exists for an aggregate, the entity-generator's parallel variant
    # (*Entity / *Repository / *Port / *JpaAdapter, plus its domain model/service)
    # would create a DUPLICATE @Entity mapping the same table — exactly the INTL
    # conflict. Skip the per-table unit for base-owned aggregates. Tables with no
    # base counterpart (brownfield, or tables absent from generator-config.yml) are
    # still emitted in full. --allow-duplicate-layer disables this guard.
    base_entity_dir = main_java / "infrastructure" / "persistence" / "entity"

    def _base_layer_owns(cls_name: str) -> bool:
        if allow_duplicate_layer:
            return False
        return (base_entity_dir / f"{cls_name}JpaEntity.java").exists()

    base_owned: list[str] = []

    # ── 1. Per-table: domain, entity, repo, port/out, adapter ─────────────────
    for t in tables:
        cls = resolve_class_name(t["table_name"], overrides)
        if _base_layer_owns(cls):
            base_owned.append(cls)
            print(f"    [=] {cls}: base layer canônica presente ({cls}JpaEntity) "
                  f"— pulando domain/entity/repo/port/adapter do entity-gen")
            continue
        _write(main_java / "domain" / "model" / f"{cls}.java", gen_domain_record(t, pkg, overrides))
        _write(main_java / "infrastructure" / "persistence" / "entity" / f"{cls}Entity.java", gen_jpa_entity(t, pkg, overrides))
        _write(main_java / "infrastructure" / "persistence" / "repository" / f"{cls}Repository.java", gen_jpa_repository(t, pkg, overrides))
        _write(main_java / "application" / "port" / "out" / f"{cls}Port.java", gen_port_out(t, pkg, overrides))
        _write(main_java / "infrastructure" / "persistence" / "adapter" / f"{cls}JpaAdapter.java", gen_jpa_adapter(t, pkg, overrides))

    if base_owned:
        print(f"\n  [=] {len(base_owned)} agregado(s) com layer base canônica preservada "
              f"(sem duplicação): {', '.join(base_owned)}")

    # ── 2. Domain services — one pure stub per aggregate (table) ──────────────
    if with_domain_services:
        emitted = [t for t in tables if not _base_layer_owns(resolve_class_name(t["table_name"], overrides))]
        print(f"\n  Domain services: {len(emitted)}")
        for t in emitted:
            cls = resolve_class_name(t["table_name"], overrides)
            _write(main_java / "domain" / "service" / f"{cls}DomainService.java",
                   gen_domain_service(t, pkg, overrides))

    # ── 2. Port/in from spec §8 ──────────────────────────────────────────────
    # Always parse — use case list is needed for controller wiring regardless of --no-usecases
    ucs = parse_use_cases_from_spec(service, overrides)
    if with_use_cases and ucs:
        print(f"\n  Use cases from spec §8: {len(ucs)}")
        for uc in ucs:
            _write(main_java / "application" / "port" / "in" / f"{uc}.java",
                   gen_use_case_port_in(uc, pkg))
            svc_name = uc.replace("UseCase", "Service")
            _write(main_java / "application" / "service" / f"{svc_name}.java",
                   gen_use_case_service(uc, pkg))

    # ── 3. Controllers + DTOs from api-contract.md + spec §10 ─────────────────
    if with_controllers:
        endpoints = parse_api_contract(service, overrides)
        if endpoints:
            raw_groups: dict[str, list[dict]] = {}
            for ep in endpoints:
                raw_groups.setdefault(ep["path_prefix"], []).append(ep)
            groups = _merge_singleton_groups(raw_groups)
            dto_fields = parse_dto_fields_from_spec(service, overrides)
            print(f"\n  Controllers: {len(groups)} groups, {len(endpoints)} endpoints")
            for base_path, eps in groups.items():
                # Derive controller name from last 2 meaningful segments
                segs = [s for s in base_path.rstrip("/").split("/") if s and s not in ("api", "v1")]
                word = "_".join(segs[-2:]) if len(segs) >= 2 else (segs[-1] if segs else "Root")
                ctrl = to_pascal(word.replace("-", "_")) + "Controller"
                _write(main_java / "api" / "controller" / f"{ctrl}.java",
                       gen_controller(ctrl, base_path, eps, pkg, ucs))
            if dto_fields:
                print(f"  DTOs from spec §10: {len(dto_fields)} contracts")
                for name, fields in dto_fields.items():
                    clean = re.sub(r"\s+", " ", name.replace("Input", "").replace("Output", "").strip())
                    pascal = "".join(w.capitalize() for w in clean.split())
                    if "input" in name.lower() or "request" in name.lower():
                        _write(main_java / "api" / "dto" / f"{pascal}Request.java", gen_dto_record(f"{pascal}Request", fields, pkg, "Request"))
                    else:
                        _write(main_java / "api" / "dto" / f"{pascal}Response.java", gen_dto_record(f"{pascal}Response", fields, pkg, "Response"))

    # ── 5. Feign clients from spec §11 ───────────────────────────────────────
    if with_clients:
        integrations = parse_integrations_from_spec(service, overrides)
        if integrations:
            print(f"\n  Feign clients from spec §11: {len(integrations)}")
            for intg in integrations:
                cls = to_pascal(intg["service"].replace("-", "_")) + "Client"
                _write(main_java / "infrastructure" / "clients" / f"{cls}.java",
                       gen_feign_client(intg["service"], intg["operations"], pkg))

    # ── 6+7. JMS producers + consumers from event-contracts.md ───────────────
    if with_messaging:
        published, consumed = parse_event_contracts(service, overrides)
        if published:
            print(f"\n  JMS producers: {len(published)}")
            for evt in published:
                cls = to_pascal(evt) + "Producer"
                _write(main_java / "infrastructure" / "messaging" / "producer" / f"{cls}.java",
                       gen_event_producer(evt, pkg))
        if consumed:
            print(f"\n  JMS consumers: {len(consumed)}")
            for evt_dict in consumed:
                cls = to_pascal(evt_dict["name"]) + "Consumer"
                _write(main_java / "infrastructure" / "messaging" / "consumer" / f"{cls}.java",
                       gen_event_consumer(evt_dict["name"], evt_dict["description"], pkg))
        elif (_get_spec_dir(service, overrides) / "contracts" / "event-contracts.md").exists():
            # event-contracts.md exists but consumed events have no named ### entries
            # → generic consumer (audit-trace-capability pattern)
            ec_text = (_get_spec_dir(service, overrides) / "contracts" / "event-contracts.md"
                       ).read_text(encoding="utf-8")
            if "Eventos Consumidos" in ec_text:
                print(f"\n  JMS consumers: 1 (generic — categorical events)")
                svc_pascal = to_pascal(service.replace("-", "_"))
                cls = f"{svc_pascal}EventConsumer"
                _write(main_java / "infrastructure" / "messaging" / "consumer" / f"{cls}.java",
                       gen_generic_consumer(service, pkg))

    # ── 8. Cleanup package-info.java ──────────────────────────────────────────
    print(f"\n  Package-info cleanup:")
    removed = cleanup_package_info(service_root, pkg_path, dry_run)
    if removed == 0:
        print(f"    (none to remove)")

    stats = {"created": len(created), "skipped": len(skipped), "removed": removed, "errors": 0}
    print(f"\n  Created: {len(created)}  |  Skipped: {len(skipped)}  |  Removed: {removed} package-info")
    return stats


# ── CLI ────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="be-entity-generator.py",
        description="Gera domain, persistencia, controllers e DTOs a partir do SQL e spec.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/be-entity-generator.py identity-session-service\n"
            "  python scripts/be-entity-generator.py --force identity-session-service\n"
            "  python scripts/be-entity-generator.py --dry-run all\n"
            "  python scripts/be-entity-generator.py --no-usecases --no-controllers "
            "audit-trace-capability\n"
        ),
    )
    parser.add_argument(
        "service",
        help="Service name (e.g. identity-session-service) or 'all' to "
             "regenerate for every known service.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be generated without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files.",
    )
    parser.add_argument(
        "--no-usecases",
        action="store_true",
        help="Skip generation of use case ports + service stubs.",
    )
    parser.add_argument(
        "--no-controllers",
        action="store_true",
        help="Skip generation of API controllers + DTOs.",
    )
    parser.add_argument(
        "--no-domain-services",
        action="store_true",
        help="Skip generation of domain service stubs.",
    )
    parser.add_argument(
        "--no-clients",
        action="store_true",
        help="Skip generation of Feign client stubs.",
    )
    parser.add_argument(
        "--no-messaging",
        action="store_true",
        help="Skip generation of producer/consumer stubs.",
    )
    parser.add_argument(
        "--allow-duplicate-layer",
        action="store_true",
        help="Emit the per-table persistence/port/adapter layer even when the "
             "module-generator base layer (*JpaEntity) already owns the aggregate. "
             "Default OFF: the base layer is canonical and duplicates are skipped "
             "(see workflow-improvements.md B1).",
    )
    parser.add_argument(
        "--spec-dir",
        metavar="PATH",
        help="Override the default _get_spec_dir() lookup (tool services).",
    )
    parser.add_argument(
        "--package",
        metavar="FULL_PACKAGE",
        help="Override SERVICE_PACKAGES lookup with a full Java package "
             "(e.g. com.acme.identity). Strips PKG_BASE. prefix internally.",
    )
    return parser


def main() -> None:
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()

    parser = _build_parser()
    args = parser.parse_args()

    # D-092: previously this assigned three module globals
    # (_SPEC_DIR_OVERRIDE, _PACKAGE_OVERRIDE, _AGGREGATE_NAME_OVERRIDE) that
    # were read deep in the call stack. Now collected into a single
    # `GenerationOverrides` value flowing explicitly through
    # generate_for_service. `_PACKAGE_OVERRIDE` was a one-shot setup step
    # (register tool service in SERVICE_PACKAGES) and stays as local logic.
    overrides = GenerationOverrides()
    if args.spec_dir:
        overrides.spec_dir = Path(args.spec_dir)
        overrides.aggregate_names = _load_aggregate_overrides(overrides.spec_dir)
    if args.package:
        if args.service != "all" and args.service not in SERVICE_PACKAGES:
            suffix = args.package.removeprefix(PKG_BASE + ".")
            SERVICE_PACKAGES[args.service] = suffix

    name = args.service
    common = dict(
        dry_run=args.dry_run,
        force=args.force,
        with_use_cases=not args.no_usecases,
        with_controllers=not args.no_controllers,
        with_domain_services=not args.no_domain_services,
        with_clients=not args.no_clients,
        with_messaging=not args.no_messaging,
        allow_duplicate_layer=args.allow_duplicate_layer,
        overrides=overrides,
    )

    if name == "all":
        tc, ts, tr = 0, 0, 0
        for svc in SERVICE_PACKAGES:
            sql = SERVICES_DIR / svc / "src" / "main" / "resources" / "db" / "migration" / "V1__create_initial_schema.sql"
            if not sql.exists():
                print(f"\n  [SKIP] {svc}")
                continue
            st = generate_for_service(svc, **common)
            tc += st.get("created", 0)
            ts += st.get("skipped", 0)
            tr += st.get("removed", 0)
        print(f"\n[+] All: {tc} created, {ts} skipped, {tr} package-info removed")
        return

    if name not in SERVICE_PACKAGES:
        print(f"[!] Unknown: {name}")
        sys.exit(1)

    generate_for_service(name, **common)


if __name__ == "__main__":
    main()
