#!/usr/bin/env python3
"""
be-migration-generator.py — Gera migracao Flyway V1 a partir do data-model.md do servico.

Le o arquivo contracts/data-model.md da spec do servico e gera:
  V1__create_initial_schema.sql  — com CREATE TABLE para cada tabela do modelo

Uso:
    python scripts/be-migration-generator.py <SERVICE_NAME>
    python scripts/be-migration-generator.py authorization-policy-service

    python scripts/be-migration-generator.py --issue <ISSUE_ID>
    python scripts/be-migration-generator.py --issue APS-008

Flags:
    --dry-run     Imprime o SQL gerado sem criar o arquivo
    --force       Sobrescreve arquivo existente

Economia: elimina ~3.000-5.000 tokens de LLM (DDL boilerplate).
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

# Project context
try:
    from be_context_helper import load_project_context
    _CTX = load_project_context()
except (ImportError, Exception):
    _CTX = None

GLOBAL_SCHEMA = _CTX.global_schema if _CTX and _CTX.global_schema else "global"


# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = ROOT / "docs" / "architecture" / "backend" / "services"
SERVICES_DIR = ROOT / "backend" / "services"
PLANS_DIR = ROOT / "docs" / "architecture" / "backend" / "plans"

# ── Service catalog ─────────────────────────────────────────────────────────────

ISSUE_PREFIX_TO_SERVICE = {
    "ISS": "identity-session-service",
    "APS": "authorization-policy-service",
    "TCS": "tenant-context-service",
    "ADM": "hub-administration-service",
    "TCE": "tool-catalog-entitlement-service",
    "AUD": "audit-trace-capability",
    "GWY": "hub-api-gateway",
}


def _resolve_service_from_issue_prefix(prefix: str, ctx) -> str | None:
    """D-080 (+ D-081 field rename): resolve a 3-5-letter issue prefix to a
    service name.

    Resolution order:
      1. Legacy `ISSUE_PREFIX_TO_SERVICE[prefix]` (hub-platform compat).
      2. project-context.modules.registry — find a module whose `prefix`
         (case-insensitive) matches; return its `backendService` (optional
         field, shared convention with be-bdd-generator + be-infra-
         generator), or convention `<prefix-lower>-service`.

    Returns None when neither matches; caller surfaces an actionable error.
    """
    p_upper = prefix.upper()
    if p_upper in ISSUE_PREFIX_TO_SERVICE:
        return ISSUE_PREFIX_TO_SERVICE[p_upper]
    if not ctx or not getattr(ctx, "modules", None):
        return None
    for m in ctx.modules:
        if (m.get("prefix") or "").upper() == p_upper:
            return m.get("backendService") or f"{p_upper.lower()}-service"
    return None


def service_from_issue(issue_id: str) -> str | None:
    """Find service that owns this issue, by parsing the issue id's prefix
    (D-080: project-aware via modules.registry).
    """
    prefix = issue_id.split("-")[0].upper()
    return _resolve_service_from_issue_prefix(prefix, _CTX)


def service_from_plan(issue_id: str) -> str | None:
    plan_path = PLANS_DIR / f"plan-{issue_id}.md"
    if not plan_path.exists():
        return None
    text = plan_path.read_text(encoding="utf-8")
    m = re.search(r"\|\s*[Ss]ervi[çc]o\s*\|\s*([^\|]+)\|", text)
    return m.group(1).strip() if m else None


# ── SQL blocks parser (canonical SQL block format) ──────────────────────────────


def parse_sql_blocks(spec_dir: Path) -> list[str]:
    """Extrai blocos ```sql``` do data-model.md em ordem de aparição.

    Canonical format (definido em be-architect-specs.md):
    cada entidade tem um bloco SQL executável embarcado no markdown. O DDL
    sai direto desses blocos, sem inferência de tipos.

    Retorna lista vazia se não houver blocos `sql` — caller cai no fallback
    de inferência por sufixo (`parse_data_model`) para compatibilidade.
    """
    dm = spec_dir / "contracts" / "data-model.md"
    if not dm.exists():
        return []
    text = dm.read_text(encoding="utf-8")
    # Casa ```sql, ```SQL, ``` sql (com espaço); aceita newline opcional após o info string
    return re.findall(r"```\s*sql\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)


def generate_migration_from_sql_blocks(service: str, blocks: list[str]) -> str:
    """Concatena blocos sql do data-model.md em V1__create_initial_schema.sql."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"""\
-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   {service}
-- Generated: {now} by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de {len(blocks)} blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

