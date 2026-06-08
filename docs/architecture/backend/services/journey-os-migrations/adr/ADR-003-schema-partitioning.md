# ADR-003 — Schema partitioning (global vs per-tenant paths)

**Status:** accepted

## Context
Journey OS uses `schema-per-tenant` with a shared global schema `journeyos_global`.
The centralized runner must apply two distinct migration sets — cross-tenant objects
and per-tenant objects — without ambiguity about where each migration lands.

## Decision
Partition migrations by **path-encoded schema target**:
- `db/migration/global/V*.sql` → applied once to `journeyos_global`.
- `db/migration/empresa/V*.sql` → applied to **each** tenant (`empresa`) schema.
Flyway is configured with separate locations and a target-schema strategy per set. Each
file name still carries the owning module: `V<N>__<module>_<description>.sql`.

## Alternatives considered
- **Single flat migration folder with schema-qualified DDL:** rejected — fragile,
  easy to target the wrong schema, hard to fan out per tenant.
- **Naming-convention-only (schema in filename, single folder):** rejected — less
  explicit than path separation and error-prone for the per-tenant loop.

## Consequences
- (+) Unambiguous schema targeting; clean per-tenant fan-out.
- (+) Reviewers immediately see whether a change is global or tenant-scoped.
- (−) Two locations to manage; the per-tenant loop needs the tenant list (Gap G1).

## References
- `project-context.json.multiTenancy` (schema-per-tenant, `journeyos_global`).
- 05-persistence-model.md; ADR-004.
