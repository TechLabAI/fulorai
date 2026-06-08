---
service: journey-os-migrations
module: MIG
type: infra
basePackage: com.journeyos.mig
status: draft
relatedAdrs: [ADR-001, ADR-002, ADR-003, ADR-004, ADR-005]
---

# journey-os-migrations — Service Spec (entry point)

> Centralized Flyway migration runner for Journey OS. Owns **all** schema DDL for the
> global schema (`journeyos_global`) and every tenant (`empresa`) schema. No business
> domain, no business HTTP API. See `_brief.md` and docs `01..06` for vision.

## Map of specs

| Doc | Purpose |
|-----|---------|
| `contracts/api-contract.md` | Operational surface only (actuator/health); no business API. |
| `contracts/data-model.md` | Foundational DDL: extensions + schema bootstrap (canonical `sql` blocks). |
| `contracts/event-contracts.md` | None — MIG publishes/consumes no platform events. |
| `contracts/hub-integration.md` | None at runtime; transitive dependency only. |
| `contracts/integration-contracts.md` | PostgreSQL (RDS/Aurora) — the sole external system. |
| `events/event-catalog.md` | Empty catalog (no events). |
| `spec/backend/SPEC-01-api-surface.md` | Actuator/health surface, no domain endpoints. |
| `spec/backend/SPEC-04-data-model-migrations.md` | Migration layout, ordering, naming, fan-out. |
| `spec/backend/SPEC-05-idempotency-concurrency.md` | Flyway history, locking, exactly-once. |
| `spec/backend/SPEC-06-security.md` | Migration role, secrets via `${VAR}`. |
| `spec/backend/SPEC-07-observability-health.md` | Logs, actuator, Flyway info. |
| `diagrams/c4-*.puml` | Context / container / component. |

## SPECs intentionally omitted (with reason)
- **SPEC-02 core orchestration** → folded into SPEC-04 (the "orchestration" is the
  migration run itself).
- **SPEC-03 sub-feature** → none for MVP.
- **SPEC-08 BDD scenarios / `tests/cucumber/`** → N/A: infra service, no EARS business
  domain; the A3 specs-validate (EARS→BDD) step is **N/A** for MIG.
- **SPEC-09 messaging** → N/A: no Artemis/Kafka participation.
- **SPEC-10 integrations** → reduced to `integration-contracts.md` (PostgreSQL only).

## Acceptance (service-level, EARS)
- THE SYSTEM SHALL apply all pending migrations for `journeyos_global` and every known
  tenant schema, in version order, before exiting successfully.
- WHEN a checksum mismatch or out-of-order version is detected, THE SYSTEM SHALL fail
  fast and exit non-zero without applying further migrations.
- IF database credentials are missing, THEN THE SYSTEM SHALL fail to start with a clear
  configuration error.

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.
