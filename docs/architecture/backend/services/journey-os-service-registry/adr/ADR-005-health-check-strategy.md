# ADR-005 — Health-check, self-preservation & HA posture

- **Status:** accepted

## Context

REG must be probeable by the orchestrator and must decide how aggressively to evict instances that stop sending heartbeats. Eureka's **self-preservation** mode stops evictions when it suspects a network partition (mass heartbeat loss), trading staleness for availability. In dev this causes confusing "phantom UP" instances; in prod it protects against partition-induced mass eviction. HA (peer replication) is also a posture decision.

## Decision

1. **Health checks:** expose Actuator `health` (+ `info`) and use `GET /actuator/health` as the container liveness/readiness probe.
2. **Self-preservation:** **disabled in `local`** (fast eviction, accurate dashboard during dev) and **left at Eureka defaults in `prod`** (partition protection). Lease/eviction intervals tuned per profile via `eureka.server.*` and `eureka.instance.*`.
3. **HA posture:** **single node in MVP** (documented SPOF, R1). Production-grade **peer-replicated** Eureka (`eureka.client.service-url.defaultZone` pointing at peers, `register-with-eureka=true` between peers) is deferred to a future hardening ADR.

## Alternatives considered

1. **Self-preservation on everywhere** — confusing stale instances during local dev; rejected for `local`.
2. **Self-preservation off everywhere** — risks mass eviction during real prod partitions; rejected for `prod`.
3. **Multi-node HA from day one** — premature operational complexity for the current phase; deferred.

## Consequences

- **Positive:** accurate local dashboard; partition-safe prod; clear health contract for orchestration.
- **Negative:** MVP is a SPOF (mitigated by client-side cached registries); the eventual move to HA changes config (peer URLs, self-registration) and warrants its own ADR.

## References

- `docs/architecture/backend/standards/platform-patterns.md` §7
- `06-risks-gaps-assumptions.md` (R1, R3)
- `01-architectural-vision.md` §7 (Success Signals)
