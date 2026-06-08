# Event Contracts · MIG (`journey-os-migrations`)

## Published events
**None.** MIG does not publish to Artemis/Kafka. It is a boot-time migration step, not a
runtime event producer.

## Consumed events
**None.** MIG consumes no platform events.

## Idempotency
Not applicable at the messaging layer. Migration idempotency is guaranteed by Flyway's
schema-history (each version applies exactly once per schema) — see
`SPEC-05-idempotency-concurrency.md`.

## Payload versioning
Not applicable (no events).

> Operational signals such as "migration applied" exist only as **logs / actuator info**,
> never as platform events. They are intentionally kept off the cross-module event catalog.
