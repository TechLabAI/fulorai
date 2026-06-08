# WRKS-004 -- LoginService (OIDC → JWT, seleção de empresa, session policy)

## Contexto
Caso de uso central do golden path: transformar uma identidade autenticada (Keycloak OIDC)
numa credencial JWT escopada por tenant.

## Spec de referencia
- SPEC-02-identity-session
- SPEC-06-security

## Escopo
- `LoginService` (@Service, @Transactional): troca código OIDC (IdpPort) → resolve/auto-cria
  `usuario` por `idp_subject` → carrega `usuario_empresa` ativas → seleção (1 auto / N lista).
- Emite JWT (TokenIssuerPort) com claims `sub, empresa_id, papel, modelo_acesso_versao, data_scope, exp`.
- TTL por papel via session policy (`shared/rbac/session-policy.md`). Grava sessão + refresh cookie.
- Publica `journey-os.sessao.estabelecida`.

## Resultado esperado
Login single-empresa emite JWT; multi-empresa devolve lista; sem associação ativa → 422.

## Criterios de aceite
- [ ] Single-empresa → JWT com `empresa_id` correto + refresh cookie httpOnly/secure/sameSite=strict.
- [ ] N>1 sem seleção → lista de empresas, sem JWT de tenant.
- [ ] Sem `usuario_empresa` ativo → 422 `wrks.usuario.sem-empresa-ativa`.
- [ ] Código OIDC inválido → 401 `iam.credenciais-invalidas`.
- [ ] `@Transactional` apenas no service (RULE-03).

## Dependencias
- WRKS-003 (precede), WRKS-011 (TokenIssuer), INT-WRKS-002 (Keycloak)

## Estimativa
L

## Prioridade
P2
