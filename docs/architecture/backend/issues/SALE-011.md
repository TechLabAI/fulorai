# SALE-011 — Feign AccessEvaluateClient (WRKS) + Resilience4j

## Contexto
Integrar autorização `sale.*` via WRKS `AccessDecision` (Feign), com circuit breaker e
deny-by-default.

## Spec de referencia
- SPEC-10, `contracts/hub-integration.md` §1

## Escopo
`AccessEvaluateClient` (`@FeignClient(name="wrks-service")`) em `infrastructure.clients`;
Resilience4j (timeout/circuit breaker); cache Redis (`AccessDecisionCachePort`).

## Resultado esperado
Autorização resiliente por requisição.

## Criterios de aceite
- [ ] `@FeignClient` apenas em `infrastructure.clients` (RULE-06)
- [ ] circuito aberto → deny-by-default + 503 `sale.dependencia.indisponivel`
- [ ] cache invalidado por `modelo.acesso.alterado`
- [ ] teste com WireMock

## Dependencias
- SALE-001 (precede)

## Estimativa
M

## Prioridade
P4
