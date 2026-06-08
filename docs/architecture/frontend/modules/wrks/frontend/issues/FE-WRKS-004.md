## [FE-WRKS-004] EmpresaApiService + WorkspaceFacade

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`EmpresaApiService` (HTTP via `access-http-base`) + `WorkspaceFacade` (signals) cobrindo list/get/update de `/api/v1/iam/empresas`, expondo `workspace()`, `loading()`, `error()`.

**Context / Problem statement:**
- Dashboard e settings precisam dos dados da empresa ativa. Fonte: SPEC-04 (Empresa). Bloqueia FE-WRKS-011/012.

**Approach (execution path):**
1) `EmpresaApiService` com `list`, `get`, `update` (sem enviar `empresa_id` em body/path — claim JWT).
2) `WorkspaceFacade` com `signal` privado + `.asReadonly()`; `load()` / `save()`.
3) `reset()` para invalidar no `switchTo` (ADR-005).

**Non-goals:** criar/provisionar empresa (fora do MVP); org structure (FE-WRKS-007).

**Layer(s):** frontend / libs/wrks/data-access
**Bounded context:** wrks

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Empresa)

**Architecture alignment:** ADR-002 (signals); tag `type:data-access` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/data-access/src/lib/empresa-api.service.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/workspace.facade.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/dtos/empresa.dto.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-data-access` PASS (facade signals) (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:wrks · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build wrks-data-access` PASS
- Zero `HttpClient` fora do service; zero `empresaId` lido do JWT

**Dependencies:** FE-WRKS-002 · INT-FE-WRKS-004 (interceptors)
**API / Contract impact:** `GET/PUT /empresas/{id}` (perm `wrks.empresa.read/editar`).
**Risks / Notes:** OpenAPI ainda não materializado (R-1) — DTO segue `api-contract.md`.