"""
    body = "\n\n".join(b.rstrip() for b in blocks)
    return header + body + "\n"


# ── Data model parser (legacy fallback — inferência por sufixo) ───────────────


def parse_data_model(spec_dir: Path) -> tuple:
    """Parse data-model.md, return (schema_name, {table: [field, ...]})."""
    dm = spec_dir / "contracts" / "data-model.md"
    if not dm.exists():
        return GLOBAL_SCHEMA, {}

    text = dm.read_text(encoding="utf-8")

    # Extract schema name
    schema = GLOBAL_SCHEMA
    sm = re.search(r"^##\s*Schema\s*\n+[-*]\s*(\w+)", text, re.MULTILINE)
    if sm:
        schema = sm.group(1).strip()

    # Extract tables + fields
    tables = {}
    current = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("### "):
            current = s[4:].strip()
            tables[current] = []
        elif s.startswith("- ") and current:
            field = s[2:].strip()
            if re.match(r"^[a-z][a-z0-9_]*$", field):
                tables[current].append(field)

    return schema, tables


# ── SQL type resolver ──────────────────────────────────────────────────────────

def sql_type(field: str, table: str, fields: list) -> str:
    """Determine PostgreSQL column type for a field name."""
    # Primary key — first *_id in the table is the PK
    pk = next((f for f in fields if f.endswith("_id")), None)
    if field == pk:
        return "UUID"

    if field.endswith("_id"):
        return "UUID"
    if field.endswith("_at") or field.endswith("_date"):
        return "TIMESTAMPTZ"
    if field.endswith("_status"):
        return "VARCHAR(50)"
    if field.endswith("_type"):
        return "VARCHAR(50)"
    if field.endswith("_code"):
        return "VARCHAR(100)"
    if field.endswith("_name"):
        return "VARCHAR(255)"
    if field.endswith("_key"):
        return "VARCHAR(255)"
    if field.endswith("_expression"):
        return "TEXT"
    if field.endswith("_payload") or field.endswith("_data") or field.endswith("_metadata"):
        return "JSONB"
    if field.endswith("_version"):
        return "BIGINT"
    if field.endswith("_count") or field.endswith("_number"):
        return "INTEGER"
    if field.endswith("_enabled") or field.endswith("_active"):
        return "BOOLEAN"
    return "VARCHAR(255)"


def sql_nullability(field: str, fields: list) -> str:
    """NOT NULL for most columns; nullable for optional/audit columns."""
    nullable_suffixes = ("_at", "_payload", "_data", "_metadata", "_result",
                         "_revoked_at", "_last_restore_at")
    pk = next((f for f in fields if f.endswith("_id")), None)
    if field == pk:
        return "NOT NULL"
    if any(field.endswith(s) for s in nullable_suffixes):
        # created_at is NOT NULL (has default), revoked_at/expires_at may be nullable
        if field == "created_at" or field == "issued_at":
            return "NOT NULL DEFAULT now()"
        if field == "updated_at":
            return "NOT NULL DEFAULT now()"
        return ""  # nullable
    return "NOT NULL"


def sql_default(field: str, col_type: str) -> str:
    """Return DEFAULT clause for a column."""
    if field == "created_at" or field == "issued_at":
        return " DEFAULT now()"
    if field == "updated_at":
        return " DEFAULT now()"
    if col_type == "UUID" and not field.endswith("_id") or field == next(iter([field]), ""):
        return ""
    if col_type == "UUID":
        return " DEFAULT gen_random_uuid()"
    return ""


# ── DDL generator ──────────────────────────────────────────────────────────────


def generate_create_table(schema: str, table: str, fields: list) -> str:
    """Generate CREATE TABLE statement for a table."""
    if not fields:
        return f"-- WARNING: no fields parsed for table {table}\n"

    pk_field = next((f for f in fields if f.endswith("_id")), None)
    col_lines = []

    for field in fields:
        col_type = sql_type(field, table, fields)
        nullability = sql_nullability(field, fields)

        if field == pk_field:
            col_lines.append(f"  {field:<35} {col_type:<15} DEFAULT gen_random_uuid() NOT NULL")
        elif col_type in ("TIMESTAMPTZ",) and field in ("created_at", "issued_at", "updated_at"):
            col_lines.append(f"  {field:<35} {col_type:<15} DEFAULT now() NOT NULL")
        elif not nullability:
            # nullable
            col_lines.append(f"  {field:<35} {col_type}")
        else:
            col_lines.append(f"  {field:<35} {col_type:<15} {nullability}")

    # Primary key constraint
    pk_constraint = ""
    if pk_field:
        pk_constraint = f",\n  CONSTRAINT pk_{table} PRIMARY KEY ({pk_field})"

    cols_block = ",\n".join(col_lines) + pk_constraint

    schema_prefix = f"{schema}." if schema and schema != "public" else ""

    return (
        f"CREATE TABLE IF NOT EXISTS {schema_prefix}{table} (\n"
        f"{cols_block}\n"
        f");\n"
    )


def generate_indexes(schema: str, table: str, fields: list) -> list:
    """Generate useful indexes for a table."""
    indexes = []
    schema_prefix = f"{schema}." if schema and schema != "public" else ""

    # Index on created_at for time-range queries
    if "created_at" in fields or "issued_at" in fields:
        ts_field = "created_at" if "created_at" in fields else "issued_at"
        indexes.append(
            f"CREATE INDEX IF NOT EXISTS idx_{table}_{ts_field} "
            f"ON {schema_prefix}{table}({ts_field});"
        )

    # Index on *_status for status filtering
    status_fields = [f for f in fields if f.endswith("_status")]
    for sf in status_fields[:1]:  # max one status index
        indexes.append(
            f"CREATE INDEX IF NOT EXISTS idx_{table}_{sf} "
            f"ON {schema_prefix}{table}({sf});"
        )

    # Index on tenant_id if present (multi-tenant query pattern)
    if "tenant_id" in fields:
        indexes.append(
            f"CREATE INDEX IF NOT EXISTS idx_{table}_tenant_id "
            f"ON {schema_prefix}{table}(tenant_id);"
        )

    return indexes


def generate_migration_sql(service: str, schema: str, tables: dict) -> str:
    """Generate the full V1 migration SQL."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"""\
