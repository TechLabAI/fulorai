# INT-COMM-005 -- Kafka producers/consumers wiring + DLQ

## Contexto
Infra de mensageria: tópicos, producers via outbox, consumers idempotentes e DLQ.

## Spec de referencia
- SPEC-09-messaging-architecture
- event-contracts.md

## Escopo
- `spring-kafka` configurado (`KAFKA_BOOTSTRAP_SERVERS`); serialização do envelope `journey-os.*`.
- Outbox publisher (lê `outbox_event`, publica `journey-os.mensagem.*`).
- Consumers registrados (idempotência via `processed_events`).
- DLQ `journey-os.dlq.<evento>` após 3 retentativas; replay administrativo.

## Resultado esperado
Eventos fluem de forma confiável (outbox + DLQ); consumo idempotente.

## Criterios de aceite
- [ ] Producer publica via outbox (sem evento fantasma em rollback).
- [ ] Consumer reentregue → no-op.
- [ ] Falha persistente → mensagem na DLQ.

## Dependencias
- COMM-014 (relaciona)

## Estimativa
M

## Prioridade
P6
