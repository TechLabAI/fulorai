# SPEC-05 — Idempotency & Concurrency

> Ref: `contracts/event-contracts.md §3`, `contracts/data-model.md §3.7`. ADR-003.

## Objetivo

Garantir idempotência no consumo de eventos, na projeção Elastic e na ingestão de conhecimento;
controlar concorrência na indexação de nós.

## Escopo

**In:** dedupe de consumo por `eventId`; projeção idempotente por doc-id determinístico (ledger
`evento_indexado`); ingestão de asset idempotente por `assetId:versao`; trava otimista na
reindexação de nó.
**Out:** transações distribuídas (saga) — não aplicável no MVP.

## Decisões técnicas

- **Consumo Kafka:** dedupe por `eventId` (verificação + offset commit pós-processamento).
- **Projeção Elastic:** doc-id determinístico; `evento_indexado.evento_id` como PK → reprojeção = no-op.
- **Ingestão asset:** `UPSERT` lógico por `fonte.referencia = assetId:versao`.
- **Reindexação de nó:** `versao` + checagem otimista; concorrência → `409`.

## Casos de borda

- Reentrega de evento após crash → no-op.
- Dois indexadores do mesmo nó → um vence, outro `409`.
- Replay de DLQ → reprojeção idempotente.

## Critérios de aceite (EARS)

- IF um `eventId` já processado é reentregue, THEN THE SYSTEM SHALL tratá-lo como no-op.
- WHEN uma projeção com doc-id já presente é reprocessada, THE SYSTEM SHALL não criar documento duplicado.
- IF duas indexações concorrentes do mesmo nó ocorrem, THEN THE SYSTEM SHALL aceitar uma e responder `409` à outra.
- WHEN um asset já ingerido é reentregue, THE SYSTEM SHALL atualizar o nó existente em vez de duplicar.
