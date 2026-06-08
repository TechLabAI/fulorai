# LEAD-015 -- Kafka producers: eventos lead.* via transactional outbox

## Contexto
Publicação dos eventos de domínio do LEAD via `LeadEventPublisherPort`, com transactional outbox
para não perder/duplicar eventos.

## Spec de referencia
- SPEC-09-messaging-architecture
- SPEC-05-idempotency-concurrency

## Escopo
- `infrastructure.messaging.producer` implementa `LeadEventPublisherPort`.
- Publica `journey-os.lead.{capturado,qualificado,score.atualizado,segmento.alterado}`.
- Headers: `correlationId`, `empresaId`, `eventId`, `occurredAt`, `source=lead-service`, `schemaVersion`.
- Outbox: commit DB sem publish não emite; retry de publish não reaplica DB.

## Resultado esperado
Cada evento de domínio publicado exatamente uma vez (do ponto de vista do consumidor), com headers padronizados.

## Criterios de aceite
- [ ] Os 4 eventos publicados com o envelope/headers da `event-contracts.md`.
- [ ] Outbox garante publish atômico com o commit transacional.
- [ ] Sem PII no payload (apenas identificadores + score/dimensões).

## Dependencias
- LEAD-005 (gera os eventos)
- INT-LEAD-005 (outbox)

## Estimativa
M

## Prioridade
P6
