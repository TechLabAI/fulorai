# SPEC-05 — Idempotency & Concurrency (LEAD)

## Objective
Guarantee safe behaviour under retries and concurrency for capture, scoring and event consumption.

## Scope
- **In:** capture dedup, score recompute idempotency, rule activation atomicity, event publish/consume.
- **Out:** global IAM concurrency (WRKS).

## Technical decisions
- Capture idempotent by `chave_natural` (DB unique + upsert). Score idempotent by
  `(lead_id, versao_regra, hash_sinais)`. Transactional outbox for publish (ADR-003). Optimistic
  locking on `regra_qualificacao` activation.

## Implementation & acceptance criteria (EARS)
### Capture
- `WHEN a lead is captured concurrently with the same chave_natural, THE SYSTEM SHALL persist exactly one lead (no duplicate) and merge attributes.`

### Score recompute
- `WHEN a recompute runs with an unchanged (versao_regra, hash_sinais) for a lead, THE SYSTEM SHALL be a no-op and SHALL NOT create a new maturity_score row.`
- `WHEN concurrent recomputes occur for the same lead, THE SYSTEM SHALL serialize them so the persisted score reflects the latest signals (no lost update).`

### Rule activation
- `WHEN a rule version is activated, THE SYSTEM SHALL deactivate the previous active version in the same transaction (exactly one active rule).`

### Event consume
- `IF an event with the same (correlationId, evento) was already processed, THEN THE SYSTEM SHALL skip it (idempotent consume).`
- `THE SYSTEM SHALL process consumed events at-least-once and deduplicate on the idempotency key.`

### Publish
- `THE SYSTEM SHALL publish domain events via a transactional outbox so a DB commit failure publishes nothing and a publish retry does not double-apply DB changes.`

## Edge cases
- Outbox publish failure → retry without re-applying the DB change.
- Elastic index update failure → retried out-of-band; transactional state remains correct.

## References
- ADR-003, ADR-005; `contracts/event-contracts.md` §3; `contracts/data-model.md`.
