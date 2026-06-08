# SPEC-10 — Integrations (SALE)

## Objective
Define integrations with WRKS, LEAD, Elasticsearch, the checkout source, MIG and Eureka.

## Scope
- **In:** WRKS (Feign auth + events), LEAD (events), Elasticsearch (revenue/campaign), checkout ingestion, MIG (schema), Eureka (discovery).
- **Out:** TechLab AI (not used in MVP), downstream consumers (event-only, ADR-003).

## Technical decisions
- WRKS `AccessEvaluateClient` (`@FeignClient(name="wrks-service")`) in `infrastructure.clients`, Resilience4j (timeout/circuit breaker), deny-by-default on open.
- Elastic `direct-java-client` adapter (`SaleSearchPort`) indexing `revenue-events`/`campaign-events`; best-effort, never blocks revenue.
- Checkout: inbound `POST /compras` (service token) in MVP; INTL Event Platform post-MVP.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL authorize sale.* via WRKS AccessDecision and SHALL validate JWT via WRKS JWKS.`
- `WHILE the WRKS circuit is open, THE SYSTEM SHALL deny authorization and respond 503 'sale.dependencia.indisponivel'.`
- `WHEN a compra is confirmed or revenue attributed, THE SYSTEM SHALL project documents to revenue-events asynchronously.`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL retain the transactional record and retry indexing without failing the request.`
- `THE SYSTEM SHALL boot only after MIG has provisioned emp_<slug> (ddl-auto=validate).`
- `THE SYSTEM SHALL register with Eureka for service discovery.`
- `THE SYSTEM SHALL NOT call any AI provider or payment gateway directly.`

## Edge cases
- LEAD absent: opportunities created via API; golden path automation degraded, not broken.
- Checkout duplicate webhook: idempotent ingestion (SPEC-05).

## References
- ADR-003, ADR-005; `contracts/hub-integration.md`, `contracts/integration-contracts.md`; `platform-patterns.md`.
