# SPEC-01 — API Surface (WRKS)

## Objective
Define the REST surface of `wrks-service` under `/api/v1/iam/**` and its invariants.

## Scope
- **In:** session, access, empresa, usuario, papel, business-unit, team, auditoria endpoints.
- **Out:** UI; token validation at the edge (GWY); migration DDL (MIG).

## Technical decisions
- Spring MVC (not reactive) — ADR-001. JWT RS256 — ADR-005. ProblemDetail RFC 7807 (`shared/contratos/error-model.md`).
- Full contract: `contracts/api-contract.md`.

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL expose all IAM endpoints under the base path /api/v1/iam.`
- `THE SYSTEM SHALL return application/problem+json for every error response.`
- `THE SYSTEM SHALL require a Bearer JWT for all endpoints except sessao/login, sessao/refresh, sessao/restore and .well-known/jwks.json.`
- `WHEN a request lacks a required X-Correlation-Id, THE SYSTEM SHALL generate one and echo it in the response and logs.`
- `THE SYSTEM SHALL derive empresa_id from the JWT claim and SHALL NOT accept it from request body or path for tenant-scoped operations.`
- `IF a request body fails bean validation, THEN THE SYSTEM SHALL respond 422 category validation with error.fields populated.`

## Edge cases
- Missing/expired JWT → 401 `iam.token-expirado`. Stale model version → 401 `iam.sessao.versao-desatualizada`.
- `X-Empresa-Id` header present but different from claim → ignored (claim wins); logged.

## References
- `contracts/api-contract.md`, ADR-005, `shared/rbac/session-policy.md`.
