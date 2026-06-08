# SALE-017 — Observability + health

## Contexto
Expor health/readiness e métricas de negócio/técnicas do `sale-service`.

## Spec de referencia
- SPEC-07

## Escopo
Actuator health (liveness) + readiness (Postgres/Kafka); Micrometer (receita reconhecida, conversão
por estágio, atribuição por modelo, latência de ingestão, recálculo de LTV; Feign/outbox/consumer
lag); MDC com `correlationId`/`empresaId`, sem PII.

## Resultado esperado
Serviço observável.

## Criterios de aceite
- [ ] `/actuator/health` + `/actuator/health/readiness` (gated em Postgres/Kafka)
- [ ] métricas de negócio e técnicas expostas
- [ ] readiness falha fechado se schema inválido (migrations não aplicadas)
- [ ] nenhuma PII em logs/métricas/traces

## Dependencias
- SALE-009 (precede)

## Estimativa
S

## Prioridade
P7