-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   {service}
-- Schema:    {schema}
-- Generated: {now} by be-migration-generator.py
--
-- Edit column types / constraints before applying to a real database.
-- Run: ./gradlew :{service}:integrationTest to validate against Testcontainers.
-- =============================================================================

"""
    if not tables:
        return header + f"-- WARNING: no tables found in data-model.md for {service}\n"

    # Schema creation (skip for public)
    schema_block = ""
    if schema and schema != "public":
        schema_block = f"CREATE SCHEMA IF NOT EXISTS {schema};\n\n"

    blocks = []
    for table, fields in tables.items():
        create_sql = generate_create_table(schema, table, fields)
        indexes = generate_indexes(schema, table, fields)
        block = create_sql
        if indexes:
            block += "\n".join(indexes) + "\n"
        blocks.append(block)

    return header + schema_block + "\n".join(blocks)


# ── Main ───────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="be-migration-generator.py",
        description="Gera migracao Flyway V1 a partir do data-model.md do servico.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/be-migration-generator.py authorization-policy-service\n"
            "  python scripts/be-migration-generator.py --issue APS-008 --dry-run\n"
            "  python scripts/be-migration-generator.py <service> --spec-dir <path>\n"
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
        "--dry-run",
        action="store_true",
        help="Print the generated SQL to stdout without writing the file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite V1__create_initial_schema.sql if it already exists.",
    )
    parser.add_argument(
        "--spec-dir",
        metavar="PATH",
        help="Override the default SPECS_DIR/<service>-spec lookup "
             "(useful for tool services living outside docs/architecture).",
    )
    return parser


def main():
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()

    parser = _build_parser()
    args = parser.parse_args()

    # D-089: same XOR check as D-088. mutually_exclusive_group + nargs="?"
    # has ambiguous "not provided" semantics, so enforce manually.
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

    dry_run = args.dry_run
    force = args.force

    if args.spec_dir:
        spec_dir = Path(args.spec_dir)
    else:
        spec_dir = SPECS_DIR / f"{service}-spec"
    if not spec_dir.exists():
        print(f"[!] Spec directory not found: {spec_dir}")
        sys.exit(1)

    # Caminho preferido: blocos ```sql``` embarcados em data-model.md (canonical format).
    sql_blocks = parse_sql_blocks(spec_dir)

    print(f"[+] Migration generator — {service}")
    if sql_blocks:
        print(f"    Modo: extração de {len(sql_blocks)} blocos ```sql``` de data-model.md")
        sql = generate_migration_from_sql_blocks(service, sql_blocks)
    else:
        # Fallback legado: inferência por sufixo (compatibilidade com docs antigos).
        schema, tables = parse_data_model(spec_dir)
        print(f"    Modo: legacy fallback (sem blocos sql) — inferência por sufixo")
        print(f"    Schema: {schema}")
        print(f"    Tables: {len(tables)} ({', '.join(tables)})")
        sql = generate_migration_sql(service, schema, tables)
    print()

    if dry_run:
        print("=== DRY RUN — SQL output ===")
        print(sql)
        return

    # Output path
    service_root = SERVICES_DIR / service
    if not service_root.exists():
        print(f"[!] Service directory not found: {service_root}")
        print(f"    Run scaffold for *-001 issue first.")
        sys.exit(1)

    migration_dir = service_root / "src" / "main" / "resources" / "db" / "migration"
    migration_dir.mkdir(parents=True, exist_ok=True)

    migration_file = migration_dir / "V1__create_initial_schema.sql"

    if migration_file.exists() and not force:
        print(f"[>] Migration file already exists: {migration_file.relative_to(ROOT)}")
        print(f"    Use --force to overwrite, or --dry-run to preview.")
        sys.exit(0)

    migration_file.write_text(sql, encoding="utf-8")
    print(f"[+] Generated: {migration_file.relative_to(ROOT)}")
    print()
    print("    IMPORTANT: Review generated SQL before applying:")
    print("    - Verify column types match your domain requirements")
    print("    - Add FK constraints where applicable")
    print("    - Add UNIQUE constraints if needed")
    print("    - Validate with: ./gradlew :{service}:integrationTest".format(service=service))


if __name__ == "__main__":
    main()



