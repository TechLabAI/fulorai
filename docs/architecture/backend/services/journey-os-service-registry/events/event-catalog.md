# Event Catalog — journey-os-service-registry (REG)

> **No events.** REG neither publishes nor consumes Journey OS domain events. See ADR-003
> (messaging strategy: none). Eureka's internal registration/eviction notifications are
> framework-internal and are intentionally **not** modeled as Journey OS events.

| Event | Type (published/consumed) | Payload | Known consumers | Queue/Topic |
|---|---|---|---|---|
| _(none)_ | — | — | — | — |

## Rationale

- REG holds no broker connection and participates in no saga.
- Discovery state is consumed via the Eureka client API (synchronous fetch), not via the event bus.
- Therefore there is no contribution to `docs/architecture/shared/contratos/event-catalog.md` or to the Event Catalog in `services-catalog.md` §6 from this module.
