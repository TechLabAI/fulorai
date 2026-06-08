# 04 — Backend Architecture Direction · MIG (`journey-os-migrations`)

## 1. Stack
- **Java 21**, **Spring Boot 3.5.x**, **Gradle (Kotlin DSL)**.
- **Flyway** (core migration engine) + **PostgreSQL 15+** driver.
- **pgvector** extension (provisioned in `journeyos_global`).
- **Spring Boot Actuator** for health/info (incl. Flyway endpoint).
- No JPA entities, no Artemis/Kafka, no Eureka client required for the migration run
  (MIG is a boot-time step; registry participation optional and not in MVP).

## 2. Service Boundary
**Single service**, deliberately reduced. MIG is the only component allowed to apply
DDL. It is not decomposed; its sole responsibility is executing the centralized
migration set against the global and tenant schemas.

## 3. Package Organization
Base package `com.journeyos.mig`, canonical hexagonal layout (reduced for infra):
```
com.journeyos.mig/
├── api/                 # actuator/health only — no domain controllers
├── application/
│   └── service/         # MigrationRunner orchestration (which schemas / order)
├── domain/
│   └── model/           # SchemaTarget, MigrationVersion (POJOs, zero Spring/JPA)
└── infrastructure/
    ├── config/          # FlywayConfig, DataSource, MigrationProperties
    └── persistence/     # tenant-schema enumeration, per-schema Flyway execution
```
ArchUnit rules still apply: domain free of Spring/JPA, base package mandatory
(RULE-01, RULE-02, RULE-09). Most rules are trivially satisfied (no controllers,
repositories, Feign clients, or `@Transactional` use cases in MVP).

## 4. Hub Service Dependencies
None at runtime. MIG depends only on the PostgreSQL cluster. All business services
depend on MIG **transitively** (their schema must be prepared first) — enforced
operationally by run order, not by code coupling.

## 5. External Integrations
- **PostgreSQL (RDS/Aurora):** sole external system; requires a migration role with
  DDL + `CREATE EXTENSION` privileges. Connection via `${VAR_NAME}` env config.

## 6. Async vs Sync Decisions
- Migration execution is **synchronous and blocking** by design: the run must
  complete (or fail fast) before downstream services start.
- No messaging. No async flows. The only "fan-out" is iterating tenant schemas,
  performed sequentially and deterministically.
