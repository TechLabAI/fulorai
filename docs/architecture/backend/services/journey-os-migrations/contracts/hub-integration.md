# Hub Integration · MIG (`journey-os-migrations`)

## Runtime dependencies on other services
**None.** MIG makes no Feign/HTTP calls to any Journey OS service. It depends only on the
PostgreSQL cluster (see `integration-contracts.md`).

## Services that depend on MIG
**All of them — transitively.** Every business and infra service requires its schema to
be prepared by MIG and runs with `spring.jpa.hibernate.ddl-auto=validate`. This is an
**operational ordering** dependency (run MIG first), not a code/network coupling.

```
MIG (apply schema) ──prepares──▶ journeyos_global + empresa_* schemas
                                          │
   WRKS · LEAD · ASST · JRNY · COMM · SALE · INTL ──boot with ddl-auto=validate
```

## Tenant registry (forward dependency)
The authoritative list of tenant (`empresa`) schemas is expected to live in a global
registry table owned by **WRKS**. MIG will read it to drive the per-tenant migration
fan-out once WRKS exists. For MVP, a single sample tenant schema is sufficient
(Gap G1 in `06-risks-gaps-assumptions.md`).
