# SPEC-01 — API Surface · MIG

## Objective
Define the (deliberately minimal) HTTP surface of `journey-os-migrations`.

## Scope
- **In:** Spring Boot Actuator health/info/flyway endpoints, network-restricted.
- **Out:** any business REST API, command/query endpoints, OAuth2-protected resources.

## Technical decisions
- No domain controllers (ADR-001 keeps the hexagonal layout; `api/` holds only health).
- Actuator is the sole surface, used by orchestrators/probes — not by business clients.

## Implementation
- Expose `health` (with `liveness`/`readiness` groups), `info`, and `flyway` actuator IDs.
- `management.endpoints.web.exposure.include=health,info,flyway`.
- Readiness reflects DB reachability + "no failing migration run".
- Bind actuator to an internal port/interface or protect via network policy.

## Edge cases
- Process invoked as a one-shot migration job (no long-lived HTTP): actuator may be
  disabled; readiness is then implicit in the process exit code.
- Unknown actuator endpoint → `404`.

## Acceptance criteria (EARS)
- THE SYSTEM SHALL expose `/actuator/health` reflecting datastore reachability.
- WHILE a migration run is in progress, THE SYSTEM SHALL report readiness `OUT_OF_SERVICE`.
- WHEN all migrations have applied successfully, THE SYSTEM SHALL report readiness `UP`.
- IF a non-listed endpoint is requested, THEN THE SYSTEM SHALL return `404`.
- THE SYSTEM SHALL NOT expose a business REST API.

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Related: ADR-001.
