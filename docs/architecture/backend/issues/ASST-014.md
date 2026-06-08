# ASST-014 -- Messaging: producers (outbox) + consumers idempotentes

## Contexto
Publicação de eventos de domínio via outbox e consumo idempotente dos eventos de WRKS.

## Spec de referencia
- SPEC-09-messaging-architecture
- contracts/event-contracts.md

## Escopo
- Producers (outbox): `asset.criado`, `asset.aprovado`, `asset.rejeitado`, `asset.versao.publicada`.
- Consumers: `modelo.acesso.alterado` (evict cache), `empresa.provisionada` (seed tenant) — idempotentes (`processed_events`).
- DLQ (3 retries) + sem chamada Feign síncrona dentro do consumer.

## Resultado esperado
Eventos consistentes com o commit (outbox); consumo idempotente; falhas → DLQ.

## Criterios de aceite
- [ ] Rollback da TX não publica evento (outbox).
- [ ] Reentrega (mesmo `eventId`) → no-op.
- [ ] `asset.versao.publicada` carrega `assetId/versaoId/numero/tipoAsset`.
- [ ] Consumer não faz chamada Feign síncrona.

## Dependencias
- ASST-006 (precede); INT-ASST-005

## Estimativa
L

## Prioridade
P6
