# SPEC-07 — Observability & Health (REG · journey-os-service-registry)

> EARS guide: `docs/architecture/backend/standards/ears-notation.md`. Related: ADR-005, `platform-patterns.md` §4, §7.

## Objective

Define how REG reports health and exposes operational visibility for probes and operators.

## Scope

**In:** Actuator `health`/`info`; the Eureka dashboard as the primary operational view;
logging pattern with the `service` MDC field; self-preservation/eviction tuning by profile.
**Out:** distributed tracing/correlation-id propagation (REG initiates no business requests);
metrics export to INTL/Elastic (future, owned by INTL); alerting on mass de-registration (future).

## Technical decisions

- `GET /actuator/health` is the orchestrator liveness/readiness probe.
- The **Eureka dashboard** (`/`) is the human operational view of UP/DOWN instances.
- **Self-preservation:** disabled in `local`, default (on) in `prod` (ADR-005).
- Logging uses the standard console pattern; `service=journey-os-service-registry` in MDC.

## Implementation

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info
  endpoint:
    health:
      probes:
        enabled: true

# local profile
eureka:
  server:
    enable-self-preservation: false
    eviction-interval-timer-in-ms: 15000
```

```yaml
logging:
  pattern:
    console: "%d{ISO8601} [%X{service}] %-5level %logger{36} - %msg%n"
  level:
    com.journeyos: INFO
    com.netflix.eureka: INFO
```

## Edge cases

- Mass heartbeat loss in `prod` → self-preservation holds instances to avoid partition-induced eviction (intended).
- In `local`, fast eviction makes the dashboard reflect reality quickly during dev.

## Acceptance criteria (EARS)

- THE SYSTEM SHALL expose `GET /actuator/health` returning `UP` while operational.
- WHERE the orchestrator probes liveness/readiness, THE SYSTEM SHALL respond on `GET /actuator/health`.
- THE SYSTEM SHALL serve the Eureka dashboard at `GET /` showing registered apps and their status.
- WHILE running under the `local` profile, THE SYSTEM SHALL disable self-preservation.
- WHILE running under the `prod` profile, THE SYSTEM SHALL keep self-preservation at the Eureka default.
- THE SYSTEM SHALL tag logs with the `service` field `journey-os-service-registry`.
