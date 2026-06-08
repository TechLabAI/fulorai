# Event Catalog — ASST (asst-service)

> Per-service view of events. Canonical platform catalog:
> `docs/architecture/shared/contratos/event-catalog.md` (generated). Cross-reference summary:
> `docs/architecture/backend/standards/services-catalog.md` §6.

| Event | Type | Payload (link) | Known consumers |
|---|---|---|---|
| `journey-os.asset.criado` | published | `../contracts/event-contracts.md` §1 | INTL (analytics), WRKS (audit) |
| `journey-os.asset.aprovado` | published | `../contracts/event-contracts.md` §1 | audit/notification |
| `journey-os.asset.rejeitado` | published | `../contracts/event-contracts.md` §1 | author notification, audit |
| `journey-os.asset.versao.publicada` | published (**anchor**) | `../contracts/event-contracts.md` §1 | COMM, JRNY, SALE, INTL |
| `journey-os.modelo.acesso.alterado` | consumed | WRKS — `../contracts/event-contracts.md` §2 | ASST (cache evict) |
| `journey-os.empresa.provisionada` | consumed | WRKS — `../contracts/event-contracts.md` §2 | ASST (tenant seed) |

- Envelope, idempotency (`processed_events`), DLQ and outbox: see the platform catalog.
- All ASST events are tenant-scoped (`empresaId` in envelope).
