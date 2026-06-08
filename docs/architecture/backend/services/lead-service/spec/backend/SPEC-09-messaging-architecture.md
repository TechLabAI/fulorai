# SPEC-09 — Messaging Architecture (LEAD)

## Objective
Define the Kafka producer/consumer architecture for `lead-service`.

## Scope
- **In:** produced `lead.*` events, consumed WRKS events, outbox, idempotent consume, context propagation.
- **Out:** payload contracts (`contracts/event-contracts.md`).

## Technical decisions
- Kafka (AWS MSK), topic = `journey-os.<aggregate>.<verb>` (ADR-003). Producers/consumers in
  `infrastructure.messaging/{producer,consumer}`; domain publishes via `LeadEventPublisherPort`.
  Transactional outbox for publish; idempotent consume by `(correlationId, evento)`.

## Produced
`journey-os.lead.capturado`, `journey-os.lead.qualificado` (anchor), `journey-os.lead.score.atualizado`,
`journey-os.lead.segmento.alterado`.

## Consumed (from WRKS)
`journey-os.empresa.provisionada` (seed per tenant), `journey-os.modelo.acesso.alterado` (cache invalidation).

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL publish each domain event exactly once via the outbox, carrying correlationId, empresaId, eventId, occurredAt, source, schemaVersion.`
- `WHEN journey-os.empresa.provisionada is consumed, THE SYSTEM SHALL idempotently seed default rule and segments for the new tenant.`
- `WHEN journey-os.modelo.acesso.alterado is consumed, THE SYSTEM SHALL invalidate affected AccessDecision cache entries.`
- `WHEN consuming, THE SYSTEM SHALL set EmpresaContextHolder from the empresaId header and clear() in finally.`
- `IF a consumed event was already processed (correlationId, evento), THEN THE SYSTEM SHALL skip it.`

## Edge cases
- Consumer lag / replays handled by idempotent consume. Schema evolution: additive→minor bump; breaking→`.v2` topic.

## References
- ADR-003; `contracts/event-contracts.md`; `docs/architecture/backend/standards/platform-patterns.md`.
