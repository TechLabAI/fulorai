# Event Contracts — COMM (Communication Hub)

> Events produced/consumed by `comm-service` over Kafka/AWS MSK. Envelope follows
> `shared/contratos/event-catalog.md` (eventId, eventType, eventVersion, producer, empresaId,
> correlationId, actor, data). Producers use the **outbox** pattern; consumers are **idempotent**
> on `eventId`. EARS for behavior. Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Produced events

| Event | Trigger | Consumers |
|---|---|---|
| `journey-os.mensagem.enfileirada` | dispatch accepted & queued | INTL (`communication-events`) |
| `journey-os.mensagem.enviada` | **anchor** — handed to channel provider OK | JRNY (journey advance), SALE (touch), INTL |
| `journey-os.mensagem.entregue` | provider delivery receipt | SALE (attribution), INTL |
| `journey-os.mensagem.falhada` | failed after retries / provider rejection | INTL (failure analytics), WRKS (audit) |

### `journey-os.mensagem.enfileirada`
- `data`: `{ mensagemId, canal, leadId, templateId? }`
- `WHEN a dispatch is accepted, THE SYSTEM SHALL enqueue journey-os.mensagem.enfileirada in the same transaction via the outbox.`

### `journey-os.mensagem.enviada` (anchor)
- `data`: `{ mensagemId, canal, provedor, leadId, provedorMessageId }`
- `WHEN a message is successfully handed to the channel provider, THE SYSTEM SHALL emit journey-os.mensagem.enviada after the send transaction commits (outbox).`
- `IF the send is retried for an already-sent message, THEN THE SYSTEM SHALL NOT emit a duplicate event (idempotent on mensagemId).`

### `journey-os.mensagem.entregue`
- `data`: `{ mensagemId, canal, entregueEm }`
- `WHEN a provider delivery callback confirms delivery, THE SYSTEM SHALL emit journey-os.mensagem.entregue.`

### `journey-os.mensagem.falhada`
- `data`: `{ mensagemId, canal, motivo, tentativas }`
- `WHEN a message exhausts dispatch retries or is rejected by the provider, THE SYSTEM SHALL emit journey-os.mensagem.falhada with the failure reason.`

## 2. Consumed events

| Event | Producer | Reaction |
|---|---|---|
| `journey-os.modelo.acesso.alterado` | WRKS | invalidate cached AccessDecision for the tenant/role |
| `journey-os.empresa.provisionada` | WRKS | seed default channels/templates for the new tenant |
| `journey-os.asset.versao.publicada` | ASST | flag templates bound to that asset for review |
| `journey-os.lead.segmento.alterado` | LEAD | re-evaluate routing audience for the lead |
| `journey-os.lead.roteado` | JRNY | trigger a stage-action dispatch (if configured) |
| `journey-os.estagio.transicionado` | JRNY | trigger a stage-transition dispatch (if configured) |
| `journey-os.oportunidade.estagio.alterado` | SALE | trigger a sales-stage nurture dispatch (if configured) |

### `journey-os.modelo.acesso.alterado`
- `WHEN journey-os.modelo.acesso.alterado is consumed, THE SYSTEM SHALL evict the affected AccessDecision cache entries before serving the next authorization check.`

### `journey-os.empresa.provisionada`
- `WHEN journey-os.empresa.provisionada is consumed for a new empresa, THE SYSTEM SHALL initialize tenant-scoped channel/template defaults idempotently.`
- `IF the event was already processed (eventId in processed_events), THEN THE SYSTEM SHALL skip it as a no-op.`

### `journey-os.asset.versao.publicada`
- `WHEN journey-os.asset.versao.publicada is consumed for an asset referenced by a template, THE SYSTEM SHALL flag that template for review AND SHALL NOT auto-activate a new template version.`

### `journey-os.lead.roteado` / `journey-os.estagio.transicionado` / `journey-os.oportunidade.estagio.alterado`
- `WHERE a routing rule binds the event/stage to a template, WHEN the trigger event is consumed, THE SYSTEM SHALL create a dispatch using a derived chave_idempotencia (event-scoped) so the same trigger never dispatches twice.`

## 3. Idempotency & versioning

- **Idempotency key (consume):** `eventId`; consumers persist it in `processed_events` before side effects.
- **Idempotency key (dispatch):** event-triggered sends derive a deterministic `chave_idempotencia` from `(eventId, leadId, regraId)` so a re-delivered trigger does not produce a second message.
- **Window:** retained ≥ 30 days (aligned to platform default).
- **Payload versioning:** `eventVersion` starts at `v1`; breaking changes add a `.v2` topic and keep `v1` during deprecation (per `event-catalog.md`).
- **DLQ:** 3 retries (1s/5s/30s backoff) → `journey-os.dlq.<evento>`.
