# SALE-015 — Producers de eventos (outbox)

## Contexto
Publicar os 7 eventos de domínio via transactional outbox no Kafka.

## Spec de referencia
- SPEC-09, `contracts/event-contracts.md` §1

## Escopo
`SaleEventPublisherPort` + producer em `infrastructure.messaging.producer`; outbox; headers
canônicos; sem PII além de `contatoRef`.

## Resultado esperado
Eventos `oportunidade.*`/`compra.*`/`receita.*`/`ltv.*` publicados de forma confiável.

## Criterios de aceite
- [ ] publicação via outbox (sem evento sem commit)
- [ ] tópicos `journey-os.<aggregate>.<verb>` + headers `correlationId/empresaId/eventId/...`
- [ ] valores monetários como decimal/string (sem float)

## Dependencias
- SALE-005, SALE-006, SALE-007, SALE-008 (precede)

## Estimativa
M

## Prioridade
P6
