# SPEC-03 — RBAC & AccessDecision (sub-feature)

## Objective
Own the canonical access model and serve `AccessDecision` to GWY and all services, with
fast cross-service invalidation on change.

## Scope
- **In:** roles/permissions/bundles, `usuario_empresa` role+data_scope, `modelo_acesso_versao`,
  `POST /access/evaluate`, cache + invalidation, JWKS.
- **Out:** data_scope **enforcement** in business services (lives in each service via Hibernate
  Filter — `shared/rbac/enforcement.md`); WRKS only **declares** the data_scope in the decision.

## Technical decisions
- Roles are canonical (INFOPRODUTOR/HEAD_GROWTH/SDR), seeded from `rbac.arch.json`. Bundles
  explicit (no wildcard). Version-based cache invalidation — ADR-003/ADR-005.

## Implementation
- `AvaliarAcessoService`: cache lookup (AccessDecisionCachePort) keyed `{usuarioId}:{empresaId}` →
  on miss, load association + role bundle + version → build `AccessDecisionResponse` → cache 5 min.
- `GerenciarPapelService`: on bundle change → bump `modelo_acesso_versao` (same tx) → publish
  `modelo.acesso.alterado` → consumers invalidate.
- JWKS endpoint serves the RS256 public keys.

## Acceptance criteria (EARS)
- `THE SYSTEM SHALL return AccessDecision with role, explicit permission list, data_scope, and modelo_acesso_versao.`
- `WHILE a cached decision matches the current version, THE SYSTEM SHALL serve it from Redis.`
- `WHEN a role bundle changes, THE SYSTEM SHALL bump modelo_acesso_versao in the same transaction and publish journey-os.modelo.acesso.alterado.`
- `IF a JWT presents a modelo_acesso_versao below the current value, THEN THE SYSTEM SHALL respond 401 iam.sessao.versao-desatualizada.`
- `IF a bundle edit references a permission absent from the catalogue, THEN THE SYSTEM SHALL reject (wrks.papel.permissao-desconhecida).`
- `THE SYSTEM SHALL expose JWKS publicly without authentication.`

## Edge cases
- Redis down → evaluate from PostgreSQL. Inactive association → 404. Permission seeds missing → bundle edit fails fast.

## References
- `shared/rbac/{modelo,papeis,permissoes,data-scope,enforcement}.md`, ADR-003, ADR-005.
