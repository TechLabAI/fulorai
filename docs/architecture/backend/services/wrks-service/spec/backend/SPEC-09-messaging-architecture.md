# SPEC-09 — Messaging Architecture (WRKS)

## Objective
Define Kafka producers/consumers, the transactional outbox, and the audit sink.

## Scope
- **In:** publish identity lifecycle events; consume all `journey-os.*` for audit; context propagation.
- **Out:** business events of other modules (only consumed for audit).

## Technical decisions
- Kafka (AWS MSK) — ADR-003. Topics `journey-os.<aggregate>.<verb>`. Transactional outbox for
  publish atomicity. Header `empresaId` for async context propagation.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL publish journey-os.modelo.acesso.alterado, .usuario.criado, .usuario.empresa.associado, .empresa.provisionada, .sessao.estabelecida, .sessao.encerrada.`
- `THE SYSTEM SHALL publish events via a transactional outbox so a published event implies the DB change committed.`
- `THE SYSTEM SHALL subscribe to all journey-os.* topics and persist one evento_auditoria per event (idempotent on correlationId+evento).`
- `WHEN consuming an event, THE SYSTEM SHALL populate EmpresaContextHolder from the empresaId header and clear() it in a finally block.`
- `THE SYSTEM SHALL index each audited event into Elastic audit-events asynchronously after the row is persisted.`

## Edge cases
- Consumer lag / redelivery → idempotent consume. Outbox relay failure → retry; no double publish. Poison message → DLT after N retries.

## References
- ADR-003, `contracts/event-contracts.md`, `shared/multi-empresa.md`, `platform-patterns.md`.
