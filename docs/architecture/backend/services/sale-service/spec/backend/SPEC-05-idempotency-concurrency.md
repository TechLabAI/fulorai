# SPEC-05 — Idempotency & Concurrency (SALE)

## Objective
Guarantee safe behaviour under retries and concurrency for purchase ingestion, attribution, opportunity creation and event consumption.

## Scope
- **In:** purchase dedup, re-attribution idempotency, model activation atomicity, opportunity-from-lead dedup, event publish/consume.
- **Out:** global IAM concurrency (WRKS).

## Technical decisions
- Purchase idempotent by `(id_externo, origem)` (DB unique + upsert). Re-attribution idempotent by `(compra_id, versao_modelo)`. Transactional outbox for publish (ADR-003). Optimistic locking on `modelo_atribuicao` activation.

## Implementation & acceptance criteria (EARS)
### Purchase ingestion
- `WHEN the same (id_externo, origem) is registered concurrently, THE SYSTEM SHALL persist exactly one compra and recognize revenue once.`
- `WHEN a previously confirmed (id_externo, origem) is re-registered, THE SYSTEM SHALL return the existing compra (duplicada=true) and SHALL NOT republish journey-os.compra.confirmada.`

### Re-attribution
- `WHEN re-attribution runs for a compra with an unchanged active model version, THE SYSTEM SHALL be a no-op.`
- `WHEN concurrent attributions occur for the same compra, THE SYSTEM SHALL serialize them so the persisted breakdown reflects the active model (no lost update).`

### Model activation
- `WHEN an attribution model version is activated, THE SYSTEM SHALL deactivate the previous active version in the same transaction (exactly one active model).`

### Opportunity from lead
- `IF a lead.qualificado event is consumed for a lead that already has an open oportunidade, THEN THE SYSTEM SHALL update it and SHALL NOT create a duplicate.`

### Event consume / publish
- `IF an event with the same (correlationId, evento) was already processed, THEN THE SYSTEM SHALL skip it (idempotent consume).`
- `THE SYSTEM SHALL publish domain events via a transactional outbox so a DB commit failure publishes nothing and a publish retry does not double-apply DB changes.`

## Edge cases
- Outbox publish failure → retry without re-applying the DB change.
- Elastic index update failure → retried out-of-band; transactional state remains correct.
- Reversal/cancel of an already-attributed compra → revenue and LTV adjusted exactly once.

## References
- ADR-003, ADR-005; `contracts/event-contracts.md` §3; `contracts/data-model.md`.
