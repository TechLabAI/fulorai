# SPEC-10 — Integrations (LEAD)

## Objective
Define how `lead-service` integrates with WRKS, TechLab AI, Elasticsearch, MIG and Eureka.

## Scope
- **In:** WRKS (auth, JWKS, events), TechLab AI (`qualification`), Elasticsearch (`leads`), MIG (schema), Eureka (discovery).
- **Out:** downstream consumers (event-only — see `hub-integration.md`).

## Technical decisions
- Feign + Resilience4j for WRKS; JWKS for JWT validation. TechLab AI HTTP client behind a port,
  fail-open. Elastic via direct Java client. MIG owns the schema (validate). Eureka for discovery.

## Acceptance criteria (EARS)
### WRKS
- `THE SYSTEM SHALL validate JWTs using the WRKS JWKS endpoint and SHALL authorize via WRKS AccessDecision (cached).`
- `IF WRKS is unavailable and no cache exists, THEN THE SYSTEM SHALL fail closed (503).`

### TechLab AI (`qualification`)
- `WHERE the assist flag is enabled, THE SYSTEM SHALL call TechLab AI for free-text signals and SHALL fail open to the deterministic score on any failure.`
- `THE SYSTEM SHALL use DTOs generated from integrations/techlab-ai/openapi.json and SHALL NOT call an AI provider directly.`

### Elasticsearch (`leads`)
- `WHEN a lead's score or segment changes, THE SYSTEM SHALL (re)index the lead document in the leads index.`
- `IF Elasticsearch is unavailable, THEN THE SYSTEM SHALL preserve the transactional write and retry indexing out-of-band.`

### MIG / Eureka
- `THE SYSTEM SHALL run ddl-auto=validate against the MIG-provisioned emp_<slug> schema and SHALL register with Eureka.`

## Edge cases
- TechLab AI snapshot empty (P3 blocked) → assist flag disabled; deterministic path unaffected.
- Elastic schema/mapping for `leads` defined with the elastic-stack overlay (controlled fields, no PII).

## References
- `contracts/{integration-contracts,techlab-ai-integration,hub-integration}.md`; ADR-003/004; `project-context.json` (stack.elastic).
