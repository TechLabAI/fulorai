# WRKS-009 -- Adapter Keycloak OIDC (IdpPort) + resiliência

## Contexto
Integração com o IdP (Keycloak) para autenticação OIDC. WRKS é dono da autorização; Keycloak
apenas autentica (ADR-002).

## Spec de referencia
- SPEC-10-integrations
- integration-contracts.md

## Escopo
- `infrastructure/clients`: adapter de `IdpPort` (Authorization Code: troca código→tokens,
  fetch `sub`/userinfo, validação do token do IdP).
- Mapeia `sub` → `usuario.idp_subject`.
- Resilience4j: circuit-breaker + timeout 2s; sem retry no login (fail fast); sem bypass.

## Resultado esperado
Login OIDC funcional; Keycloak indisponível → 502 sem bypass; JWTs existentes seguem válidos.

## Criterios de aceite
- [ ] Troca de código mapeia `sub` para `usuario.idp_subject`.
- [ ] Keycloak down → 502 `upstream_error`, sem bypass de autenticação.
- [ ] `@FeignClient`/cliente HTTP apenas em `infrastructure.clients` (RULE-06).
- [ ] Stub WireMock nos testes.

## Dependencias
- WRKS-004 (consumidor), INT-WRKS-002

## Estimativa
M

## Prioridade
P4
