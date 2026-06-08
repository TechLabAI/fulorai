# ADR-004 — Multi-tenancy strategy (schema-per-tenant)

**Status:** accepted

## Context
The platform is multi-tenant (term: `empresa`). The global decision (`project-context
.json.multiTenancy`, global ADR-003) is `schema-per-tenant` with a shared
`journeyos_global` schema. MIG must materialize this isolation model at the DDL level.

## Decision
MIG implements `schema-per-tenant`:
- Shared cross-tenant objects, reference data, and extensions live in `journeyos_global`.
- Each `empresa` gets its own schema containing tenant-scoped business tables.
- MIG applies global migrations once and per-tenant migrations to every tenant schema.
- The authoritative tenant list is read from a **global tenant registry** (owned by WRKS)
  — to be finalized in specs (Gap G1). For MVP, a global schema plus one sample tenant
  schema is sufficient to validate the model.

## Alternatives considered
- **Single shared schema with `tenant_id` column (row-level):** rejected — weaker
  isolation, conflicts with the project-wide decision.
- **Database-per-tenant:** rejected — operationally heavy at this stage; not the chosen
  isolation strategy.

## Consequences
- (+) Strong logical isolation per tenant; aligns with the platform decision.
- (+) Per-tenant migration path (ADR-003) maps cleanly to this model.
- (−) Migration cost grows with tenant count (Risk R1).
- (−) Requires a reliable tenant-enumeration source (Gap G1).

## References
- Global ADR-003 (multi-tenancy); `project-context.json.multiTenancy`.
- ADR-003 (schema partitioning).
