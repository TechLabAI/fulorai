---
service: journey-os-service-registry
module: REG
type: infra/registry
package: com.journeyos.reg
port: 8761
status: draft
specSet: reduced
ears: true
sourceVision:
  - 01-architectural-vision.md
  - 02-architecture-blueprint.md
  - 04-backend-architecture-direction.md
adrs:
  - adr/ADR-001-hexagonal-architecture.md
  - adr/ADR-002-eureka-vs-consul.md
  - adr/ADR-003-messaging-strategy.md
  - adr/ADR-004-multitenant-strategy.md
  - adr/ADR-005-health-check-strategy.md
---

# REG — Service Registry Spec (journey-os-service-registry)

> **Reduced spec set.** REG is an infrastructure module (a Netflix Eureka Server) with
> **no business domain**: no data model, no domain events, no messaging, no multi-tenancy,
> no hand-authored REST API. Accordingly, several standard SPECs are **N/A** (see map).
> EARS notation guide: `docs/architecture/backend/standards/ears-notation.md`.

## Purpose

Provide and document the contract for the Journey OS service-discovery authority: a
standalone Eureka Server on port **8761** with which every backend microservice registers
and from which GWY and Feign clients resolve instances by logical name.

## Spec map

| Artifact | Present | Notes |
|---|---|---|
| `setup-local.md` | ✅ | Port + env + run/verify commands |
| `contracts/api-contract.md` | ✅ | Eureka REST surface + dashboard + Actuator (framework-provided) |
| `contracts/integration-contracts.md` | ✅ | Client registration contract (what clients must send) |
| `events/event-catalog.md` | ✅ (empty) | No events published/consumed |
| `contracts/data-model.md` | ❌ N/A | No database (see `05-persistence-model.md`) |
| `contracts/event-contracts.md` | ❌ N/A | No messaging (ADR-003) |
| `contracts/techlab-ai-integration.md` | ❌ N/A | No AI usage |
| `contracts/hub-integration.md` | ❌ N/A | No outbound Hub/Feign calls |
| `tests/cucumber/*.feature` | ❌ N/A | No domain behavior; specs-validate (EARS→BDD) is N/A for REG |
| `SPEC-01-api-surface.md` | ✅ | Eureka + Actuator surface |
| `SPEC-06-security.md` | ✅ | Network restriction; dashboard auth out of scope |
| `SPEC-07-observability-health.md` | ✅ | Actuator health/info, logging, dashboard |
| `SPEC-02/03/04/05/08/09/10` | ❌ N/A | No orchestration/data/idempotency/BDD/messaging/integrations domain |
| `diagrams/c4-{context,container,component}.puml` | ✅ | C4 views |

## Acceptance criteria (module-level, EARS)

- THE SYSTEM SHALL expose the Eureka registration/discovery endpoints under `/eureka/*` on port 8761.
- THE SYSTEM SHALL serve the Eureka dashboard at `GET /`.
- THE SYSTEM SHALL expose `GET /actuator/health` returning `UP` when the server is operational.
- THE SYSTEM SHALL NOT register itself as a Eureka client (`register-with-eureka=false`, `fetch-registry=false`).
- WHEN a client posts a valid registration, THE SYSTEM SHALL store the instance and make it discoverable.
- WHEN a registered instance stops sending heartbeats beyond the lease-expiry window, THE SYSTEM SHALL evict the instance (subject to self-preservation, ADR-005).

## Next stage

→ `/be-architect-backlog REG`
