# SPEC-04 — Data Model & Migrations · MIG

## Objective
Define how MIG organizes, orders, and applies migrations across the global schema and the
per-tenant (`empresa`) schemas. This is MIG's core responsibility ("orchestration" =
the migration run).

## Scope
- **In:** migration file layout, naming, schema-aware routing, version ordering, per-tenant
  fan-out, baseline, extension bootstrap.
- **Out:** the content of business tables (owned by each module's `data-model.md`).

## Technical decisions (→ ADRs)
- Centralized Flyway, services `validate`-only → **ADR-002**.
- Path-encoded schema targets (`global/`, `empresa/`) → **ADR-003**.
- `schema-per-tenant` + shared `journeyos_global` → **ADR-004**.
- `baselineOnMigrate` + forward-only → **ADR-005**.

## Implementation
### Layout
```
src/main/resources/db/migration/
├── global/    V*.sql  → applied once to journeyos_global
└── empresa/   V*.sql  → applied to each tenant schema
```
### Naming
- `V<N>__<module>_<description>.sql` (e.g. `V1__mig_enable_extensions.sql`,
  `V10__wrks_create_tenant_registry.sql`).
- Reserved version ranges per owner: see `contracts/data-model.md` §4.

### Flyway configuration (infrastructure/config)
- Two configured locations (or two Flyway instances): one per schema target.
- `baselineOnMigrate=true`, `validateOnMigrate=true`, `outOfOrder=false`,
  `cleanDisabled=true` (no destructive clean in any environment).
- Global run first, then iterate tenant schemas (tenant list from registry; MVP: a
  configured sample tenant).

### Bootstrap (V1 range)
- Enable extensions in `journeyos_global` (`contracts/data-model.md` §0).

## Edge cases
- Fresh/empty database → baseline then apply from V1.
- Pre-existing database → baseline at the agreed version.
- New tenant schema appears → create schema, apply full `empresa/` set to it.
- Partial per-tenant failure → fail fast; record which schema failed.

## Acceptance criteria (EARS)
- THE SYSTEM SHALL apply `global/V*` migrations to `journeyos_global` in version order.
- WHEN tenant schemas are present, THE SYSTEM SHALL apply `empresa/V*` migrations to each
  tenant schema in version order.
- WHEN the target database has no schema history, THE SYSTEM SHALL baseline before applying.
- IF an out-of-order or checksum-mismatched migration is detected, THEN THE SYSTEM SHALL
  fail fast and apply no further migrations.
- THE SYSTEM SHALL keep `clean` disabled so no schema can be destructively wiped.
- THE SYSTEM SHALL enable required extensions (`vector`, `uuid-ossp`, `pgcrypto`,
  `pg_trgm`, `unaccent`) in the global schema before dependent migrations run.

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.
