## [FE-WRKS-007] BusinessUnit/Team ApiService + OrgStructureFacade

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`BusinessUnitApiService` + `TeamApiService` + `OrgStructureFacade` (signals) para org structure (`/business-units`, `/teams`), alimentando o settings de workspace.

**Context / Problem statement:**
- Settings (FE-WRKS-012) edita org structure. Fonte: SPEC-04 (BusinessUnit, Team).

**Approach (execution path):**
1) Services com list/create/update escopados à empresa (claim JWT).
2) `OrgStructureFacade`: `businessUnits()` (árvore), `addBusinessUnit()`, `addTeam()`, `saving()`.

**Non-goals:** excluir BU/team (fora do MVP); UI (FE-WRKS-012).

**Layer(s):** frontend / libs/wrks/data-access
**Bounded context:** wrks

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (BusinessUnit/Team)

**Architecture alignment:** ADR-002; `type:data-access` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/data-access/src/lib/business-unit-api.service.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/team-api.service.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/org-structure.facade.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-data-access` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:wrks · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build wrks-data-access` PASS

**Dependencies:** FE-WRKS-002 · INT-FE-WRKS-004
**API / Contract impact:** `/business-units`, `/teams` (perm `wrks.business_unit.*`, `wrks.team.*`).
**Risks / Notes:** flag `wrks.org-structure` pode esconder esta área — facade tolera ausência.
