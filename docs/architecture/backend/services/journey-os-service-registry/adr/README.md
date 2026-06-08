# ADR Index — REG (journey-os-service-registry)

> Architecture Decision Records for the Service Registry (Eureka) infra module.
> Module type: **infra / registry** — several "standard service" ADRs resolve to *Not applicable*.

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-001](ADR-001-hexagonal-architecture.md) | Hexagonal architecture (applicability for an infra module) | accepted |
| [ADR-002](ADR-002-eureka-vs-consul.md) | Service discovery: Eureka vs Consul vs K8s-native | accepted |
| [ADR-003](ADR-003-messaging-strategy.md) | Messaging strategy (none for REG) | accepted |
| [ADR-004](ADR-004-multitenant-strategy.md) | Multi-tenancy strategy (tenant-agnostic) | accepted |
| [ADR-005](ADR-005-health-check-strategy.md) | Health-check, self-preservation & HA posture | accepted |

## Relationship Map

- **ADR-001** frames *why the standard hexagonal/ArchUnit rules are mostly N/A* here; it is the lens through which ADR-003 and ADR-004 read as "none".
- **ADR-002** is the foundational choice (Eureka) that justifies the whole module's existence.
- **ADR-005** depends on ADR-002 (Eureka knobs) and feeds the risks in `06-risks-gaps-assumptions.md` (SPOF, eviction).
- **ADR-003** and **ADR-004** record *deliberate absence* of messaging and multi-tenancy.

## Process

Status values: `proposed` | `accepted` | `superseded by ADR-YYY`.
All five ADRs are `accepted` as the baseline for the infra module. Revisit ADR-005 when moving REG to production-grade HA (peer replication).
