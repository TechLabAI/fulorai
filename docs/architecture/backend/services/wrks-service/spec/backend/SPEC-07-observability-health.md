# SPEC-07 — Observability & Health (WRKS)

## Objective
Logging, metrics, tracing and health for the identity authority.

## Scope
- **In:** MDC, Prometheus metrics, health/readiness, audit trail visibility.
- **Out:** platform dashboards (INTL/Elastic).

## Technical decisions
- `@Slf4j` (no System.out). MDC keys `empresaId`, `correlationId`, `usuarioId`. Actuator + Micrometer/Prometheus.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL include correlationId, empresaId and usuarioId in the MDC of every request and async consume.`
- `THE SYSTEM SHALL expose /actuator/health with readiness reflecting PostgreSQL, Redis, Kafka and Keycloak connectivity.`
- `THE SYSTEM SHALL emit metrics journey-os_iam_session_active_total{papel}, journey-os_iam_session_refresh_total{papel,outcome}, journey-os_iam_session_logout_total{motivo}, journey-os_iam_session_blacklist_size.`
- `THE SYSTEM SHALL emit a metric for access_evaluate latency and cache hit ratio.`
- `WHEN any journey-os.* event is audited, THE SYSTEM SHALL record source_service and correlationId.`
- `THE SYSTEM SHALL NOT log secrets, tokens, or refresh tokens.`

## Edge cases
- Keycloak unhealthy → readiness degraded but liveness up (existing JWTs valid). Blacklist size alert > 10k.

## References
- `shared/rbac/session-policy.md` (metrics), `java-conventions.md` (SLF4J/MDC).
