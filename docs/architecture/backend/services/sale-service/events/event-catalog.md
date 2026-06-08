# Event Catalog — SALE

> Source of truth for SALE topics. Full payloads in `contracts/event-contracts.md`.
> Kafka (AWS MSK), naming `journey-os.<aggregate>.<verb>`.

| Event | Type | Payload | Known consumers |
|---|---|---|---|
| `journey-os.oportunidade.criada` | published | [event-contracts §1](../contracts/event-contracts.md) | INTL, JRNY |
| `journey-os.oportunidade.estagio.alterado` | published | [event-contracts §1](../contracts/event-contracts.md) | INTL (funnel), COMM |
| `journey-os.oportunidade.ganha` | published | [event-contracts §1](../contracts/event-contracts.md) | INTL, COMM, WRKS (audit) |
| `journey-os.oportunidade.perdida` | published | [event-contracts §1](../contracts/event-contracts.md) | INTL (loss analytics) |
| `journey-os.compra.confirmada` (**anchor**) | published | [event-contracts §1](../contracts/event-contracts.md) | INTL (`revenue-events`), WRKS (audit), COMM (post-sale) |
| `journey-os.receita.atribuida` | published | [event-contracts §1](../contracts/event-contracts.md) | INTL (ROI by source/campaign) |
| `journey-os.ltv.atualizado` | published | [event-contracts §1](../contracts/event-contracts.md) | INTL, LEAD (value signal — post-MVP) |
| `journey-os.lead.qualificado` | consumed | from LEAD | creates/updates oportunidade |
| `journey-os.lead.score.atualizado` | consumed | from LEAD | reprioritizes oportunidade |
| `journey-os.empresa.provisionada` | consumed | from WRKS | seed pipeline/ofertas/attribution model |
| `journey-os.modelo.acesso.alterado` | consumed | from WRKS | invalidate AccessDecision cache |

> Post-MVP consumed: `journey-os.lead.roteado` / `journey-os.estagio.transicionado` / `journey-os.jornada.concluida` (JRNY) as touchpoints/responsible.
