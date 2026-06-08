## [FE-LEAD-004] Lead data-access: LeadApiService + LeadList/LeadDetail facades

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/6 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`LeadApiService` (list/get/update/qualify/anonimizar/expurgar) + `LeadListFacade` e `LeadDetailFacade`
com signals (`fila`, `filtros`, `paginacao`, `leadSelecionado`, `score`, `acoes`, `loading`, `error`).
Refetch do score após update/qualify; invalidação da fila na troca de empresa.

**Context / Problem statement:**
- Núcleo de dados do módulo: fila priorizada (Elastic) + detalhe com breakdown 6D + `assistIa`.
- Fonte: SPEC-04, SPEC-03. Cobre **G5** (profile-update→refetch). Bloqueia: FE-LEAD-009, 011, 012, 013.

**Approach (execution path):**
1) `LeadApiService` via `@journeyos/shared/access-http-base` (`/api/v1/leads`).
2) `LeadListFacade`: `list(filtro,page,size)` → signals; effect de troca de empresa invalida a fila.
3) `LeadDetailFacade`: `get(id)`, `update`, `qualify`, `anonimizar`, `expurgar`; `computed` de `acoes` por estado+permissão; refetch do score após mutação.

**Non-goals:** componentes de UI (P3); mapeamento de erro detalhado (FE-LEAD-008).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` · `SPEC-03-view-models.md`

**Architecture alignment:** Signals-first (ADR-002); `signal` privado + `.asReadonly()`; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/data-access/src/lib/lead-api.service.ts` — _MISSING_
- 🔲 `libs/lead/data-access/src/lib/lead-list.facade.ts` — _MISSING_
- 🔲 `libs/lead/data-access/src/lib/lead-detail.facade.ts` — _MISSING_
- 🔲 `libs/lead/data-access/src/lib/models/*` (DTOs FE provisórios) — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:lead · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build lead-data-access` PASS
- `WHEN` perfil é atualizado, o score é refetchado (SPEC-04 EARS); troca de empresa invalida a fila

**Dependencies:** FE-LEAD-002, INT-FE-LEAD-001
**API / Contract impact:** `GET/PUT /leads`, `POST /leads/{id}/qualify|anonimizar`, `DELETE /leads/{id}`.
**Risks / Notes:** `@journeyos/shared/contracts` ausente → DTOs provisórios; substituir quando BE expor OpenAPI.
