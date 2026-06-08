# 03 — Initial Domain Framing · MIG (`journey-os-migrations`)

> MIG is an infrastructure service with **no business domain**. This framing captures
> only the thin operational vocabulary needed to reason about migration runs.

## 1. Ubiquitous Language
- **Migration** — a versioned, ordered DDL/DML change (`V<N>__<module>_<description>.sql`).
- **Schema target** — which schema a migration applies to: `global` or `empresa`.
- **Global schema** — `journeyos_global`; shared, cross-tenant objects + extensions.
- **Tenant schema** — one schema per `empresa` (the project's tenant term).
- **Baseline** — initial version stamped on a pre-existing/empty database.
- **Schema history** — Flyway's bookkeeping table of applied versions.
- **Drift** — divergence between expected (checksum/order) and actual applied state.

## 2. Aggregates and Entities (initial draft)
None — MIG owns no business aggregates. The only stateful artifacts are Flyway's
schema-history tables (managed by Flyway, not modeled as JPA entities). Optional thin
value objects: `SchemaTarget` (GLOBAL | EMPRESA), `MigrationVersion`.

## 3. Domain Events (initial)
No published/consumed business events. Conceptual operational signals only
(logs/health, not Kafka): `MigrationRunStarted`, `MigrationApplied`,
`MigrationRunCompleted`, `MigrationRunFailed`. These are **not** part of the event
platform and are not on the cross-module event catalog.

## 4. State Transitions (high level)
```
PENDING ──apply──▶ APPLIED
PENDING ──checksum/order mismatch──▶ FAILED (fail-fast, run aborts)
(empty db) ──baseline──▶ BASELINED ──▶ PENDING(V1..)
```

## 5. Invariants
- A given migration version applies **exactly once** per schema (Flyway history).
- Migrations are **forward-only** in normal operation (no destructive Undo).
- Migration order is total and immutable once applied (no editing applied files).
- Every `V*` unambiguously targets exactly one schema class (`global` or `empresa`)
  via its path.
- No business service may apply DDL; downstream is `validate`-only.
