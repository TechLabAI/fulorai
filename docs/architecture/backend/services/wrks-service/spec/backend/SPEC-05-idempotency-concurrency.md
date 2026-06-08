# SPEC-05 — Idempotency & Concurrency (WRKS)

## Objective
Guarantee safe behaviour under retries and concurrency for provisioning, refresh rotation,
version bumps, and audit consumption.

## Scope
- **In:** empresa provisioning saga, refresh-token rotation, modelo_acesso_versao bump, audit consume.
- **Out:** business-service idempotency.

## Technical decisions
- Transactional outbox for event publish (ADR-003). Optimistic concurrency on RBAC mutations.

## Implementation & acceptance criteria (EARS)

### Provisioning saga
- `WHEN empresa creation is retried for an existing slug in PROVISIONANDO, THE SYSTEM SHALL NOT create a duplicate schema and SHALL re-trigger MIG idempotently.`
- `WHEN MIG confirms a schema already created, THE SYSTEM SHALL transition the empresa to ATIVA exactly once.`

### Refresh rotation
- `WHEN a refresh token is used, THE SYSTEM SHALL atomically invalidate it and issue a new one.`
- `IF a refresh token is presented after it was rotated, THEN THE SYSTEM SHALL reject it (iam.refresh-invalido) AND SHALL flag possible reuse.`

### Version bump
- `WHEN concurrent RBAC mutations occur, THE SYSTEM SHALL serialize the modelo_acesso_versao bump so the version is strictly increasing (no lost updates).`

### Audit consume
- `IF an event with the same (correlationId, evento) was already persisted, THEN THE SYSTEM SHALL skip it (idempotent).`
- `THE SYSTEM SHALL process audit events at-least-once and deduplicate on the idempotency key.`

## Edge cases
- Outbox publish failure → retry without double-applying the DB change. Redis blacklist loss → revocation degrades to token TTL.

## References
- ADR-003, ADR-005, `contracts/event-contracts.md` §3.
