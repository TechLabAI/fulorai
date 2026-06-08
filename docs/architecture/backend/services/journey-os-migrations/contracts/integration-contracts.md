# Integration Contracts · MIG (`journey-os-migrations`)

## External systems

### PostgreSQL 15+ (AWS RDS / Aurora) — sole external system
- **Purpose:** the target datastore whose schema MIG owns and evolves.
- **Driver:** PostgreSQL JDBC; Flyway core as the migration engine.
- **Connection:** JDBC URL, user, password supplied via environment (`${VAR_NAME}`) —
  never hardcoded (see `SPEC-06-security.md`).
- **Privileges required:** a dedicated **migration role** with `CONNECT`, `CREATE` on the
  database, `CREATE SCHEMA`, DDL on target schemas, and `CREATE EXTENSION`.
- **Extensions used:** `vector` (pgvector), `uuid-ossp`, `pgcrypto`, `pg_trgm`, `unaccent`.

## Auth
- Database username/password (migration role). No OAuth2 / mTLS to external APIs (MIG
  calls no external HTTP services).

## Rate limits / SLA
- Not applicable (single batch DB connection). The relevant SLA is that the migration run
  completes (or fails fast) **before** dependent services start.

## Fallback / circuit breaker / retry
- **No circuit breaker / Resilience4j** — a migration run is not a resilient runtime call;
  it must either succeed completely or fail fast.
- **Connection retry:** bounded startup retry on transient DB-unavailable (configurable),
  then fail fast.
- **On migration failure:** abort the run, exit non-zero, leave schema history consistent;
  remediation is a corrective forward migration (ADR-005), never an automatic destructive
  rollback.

### Behavior (EARS)
- WHEN the database is unreachable at startup, THE SYSTEM SHALL retry up to the configured
  limit and then fail fast with a non-zero exit.
- IF a migration fails mid-run, THEN THE SYSTEM SHALL stop, record the failure in schema
  history, and not attempt subsequent migrations.
