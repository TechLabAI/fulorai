# SPEC-07 — Observability & Health

> EARS guide linkado. Padrões: `platform-patterns.md` (MDC), Actuator/Micrometer.

## Objetivo

Definir health checks, métricas, logging estruturado e tracing de `asst-service`, com foco no
custo/latência do Asset Studio (TechLab AI) e na indexação Elastic.

## Escopo

- **In:** `/actuator/health` (liveness/readiness), métricas Micrometer, MDC (`correlationId`, `empresaId`), logs SLF4J.
- **Out:** dashboards/alertas (INTL/observabilidade central).

## Decisões técnicas

- Actuator + Micrometer (Prometheus registry). Health groups: db, kafka, elastic, techlab-ai (degradado ≠ down).
- MDC interceptor propaga `X-Correlation-Id`; `@Slf4j` (nunca `System.out`).
- Métricas-chave: `asst_studio_compose_latency`, `asst_studio_compose_failures`, `asst_publish_total`, `asst_index_failures`.

## Casos de borda

- TechLab AI down → readiness permanece UP (Studio degradado, serviço saudável).
- Elastic down → readiness UP; métrica `asst_index_failures` incrementa.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose /actuator/health with liveness and readiness probes.`
- `WHILE TechLab AI is unavailable, THE SYSTEM SHALL report readiness=UP (the Studio is degraded, not the service).`
- `THE SYSTEM SHALL include correlationId and empresaId in every log line via MDC.`
- `WHEN an Asset Studio composition is attempted, THE SYSTEM SHALL record its latency and outcome as metrics.`
- `WHEN an Elasticsearch index operation fails, THE SYSTEM SHALL increment a failure metric AND SHALL NOT fail the originating write.`
- `THE SYSTEM SHALL NOT use System.out for logging.`
