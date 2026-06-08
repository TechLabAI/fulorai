# ADR-003 — Messaging strategy (none for REG)

- **Status:** accepted

## Context

Journey OS uses asynchronous messaging (ActiveMQ Artemis / Kafka) with a canonical `EventEnvelope` for inter-service domain events and sagas (`platform-patterns.md` §1, §6). Standard services declare producers/consumers. The default ADR-003 for a domain module chooses an async messaging posture.

## Decision

REG **participates in no messaging**. It declares **no producers and no consumers**, holds no broker connection, and emits no Journey OS domain events. Service registration/eviction is handled entirely by the synchronous Eureka HTTP protocol and stays internal to the framework.

## Alternatives considered

1. **Publish registry change events to the broker** (e.g. `service.instance.registered`) — would couple infra discovery to the domain event bus, create noisy low-value traffic, and duplicate what Eureka already does; rejected as scope creep.
2. **No messaging (chosen)** — keeps REG a pure, dependency-light infra component.

## Consequences

- **Positive:** no broker dependency for REG; nothing to make idempotent; smaller blast radius and simpler ops.
- **Negative:** other services cannot react to registry changes via the event bus — acceptable, since discovery state is consumed via the Eureka client API, not via events.

## References

- `docs/architecture/backend/standards/platform-patterns.md` §1, §6
- `04-backend-architecture-direction.md` §6
