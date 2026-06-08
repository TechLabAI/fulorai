# SPEC-05 — Idempotency & Concurrency

> EARS guide linkado. Relaciona SPEC-02 (dispatch), SPEC-09 (events), contratos webhook (SPEC-01).

## Objetivo

Garantir que disparos, callbacks de provedor, composição IA e consumo de eventos sejam
idempotentes, e que transições de entrega concorrentes não corrompam o estado.

## Escopo

- **In:** `Idempotency-Key` no disparo e no Template Studio; idempotência de webhook por `(provedorMessageId, tipo)`; idempotência de consumers (`processed_events`); idempotência de disparo disparado por evento (`chave_idempotencia` derivada); concorrência otimista em transições.
- **Out:** retries de transporte (Kafka/Feign/provider — platform-patterns/SPEC-10).

## Decisões técnicas

- **Disparo:** `chave_idempotencia` (do header ou derivada de `(eventId, leadId, regraId)`) é `UNIQUE` em `mensagem`; replay retorna a mensagem existente (200), sem novo envio ao provedor.
- **Template Studio:** `Idempotency-Key` → uma única chamada à TechLab AI; replay retorna o mesmo corpo.
- **Webhook:** processamento idempotente por `(provedorMessageId, tipo)`; callback duplicado = no-op ack.
- **Consumers:** persistem `eventId` em `processed_events` antes de efeitos colaterais.
- **Concorrência otimista:** coluna `@Version`/checagem de estado na transição da máquina de entrega.

## Casos de borda

- Dois `POST /messages` com a mesma key (corrida) → um cria, o outro vê UNIQUE e retorna a existente.
- Worker reprocessa um job já enviado → detecta `estado_entrega` já `ENVIADA` → no-op (não reenvia, não re-emite).
- Webhook `ENTREGUE` chega duas vezes → uma transição, um evento.
- Trigger JRNY reentregue (mesmo `eventId`) → `chave_idempotencia` derivada já existe → sem segundo disparo.

## Critérios de aceite (EARS)

- `IF the same chave_idempotencia (per tenant) is used twice on dispatch, THEN THE SYSTEM SHALL produce exactly one message and return the original with 200 without calling the provider again.`
- `IF the same Idempotency-Key is replayed on Template Studio, THEN THE SYSTEM SHALL call TechLab AI exactly once and return the original composed body.`
- `IF the same provider callback (provedorMessageId + tipo) is delivered twice, THEN THE SYSTEM SHALL process it once and ack the duplicate as a no-op.`
- `WHEN a consumed event's eventId already exists in processed_events, THE SYSTEM SHALL skip processing as a no-op.`
- `THE SYSTEM SHALL persist eventId in processed_events before performing any side effect of a consumed event.`
- `WHEN two delivery-state transitions target the same message concurrently, THE SYSTEM SHALL apply at most one and reject the other with 409 error.code 'comm.mensagem.estado-invalido'.`
- `WHEN an event-triggered dispatch is re-delivered, THE SYSTEM SHALL derive a deterministic chave_idempotencia so the trigger never dispatches twice.`
