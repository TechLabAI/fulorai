# Event Contracts — ASST (Asset Hub)

> Events produced/consumed by `asst-service` over Kafka/AWS MSK. Envelope follows
> `shared/contratos/event-catalog.md` (eventId, eventType, eventVersion, producer, empresaId,
> correlationId, actor, data). Producers use the **outbox** pattern; consumers are **idempotent**
> on `eventId`. EARS for behavior. Guide: `docs/architecture/backend/standards/ears-notation.md`.

## 1. Produced events

| Event | Trigger | Consumers |
|---|---|---|
| `journey-os.asset.criado` | asset created (RASCUNHO) | INTL (analytics), WRKS (audit) |
| `journey-os.asset.aprovado` | version approved | audit/notification |
| `journey-os.asset.rejeitado` | version rejected | author notification, audit |
| `journey-os.asset.versao.publicada` | **anchor** — version becomes current | COMM, JRNY, SALE, INTL |

### `journey-os.asset.criado`
- `data`: `{ assetId, tipoAsset, donoId, titulo }`
- `WHEN an asset is created, THE SYSTEM SHALL enqueue journey-os.asset.criado in the same transaction via the outbox.`

### `journey-os.asset.aprovado` / `journey-os.asset.rejeitado`
- `data`: `{ assetId, versaoId, numero, revisorId, comentario? }`
- `WHEN a review decision is persisted, THE SYSTEM SHALL emit the matching aprovado/rejeitado event with the reviewer identity.`

### `journey-os.asset.versao.publicada` (anchor)
- `data`: `{ assetId, versaoId, numero, tipoAsset, publicadoPor }`
- `WHEN a version is published, THE SYSTEM SHALL emit journey-os.asset.versao.publicada after the publication transaction commits (outbox).`
- `IF publication is retried for an already-published version, THEN THE SYSTEM SHALL NOT emit a duplicate event (idempotent on assetId+versaoId).`

## 2. Consumed events

| Event | Producer | Reaction |
|---|---|---|
| `journey-os.modelo.acesso.alterado` | WRKS | invalidate cached AccessDecision for the tenant/role |
| `journey-os.empresa.provisionada` | WRKS | seed default asset-type catalog/config for the new tenant |

### `journey-os.modelo.acesso.alterado`
- `WHEN journey-os.modelo.acesso.alterado is consumed, THE SYSTEM SHALL evict the affected AccessDecision cache entries before serving the next authorization check.`

### `journey-os.empresa.provisionada`
- `WHEN journey-os.empresa.provisionada is consumed for a new empresa, THE SYSTEM SHALL initialize tenant-scoped asset configuration idempotently.`
- `IF the event was already processed (eventId in processed_events), THEN THE SYSTEM SHALL skip it as a no-op.`

## 3. Idempotency & versioning

- **Idempotency key:** `eventId`; consumers persist it in `processed_events` before side effects.
- **Window:** retained ≥ 30 days (aligned to platform default).
- **Payload versioning:** `eventVersion` starts at `v1`; breaking changes add a `.v2` topic and keep `v1` during deprecation (per `event-catalog.md`).
- **DLQ:** 3 retries (1s/5s/30s backoff) → `journey-os.dlq.<evento>`.
