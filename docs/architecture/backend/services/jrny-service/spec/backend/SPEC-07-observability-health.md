# SPEC-07 — Observability & Health

> ADR-003 (resiliência/assist). Padrões: `platform-patterns.md` (MDC), Actuator/Micrometer.
> EARS guide: `docs/architecture/backend/standards/ears-notation.md`.

## Objetivo

Definir health checks, métricas, logging estruturado e tracing de `jrny-service`, com foco na
latência da avaliação de roteamento, na chamada à TechLab AI (`orchestration`) e na taxa de
fallback determinístico (assist indisponível).

## Escopo

- **In:** `/actuator/health` (liveness/readiness), métricas Micrometer, MDC (`correlationId`, `empresaId`, `leadId`), logs SLF4J.
- **Out:** dashboards/alertas (INTL/observabilidade central).

## Decisões técnicas

- Actuator + Micrometer (Prometheus registry). Health groups: db, kafka, elastic, techlab-ai (degradado ≠ down).
- MDC interceptor propaga `X-Correlation-Id`; consumers populam `empresaId`+`leadId` no MDC; `@Slf4j` (nunca `System.out`).
- Métricas-chave: `jrny_routing_eval_latency`, `jrny_routing_decisions_total{resultado}`, `jrny_ai_assist_total{estado}` (USADO/IGNORADO/INDISPONIVEL), `jrny_ai_fallback_total`, `jrny_index_failures{indice}`.

## Casos de borda

- TechLab AI down → readiness permanece UP (assist degradado, serviço saudável); `jrny_ai_fallback_total` incrementa.
- Elastic down → readiness UP; `jrny_index_failures` incrementa; decisão não é revertida.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose /actuator/health with liveness and readiness probes.`
- `WHILE TechLab AI is unavailable, THE SYSTEM SHALL report readiness=UP (the routing assist is degraded, not the service).`
- `THE SYSTEM SHALL include correlationId, empresaId and leadId in every log line via MDC on the routing path.`
- `WHEN a routing evaluation completes, THE SYSTEM SHALL record its latency and the decision resultado as metrics.`
- `WHEN the deterministic fallback is used because the AI assist was unavailable, THE SYSTEM SHALL increment a fallback metric.`
- `WHEN an Elasticsearch index operation fails, THE SYSTEM SHALL increment a failure metric AND SHALL NOT fail or revert the routing decision.`
- `THE SYSTEM SHALL NOT use System.out for logging.`
