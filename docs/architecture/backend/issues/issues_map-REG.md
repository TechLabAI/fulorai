# Issues Map — REG (journey-os-service-registry)

> Infra/registry module. Reduced backlog: **5 functional issues, 0 integration issues.**
> No `INT-REG-*` issues — REG has no inbound integration code to build (it only hosts the
> Eureka surface; the *client* registration contract is honored by other services).

## By issue

| Issue | Title | Priority | Estimate | Depends on |
|---|---|---|---|---|
| REG-001 | Scaffold Eureka Server application | P1 | S | — |
| REG-002 | Base application.yml (port, self-registration off, actuator) | P1 | S | REG-001 |
| REG-003 | Profile overlays + self-preservation tuning | P2 | S | REG-002 |
| REG-004 | Health probe + structured logging | P3 | S | REG-002 |
| REG-005 | Reduced ArchUnit check (RULE-09 base package) | P4 | S | REG-001 |

## By SPEC

| SPEC | Issues |
|---|---|
| SPEC-01-api-surface | REG-001, REG-002 |
| SPEC-06-security | (covered via REG-002 actuator exposure; network restriction is deployment-level) |
| SPEC-07-observability-health | REG-002, REG-003, REG-004 |

## By priority

| Priority | Issues | Theme |
|---|---|---|
| P1 | REG-001, REG-002 | Scaffold + base config |
| P2 | REG-003 | Profiles + self-preservation |
| P3 | REG-004 | Observability + health |
| P4 | REG-005 | Architecture guard (RULE-09) |

## By layer

| Layer | Issues |
|---|---|
| infrastructure/config (app + profiles) | REG-002, REG-003, REG-004 |
| entry point | REG-001 |
| test/architecture | REG-005 |
| api/application/domain | _(none — not applicable, ADR-001)_ |

## Numbering note

Sequence REG-001..REG-005, no gaps. No `INT-REG-*` issues issued (rationale above).
