# API Contract — WRKS (`/api/v1/iam/**`)

> REST surface of `wrks-service`. All error responses use `application/problem+json` (RFC 7807,
> `shared/contratos/error-model.md`). EARS invariants per endpoint.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## Conventions

- Base path: `/api/v1/iam`.
- Auth: Bearer JWT (RS256) issued by WRKS, **except** `sessao/login`, `sessao/refresh`,
  `sessao/restore` and `.well-known/jwks.json` (bootstrap/public).
- Mandatory headers downstream: `X-Correlation-Id` (propagated/generated), `Authorization`.
- Tenant: `empresa_id` travels as a JWT claim (not a path/body field). `X-Empresa-Id` is
  accepted for debug/log only and never overrides the claim.
- Authorization: `wrks.*` permissions for admin resources; session endpoints gated by
  authentication + ownership.

---

## 1. Session — `/sessao`

### POST `/sessao/login`
OIDC callback completion → issues platform JWT.
- Request: `{ "code": "<oidc-code>", "redirectUri": "...", "empresaId": "emp_x?" }`
- Response 200: `{ "accessToken": "...", "empresaSelecionada": "emp_x" }` + `Set-Cookie: refresh-token` (httpOnly, secure, sameSite=strict). When the user has N>1 empresas and none chosen: 200 `{ "empresasDisponiveis": [...], "selecaoNecessaria": true }`.

- `WHEN a valid OIDC code is presented AND the user has exactly one active usuario_empresa, THE SYSTEM SHALL issue a JWT with that empresa_id and set a rotating refresh-token cookie.`
- `WHEN the authenticated user has more than one active empresa AND no empresaId is supplied, THE SYSTEM SHALL return the list of available empresas and SHALL NOT issue a tenant-scoped JWT.`
- `IF the user has no active usuario_empresa, THEN THE SYSTEM SHALL reject login with 422 error.code 'wrks.usuario.sem-empresa-ativa'.`
- `IF the OIDC code is invalid or expired, THEN THE SYSTEM SHALL reject with 401 error.code 'iam.credenciais-invalidas'.`

### POST `/sessao/trocar-empresa`
- Request: `{ "empresaId": "emp_y" }` (Bearer required)
- Response 200: `{ "accessToken": "..." }` (new JWT, new empresa_id).
- `WHEN the caller has an active usuario_empresa for the target empresa, THE SYSTEM SHALL issue a new JWT scoped to it without re-authentication.`
- `IF the caller has no active association with the target empresa, THEN THE SYSTEM SHALL reject with 403 error.code 'wrks.empresa.acesso-negado'.`

### POST `/sessao/refresh`
- Uses httpOnly refresh-token cookie. Response 200: `{ "accessToken": "..." }` + rotated cookie.
- `WHEN a valid, non-blacklisted refresh token is presented, THE SYSTEM SHALL issue a new access token, rotate the refresh token, and invalidate the previous one.`
- `IF the refresh token is missing, expired, reused or blacklisted, THEN THE SYSTEM SHALL reject with 401 error.code 'iam.refresh-invalido'.`

### POST `/sessao/logout`
- Response 204. Clears cookie + blacklists `sub`+`jti`.
- `WHEN logout is requested, THE SYSTEM SHALL clear the refresh-token cookie AND add the access token jti to the Redis blacklist with TTL equal to the access token's remaining lifetime.`

### GET `/sessao/restore`
- Restores session from refresh-token cookie. Response 200: `{ "accessToken": "...", "empresaSelecionada": "..." }` or 401.

---

## 2. Access — `/access`

### POST `/access/evaluate`
- Request: `{ "usuarioId": "uuid", "empresaId": "emp_x" }` (machine-to-machine; service token).
- Response 200: `AccessDecisionResponse` `{ usuarioId, empresaId, papel, permissoes[], dataScope?, modeloAcessoVersao, sessionPolicy{ accessTokenTtl, refreshTtl, idleTimeout } }`.
- `THE SYSTEM SHALL return the AccessDecision for the (usuarioId, empresaId) pair including role, explicit permission list, data scope, and current modelo_acesso_versao.`
- `WHILE a cached AccessDecision is present and the modelo_acesso_versao matches, THE SYSTEM SHALL serve it from Redis without hitting PostgreSQL.`
- `IF the (usuarioId, empresaId) association is inactive or absent, THEN THE SYSTEM SHALL respond 404 error.code 'wrks.usuario.associacao-nao-encontrada'.`

