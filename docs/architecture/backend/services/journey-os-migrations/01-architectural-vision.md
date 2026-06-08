# 01 — Architectural Vision · MIG (`journey-os-migrations`)

> Type: infra (centralized Flyway) · Base package: `com.journeyos.mig`

## 1. Intent
Provide a single, authoritative, version-controlled source of truth for **all**
database schema in Journey OS — the global schema and every tenant (`empresa`)
schema — so that no business microservice ever owns its DDL. Every other service
boots with `ddl-auto=validate` against a schema MIG has already prepared.

## 2. Problem Statement
With ~7 business services plus infra services sharing one PostgreSQL cluster under a
`schema-per-tenant` model, letting each service manage its own DDL would produce
drift, ordering hazards, and irreproducible environments. MIG removes that risk by
owning schema evolution centrally and deterministically.

## 3. Personas
- **Platform / DevOps engineer (primary):** runs MIG first in CI/CD and locally;
  guarantees the cluster is at the expected version before services start.
- **Backend developer (secondary):** contributes `V<N>__<module>_<description>.sql`
  files reviewed via PR; never applies DDL from a business service.

## 4. MVP Scope (in)
- Spring Boot runner that executes Flyway against PostgreSQL on `bootRun`.
- Global schema (`journeyos_global`) migration set.
- Per-tenant (`empresa`) migration set under a dedicated path.
- Schema-aware, ordered, versioned migration files.
- `pgvector` extension provisioning in the global schema.
- Flyway baseline for fresh databases.

## 5. Out of Scope (MVP)
- Business domain logic, aggregates, domain REST endpoints.
- Destructive auto-rollback / down-migrations.
- Runtime dynamic tenant onboarding orchestration (owned by WRKS).
- Application-level data seeding beyond reference data needed for `validate`.

## 6. Architectural Principles
- **Single source of schema truth** — DDL lives only here.
- **Forward-only migrations** — no destructive Undo in normal flow.
- **Schema-aware ordering** — each `V*` declares the schema it targets via path.
- **Reproducibility** — same migration set yields the same schema in every env.
- **Hexagonal compliance** — even as infra, respects `com.journeyos.mig` base
  package and the project's ArchUnit-enforced boundaries (ADR-001).
- **Validate downstream** — services never mutate schema; only `validate`.

## 7. Success Signals
- A fresh PostgreSQL reaches the expected version by running MIG alone.
- Every business service starts cleanly with `ddl-auto=validate` (zero validation
  errors) after MIG runs.
- A new tenant schema can be created and migrated to current version deterministically.
- CI fails the build on any migration drift or out-of-order version.
