# ASST-015 -- Observability + health (Actuator, métricas, MDC)

## Contexto
Health checks, métricas e logging estruturado, com foco em latência do Asset Studio e indexação
Elastic.

## Spec de referencia
- SPEC-07-observability-health

## Escopo
- Actuator health (db, kafka, elastic, techlab-ai como degradado≠down) + liveness/readiness.
- Micrometer: `asst_studio_compose_latency`, `asst_studio_compose_failures`, `asst_publish_total`, `asst_index_failures`.
- MDC interceptor (`correlationId`, `empresaId`); `@Slf4j` (sem `System.out`).

## Resultado esperado
Serviço observável; readiness UP mesmo com TechLab AI/Elastic degradados.

## Criterios de aceite
- [ ] `/actuator/health` com liveness/readiness.
- [ ] TechLab AI down → readiness=UP (Studio degradado).
- [ ] Logs incluem `correlationId` e `empresaId`.
- [ ] Métricas do Studio/index expostas.

## Dependencias
- ASST-001 (precede)

## Estimativa
S

## Prioridade
P7
