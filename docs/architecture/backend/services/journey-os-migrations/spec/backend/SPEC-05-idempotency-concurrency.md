# SPEC-05 — Idempotency & Concurrency · MIG

## Objective
Guarantee that migrations apply exactly once and that concurrent MIG invocations cannot
corrupt the schema or its history.

## Scope
- **In:** Flyway schema-history semantics, advisory locking, concurrent-run safety,
  re-run safety.
- **Out:** application-level business idempotency (no business operations exist here).

## Technical decisions
- Idempotency is delegated to **Flyway schema history** (`flyway_schema_history` per
  schema): a version recorded as applied is never re-applied.
- Concurrency is guarded by **Flyway's database lock** (advisory/table lock), preventing
  two runners from migrating the same schema simultaneously.

## Implementation
- On each run, Flyway acquires the lock per schema, computes pending vs. applied by
  version + checksum, applies pending in order, releases the lock.
- Extension bootstrap uses `CREATE EXTENSION IF NOT EXISTS` (idempotent regardless).
- Per-tenant fan-out locks each tenant schema independently.

## Edge cases
- Two CI jobs start MIG at once → the second blocks on the lock, then sees no pending work.
- A crashed run leaves the lock held → Flyway lock is released on connection drop; a stale
  state surfaces as a failed/pending entry resolved on the next run (repair if needed).
- Re-running MIG with no new files → no-op (all versions already applied).

## Acceptance criteria (EARS)
- THE SYSTEM SHALL apply each migration version exactly once per schema.
- WHILE another MIG instance holds the migration lock for a schema, THE SYSTEM SHALL wait
  for the lock rather than apply migrations concurrently.
- WHEN MIG is re-run with no pending migrations, THE SYSTEM SHALL complete as a no-op.
- IF a checksum of an already-applied migration changed, THEN THE SYSTEM SHALL fail
  validation and not proceed.

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Related: ADR-002, ADR-005.
