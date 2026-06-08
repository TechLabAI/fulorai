# SPEC-06 — Security (REG · journey-os-service-registry)

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Related: ADR-004, ADR-005.

## Objective

Define the security posture of the Eureka registry for the MVP and the deferred hardening.

## Scope

**In:** network-level access restriction; absence of application auth (documented decision);
no tenant context.
**Out (MVP, deferred to hardening):** dashboard authentication behind an IdP; mTLS between
clients and the registry; RBAC on registry mutations.

## Technical decisions

- **No application-level auth** on `/eureka/*`, `/`, `/actuator/*` in MVP — access is
  restricted at the network boundary (cluster-internal network / security group). This is a
  deliberate scope decision (`01-architectural-vision.md` §5, risk R2).
- **Tenant-agnostic:** no `empresaId`, no JWT tenant claim, no `EmpresaContextHolder` (ADR-004).
- Self-preservation/eviction is an availability control, specified in `SPEC-07` / ADR-005.

## Implementation

- Do **not** add `spring-boot-starter-security` in MVP (no auth layer).
- Deployment restricts inbound 8761 to the internal network; the dashboard is not exposed publicly.
- Actuator exposure limited to `health,info` (no sensitive endpoints like `env`, `beans`).

## Edge cases

- Public exposure of 8761 would leak topology → prevented by network policy, not by app code.
- An unauthenticated `PUT .../status` could force an instance OUT_OF_SERVICE → acceptable
  only because the port is network-restricted; revisit when adding auth.

## Acceptance criteria (EARS)

- THE SYSTEM SHALL restrict inbound access to port 8761 to the internal cluster network (deployment-enforced).
- THE SYSTEM SHALL NOT expose Actuator endpoints beyond `health` and `info`.
- THE SYSTEM SHALL NOT require or process any tenant identifier.
- WHERE production hardening is enabled (future), THE SYSTEM SHALL authenticate dashboard and registry-mutation requests — explicitly deferred beyond MVP (ADR-005).
- IF the registry port is reachable from an untrusted network, THEN THE deployment SHALL be treated as misconfigured (operational guard, not app-enforced in MVP).
