# SALE-019 — Hardening (resiliência, re-atribuição em lote, runbook)

## Contexto
Endurecer SLAs, retries, circuit breaker e o caminho de re-atribuição ao trocar modelo; runbook
operacional.

## Spec de referencia
- SPEC-03, SPEC-10, ADR-005

## Escopo
Re-atribuição em lote pequeno síncrono na ativação de modelo; retries/backoff; timeouts; runbook
(estorno/cancelamento, reprocesso de webhook duplicado). Pipeline assíncrono dedicado fica pós-MVP.

## Resultado esperado
Serviço robusto sob carga e falhas.

## Criterios de aceite
- [ ] re-atribuição idempotente por `(compra_id, versao_modelo)`
- [ ] circuit breaker/timeout configurados (WRKS, Elastic)
- [ ] runbook documentado (estorno, webhook duplicado, troca de modelo)

## Dependencias
- SALE-007, SALE-012 (precede)

## Estimativa
M

## Prioridade
P9
