# INT-INTL-005 -- Integração Kafka (consumers + producer)

## Contexto
Mensageria transversal de INTL (consumo + publicação do evento-âncora).

## Spec de referência
- SPEC-09, `contracts/event-contracts.md`, `integration-contracts.md §3`

## Escopo
Consumer group `intl-service`; envelope canônico; dedupe por `eventId`; producer outbox de
`copilot.resposta.gerada`; DLQ de mensageria. Testes com broker embarcado/Testcontainers.

## Resultado esperado
Eventos consumidos/publicados de forma idempotente e consistente.

## Critérios de aceite
- [ ] Reentrega → no-op
- [ ] Producer exactly-once via outbox
- [ ] DLQ de mensageria após retries
- [ ] Envelope com `empresa`/`correlationId`

## Dependências
- INTL-013

## Estimativa
M

## Prioridade
P6
