# SPEC-09 — Messaging Architecture (SALE)

## Objective
Define Kafka topology: produced/consumed topics, outbox, ordering, consumer idempotency.

## Scope
- **In:** produced `oportunidade.*`/`compra.*`/`receita.*`/`ltv.*`; consumed `lead.*`/WRKS events; transactional outbox; tenant header propagation.
- **Out:** broker provisioning (AWS MSK), schema registry policy (platform).

## Technical decisions
- Kafka/AWS MSK (ADR-003). Producer behind `SaleEventPublisherPort` in `infrastructure.messaging.producer`; consumers in `infrastructure.messaging.consumer`.
- Transactional outbox: events persisted with the domain change, published after commit.
- `empresaId` travels as a header; consumers set `EmpresaContextHolder` and `clear()` in `finally`.

## Implementation & acceptance criteria (EARS)
### Produced
- `WHEN a domain state change is committed, THE SYSTEM SHALL publish the corresponding event via the transactional outbox (no event without a committed change).`
- `THE SYSTEM SHALL name topics journey-os.<aggregate>.<verb> and include correlationId, empresaId, eventId, occurredAt, source, schemaVersion headers.`
- `THE SYSTEM SHALL NOT include buyer PII beyond contatoRef in any payload.`

### Consumed
- `WHEN journey-os.lead.qualificado is consumed, THE SYSTEM SHALL establish the tenant context from the header before persisting and create/update the oportunidade idempotently.`
- `WHEN journey-os.empresa.provisionada is consumed, THE SYSTEM SHALL seed pipeline/ofertas/attribution-model defaults idempotently.`
- `IF a consumed event was already processed (correlationId, evento), THEN THE SYSTEM SHALL skip it.`
- `THE SYSTEM SHALL process consumed events at-least-once and deduplicate on the idempotency key.`

## Edge cases
- Consumer failure after partial work → reprocess is safe (idempotent keys).
- Out-of-order `lead.score.atualizado` before `lead.qualificado` → tolerated (update no-op if no opportunity yet).

## References
- ADR-003; `contracts/event-contracts.md`; `platform-patterns.md` (outbox, MDC).
