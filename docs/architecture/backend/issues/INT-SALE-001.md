# INT-SALE-001 — Integração WRKS (AccessDecision/JWT)

## Contexto
Validar a integração de autorização com WRKS: JWKS para JWT e `AccessDecision` para `sale.*`.

## Spec de referencia
- `contracts/hub-integration.md` §1, SPEC-06, SPEC-10

## Escopo
Contract test (WireMock) do `AccessEvaluateClient`; validação de JWT via JWKS; deny-by-default em
circuito aberto.

## Resultado esperado
Autorização inter-serviço confiável.

## Criterios de aceite
- [ ] JWT inválido → 401; permissão ausente → 403
- [ ] circuito aberto → 503 `sale.dependencia.indisponivel`
- [ ] cache invalidado por `modelo.acesso.alterado`

## Dependencias
- SALE-011, SALE-013 (precede)

## Estimativa
M

## Prioridade
P5
