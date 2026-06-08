# INTL-012 -- Security + multi-tenancy + LGPD

## Contexto
Autenticação, autorização `intl.*`, isolamento de tenant e conformidade LGPD.

## Spec de referência
- SPEC-06, `contracts/hub-integration.md §1`, ADR-004

## Escopo
OAuth2 resource server (JWKS de WRKS); `AccessEvaluateClient` + `AccessDecisionCachePort` (Redis,
invalidado por `modelo.acesso.alterado`); `EmpresaContextHolder` (claim `empresa`); injeção
obrigatória do filtro `empresa` no `IntlSearchPort`; MDC; suporte LGPD (anonimização/expurgo).

## Resultado esperado
Acesso fail-closed; zero vazamento cross-tenant.

## Critérios de aceite
- [ ] `401`/`403` corretos; AccessDecision fail-closed
- [ ] Tenant só do claim JWT `empresa`
- [ ] Toda query Elastic carrega filtro `empresa` (teste de isolamento)
- [ ] Citação nunca cruza tenant; expurgo LGPD remove PII da `empresa`

## Dependências
- INTL-005, INTL-010 (precedem)

## Estimativa
L

## Prioridade
P5
