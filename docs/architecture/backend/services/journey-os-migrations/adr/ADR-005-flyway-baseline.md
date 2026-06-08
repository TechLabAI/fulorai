# ADR-005 — Flyway baseline & forward-only policy

**Status:** accepted

## Context
The cluster will be initialized fresh in some environments and may pre-exist in others.
We must decide how MIG handles an empty/legacy database and whether destructive
rollbacks are allowed.

## Decision
- **Baseline on migrate:** enable Flyway `baselineOnMigrate` so a fresh/empty database is
  stamped at baseline then migrated from `V1`. Pre-existing databases are baselined at the
  agreed version.
- **Forward-only:** no Flyway Undo / destructive down-migrations in normal operation. A bad
  migration is remediated by a new corrective forward migration.
- **Immutability:** applied migration files are never edited (checksum stability); CI
  validates and fails fast on drift or out-of-order versions.

## Alternatives considered
- **Undo/down-migrations enabled:** rejected — destructive, risky in multi-tenant prod,
  and a Flyway Teams feature; forward-only corrective migrations are safer.
- **No baseline (require empty DB only):** rejected — too rigid for environments with any
  pre-existing state.

## Consequences
- (+) Safe, auditable, reproducible schema evolution.
- (+) Fresh environments bootstrap automatically.
- (−) No instant rollback; mistakes require a forward fix (acceptable for DDL safety).

## References
- ADR-002 (centralized Flyway); 05-persistence-model.md.
- Flyway `baselineOnMigrate`, `validateOnMigrate`.
