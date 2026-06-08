# 05 — Persistence Model · MIG (`journey-os-migrations`)

> MIG is the owner of the persistence **schema** for the whole platform, but holds no
> business data of its own.

## 1. Schema Strategy
- **Isolation:** `schema-per-tenant` (project term: `empresa`), per `project-context.json`.
- **Global schema:** `journeyos_global` — shared, cross-tenant objects, reference data,
  and PostgreSQL extensions (notably `pgvector`).
- **Tenant schemas:** one schema per `empresa`, holding tenant-scoped business tables.
- MIG applies two migration sets, distinguished by path:
  - `db/migration/global/V*.sql` → `journeyos_global`
  - `db/migration/empresa/V*.sql` → each tenant schema
- Naming (per CLAUDE.md): `V<N>__<module>_<description>.sql`, e.g.
  `V1__wrks_create_workspace.sql`.

## 2. Initial Entities
None owned by MIG. The only MIG-managed tables are Flyway's schema-history tables
(`flyway_schema_history`), created per schema by Flyway itself. Business tables are
authored by each module's developers as migration files but conceptually owned by
that module's data-model spec.

## 3. Migration Strategy
- **Centralized Flyway** in `journey-os-migrations` (NOT per-service Flyway).
- All services run `spring.jpa.hibernate.ddl-auto=validate`; they never create/alter.
- **Forward-only**; applied files are immutable (editing breaks checksums → fail-fast).
- **Baseline** on fresh databases, then apply from `V1` (see ADR-005).
- **Local dev order:** run `./gradlew :journey-os-migrations:bootRun` **first**, then
  start other services.
- **Extension provisioning:** `CREATE EXTENSION IF NOT EXISTS vector;` in the earliest
  global migration.

## 4. Data Lifecycle
- **Retention:** schema-history is permanent (audit of schema evolution).
- **Archival:** none for MIG itself; tenant data lifecycle is owned by the respective
  business modules, not by MIG.
- **Tenant decommission:** dropping a tenant schema is an operational action governed
  by WRKS/platform policy, out of scope for MIG MVP.
