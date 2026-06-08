# INT-WRKS-006 -- Contrato provider AccessDecision/JWKS (GWY + todos os serviços)

## Contexto
WRKS é provider de autorização: contrato estável de `AccessDecision` (HTTP) + JWKS + evento
`modelo.acesso.alterado` consumido por GWY e todos os serviços.

## Spec de referencia
- hub-integration.md §1
- event-contracts.md §1
- SPEC-03-rbac-access-decision

## Escopo
- Contrato `POST /access/evaluate` (token de serviço) + `AccessDecisionResponse` versionado.
- JWKS estável; evento `modelo.acesso.alterado` para invalidação de cache cross-serviço.
- Testes de contrato (Pact-style) consumer↔provider.

## Resultado esperado
Consumidores não acessam IAM diretamente; invalidação de cache propaga em < 5s.

## Criterios de aceite
- [ ] `evaluate` retorna contrato versionado estável.
- [ ] `modelo.acesso.alterado` publicado a cada mudança de RBAC.
- [ ] Teste de contrato provider passa.

## Dependencias
- WRKS-012, WRKS-015

## Estimativa
M

## Prioridade
P6