### GET `/.well-known/jwks.json`
- Public. Returns the RS256 public JWK set used by GWY and services to validate JWTs.
- `THE SYSTEM SHALL expose the current signing public key(s) as a JWK set without authentication.`

---

## 3. Workspace (empresa) — `/empresas`  · perm `wrks.empresa.*`

| Verb | Path | Permission | Notes |
|---|---|---|---|
| GET | `/empresas` | `wrks.empresa.read` | list (group-admin scope) |
| POST | `/empresas` | `wrks.empresa.criar` | creates row, returns `PROVISIONANDO` |
| GET | `/empresas/{id}` | `wrks.empresa.read` | |
| PUT | `/empresas/{id}` | `wrks.empresa.editar` | parameters/soft-delete |
| POST | `/empresas/{id}/provisionar` | `wrks.empresa.provisionar` | (re)trigger MIG |

- `WHEN an empresa is created, THE SYSTEM SHALL persist it as PROVISIONANDO, trigger MIG to create schema emp_<slug>, and publish journey-os.empresa.provisionada only after MIG confirms.`
- `IF the slug already exists, THEN THE SYSTEM SHALL reject with 409 error.code 'wrks.empresa.slug-duplicado'.`
- `IF MIG provisioning fails, THEN THE SYSTEM SHALL keep the empresa in PROVISIONANDO and respond 502 error.code 'wrks.empresa.provisionamento-falhou'.`

## 4. Users — `/usuarios`  · perm `wrks.usuario.*`

| Verb | Path | Permission |
|---|---|---|
| GET | `/usuarios` | `wrks.usuario.read` |
| POST | `/usuarios` | `wrks.usuario.criar` |
| GET/PUT/DELETE | `/usuarios/{id}` | `read`/`editar`/`excluir` (soft) |
| POST | `/usuarios/{id}/empresas` | `wrks.usuario.associar` (assign role+data_scope) |

- `IF the email already belongs to an active usuario, THEN THE SYSTEM SHALL reject with 409 error.code 'wrks.usuario.duplicado'.`
- `IF the caller assigns a role hierarchically above their own, THEN THE SYSTEM SHALL reject with 403 error.code 'wrks.papel.escalonamento'.`

## 5. Roles & permissions — `/papeis`  · perm `wrks.papel.*`

| Verb | Path | Permission |
|---|---|---|
| GET | `/papeis` | `wrks.papel.read` |
| GET | `/papeis/{codigo}/permissoes` | `wrks.papel.read` |
| PUT | `/papeis/{codigo}/permissoes` | `wrks.papel.editar` |

- `WHEN a role's permission bundle changes, THE SYSTEM SHALL increment modelo_acesso_versao in the same transaction and publish journey-os.modelo.acesso.alterado.`
- `IF a referenced permission code is not in the canonical catalogue, THEN THE SYSTEM SHALL reject with 422 error.code 'wrks.papel.permissao-desconhecida'.`

## 6. Org structure — `/business-units`, `/teams`  · perm `wrks.business_unit.*`, `wrks.team.*`

CRUD scoped to the caller's empresa (JWT claim). Standard read/criar/editar.

## 7. Audit — `/auditoria`  · perm `wrks.auditoria.read`

- GET `/auditoria?empresaId&from&to&evento` → paged `evento_auditoria` (also indexed in Elastic `audit-events`).

---

## Error catalogue (WRKS)

| error.code | HTTP | category |
|---|---|---|
| `iam.credenciais-invalidas` | 401 | auth |
| `iam.token-expirado` | 401 | auth |
| `iam.refresh-invalido` | 401 | auth |
| `iam.sessao.versao-desatualizada` | 401 | session_stale |
| `iam.ip-fora-de-escopo` | 403 | forbidden |
| `wrks.empresa.acesso-negado` | 403 | forbidden |
| `wrks.papel.escalonamento` | 403 | forbidden |
| `wrks.usuario.nao-encontrado` | 404 | not_found |
| `wrks.usuario.associacao-nao-encontrada` | 404 | not_found |
| `wrks.usuario.duplicado` | 409 | conflict |
| `wrks.empresa.slug-duplicado` | 409 | conflict |
| `wrks.usuario.sem-empresa-ativa` | 422 | business_rule |
| `wrks.papel.permissao-desconhecida` | 422 | validation |
| `wrks.empresa.provisionamento-falhou` | 502 | upstream_error |

> Cross-cutting `iam.*` codes are emitted by WRKS and re-emitted by GWY/all services on JWT
> validation (see `shared/rbac/session-policy.md`).
