# ASST-012 -- Security: JWT + AccessDecision + permissões asst.* + tenant guard

## Contexto
Autenticação por JWT (WRKS), autorização por permissões `asst.*` via AccessDecision e isolamento
de tenant por schema.

## Spec de referencia
- SPEC-06-security
- contracts/hub-integration.md

## Escopo
- Filtro de segurança: valida JWT contra JWKS de WRKS; popula `EmpresaContextHolder` do claim.
- `AccessDecisionPort` → resolve papel/permissões; cache invalidado por `modelo.acesso.alterado`.
- Anotações de autorização por endpoint (`asst.asset.criar|...|publicar`, `asst.studio.compor`).
- Tenant guard: nenhum dado cross-empresa.

## Resultado esperado
Endpoints protegidos; cross-tenant impossível; permissão ausente → 403.

## Criterios de aceite
- [ ] Sem JWT válido → 401 `asst.auth.token-invalido`.
- [ ] Falta permissão → 403 `asst.acesso.permissao-negada`.
- [ ] JWT de empresa A nunca acessa asset de empresa B.
- [ ] `@Transactional` não aparece em controller/adapter (RULE-03).

## Dependencias
- ASST-003 (precede); INT-ASST-002 (AccessDecision)

## Estimativa
M

## Prioridade
P5
