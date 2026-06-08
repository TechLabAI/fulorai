## [FE-ASST-002] ASST routes + module entry + nav.config

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 30 -- Inicial
**Done/Total:** 3/6 itens
**GitHub:** [#TBD]

**Outcome:**
`ASST_ROUTES` populado com as 4 rotas (library, detail, studio, approvals) + redirect `/asst →
/asst/library`, `AsstModule` (entry lazy) e `asst.nav.config.ts` consistentes com SPEC-01. Host
`apps/asst` carrega `@journeyos/asst`.

**Context / Problem statement:**
- O Shell carrega o módulo via `loadChildren` → `@journeyos/asst` (ADR-003/ADR-006). As sub-rotas usam `loadComponent`.
- Fonte: SPEC-01. Depende de FE-ASST-001. Bloqueia: FE-ASST-009..015, FE-ASST-016.

**Approach (execution path):**
1) Definir `ASST_ROUTES` com guards por rota (`authGuard, empresaGuard, accessGuard('<perm>')`) e `data` (title/breadcrumbs/permissionRequired).
2) Cada rota usa `loadComponent` para a page da feature correspondente (stub até P3).
3) `asst.nav.config.ts` com `breadcrumbRoot: 'Assets'`.

**Non-goals:** implementação das pages (P3); guards customizados (FE-ASST-016).

**Layer(s):** frontend / `libs/asst/shell-entry` + `apps/asst`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md`

**Architecture alignment:** lazy `loadComponent`; tags `scope:asst`.

**Implementation checklist (by file):**
- ◐ [PARTIAL] `libs/asst/shell-entry/src/lib/asst.routes.ts` (`ASST_ROUTES = []` vazio — faltam as 4 rotas + redirect + guards)
- ✅ [DONE] `libs/asst/shell-entry/src/lib/asst.module.ts` (`AsstModule` entry com `RouterModule.forChild(ASST_ROUTES)`)
- ✅ [DONE] `libs/asst/shell-entry/src/lib/asst.nav.config.ts` (`breadcrumbRoot: 'Assets'`)
- ✅ [DONE] `apps/asst/src/app/app.routes.ts` (carrega `@journeyos/asst` via loadChildren → AsstModule)

**Tests**
- 🔲 [MISSING] `nx test asst-shell-entry` PASS · 🔲 [MISSING] `nx lint asst` PASS

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:asst · priority:P1

**Acceptance criteria:**
- `npx nx build asst` PASS; rotas resolvem (loadComponent) sem erro de compilação
- Guards aplicados conforme SPEC-01 (todas pós-contexto)

**Dependencies:** FE-ASST-001
**API / Contract impact:** nenhum (routing).
**Risks / Notes:** redirect `/asst` deve usar `pathMatch: 'full'`.
