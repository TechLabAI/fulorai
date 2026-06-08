# SPEC-06 — Security

> ADR-004 (multi-tenancy). RBAC: `shared/rbac/{modelo,permissoes,data-scope}.md`. EARS guide linkado.

## Objetivo

Definir autenticação (JWT WRKS), autorização (`asst.*`), isolamento de tenant e proteção de
dados (LGPD) em `asst-service`.

## Escopo

- **In:** validação de JWT (JWKS WRKS), resolução de `AccessDecision`, guarda de tenant, permissões por endpoint, LGPD.
- **Out:** emissão de token/login (WRKS); políticas de IdP (Keycloak).

## Decisões técnicas

- Filtro de segurança valida JWT contra `WRKS_JWKS_URI`; popula `EmpresaContextHolder` a partir do claim `empresa_id`.
- Autorização por `AccessDecision` (Feign WRKS), cache invalidado por `modelo.acesso.alterado`.
- `MultiTenantConnectionProvider` aplica `SET search_path TO emp_<id>, journeyos_global, public`.

## Permissões `asst.*`

`asst.asset.criar`, `asst.asset.editar`, `asst.asset.ler`, `asst.asset.submeter`,
`asst.asset.aprovar`, `asst.asset.publicar`, `asst.asset.arquivar`, `asst.studio.compor`.
(Confirmar/registrar em `shared/rbac/permissoes.md`.)

## Casos de borda

- JWT de empresa A acessando asset de empresa B → 404 (nunca vaza existência cross-tenant).
- `data_scope` restrito (SDR) → enxerga subconjunto conforme decisão de acesso.

## Critérios de aceite (EARS)

- `IF a request has no valid JWT, THEN THE SYSTEM SHALL reject with 401 error.code 'asst.auth.token-invalido'.`
- `THE SYSTEM SHALL fix the tenant schema from the JWT empresa_id claim and SHALL ignore any empresa id supplied in path/body/header for data access.`
- `IF the AccessDecision lacks the required asst.* permission for the operation, THEN THE SYSTEM SHALL reject with 403 error.code 'asst.acesso.permissao-negada'.`
- `THE SYSTEM SHALL never return an asset, version or approval belonging to another empresa.`
- `WHEN journey-os.modelo.acesso.alterado is received, THE SYSTEM SHALL invalidate the affected cached AccessDecision before the next check.`
- `WHERE a data_scope restriction applies to the caller, THE SYSTEM SHALL filter results accordingly.`
