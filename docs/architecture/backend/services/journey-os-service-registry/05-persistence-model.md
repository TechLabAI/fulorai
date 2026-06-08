# 05 — Persistence Model (REG · journey-os-service-registry)

> **REG is stateless from a database perspective.** This document exists to record that
> explicitly so the backlog and scaffold stages generate **no** entities, repositories,
> or Flyway migrations for this module.

## 1. Schema Strategy

**No schema.** REG owns no `journeyos_global` objects and no per-`empresa` (`emp_*`) objects. It does not connect to PostgreSQL. It is excluded from the centralized `journey-os-migrations` scope.

## 2. Initial Entities

**None.** The only "store" is Eureka's **in-memory registry** of service instances and leases, fully managed by Spring Cloud Netflix. It is not a Journey OS entity and is not persisted.

## 3. Migration Strategy

**Not applicable.** REG contributes no migration scripts. `journey-os-migrations` does not provision anything for REG.

## 4. Data Lifecycle

- The registry is **volatile**: on restart it is empty and rebuilds as clients re-register and heartbeat.
- No retention, archival, backup, or GDPR/LGPD data concerns — REG stores no personal or tenant data, only ephemeral service-instance metadata (app name, host, port, status).
