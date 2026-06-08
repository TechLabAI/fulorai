# SPEC-01 — API Surface (LEAD)

## Objective
Define the REST surface of `lead-service` and its cross-cutting request/response invariants.

## Scope
- **In:** `/api/v1/leads/**`, `/api/v1/surveys/**`, `/api/v1/qualification/**`, `/api/v1/segments/**`; auth, headers, error model.
- **Out:** internal orchestration (SPEC-02), scoring math (SPEC-03), persistence (SPEC-04).

## Technical decisions
- Hexagonal: controllers in `api.controller`, DTO `records` in `api.dto`, `@RestControllerAdvice` →
  RFC 7807 `ProblemDetail` (ADR-001). JWT resource server validates WRKS-issued tokens (SPEC-06).
- Full contract: `contracts/api-contract.md`.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL expose all business endpoints under /api/v1 and require a valid WRKS-issued Bearer JWT (except /actuator/health).`
- `THE SYSTEM SHALL resolve the tenant from the empresa_id JWT claim and SHALL ignore X-Empresa-Id for authorization.`
- `WHEN any request is received without X-Correlation-Id, THE SYSTEM SHALL generate one and echo it in the response.`
- `IF the caller lacks the required lead.* permission, THEN THE SYSTEM SHALL respond 403 application/problem+json.`
- `IF a path resource id does not exist in the current empresa, THEN THE SYSTEM SHALL respond 404 error.code 'lead.lead.nao-encontrado'.`
- `THE SYSTEM SHALL return all error bodies as application/problem+json with a stable error.code.`

## Edge cases
- Capture from public landing pages arrives via GWY/integration with a service token, not anonymously.
- Listing endpoints are read-backed by Elastic; on Elastic outage they degrade to PostgreSQL with reduced filtering.

## Acceptance
- Contract tests assert status codes, permissions and ProblemDetail shape per `api-contract.md`.

## References
- ADR-001, `contracts/api-contract.md`, `shared/contratos/error-model.md`.
