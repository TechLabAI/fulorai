## [FE-ASST-004] AssetApiService + AssetCatalogFacade (catálogo)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`AssetApiService` (list/get/create/update/archive) + `AssetCatalogFacade` (signals `catalogo`,
`paginacao`, `filtro`, `loading`, `error`) em `libs/asst/data-access`, consumindo `/api/v1/assets`
via `@journeyos/shared/access-http-base`.

**Context / Problem statement:**
- Catálogo + busca + criação dependem deste resource. Fonte: SPEC-04 (Asset). Depende de INT-FE-ASST-001.
- Bloqueia: FE-ASST-009, FE-ASST-010.

**Approach (execution path):**
1) `AssetApiService` com `list(filtro)` → `GET /?tipo=&estado=&tag=&q=&page=&size=`, `get`, `create`, `update(PATCH)`, `archive`.
2) `AssetCatalogFacade`: `signal<T>` privado + `.asReadonly()`; converte Observable→signal; `computed` de paginação.
3) Escopo por empresa + invalidação na troca (gancho para INT-FE-ASST-003).

**Non-goals:** UI (P3); error mapping detalhado (FE-ASST-008).

**Layer(s):** frontend / `libs/asst/data-access`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Asset)

**Architecture alignment:** ADR-002 signals; sem BehaviorSubject; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/data-access/src/lib/asset-api.service.ts` (apenas o stub default `asst-data-access.component.*` existe; service nao criado)
- 🔲 [MISSING] `libs/asst/data-access/src/lib/asset-catalog.facade.ts` (inexistente)
- 🔲 [MISSING] `libs/asst/data-access/src/lib/dto/asset.dto.ts` (inexistente)

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS (mock HttpClient) · 🔲 [MISSING] `nx lint asst-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:asst · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build asst-data-access` PASS
- Facade expõe apenas signals read-only; nenhum componente chama HttpClient direto

**Dependencies:** INT-FE-ASST-001
**API / Contract impact:** `GET/POST /api/v1/assets`, `GET/PATCH /{id}`, `POST /{id}/arquivar`.
**Risks / Notes:** `q` resolvido no BE (Elastic+fallback); o FE só passa a query (R-1: contrato a estabilizar).
