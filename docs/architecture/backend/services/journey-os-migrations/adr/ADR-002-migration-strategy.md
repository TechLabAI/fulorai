# ADR-002 — Centralized Flyway migration strategy

**Status:** accepted

## Context
In a fleet of microservices sharing one PostgreSQL cluster, schema ownership can be
per-service (each service runs its own Flyway/`ddl-auto=update`) or centralized. Per
CLAUDE.md, all migrations for all schemas must live in one place and services must run
`ddl-auto=validate`.

## Decision
Use a **single centralized Flyway runner** (`journey-os-migrations`) that owns every
migration for every schema. Business services never apply DDL; they run with
`spring.jpa.hibernate.ddl-auto=validate`. Migration files follow
`V<N>__<module>_<description>.sql` and are organized by path per schema target
(`db/migration/global/`, `db/migration/empresa/`).

## Alternatives considered
- **Per-service Flyway:** rejected — produces drift, ordering hazards across cross-module
  FKs, and irreproducible environments.
- **`ddl-auto=update` per service:** rejected — non-deterministic schema, no audit trail,
  unsafe for production and multi-tenancy.
- **Liquibase:** rejected — Flyway is the project standard; no compelling reason to diverge.

## Consequences
- (+) One ordered version history; reproducible across environments.
- (+) Clear ownership; services are schema-read-only at boot.
- (−) MIG must run **before** any service (operational ordering dependency).
- (−) Cross-team coordination on a shared version sequence.

## References
- CLAUDE.md — "Migrations (CENTRALIZED in journey-os-migrations)".
- `docs/architecture/backend/standards/platform-patterns.md` (centralized Flyway).
