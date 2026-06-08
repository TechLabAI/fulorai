# SPEC-07 — Observability & Health (SALE)

## Objective
Define logging, metrics, tracing and health for `sale-service`.

## Scope
- **In:** MDC/correlation, business + technical metrics, health/readiness, audit via events.
- **Out:** central analytics (INTL), dashboards.

## Technical decisions
- `@Slf4j` (Lombok); MDC carries `correlationId`, `empresaId`; never PII.
- Micrometer metrics; Spring Boot Actuator health/readiness; outbox/consumer lag monitored.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL propagate correlationId via MDC across request, event publish and event consume.`
- `THE SYSTEM SHALL expose /actuator/health (liveness) and /actuator/health/readiness gated on PostgreSQL and Kafka.`
- `THE SYSTEM SHALL emit business metrics: recognized revenue, conversion per stage, attribution count by model, purchase ingestion latency, LTV recompute count.`
- `THE SYSTEM SHALL emit technical metrics: WRKS Feign latency/circuit state, outbox publish lag, consumer lag, Elastic index failures.`
- `IF a domain state change occurs (compra.confirmada, estorno, oportunidade close), THEN THE SYSTEM SHALL emit the corresponding event for WRKS audit consolidation.`
- `THE SYSTEM SHALL NOT include buyer PII in logs, metrics tags or traces.`

## Edge cases
- Readiness fails closed if migrations not applied (schema invalid).
- Elastic outage surfaces a metric but does not flip health to DOWN (best-effort indexing).

## References
- `docs/architecture/backend/standards/platform-patterns.md` (MDC, outbox); ADR-003.
