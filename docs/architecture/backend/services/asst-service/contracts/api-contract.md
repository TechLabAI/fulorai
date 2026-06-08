# API Contract — ASST (`/api/v1/assets/**`)

> REST surface of `asst-service`. All error responses use `application/problem+json` (RFC 7807,
> `shared/contratos/error-model.md`). EARS invariants per endpoint.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## Conventions

- Base path: `/api/v1/assets`.
- Auth: Bearer JWT (RS256) issued by WRKS; validated against WRKS JWKS. No anonymous endpoints.
- Mandatory headers: `Authorization`, `X-Correlation-Id` (propagated/generated).
- Tenant: `empresa_id` travels as a JWT claim; `EmpresaContextHolder.require()` fixes the schema.
  No `empresaId` in path/body. `X-Empresa-Id` is debug/log only and never overrides the claim.
- Authorization: `asst.<recurso>.<acao>` permissions resolved via WRKS `AccessDecision`
  (`asst.asset.criar|editar|ler|submeter|aprovar|publicar|arquivar`, `asst.studio.compor`).
- Idempotency: mutating composition/publish accept `Idempotency-Key` header (SPEC-05).

---

## 1. Asset CRUD — `/` · perm `asst.asset.*`

### POST `/`  · perm `asst.asset.criar`
Create an asset in `RASCUNHO` (no version yet).
- Request: `{ "tipoAsset": "EMAIL", "titulo": "Boas-vindas", "descricao": "...", "tags": ["onboarding"] }`
- Response 201: `AssetResponse { id, tipoAsset, titulo, estado: "RASCUNHO", versaoVigenteId: null, donoId, tags[], criadoEm }` + `Location: /api/v1/assets/{id}`.
- `WHEN a caller with permission asst.asset.criar posts a valid asset, THE SYSTEM SHALL create it in state RASCUNHO with no current version and return 201.`
- `IF tipoAsset is not one of LANDING_PAGE|EMAIL|CRIATIVO|ROTEIRO|DOCUMENTO|SCRIPT_SDR, THEN THE SYSTEM SHALL reject with 422 error.code 'asst.asset.tipo-invalido'.`
- `IF titulo is blank, THEN THE SYSTEM SHALL reject with 422 error.code 'asst.asset.titulo-obrigatorio'.`

### GET `/{id}`  · perm `asst.asset.ler`
- Response 200: `AssetResponse` (includes current state + `versaoVigenteId`).
- `IF the asset does not exist in the caller's tenant schema, THEN THE SYSTEM SHALL respond 404 error.code 'asst.asset.nao-encontrado'.`

### GET `/`  · perm `asst.asset.ler`
List/search assets. Query: `?tipo=&estado=&tag=&q=<full-text>&page=&size=`.
- Response 200: `Page<AssetResumo>`.
- `THE SYSTEM SHALL return only assets belonging to the caller's tenant schema.`
- `WHERE the q parameter is present, THE SYSTEM SHALL resolve results via the Elasticsearch assets index AND SHALL fall back to PostgreSQL filtering if the index is unavailable.`

### PATCH `/{id}`  · perm `asst.asset.editar`
Update asset metadata (titulo/descricao/tags) — **not** version content.
- `WHILE the asset is in state PUBLICADO, THE SYSTEM SHALL allow metadata edits but SHALL NOT mutate any existing versao_asset.`

### POST `/{id}/arquivar`  · perm `asst.asset.arquivar`
- Response 200. Soft-delete: `estado=ARQUIVADO`.
- `WHEN archival is requested, THE SYSTEM SHALL set estado=ARQUIVADO without physically deleting versions or approvals.`

---

## 2. Versions — `/{id}/versoes` · perm `asst.asset.editar`

### POST `/{id}/versoes`  · perm `asst.asset.editar`
Create a new immutable draft version (manual authoring).
- Request: `{ "conteudo": { ... }, "binarios": [ { "url": "...", "mime": "image/png" } ] }`
- Response 201: `VersaoAssetResponse { id, numero, estado: "RASCUNHO", origem: "MANUAL", criadoEm }`.
- `WHEN a new version is created, THE SYSTEM SHALL assign the next sequential numero for that asset and persist the version as immutable.`
- `IF a client attempts to modify an existing versao_asset, THEN THE SYSTEM SHALL reject with 409 error.code 'asst.versao.imutavel'.`

### GET `/{id}/versoes` / `GET /{id}/versoes/{numero}`  · perm `asst.asset.ler`
- Response 200: list / single `VersaoAssetResponse` (full content).

