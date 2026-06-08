# WRKS-011 -- Emissão JWT RS256 + JWKS + filtro de validação

## Contexto
WRKS é o emissor da credencial da plataforma. JWT RS256 stateless, validável via JWKS por
GWY e todos os serviços (ADR-005).

## Spec de referencia
- SPEC-06-security
- SPEC-03-rbac-access-decision

## Escopo
- `TokenIssuerPort` adapter: assina JWT RS256 (claims `sub, empresa_id, papel, modelo_acesso_versao, data_scope, exp`).
- Endpoint público `GET /api/v1/iam/.well-known/jwks.json`.
- `EmpresaContextFilter` (Security): lê claim → popula `EmpresaContextHolder` + MDC.
- Detecção de versão stale: `jwt.modelo_acesso_versao < global` → 401 `iam.sessao.versao-desatualizada`.

## Resultado esperado
JWT emitido/validado de forma distribuída; JWKS público; versão stale força refresh.

## Criterios de aceite
- [ ] JWKS retorna chave pública RS256 sem autenticação.
- [ ] Versão stale → 401 `iam.sessao.versao-desatualizada`.
- [ ] Token expirado → 401 `iam.token-expirado`.
- [ ] `EmpresaContextHolder` populado a partir do claim.

## Dependencias
- WRKS-002 (precede)

## Estimativa
M

## Prioridade
P5
