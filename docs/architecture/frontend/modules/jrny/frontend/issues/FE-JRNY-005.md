## [FE-JRNY-005] Stage data-access: StageApiService + ops no builder

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`StageApiService` (`/api/v1/journeys/{id}/estagios`) integrado ao `JourneyBuilderFacade`. Operações:
`list`, `create`, `update`, `reorder`. `StageItemVm` com `assetRefLabel` e `temRegrasSaindo`
(client-side, cruzando regras × estágios — gap G3).

**Context / Problem statement:**
- O builder precisa montar/editar/reordenar estágios ordenados e tipados.
- Fonte: SPEC-04 (Stage), SPEC-03 (StageItemVm). Bloqueia: FE-JRNY-010, FE-JRNY-011, FE-JRNY-016.

**Approach (execution path):**
1) `StageApiService` com list/create/update + helper de `reorder` (sequência de PATCH de `ordem`).
2) Derivar `StageItemVm` (label do asset; `temRegrasSaindo` via regras da jornada).
3) Validação client-side: `ordem` única, `tipoEstagio` no enum.

**Non-goals:** UI do editor (FE-JRNY-011); sortable a11y + rollback (FE-JRNY-016).

**Layer(s):** frontend / `libs/jrny/data-access`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Stage) · `SPEC-03`

**Architecture alignment:** Signals-first; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/data-access/src/lib/stage-api.service.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/stage.models.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/journey-builder.facade.ts` (estágios + reorder) (MISSING)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:jrny · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- `reorder` emite PATCHs de `ordem` em sequência; estado refletido em signal

**Dependencies:** FE-JRNY-004, INT-FE-JRNY-001
**API / Contract impact:** `/api/v1/journeys/{id}/estagios` (list/create/update).
**Risks / Notes:** sem endpoint batch de reorder (gap G4) — otimista+rollback fica em FE-JRNY-016.
