# SPEC-10 — Integrations (WRKS)

## Objective
Define external integrations and resilience: Keycloak, Redis, MIG, Elasticsearch, Eureka.

## Scope
- **In:** Keycloak OIDC, Redis cache, MIG provisioning trigger, Elastic audit index, Eureka.
- **Out:** TechLab AI (**none** — `contracts/techlab-ai-integration.md`).

## Technical decisions
- Resilience4j (retry/circuit-breaker). Cache is optimization, not source of truth. No AI provider
  called directly from Java (platform rule). Details: `contracts/integration-contracts.md`.

## Acceptance criteria (EARS)
- `WHEN exchanging an OIDC code, THE SYSTEM SHALL call Keycloak and map the sub claim to usuario.idp_subject.`
- `IF Keycloak is unreachable, THEN THE SYSTEM SHALL fail login with 502 upstream_error AND SHALL NOT bypass authentication.`
- `WHILE Redis is available, THE SYSTEM SHALL cache sessions and AccessDecision; IF unavailable, THEN it SHALL fall back to PostgreSQL.`
- `WHEN an empresa is created, THE SYSTEM SHALL trigger MIG over HTTP with retry/backoff and a circuit breaker.`
- `WHEN an event is audited, THE SYSTEM SHALL index it into Elastic audit-events with retry on failure.`
- `THE SYSTEM SHALL register with Eureka for discovery.`
- `THE SYSTEM SHALL NOT call any AI provider directly.`

## Edge cases
- MIG timeout (30s) → empresa stays PROVISIONANDO; retriable. Elastic down → PostgreSQL row remains truth.

## References
- `contracts/integration-contracts.md`, `contracts/hub-integration.md`, `contracts/techlab-ai-integration.md`.
