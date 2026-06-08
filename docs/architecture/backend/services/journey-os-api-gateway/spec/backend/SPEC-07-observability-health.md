# SPEC-07 — Observability & Health — GWY

> Acceptance criteria em EARS.

## Objetivo

Definir health checks, métricas, logs e tracing de borda para o gateway.

## Escopo

**In:** Actuator (health/info/routes/prometheus), métricas Micrometer por rota, logs estruturados
com `correlationId`, propagação de trace.
**Out:** plataforma de observabilidade (coleta/retenção em INTL/Elastic).

## 1. Health & readiness

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL expor `/actuator/health` com liveness e readiness.
- WHILE o cliente Eureka não tiver concluído o primeiro registro, THE SYSTEM SHALL reportar readiness `OUT_OF_SERVICE`.
- WHEN o Redis estiver indisponível, THE SYSTEM SHALL refletir o estado no health (componente degradado) sem necessariamente derrubar liveness (conforme política fail-open).

## 2. Métricas (Micrometer / Prometheus)

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL expor métricas em `/actuator/prometheus`.
- THE SYSTEM SHALL registrar latência e contagem por `routeId` e por status HTTP.
- WHEN uma requisição é limitada, THE SYSTEM SHALL incrementar um contador de rate-limit por `RateLimitKey` type.
- WHEN uma autenticação falha, THE SYSTEM SHALL incrementar um contador por motivo (assinatura/exp/claim).

## 3. Logs estruturados & correlação

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL incluir `correlationId` em toda linha de log de uma requisição (MDC reativo).
- THE SYSTEM SHALL registrar, no nível INFO, o `routeId` resolvido e o status final, sem corpo/PII.
- IF ocorrer erro de borda (401/403/404/429/503/504), THEN THE SYSTEM SHALL logar o motivo com o `correlationId`.

## 4. Tracing

**Acceptance criteria (EARS):**
- THE SYSTEM SHALL propagar o contexto de trace (W3C `traceparent`) ao downstream.
- WHEN ausente na entrada, THE SYSTEM SHALL iniciar um novo trace na borda.

## Casos de borda

- Alto volume: amostragem de trace configurável; logs em nível WARN/ERROR não amostrados.
- LGPD: logs não devem conter payloads nem dados pessoais (apenas metadados + correlação).

## Critérios de aceite (resumo)

- `/actuator/health`, `/actuator/prometheus` e `/actuator/gateway/routes` operacionais.
- 100% das requisições com `correlationId` em logs e downstream.
