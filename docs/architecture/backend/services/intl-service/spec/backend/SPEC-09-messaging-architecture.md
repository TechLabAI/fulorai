# SPEC-09 — Messaging Architecture

> Ref: `contracts/event-contracts.md`, `contracts/integration-contracts.md §3`. ADR-003.
> Event bus: Kafka / AWS MSK.

## Objetivo

Definir a arquitetura de mensageria de INTL: consumidores transversais, producer do evento âncora,
idempotência e DLQ de mensageria.

## Escopo

**In:** consumers (`asset.versao.publicada`, `empresa.provisionada`, `modelo.acesso.alterado`);
producer (`copilot.resposta.gerada`); envelope canônico; idempotência por `eventId`; DLQ.
**Out:** consumo dos demais `journey-os.*` para reindexação (descentralizado — ADR-003).

## Decisões técnicas

- Consumer group `intl-service`; commit pós-processamento; dedupe por `eventId`.
- Producer transacional/outbox para `copilot.resposta.gerada` (consistência com a persistência).
- DLQ de mensageria após N retries com backoff (distinta da DLQ Elastic `journey-os_dlq`).
- Envelope: `eventId`, `tipo`, `empresa`, `ocorridoEm`, `correlationId`, `versao`, `payload`.

## Componentes

- `infrastructure.messaging.consumer.{AssetPublishedConsumer, EmpresaProvisionadaConsumer, ModeloAcessoConsumer}`
- `infrastructure.messaging.producer.CopilotEventProducer`

## Casos de borda

- Reentrega → no-op (idempotência).
- Falha persistente de consumo → DLQ de mensageria (inspeção manual).
- Producer falha após commit DB → outbox reentrega.

## Critérios de aceite (EARS)

- WHEN uma resposta do copiloto é persistida, THE SYSTEM SHALL publicar `journey-os.copilot.resposta.gerada` exatamente uma vez (outbox).
- WHEN um evento consumido é reentregue, THE SYSTEM SHALL processá-lo de forma idempotente (`eventId`).
- IF o processamento de um evento falha após os retries, THEN THE SYSTEM SHALL roteá-lo para a DLQ de mensageria.
- THE SYSTEM SHALL incluir `empresa` e `correlationId` no envelope de todo evento publicado.
