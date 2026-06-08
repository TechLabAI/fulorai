# SPEC-09 — Messaging Architecture (Kafka + outbox + dispatch worker)

> EARS guide linkado. Relaciona ADR-003, `event-contracts.md`, SPEC-02 (dispatch), SPEC-05 (idempotência).

## Objetivo

Especificar a arquitetura de mensageria: publicação de eventos de domínio via outbox, o worker de
disparo que desacopla o envio ao provedor, e o consumo idempotente de eventos de outros módulos.

## Escopo

- **In:** outbox transacional; worker de disparo (lê outbox/fila, envia, atualiza estado); producers (`mensagem.*`); consumers (WRKS/ASST/LEAD/JRNY/SALE); DLQ.
- **Out:** contrato fino de cada provedor de canal (SPEC-10); broker config (platform-patterns).

## Decisões técnicas

- **Outbox:** ao aceitar disparo e a cada transição relevante, grava em `outbox_event` na mesma TX; publisher separado envia ao Kafka (evita evento fantasma em rollback).
- **Dispatch worker:** consome o job de disparo (via outbox/fila), seleciona o adapter (SPEC-03), envia sob Resilience4j; sucesso→`ENVIADA`+evento, falha→retry/backoff (1s/5s/30s) → `FALHADA`+DLQ.
- **Producers:** `journey-os.mensagem.{enfileirada,enviada,entregue,falhada}` (envelope `shared/contratos/event-catalog.md`).
- **Consumers idempotentes:** `processed_events` por `eventId` antes de efeito; gatilhos JRNY/SALE derivam `chave_idempotencia`.
- **DLQ:** `journey-os.dlq.<evento>` após 3 retentativas; replay administrativo.

## Casos de borda

- Rollback após reservar `chave_idempotencia` → outbox não publica (mesma TX); sem evento fantasma.
- Broker indisponível → outbox acumula; publisher reprocessa quando volta (em ordem).
- Consumer reentrega → no-op via `processed_events`.
- Job de disparo órfão (worker reiniciou) → retomado pela fila/outbox; idempotente por estado.

## Critérios de aceite (EARS)

- `WHEN a domain event must be published, THE SYSTEM SHALL write it to outbox_event in the same transaction as the state change.`
- `THE SYSTEM SHALL publish events to Kafka via a separate outbox publisher, never inside a transaction that may roll back.`
- `WHEN the dispatch worker fails to reach the provider, THE SYSTEM SHALL retry with backoff and, after the configured retries, route the job to the DLQ and mark the message FALHADA.`
- `WHEN a consumed event's eventId already exists in processed_events, THE SYSTEM SHALL skip it as a no-op.`
- `THE SYSTEM SHALL emit journey-os.mensagem.enviada only after the send transaction commits (anchor, idempotent on mensagemId).`
