# API Contract — journey-os-service-registry (REG)

> The endpoints below are **provided by Spring Cloud Netflix Eureka Server** — they are
> **not hand-authored** by Journey OS. This document records the surface as a contract so
> clients and operators know what to rely on. There are no `@RestController` classes in
> `com.journeyos.reg`. EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Eureka registration & discovery (`/eureka/*`)

| Verb | Path | Purpose | Success |
|---|---|---|---|
| `POST` | `/eureka/apps/{appName}` | Register an instance (body: instance metadata) | `204 No Content` |
| `PUT` | `/eureka/apps/{appName}/{instanceId}` | Renew lease (heartbeat) | `200 OK` |
| `DELETE` | `/eureka/apps/{appName}/{instanceId}` | De-register an instance | `200 OK` |
| `GET` | `/eureka/apps` | Full registry (all apps + instances) | `200 OK` |
| `GET` | `/eureka/apps/{appName}` | Instances of one app | `200 OK` |
| `PUT` | `/eureka/apps/{appName}/{instanceId}/status?value={STATUS}` | Override instance status | `200 OK` |

Content negotiation: XML (default) and JSON (`Accept: application/json`). Clients use the
Spring Cloud Eureka **client library**, not raw HTTP, in practice.

### Invariants (EARS)

- WHEN a client sends `POST /eureka/apps/{appName}` with valid instance metadata, THE SYSTEM SHALL register the instance and return `204`.
- WHEN a client sends `PUT /eureka/apps/{appName}/{instanceId}` for a known instance, THE SYSTEM SHALL renew the lease and return `200`.
- IF a heartbeat (`PUT`) targets an unknown instance, THEN THE SYSTEM SHALL return `404` so the client re-registers.
- WHEN a client sends `DELETE /eureka/apps/{appName}/{instanceId}`, THE SYSTEM SHALL remove the instance from the registry.
- THE SYSTEM SHALL serve `GET /eureka/apps` reflecting the current set of leased instances.

## 2. Dashboard

| Verb | Path | Purpose |
|---|---|---|
| `GET` | `/` | Eureka HTML dashboard (human operator view) |

- WHEN an operator requests `GET /`, THE SYSTEM SHALL return the Eureka dashboard listing registered applications and their status.

## 3. Actuator

| Verb | Path | Purpose | Success |
|---|---|---|---|
| `GET` | `/actuator/health` | Liveness/readiness probe | `200` `{"status":"UP"}` |
| `GET` | `/actuator/info` | Build/version info | `200` |

- THE SYSTEM SHALL expose `GET /actuator/health` returning `UP` while the server is operational.
- WHERE the orchestrator performs liveness/readiness probing, THE SYSTEM SHALL be probeable via `GET /actuator/health`.

## 4. Errors

Eureka returns standard HTTP status codes (`404` for unknown app/instance, `4xx` for
malformed registration). RFC 7807 `ProblemDetail` does **not** apply — there is no
hand-authored controller/`@RestControllerAdvice` in REG.

## 5. Auth

No application-level OAuth2 on the Eureka/dashboard endpoints in MVP. Access is restricted
at the network layer (cluster-internal). See `SPEC-06-security.md` and ADR-005. No tenant
claim is required or honored (REG is tenant-agnostic, ADR-004).
