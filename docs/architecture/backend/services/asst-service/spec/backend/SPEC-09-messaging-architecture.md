# SPEC-09 — Messaging Architecture

> Contrato: `contracts/event-contracts.md`. ADR-003. Padrões: `platform-patterns.md` (outbox). EARS guide linkado.

## Objetivo

Definir produção/consumo de eventos sobre Kafka/AWS MSK com outbox transacional e consumers
idempotentes.

## Escopo

- **In:** outbox para eventos produzidos; consumers de `modelo.acesso.alterado` e `empresa.provisionada`; DLQ; idempotência.
- **Out:** chamadas síncronas (Feign — hub-integration); composição IA (SPEC-03).

## Decisões técnicas

- **Outbox:** producers gravam em `outbox_event` na mesma transação do efeito; publisher separado envia (sem ghost events).
- **Consumers:** `@KafkaListener`; checagem `processed_events` antes de efeito; consumer **não** faz chamada Feign síncrona durante processamento (anti-pattern).
- **Versionamento:** `eventVersion=v1`; breaking → `.v2` com deprecation.
- **DLQ:** 3 retries (1s/5s/30s) → `journey-os.dlq.<evento>`.

## Produzidos / Consumidos

- Produz: `asset.criado`, `asset.aprovado`, `asset.rejeitado`, `asset.versao.publicada`.
- Consome: `modelo.acesso.alterado`, `empresa.provisionada`.

## Casos de borda

- Rollback da transação de publicação → evento não sai (outbox).
- Reentrega → no-op (processed_events).
- Falha persistente do consumer → DLQ + alerta.

## Critérios de aceite (EARS)

- `WHEN a domain change that must emit an event commits, THE SYSTEM SHALL write the event to outbox_event in the same transaction.`
- `IF the producing transaction rolls back, THEN THE SYSTEM SHALL NOT publish the event.`
- `WHEN a consumed event's eventId is already in processed_events, THE SYSTEM SHALL skip it.`
- `THE SYSTEM SHALL route an event to journey-os.dlq.<evento> after 3 failed deliveries.`
- `THE SYSTEM SHALL NOT perform a synchronous Feign call inside an event consumer.`
- `WHEN asset.versao.publicada is published, THE SYSTEM SHALL include assetId, versaoId, numero and tipoAsset in data.`