### GET `/{id}/published`  · perm `asst.asset.ler`
Returns the current published version (consumed by COMM/JRNY/SALE via `AssetQueryClient`).
- Response 200: `VersaoAssetResponse` (the vigente) — or 404 if never published.
- `WHILE an asset has a current published version, THE SYSTEM SHALL return that version deterministically.`
- `IF the asset has no published version, THEN THE SYSTEM SHALL respond 404 error.code 'asst.asset.sem-versao-publicada'.`

---

## 3. Asset Studio — `/{id}/studio/compose` · perm `asst.studio.compor`

### POST `/{id}/studio/compose`
AI-assisted composition via TechLab AI `document_composition`. Produces a new draft version.
- Request: `{ "brief": "...", "contexto": { ... }, "baseVersaoNumero": 2? }` + optional `Idempotency-Key`.
- Response 201: `VersaoAssetResponse { numero, origem: "ASSET_STUDIO", estado: "RASCUNHO" }`.
- `WHEN a composition request succeeds, THE SYSTEM SHALL store the result as a new versao_asset with origem=ASSET_STUDIO in state RASCUNHO and SHALL never publish it automatically.`
- `THE SYSTEM SHALL record the brief_composicao on the produced version for provenance.`
- `IF TechLab AI is unavailable or times out, THEN THE SYSTEM SHALL respond 503 error.code 'asst.studio.ia-indisponivel' AND SHALL NOT create a version.`
- `IF the same Idempotency-Key is replayed, THEN THE SYSTEM SHALL return the previously produced version without calling TechLab AI again.`

---

## 4. Approval workflow — `/{id}` actions · perms `asst.asset.submeter|aprovar|publicar`

### POST `/{id}/submit`  · perm `asst.asset.submeter`
- Request: `{ "versaoNumero": 3 }` → transitions `RASCUNHO → EM_REVISAO`.
- `WHEN submit is requested on a RASCUNHO asset with a draft version, THE SYSTEM SHALL move it to EM_REVISAO.`
- `IF the asset is not in RASCUNHO, THEN THE SYSTEM SHALL reject with 409 error.code 'asst.estado.transicao-invalida'.`

### POST `/{id}/approve`  · perm `asst.asset.aprovar`
- Request: `{ "decisao": "APROVADO" | "REJEITADO", "comentario": "..." }`.
- Response 200: `AssetResponse` (new state) + records `aprovacao`.
- `WHEN approve is requested with decisao=APROVADO on an EM_REVISAO asset, THE SYSTEM SHALL move it to APROVADO and persist an aprovacao record with the revisor identity.`
- `WHEN approve is requested with decisao=REJEITADO, THE SYSTEM SHALL move it to REJEITADO, persist the aprovacao with comentario, and emit journey-os.asset.rejeitado.`
- `IF the asset is not in EM_REVISAO, THEN THE SYSTEM SHALL reject with 409 error.code 'asst.estado.transicao-invalida'.`

### POST `/{id}/publish`  · perm `asst.asset.publicar`
- Response 200: `AssetResponse { estado: "PUBLICADO", versaoVigenteId }`.
- `WHEN publish is requested on an APROVADO asset, THE SYSTEM SHALL mark the approved version as the current published version, set estado=PUBLICADO, and emit journey-os.asset.versao.publicada.`
- `IF the asset is not in APROVADO, THEN THE SYSTEM SHALL reject with 409 error.code 'asst.estado.transicao-invalida'.`
- `WHEN a new version of an already-published asset is published, THE SYSTEM SHALL update versao_vigente_id without deleting the previous published version.`

---

## 5. Errors (RFC 7807 ProblemDetail)

| HTTP | error.code | Quando |
|---|---|---|
| 422 | `asst.asset.tipo-invalido` | tipoAsset fora do enum |
| 422 | `asst.asset.titulo-obrigatorio` | título vazio |
| 404 | `asst.asset.nao-encontrado` | asset inexistente no tenant |
| 404 | `asst.asset.sem-versao-publicada` | sem versão vigente |
| 409 | `asst.versao.imutavel` | tentativa de editar versão existente |
| 409 | `asst.estado.transicao-invalida` | transição não permitida pela state machine |
| 503 | `asst.studio.ia-indisponivel` | TechLab AI fora/timeout |
| 401 | `asst.auth.token-invalido` | JWT ausente/inválido |
| 403 | `asst.acesso.permissao-negada` | falta permissão `asst.*` |

Todos os corpos seguem `shared/contratos/error-model.md` (`type`, `title`, `status`, `detail`, `code`, `correlationId`).
