# COMM-015 -- Observability + health (MDC, métricas por canal/provedor)

## Contexto
Operabilidade: logs estruturados, MDC, métricas de entregabilidade e health checks.

## Spec de referencia
- SPEC-07-observability-health

## Escopo
- MDC (`correlationId`, `empresaId`) em request, worker de disparo e consumo de evento.
- Métricas Micrometer: latência por canal/provedor, taxa de entrega/falha, profundidade da fila, idade do outbox, CB por adapter.
- `/actuator/health` com readiness gated no DB; provedores/Elastic como health degradado.
- Logs sem segredo/`conteudo_renderizado` em claro (PII).

## Resultado esperado
Visibilidade de entregabilidade por canal; readiness não cai quando provedor/Elastic degradam.

## Criterios de aceite
- [ ] `correlationId`/`empresaId` presentes em request, worker e consumer.
- [ ] Métricas por canal/provedor expostas.
- [ ] CB de provedor aberto → health detail degradado, readiness UP.

## Dependencias
- COMM-001 (precede)

## Estimativa
S

## Prioridade
P7
