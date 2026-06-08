# SPEC-07 — Observability & Health (LEAD)

## Objective
Define health, metrics, tracing and logging for `lead-service`.

## Scope
- **In:** actuator health/readiness, domain metrics, correlation propagation, structured logging.
- **Out:** centralized dashboards (INTL/Elastic).

## Technical decisions
- Spring Boot Actuator; Micrometer metrics; `correlationId` in MDC propagated to Feign/Kafka/TechLab AI.
  Logs structured (JSON), **no PII**.

## Domain metrics
| Metric | Meaning |
|---|---|
| `lead_capturado_total{fonte}` | captures by source |
| `lead_qualificado_total{estado}` | qualification outcomes |
| `lead_score_distribuicao` | histogram of aggregate scores |
| `lead_assist_ia_fallback_total` | recomputes that fell back to deterministic |
| `lead_qualify_latency` | qualification latency |
| `lead_elastic_index_lag` | index update lag |

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL expose /actuator/health with liveness and readiness; readiness SHALL be DOWN until the empresa schema validates and Kafka/Eureka are reachable.`
- `THE SYSTEM SHALL propagate X-Correlation-Id across HTTP, Feign, Kafka and TechLab AI calls via MDC.`
- `WHEN TechLab AI assist falls back, THE SYSTEM SHALL increment lead_assist_ia_fallback_total.`
- `THE SYSTEM SHALL emit structured logs without PII (identifiers only).`
- `THE SYSTEM SHALL record the Maturity Score distribution and qualification outcome counters.`

## Edge cases
- Elastic down → readiness stays UP (read-only degradation), a metric/alert flags index lag.

## References
- `docs/architecture/backend/standards/platform-patterns.md` (MDC); SPEC-09; SPEC-10.
