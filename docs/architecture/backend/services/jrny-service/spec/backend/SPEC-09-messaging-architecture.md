# SPEC-09 — Messaging Architecture

> Contrato: `contracts/event-contracts.md`. ADR-003 (mensageria/roteamento dirigido por evento).
> Padrões: `platform-patterns.md` (outbox). EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Definir produção/consumo de eventos sobre Kafka/AWS MSK com outbox transacional e consumers
idempotentes — o roteamento de JRNY é **dirigido por evento**.

## Escopo

- **In:** outbox para eventos produzidos (`jornada.publicada`, `lead.roteado`, `estagio.transicionado`, `jornada.concluida`); consumers de LEAD (`lead.qualificado`/`score.atualizado`/`segmento.alterado`), ASST (`asset.versao.publicada`), WRKS (`modelo.acesso.alterado`/`empresa.provisionada`); DLQ; idempotência.
- **Out:** chamadas síncronas (Feign — hub-integration); contrato do assist IA (SPEC-10).

## Decisões técnicas

- **Outbox:** producers gravam em `outbox_event` na mesma transação do efeito (avanço + decisão); publisher separado envia (sem ghost events).
- **Consumers:** `@KafkaListener`; resolve tenant pelo header `empresaId`; checa `processed_events` antes de efeito; **não** faz chamada Feign síncrona durante processamento (anti-pattern — usa dados em cache/last-known).
- **Versionamento:** `eventVersion=v1`; breaking → `.v2` com deprecation.
- **DLQ:** 3 retries (1s/5s/30s) → `journey-os.dlq.<evento>`.
- **Âncora:** `lead.roteado` emitido **apenas** em decisão `ROTEADO`.

## Produzidos / Consumidos

- Produz: `jornada.publicada`, `lead.roteado` (âncora), `estagio.transicionado`, `jornada.concluida`.
- Consome: `lead.qualificado`, `lead.score.atualizado`, `lead.segmento.alterado`, `asset.versao.publicada`, `modelo.acesso.alterado`, `empresa.provisionada`.

## Casos de borda

- Rollback da transação de roteamento → nenhum evento sai (outbox).
- Reentrega → no-op (`processed_events` + índice parcial de inscrição ATIVA).
- Decisão `SEM_MUDANCA`/`NAO_ROTEADO` → decisão logada, **sem** `lead.roteado`.
- Falha persistente do consumer → DLQ + alerta.

## Critérios de aceite (EARS)

- `WHEN a routing transaction that must emit events commits, THE SYSTEM SHALL write those events to outbox_event in the same transaction.`
- `IF the routing transaction rolls back, THEN THE SYSTEM SHALL NOT publish any of its events.`
- `WHEN a consumed event's eventId is already in processed_events, THE SYSTEM SHALL skip it.`
- `THE SYSTEM SHALL route an event to journey-os.dlq.<evento> after 3 failed deliveries.`
- `THE SYSTEM SHALL NOT perform a synchronous Feign call inside an event consumer.`
- `WHEN a ROTEADO decision commits, THE SYSTEM SHALL emit journey-os.lead.roteado with leadId, jornadaId, estagioAlvoId, decisaoId and assistIa.`
- `IF a decision result is SEM_MUDANCA or NAO_ROTEADO, THEN THE SYSTEM SHALL NOT emit journey-os.lead.roteado.`
- `WHEN an enrolment reaches a terminal stage, THE SYSTEM SHALL emit journey-os.jornada.concluida.`
- `WHEN consuming any event, THE SYSTEM SHALL resolve the tenant from the envelope empresaId before processing.`
