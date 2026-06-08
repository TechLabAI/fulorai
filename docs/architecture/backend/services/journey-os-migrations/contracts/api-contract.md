# API Contract · MIG (`journey-os-migrations`)

> MIG exposes **no business REST API**. It is a boot-time migration runner. The only
> HTTP surface is the operational actuator endpoints (optional, when the process stays
> up for health checks). This file exists to satisfy the pipeline contract and to make
> the "no domain API" decision explicit.

## 1. Business resources
**None.** There are no domain resources, no CRUD, no command/query endpoints.

## 2. Operational surface (actuator only)

| Path | Verb | Purpose | Auth |
|------|------|---------|------|
| `/actuator/health` | GET | Liveness/readiness; includes DB + Flyway status. | internal/network only |
| `/actuator/health/liveness` | GET | Liveness probe. | internal |
| `/actuator/health/readiness` | GET | Readiness probe (DB reachable, migrations applied). | internal |
| `/actuator/info` | GET | Build + applied-migration summary. | internal |
| `/actuator/flyway` | GET | Flyway applied/pending migrations (when enabled). | internal |

### Invariants (EARS)
- THE SYSTEM SHALL expose `/actuator/health` returning `200` with status `UP` only when
  the datastore is reachable and no migration run is currently failing.
- WHILE a migration run is in progress, THE SYSTEM SHALL report readiness as `OUT_OF_SERVICE`.
- IF an actuator endpoint other than those listed is requested, THEN THE SYSTEM SHALL
  return `404`.
- THE SYSTEM SHALL NOT expose actuator endpoints to the public internet (network-restricted).

## 3. Errors (RFC 7807)
No domain errors. Operational/management errors follow Spring Boot defaults; actuator
endpoints are not part of any business `ProblemDetail` contract.

## 4. Auth
No OAuth2 scopes (no business API). Actuator access is restricted at the network layer
(internal only). See `SPEC-06-security.md`.

## 5. Mandatory headers
None required for the actuator surface. MIG does not participate in `X-Correlation-Id`
request propagation (it is not called by business clients).
