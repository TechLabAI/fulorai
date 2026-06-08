# MIG — Structured Brief

> Source brief for the architecture pipeline (vision → specs → backlog → scaffold).
> Module: **MIG** · Service: `journey-os-migrations` · Type: infra (centralized Flyway)

## 1. Canonical name & prefix
- **Prefix:** `MIG`
- **Canonical service name:** `journey-os-migrations`
- **Base package:** `com.journeyos.mig`

## 2. Problem it solves
Journey OS runs as a fleet of independent microservices that must never own or
mutate their own DDL. MIG centralizes and versions **all** database schema (global
schema + one schema per tenant/`empresa`) so every other service can boot with
`spring.jpa.hibernate.ddl-auto=validate` against a schema that is already prepared,
consistent, and reproducible across environments.

## 3. Personas
- **Primary:** Platform / DevOps engineer — owns the database lifecycle, runs
  migrations in CI/CD and locally before any other service starts.
- **Secondary:** Backend developer of any business module (WRKS/LEAD/…) — authors
  `V<N>__<module>_<description>.sql` files but never applies DDL from their own service.

## 4. MVP scope (in)
- Centralized Flyway runner packaged as `journey-os-migrations` (Spring Boot app).
- Global schema `journeyos_global` migrations.
- Per-tenant schema migrations (`schema-per-tenant`, term: `empresa`).
- Versioned, schema-aware migration files: `V<N>__<module>_<description>.sql`,
  organized by path (`db/migration/global/`, `db/migration/empresa/`).
- `bootRun` applies migrations; designed to run **first** in local dev and CI.
- PostgreSQL 15+ with the `pgvector` extension enabled in the global schema.
- Flyway baseline for an empty/fresh database.

## 5. Out of scope (MVP)
- Any business logic, domain aggregates, or REST domain endpoints.
- Destructive automatic rollback (Flyway Undo / down-migrations).
- Dynamic runtime tenant provisioning (only the schema-partitioning **strategy** is
  defined here; live tenant onboarding orchestration belongs to WRKS).
- Data seeding beyond reference/lookup data required by `validate`.

## 6. Mandatory external integrations
- **PostgreSQL 15+ (AWS RDS / Aurora)** — the single managed datastore.
- **pgvector** extension (required by LEAD/INTL embeddings; enabled centrally here).

## 7. TechLab AI services & cross-module events
- **TechLab AI:** none. MIG performs no AI calls.
- **Cross-module events:** none consumed/produced. MIG is a build/boot-time
  infrastructure step, not a runtime event participant. All business modules depend
  on it transitively (their schema is prepared by MIG).

## 8. Domain anchor event
- **"Migration applied"** (`schema migrated/versioned`). MIG has no business domain;
  its central act is advancing a schema to a target version in a controlled, ordered way.
