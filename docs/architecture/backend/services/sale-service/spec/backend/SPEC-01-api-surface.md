# SPEC-01 — API Surface (SALE)

## Objective
Define the REST surface of `sale-service` and its cross-cutting request/response invariants.

## Scope
- **In:** `/api/v1/oportunidades/**`, `/api/v1/ofertas/**`, `/api/v1/compras/**`, `/api/v1/atribuicao/**`, `/api/v1/ltv/**`; auth, headers, error model.
- **Out:** pipeline orchestration (SPEC-02), attribution/LTV math (SPEC-03), persistence (SPEC-04).

## Technical decisions
- Hexagonal: controllers in `api.controller`, DTO `records` in `api.dto`, `@RestControllerAdvice` →
  RFC 7807 `ProblemDetail` (ADR-001). JWT resource server validates WRKS-issued tokens (SPEC-06).
- Purchase ingestion (`POST /compras`) is service-token mediated via GWY, never anonymous.
- Full contract: `contracts/api-contract.md`.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL expose all business endpoints under /api/v1 and require a valid WRKS-issued Bearer JWT (except /actuator/health).`
- `THE SYSTEM SHALL resolve the tenant from the empresa_id JWT claim and SHALL ignore X-Empresa-Id for authorization.`
- `WHEN any request is received without X-Correlation-Id, THE SYSTEM SHALL generate one and echo it in the response.`
- `IF the caller lacks the required sale.* permission, THEN THE SYSTEM SHALL respond 403 application/problem+json.`
- `IF a path resource id does not exist in the current empresa, THEN THE SYSTEM SHALL respond 404 with a stable error.code.`
- `THE SYSTEM SHALL return all error bodies as application/problem+json with a stable error.code.`

## Edge cases
- Checkout/gateway ingestion arrives via GWY/integration with a service token, not anonymously.
- Listing/funnel endpoints are read-backed by Elastic; on Elastic outage they degrade to PostgreSQL with reduced filtering.

## Acceptance
- Contract tests assert status codes, permissions and ProblemDetail shape per `api-contract.md`.

## References
- ADR-001, `contracts/api-contract.md`, `shared/contratos/error-model.md`.
