# INT-WRKS-002 -- Integração Keycloak (OIDC) + mapeamento JWKS

## Contexto
Autenticação OIDC via Keycloak (IdP) e fornecimento de JWKS de WRKS para validação por GWY/serviços.

## Spec de referencia
- integration-contracts.md §1
- SPEC-06-security

## Escopo
- Cliente OIDC confidencial (`client_id`/`client_secret`); issuer `KEYCLOAK_ISSUER_URI`.
- Mapeamento `sub` → `usuario.idp_subject`.
- WRKS expõe JWKS próprio (par RS256) para validação distribuída.

## Resultado esperado
Login OIDC ponta-a-ponta; GWY valida JWT via JWKS de WRKS.

## Criterios de aceite
- [ ] Code exchange retorna tokens e `sub`.
- [ ] Keycloak indisponível → 502 sem bypass.
- [ ] JWKS de WRKS consumível por GWY.

## Dependencias
- WRKS-009, WRKS-011

## Estimativa
M

## Prioridade
P5
