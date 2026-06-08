# WRKS-017 -- Observabilidade + health (MDC, métricas IAM, readiness)

## Contexto
Instrumentação operacional do serviço fundação: logs estruturados, métricas de sessão/acesso
e readiness refletindo as dependências.

## Spec de referencia
- SPEC-07-observability-health

## Escopo
- `@Slf4j` + MDC (`empresaId`, `correlationId`, `usuarioId`) em request e consume async.
- Métricas Prometheus: `journey-os_iam_session_active_total{papel}`,
  `..._refresh_total{papel,outcome}`, `..._logout_total{motivo}`, `..._session_blacklist_size`,
  latência + hit ratio do `access/evaluate`.
- `/actuator/health` readiness: PostgreSQL, Redis, Kafka, Keycloak.

## Resultado esperado
Sinais operacionais completos; sem vazar segredos/tokens nos logs.

## Criterios de aceite
- [ ] MDC presente em request e consume.
- [ ] Métricas IAM expostas no `/actuator/prometheus`.
- [ ] Readiness degrada se Keycloak/Redis/Kafka/PG caem (liveness independente).
- [ ] Nenhum token/segredo logado.

## Dependencias
- WRKS-001 (precede)

## Estimativa
S

## Prioridade
P7
