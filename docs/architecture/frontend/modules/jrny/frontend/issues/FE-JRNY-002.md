## [FE-JRNY-002] Routes + lazy entry + redirect raiz

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 1/4 itens

**Outcome:**
`jrny.routes.ts` (`MODULE_ROUTES[]`) em `libs/jrny/shell-entry` com `loadComponent` por feature e
redirect `/jrny → /jrny/journeys`. Entry exportada como library `@journeyos/jrny` (ADR-003); todas as
rotas lazy, com `data` (title/breadcrumbs/permissionRequired) e guards por rota (SPEC-01).

**Context / Problem statement:**
- O Shell carrega `@journeyos/jrny` via `loadChildren`; rotas precisam refletir a tabela mestre do SPEC-01.
- Fonte: SPEC-01. Cobre gap EARS: redirect raiz. Bloqueia: FE-JRNY-009..014.

**Approach (execution path):**
1) Declarar `MODULE_ROUTES` com 7 rotas (journeys, builder, stage, rules, decisions, analytics) + redirect.
2) Anexar `canActivate: [authGuard, empresaGuard, accessGuard(<perm>)]` por rota.
3) `loadComponent` por `*PageComponent`; `data` com title/breadcrumbs/permissionRequired.

**Non-goals:** implementação dos guards (FE-JRNY-017); páginas (P3).

**Layer(s):** frontend / `libs/jrny/shell-entry`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md`

**Architecture alignment:** module-pattern; lazy entry library (ADR-003); tag `scope:jrny` `type:domain`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/shell-entry/src/lib/jrny.routes.ts` (MISSING — `JRNY_ROUTES = []` vazio: sem as 7 rotas, sem redirect `/jrny → /jrny/journeys`, sem loadComponent, sem guards/data)
- ✅ `libs/jrny/shell-entry/src/index.ts` (export `JRNY_ROUTES`) <!-- index.ts re-exporta ./lib/jrny.routes -->

**Tests**
- 🔲 `nx test jrny-shell-entry` PASS (MISSING — sem .spec.ts) · 🔲 `nx lint jrny-shell-entry` PASS (MISSING)

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build jrny-shell-entry` PASS
- `/jrny` redireciona para `/jrny/journeys` (pathMatch full)
- Cada rota lazy via `loadComponent`

**Dependencies:** FE-JRNY-001
**API / Contract impact:** nenhum direto.
**Risks / Notes:** flag `jrny.journey-analytics` condiciona a rota `/jrny/analytics` (FE-JRNY-020).
