# LEAD-017 -- Observability + health (Actuator, metrics, MDC)

## Contexto
Saúde, métricas de domínio e propagação de correlação para o `lead-service`.

## Spec de referencia
- SPEC-07-observability-health

## Escopo
- Actuator health/liveness/readiness (readiness DOWN até schema validar + Kafka/Eureka acessíveis).
- Métricas Micrometer: `lead_capturado_total{fonte}`, `lead_qualificado_total{estado}`,
  `lead_score_distribuicao`, `lead_assist_ia_fallback_total`, `lead_qualify_latency`, `lead_elastic_index_lag`.
- `correlationId` no MDC propagado a HTTP/Feign/Kafka/TechLab AI.
- Logs estruturados (JSON), sem PII.

## Resultado esperado
Serviço observável; readiness reflete dependências; métricas de score/qualificação expostas.

## Criterios de aceite
- [ ] `/actuator/health` com liveness/readiness corretos.
- [ ] Métricas de domínio expostas (incl. fallback de assist IA).
- [ ] `X-Correlation-Id` propagado em todas as saídas.
- [ ] Logs sem PII.

## Dependencias
- LEAD-005 (eventos/score para métricas)

## Estimativa
S

## Prioridade
P7
