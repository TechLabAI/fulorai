# SPEC-07 — Observability & Health

> EARS guide linkado. Relaciona SPEC-02 (dispatch), SPEC-10 (providers/Elastic).

## Objetivo

Definir logs estruturados, métricas, tracing (MDC) e health checks para operar o `comm-service`,
com visibilidade especial sobre entregabilidade por canal/provedor.

## Escopo

- **In:** MDC (`correlationId`, `empresaId`); métricas (latência por canal/provedor, taxa de entrega/falha, profundidade da fila de disparo, idade do outbox); health/readiness; logs sem dados sensíveis.
- **Out:** dashboards/alertas concretos (operacional, INTL).

## Decisões técnicas

- **Logging:** SLF4J via Lombok `@Slf4j`; nunca `System.out`; JSON estruturado; **nunca** logar `credencial_ref`/segredo nem `conteudo_renderizado` em claro (PII).
- **MDC:** `correlationId` e `empresaId` propagados em request, worker de disparo e consumo de evento.
- **Métricas (Micrometer):** `comm.dispatch.latency{canal,provedor}`, `comm.delivery.rate{canal,estado}`, `comm.dispatch.queue.depth`, `comm.outbox.age`, contadores de CB por adapter.
- **Health:** `/actuator/health` com readiness dependente de DB; provedores/Elastic como health *degradado* (não derrubam readiness — best-effort).

## Casos de borda

- Provedor de canal lento → métrica de latência sobe + CB abre; readiness do serviço permanece UP (disparo via worker degrada, não cai).
- Elastic fora → health degradado, não DOWN (projeção é best-effort).
- Outbox acumulando (worker parado) → métrica `comm.outbox.age` dispara alerta.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL include correlationId and empresaId in the MDC of every request, dispatch job, and event consumption.`
- `THE SYSTEM SHALL expose /actuator/health with readiness gated on the database only.`
- `WHILE a channel provider's circuit breaker is open, THE SYSTEM SHALL report it as a degraded health detail without marking readiness DOWN.`
- `THE SYSTEM SHALL emit per-channel/provider dispatch latency and delivery/failure-rate metrics.`
- `THE SYSTEM SHALL never log provider secrets or raw rendered personal content.`
