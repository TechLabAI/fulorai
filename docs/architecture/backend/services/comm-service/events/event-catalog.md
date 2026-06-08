# Event Catalog — COMM (comm-service)

> Per-service view of events. Canonical platform catalog:
> `docs/architecture/shared/contratos/event-catalog.md` (generated). Cross-reference summary:
> `docs/architecture/backend/standards/services-catalog.md` §6.

| Event | Type | Payload (link) | Known consumers |
|---|---|---|---|
| `journey-os.mensagem.enfileirada` | published | `../contracts/event-contracts.md` §1 | INTL (`communication-events`) |
| `journey-os.mensagem.enviada` | published (**anchor**) | `../contracts/event-contracts.md` §1 | JRNY, SALE, INTL |
| `journey-os.mensagem.entregue` | published | `../contracts/event-contracts.md` §1 | SALE (attribution), INTL |
| `journey-os.mensagem.falhada` | published | `../contracts/event-contracts.md` §1 | INTL (failure analytics), WRKS (audit) |
| `journey-os.modelo.acesso.alterado` | consumed | WRKS — `../contracts/event-contracts.md` §2 | COMM (cache evict) |
| `journey-os.empresa.provisionada` | consumed | WRKS — `../contracts/event-contracts.md` §2 | COMM (tenant seed) |
| `journey-os.asset.versao.publicada` | consumed | ASST — `../contracts/event-contracts.md` §2 | COMM (template flag) |
| `journey-os.lead.segmento.alterado` | consumed | LEAD — `../contracts/event-contracts.md` §2 | COMM (routing re-eval) |
| `journey-os.lead.roteado` | consumed | JRNY — `../contracts/event-contracts.md` §2 | COMM (stage dispatch) |
| `journey-os.estagio.transicionado` | consumed | JRNY — `../contracts/event-contracts.md` §2 | COMM (stage dispatch) |
| `journey-os.oportunidade.estagio.alterado` | consumed | SALE — `../contracts/event-contracts.md` §2 | COMM (sales nurture) |

- Envelope, idempotency (`processed_events`), DLQ and outbox: see the platform catalog.
- All COMM events are tenant-scoped (`empresaId` in envelope).
