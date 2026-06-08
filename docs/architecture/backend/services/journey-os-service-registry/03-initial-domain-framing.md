# 03 — Initial Domain Framing (REG · journey-os-service-registry)

> **REG has no business domain.** This document records that explicitly so downstream
> stages (specs, backlog, scaffold) do not attempt to generate entities, aggregates,
> migrations, or domain events for this module.

## 1. Ubiquitous Language

The only vocabulary is the **Eureka / service-discovery** vocabulary, owned by Spring Cloud Netflix, not by Journey OS:

| Term | Meaning |
|---|---|
| Eureka Server | The registry process (this service, REG). |
| Eureka Client | Any microservice that registers with and queries the server. |
| Instance | A single running deployment of a client (app name + host + port + status). |
| Lease | The time-bound registration of an instance, kept alive by heartbeats. |
| Heartbeat / renewal | Periodic signal from a client that renews its lease. |
| Self-preservation | Eureka mode that stops evicting instances when mass heartbeat loss looks like a network partition. |
| Eviction | Removal of an instance whose lease expired. |

## 2. Aggregates and Entities

**None.** There are no Journey OS aggregates, entities, or value objects. The registry of instances/leases is an internal, in-memory, framework-owned structure — not modeled by this project.

## 3. Domain Events

**None.** REG publishes no Journey OS domain events to the broker and consumes none. Eureka's internal registration/eviction notifications are framework-internal and out of scope for the event catalog.

## 4. State Transitions

Only the framework-managed instance lifecycle (informational, not modeled by us):

```
STARTING → UP → (no heartbeat) → DOWN/OUT_OF_SERVICE → evicted
```

## 5. Invariants

- REG never registers with itself (`register-with-eureka=false`, `fetch-registry=false`).
- REG holds no persistent or tenant-scoped state.
- The registry is fully reconstructable from clients re-registering after a REG restart.
