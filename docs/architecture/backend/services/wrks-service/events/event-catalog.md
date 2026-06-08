# Event Catalog — WRKS

> Source for the services-catalog event cross-reference. Kafka (AWS MSK).

| Event | Type | Payload | Known consumers |
|---|---|---|---|
| `journey-os.modelo.acesso.alterado` | published | [event-contracts §1](../contracts/event-contracts.md) | **all services** (AccessDecision cache invalidation) |
| `journey-os.usuario.criado` | published | event-contracts §1 | audit, notification |
| `journey-os.usuario.empresa.associado` | published | event-contracts §1 | audit |
| `journey-os.empresa.provisionada` | published | event-contracts §1 | services with per-tenant seeds; audit |
| `journey-os.sessao.estabelecida` | published | event-contracts §1 | audit |
| `journey-os.sessao.encerrada` | published | event-contracts §1 | audit |
| `journey-os.*` (all) | consumed | producer-defined | **WRKS** (consolidated `evento_auditoria` + Elastic `audit-events`) |

> WRKS is both a prolific producer (identity lifecycle) and the **single sink** for the
> platform-wide audit trail.
