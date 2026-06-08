# SPEC-02 — Identity & Session (core orchestration)

## Objective
The central WRKS use case: turn an authenticated identity (Keycloak OIDC) into a tenant-scoped
platform credential, and manage its lifecycle (login → switch → refresh → logout).

## Scope
- **In:** OIDC code exchange, user mapping, empresa selection, JWT issuance (RS256), refresh
  rotation, logout blacklist, session restore, trocar-empresa, tenant provisioning trigger.
- **Out:** authorization evaluation (SPEC-03), DDL (SPEC-04).

## Technical decisions
- ADR-002 (Keycloak = IdP, WRKS = authority), ADR-005 (token model). Session policy per role
  from `shared/rbac/session-policy.md` (TTLs/idle), config-driven.

## Implementation
- `LoginService`: exchange code (IdpPort) → resolve/auto-provision `usuario` by `idp_subject` →
  load active `usuario_empresa` → select empresa (1 auto, N → list) → issue JWT (TokenIssuerPort)
  → write session + refresh (SessionCachePort) → publish `sessao.estabelecida`.
- `TrocarEmpresaService`: validate active association → reissue JWT.
- `RefreshService`: validate refresh (rotation) → reissue.
- `LogoutService`: clear cookie + blacklist `jti`.
- `ProvisionarEmpresaService`: insert empresa (PROVISIONANDO) → MigrationTriggerPort → on confirm,
  set ATIVA + publish `empresa.provisionada` (saga; idempotent — SPEC-05).

## Acceptance criteria (EARS)
- `WHEN a valid OIDC code is exchanged for a user with one active empresa, THE SYSTEM SHALL issue a JWT scoped to that empresa.`
- `WHEN the user has N>1 active empresas and none is chosen, THE SYSTEM SHALL return the selectable list and SHALL NOT issue a tenant JWT.`
- `IF the user has no active association, THEN THE SYSTEM SHALL reject login (wrks.usuario.sem-empresa-ativa).`
- `WHEN trocar-empresa targets an active association, THE SYSTEM SHALL reissue a JWT without re-authentication.`
- `THE SYSTEM SHALL set the access-token TTL according to the role's session policy.`
- `WHEN MIG confirms provisioning, THE SYSTEM SHALL set the empresa ATIVA and publish journey-os.empresa.provisionada.`

## Edge cases
- Keycloak down → 502, existing JWTs keep working. First-time OIDC subject → auto-create `usuario` (inactive associations → still cannot pick empresa).

## References
- ADR-002, ADR-005, `shared/rbac/session-policy.md`, `contracts/api-contract.md` §1, §3.
