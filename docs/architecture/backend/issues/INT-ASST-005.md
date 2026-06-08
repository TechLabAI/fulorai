# INT-ASST-005 -- Kafka event bus (producer/consumer config + outbox)

## Contexto
Configuração do barramento Kafka/AWS MSK para produção (outbox) e consumo idempotente.

## Spec de referencia
- SPEC-09-messaging-architecture
- contracts/event-contracts.md

## Escopo
- `spring-kafka` config (`KAFKA_BOOTSTRAP_SERVERS`); serialização do envelope canônico.
- Outbox publisher (poll-and-send) + `outbox_event`/`processed_events` (migração compartilhada).
- Tópicos `journey-os.asset.*` (publish) + listeners `modelo.acesso.alterado`/`empresa.provisionada`.
- DLQ `journey-os.dlq.<evento>` (3 retries).

## Resultado esperado
Barramento funcional com entrega garantida (outbox) e idempotência de consumo.

## Criterios de aceite
- [ ] Producer grava em `outbox_event` na mesma TX.
- [ ] Consumers checam `processed_events` antes de efeito.
- [ ] Falha persistente → DLQ.

## Dependencias
- Kafka (existente); ASST-014

## Estimativa
M

## Prioridade
P6
