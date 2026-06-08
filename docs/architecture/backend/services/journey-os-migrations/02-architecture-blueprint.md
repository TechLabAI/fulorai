# 02 — Architecture Blueprint · MIG (`journey-os-migrations`)

## 1. System Boundary
MIG is a **build/boot-time infrastructure service**, not a runtime API. Its boundary
is: "advance the PostgreSQL cluster (global + tenant schemas) to a target Flyway
version, in order, idempotently." It exposes no business HTTP surface — only an
operational health/actuator surface and the Flyway execution itself.

## 2. External Actors and Systems
- **CI/CD pipeline** — invokes MIG before deploying/starting other services.
- **Platform/DevOps engineer** — invokes `./gradlew :journey-os-migrations:bootRun` locally.
- **PostgreSQL 15+ (RDS/Aurora)** — the target datastore (with `pgvector`).
- **All other Journey OS services** — downstream consumers of the prepared schema
  (no direct call; they depend on the result, then run `validate`).

## 3. End-to-End Flows

### Golden path — apply migrations
1. Operator/CI starts MIG (`bootRun`) with DB connection config.
2. Flyway connects, ensures the `pgvector` extension and `journeyos_global` schema exist.
3. Flyway resolves and applies pending `global/V*` migrations in order.
4. For each known tenant (`empresa`) schema, Flyway applies pending `empresa/V*` migrations.
5. Schema history tables record applied versions; MIG exits (or stays up for health checks).
6. Downstream services start with `ddl-auto=validate` and pass validation.

### Alternative — fresh database (baseline)
- No schema history present → Flyway baselines, then applies the full set from V1.

### Alternative — drift / out-of-order detected
- Checksum mismatch or out-of-order version → MIG **fails fast**; CI blocks the merge/deploy.

## 4. Internal Boundaries (hexagonal layers)
Even as an infra service, MIG keeps the canonical layering (reduced):
- **api/** — minimal: actuator/health only (no domain controllers).
- **application/** — orchestration of migration runs (which schemas, what order).
- **domain/** — thin: value objects for schema target/version (no Spring/JPA).
- **infrastructure/** — Flyway configuration, `DataSource`, schema enumeration,
  per-tenant migration execution, config.

## 5. Cross-cutting Concerns
- **Security:** DB credentials via `${VAR_NAME}` only (never hardcoded); MIG needs
  elevated DDL privileges and must run with a dedicated migration role.
- **Observability:** structured logging (SLF4J/`@Slf4j`), MDC correlation; Flyway
  applied-migration log; Spring Boot Actuator health (`/actuator/health`, `flyway` info).
- **Multi-tenancy:** `schema-per-tenant` (term `empresa`) + shared `journeyos_global`
  (see ADR-003, ADR-004). MIG iterates tenant schemas to apply per-tenant migrations.
- **Idempotency:** Flyway schema history guarantees each version applies exactly once.
