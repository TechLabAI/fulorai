# INT-LEAD-005 -- Transactional outbox + idempotent consume (Kafka)

## Contexto
Infra de mensageria confiável: transactional outbox para publish dos `lead.*` e dedup idempotente
no consumo.

## Spec de referencia
- SPEC-09-messaging-architecture
- SPEC-05-idempotency-concurrency
- integration-contracts.md

## Escopo
- Tabela/serviço de outbox no `emp_<slug>` (ou global de outbox conforme padrão da plataforma); relay para Kafka.
- Dedup de consumo por `(correlationId, evento)`.
- Config `KAFKA_BOOTSTRAP_SERVERS` via `${VAR}`.

## Resultado esperado
Publish atômico com o commit; consumo at-least-once com dedup — sem eventos perdidos/duplicados.

## Criterios de aceite
- [ ] Falha de publish não reaplica a mudança de DB; retry reenvia sem duplicar efeito.
- [ ] Evento consumido repetido é no-op (dedup por chave de idempotência).
- [ ] Cobertura de teste de integração do outbox + consume.

## Dependencias
- LEAD-015 (producers)
- LEAD-016 (consumers)

## Estimativa
M

## Prioridade
P6
