# SPEC-07 — Observability & Health

> Ref: `04-backend-architecture-direction.md §6`. Padrão de plataforma (MDC, Actuator).

## Objetivo

Tornar INTL observável: health checks, métricas de custo/latência da IA, contadores de DLQ,
correlação ponta-a-ponta.

## Escopo

**In:** `/actuator/health` (liveness/readiness com dependências), MDC (`empresa`, `traceId`,
`correlationId`, `conversaId`), métricas (custo de tokens, latência IA, taxa de degradação,
DLQ count), logs estruturados (`@Slf4j`).
**Out:** ingestão dos índices `app-logs`/`traces`/`metrics` (infra/APM, fora do MVP).

## Decisões técnicas

- Actuator + readiness considerando PG, Elastic, TechLab AI, Kafka.
- Micrometer: `intl.copilot.custo_tokens`, `intl.copilot.latencia_ms`, `intl.copilot.degradadas`,
  `intl.dlq.count`, `intl.knowledge.indexados`.
- `X-Correlation-Id` propagado a TechLab AI/Elastic; `spring.jpa.open-in-view=false`.

## Critérios de aceite (EARS)

- THE SYSTEM SHALL expor `/actuator/health` refletindo a saúde de PG, Elastic, TechLab AI e Kafka.
- WHILE a TechLab AI está em circuito aberto, THE SYSTEM SHALL reportar readiness degradada para o copiloto sem ficar `DOWN`.
- WHEN uma resposta é gerada, THE SYSTEM SHALL registrar métricas de custo de tokens e latência.
- WHEN um documento é roteado à DLQ, THE SYSTEM SHALL incrementar o contador `intl.dlq.count`.
- THE SYSTEM SHALL propagar `X-Correlation-Id` em toda chamada externa (TechLab AI/Elastic).
