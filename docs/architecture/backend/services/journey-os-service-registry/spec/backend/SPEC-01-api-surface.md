# SPEC-01 — API Surface (REG · journey-os-service-registry)

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Related: `contracts/api-contract.md`.

## Objective

Define the externally observable HTTP surface of REG and the guarantees it provides. The
surface is **entirely framework-provided** (Spring Cloud Netflix Eureka Server + Actuator);
this SPEC pins the expected behavior, not new code.

## Scope

**In:** Eureka `/eureka/*` registration/discovery endpoints; dashboard `/`; Actuator
`health`/`info`; port 8761.
**Out:** any hand-authored REST controller, DTOs, RFC 7807 advice, OAuth2 resource-server
config (none exist in REG); peer-replication endpoints (HA is deferred, ADR-005).

## Technical decisions

- Surface delivered by `@EnableEurekaServer` + `spring-boot-starter-actuator` (ADR-002).
- No hexagonal `api/` layer (ADR-001) — there is nothing to author.
- Port fixed at 8761 (ADR-002 / `02-architecture-blueprint.md`).

## Implementation

- `RegistryApplication` annotated `@SpringBootApplication @EnableEurekaServer`.
- Endpoints and content negotiation handled by the Eureka server auto-configuration.
- Actuator exposure limited to `health,info` via `management.endpoints.web.exposure.include`.

## Edge cases

- Heartbeat for an unknown instance → `404` → client re-registers.
- Malformed registration payload → `4xx` from the Eureka server.
- Dashboard requested before any client registers → renders an empty application list.

## Acceptance criteria (EARS)

- THE SYSTEM SHALL listen on port 8761.
- THE SYSTEM SHALL expose `/eureka/apps` (GET) reflecting currently leased instances.
- WHEN a client registers via `POST /eureka/apps/{appName}`, THE SYSTEM SHALL make that instance retrievable via `GET /eureka/apps/{appName}`.
- THE SYSTEM SHALL serve the dashboard at `GET /`.
- THE SYSTEM SHALL expose `GET /actuator/health` and `GET /actuator/info`.
- THE SYSTEM SHALL NOT expose Actuator endpoints other than `health` and `info`.
