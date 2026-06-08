# SPEC-06 — Security (WRKS)

## Objective
Define authentication, token issuance/validation, authorization, anti-escalation and
cross-empresa isolation for the platform's identity authority.

## Scope
- **In:** OIDC auth (Keycloak), JWT RS256 issuance + JWKS, refresh rotation + blacklist,
  permission enforcement, anti-escalation, cross-empresa guard, session policy.
- **Out:** MFA, multi-SSO, IP-restriction enforcement (config-only in MVP).

## Technical decisions
- ADR-002 (authority), ADR-005 (token model). Keycloak authenticates; WRKS authorizes.
  JWT claims: `sub, empresa_id, papel, modelo_acesso_versao, data_scope, exp`.

## Implementation & acceptance criteria (EARS)
- `THE SYSTEM SHALL sign access tokens with RS256 and expose the public keys via JWKS.`
- `THE SYSTEM SHALL store refresh tokens only as httpOnly+secure+sameSite=strict cookies and SHALL rotate them on use.`
- `WHEN an admin assigns or edits a role hierarchically above their own role level, THE SYSTEM SHALL reject the operation (wrks.papel.escalonamento).`
- `THE SYSTEM SHALL NOT return data belonging to an empresa other than the JWT's empresa_id (cross-empresa guard).`
- `THE SYSTEM SHALL call EmpresaContextHolder.require() at the entry of every application service touching empresa data (RULE-07).`
- `WHERE a role's session policy enables ip-restriction, THE SYSTEM SHALL record the configuration but SHALL NOT enforce it in the MVP.`
- `IF a permission referenced in @PreAuthorize is absent from the canonical catalogue, THEN the build SHALL fail (be-module-generator validation, D-060).`
- `THE SYSTEM SHALL never store roles/permissions in Keycloak as source of truth.`

## Edge cases
- Token replay after logout → blacklist check rejects until natural expiry. Privilege change mid-session → version bump forces refresh.

## References
- `shared/rbac/{modelo,session-policy,permissoes}.md`, ADR-002, ADR-005, `shared/contratos/error-model.md`.
