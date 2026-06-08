# Event Catalog — JRNY (jrny-service)

> Per-service view of events. Canonical platform catalog:
> `docs/architecture/shared/contratos/event-catalog.md` (generated). Cross-reference summary:
> `docs/architecture/backend/standards/services-catalog.md` §6.

| Event | Type | Payload (link) | Known consumers |
|---|---|---|---|
| `journey-os.jornada.publicada` | published | `../contracts/event-contracts.md` §1 | INTL (analytics), audit |
| `journey-os.lead.roteado` | published (**anchor**) | `../contracts/event-contracts.md` §1 | COMM, SALE, INTL |
| `journey-os.estagio.transicionado` | published | `../contracts/event-contracts.md` §1 | COMM, SALE, INTL |
| `journey-os.jornada.concluida` | published | `../contracts/event-contracts.md` §1 | SALE, INTL, audit |
| `journey-os.lead.qualificado` | consumed (**routing trigger**) | LEAD — `../contracts/event-contracts.md` §2 | JRNY (route) |
| `journey-os.lead.score.atualizado` | consumed | LEAD — `../contracts/event-contracts.md` §2 | JRNY (re-evaluate) |
| `journey-os.lead.segmento.alterado` | consumed | LEAD — `../contracts/event-contracts.md` §2 | JRNY (re-evaluate) |
| `journey-os.asset.versao.publicada` | consumed | ASST — `../contracts/event-contracts.md` §2 | JRNY (refresh stage content) |
| `journey-os.modelo.acesso.alterado` | consumed | WRKS — `../contracts/event-contracts.md` §2 | JRNY (cache evict) |
| `journey-os.empresa.provisionada` | consumed | WRKS — `../contracts/event-contracts.md` §2 | JRNY (seed default journeys) |

- Envelope, idempotency (`processed_events`), DLQ and outbox: see the platform catalog.
- All JRNY events are tenant-scoped (`empresaId` in envelope).
- `journey-os.lead.roteado` is the JRNY domain **anchor**: it is emitted only on a `ROTEADO`
  decision; `SEM_MUDANCA` / `NAO_ROTEADO` decisions are logged (`decisao_roteamento`) but produce
  no advance event.
