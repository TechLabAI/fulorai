# INTL-015 -- Observability + health

## Contexto
Tornar INTL observável (health, métricas de IA, DLQ, correlação).

## Spec de referência
- SPEC-07

## Escopo
Actuator health (PG/Elastic/TechLab AI/Kafka); métricas Micrometer (`intl.copilot.custo_tokens`,
`intl.copilot.latencia_ms`, `intl.copilot.degradadas`, `intl.dlq.count`, `intl.knowledge.indexados`);
MDC (`empresa`/`traceId`/`correlationId`/`conversaId`); logs `@Slf4j`.

## Resultado esperado
Saúde e métricas expostas; correlação ponta-a-ponta.

## Critérios de aceite
- [ ] `/actuator/health` reflete dependências
- [ ] Readiness degradada (não DOWN) quando CB da IA aberto
- [ ] Métricas de custo/latência/DLQ emitidas
- [ ] `X-Correlation-Id` propagado a TechLab AI/Elastic

## Dependências
- INTL-005, INTL-009 (precedem)

## Estimativa
M

## Prioridade
P7
