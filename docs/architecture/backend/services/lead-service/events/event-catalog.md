# Event Catalog — LEAD

> Summary of events for `lead-service`. Full payloads in `contracts/event-contracts.md`.
> Bus: Kafka (AWS MSK). Topic = queue name.

| Event | Type | Payload | Known consumers |
|---|---|---|---|
| `journey-os.lead.capturado` | published | [event-contracts §1](../contracts/event-contracts.md) | INTL, WRKS (audit) |
| `journey-os.lead.qualificado` | published (**anchor**) | [event-contracts §1](../contracts/event-contracts.md) | JRNY, SALE, COMM |
| `journey-os.lead.score.atualizado` | published | [event-contracts §1](../contracts/event-contracts.md) | JRNY, SALE, INTL |
| `journey-os.lead.segmento.alterado` | published | [event-contracts §1](../contracts/event-contracts.md) | COMM, JRNY |
| `journey-os.empresa.provisionada` | consumed | from WRKS | seeds default rule/segments per tenant |
| `journey-os.modelo.acesso.alterado` | consumed | from WRKS | invalidates AccessDecision cache |

> Post-MVP (planned consume): engagement signals from COMM/JRNY → `ENGAJAMENTO` dimension.
