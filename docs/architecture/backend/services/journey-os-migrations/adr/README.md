# ADRs · MIG (`journey-os-migrations`)

Architectural Decision Records for the centralized migrations service.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Hexagonal architecture | accepted |
| ADR-002 | Centralized Flyway migration strategy | accepted |
| ADR-003 | Schema partitioning (global vs per-tenant paths) | accepted |
| ADR-004 | Multi-tenancy strategy (schema-per-tenant) | accepted |
| ADR-005 | Flyway baseline & forward-only policy | accepted |

## Relations Map

```
ADR-001 (hexagonal) ── foundational, applies to all services
ADR-002 (central Flyway) ──▶ depends on ADR-004 (multi-tenancy shape)
ADR-003 (schema partitioning) ──▶ refines ADR-002 + ADR-004
ADR-004 (multi-tenancy) ── aligns with global ADR-003-multi-tenancy
ADR-005 (baseline/forward-only) ──▶ operational policy on top of ADR-002
```

## Process
- Status lifecycle: `proposed` → `accepted` → `superseded by ADR-YYY`.
- One ADR per decision with a visible tradeoff. No loose architectural prose.
- ADRs here are service-local; they refine the global ADRs under
  `docs/architecture/backend/adr/` (hexagonal, modular-monolith, multi-tenancy).
