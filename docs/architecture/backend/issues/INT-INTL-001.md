# INT-INTL-001 -- Integração WRKS (AccessDecision + JWKS)

## Contexto
INTL autoriza toda operação `intl.*` e valida JWT contra WRKS.

## Spec de referência
- SPEC-06, `contracts/hub-integration.md §1`, `integration-contracts.md`

## Escopo
`AccessEvaluateClient` (`@FeignClient(name="wrks-service")`) + validação JWKS; cache de
AccessDecision (`AccessDecisionCachePort`, Redis) invalidado por `modelo.acesso.alterado`.
WireMock nos testes.

## Resultado esperado
Autorização fail-closed e validação de token funcionando.

## Critérios de aceite
- [ ] `intl.*` autorizado via AccessDecision antes de executar
- [ ] JWT inválido → `401`; permissão negada → `403`
- [ ] Cache invalidado por evento

## Dependências
- INTL-012

## Estimativa
M

## Prioridade
P5
