## [FE-WRKS-011] feature-workspace — dashboard

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`WorkspaceDashboardPageComponent` exibindo resumo da empresa ativa (nome, slug, contagens) e atalhos visíveis conforme `can(<perm>)`.

**Context / Problem statement:**
- Tela inicial pós-contexto. Fonte: SPEC-01/02/03. Depende de FE-WRKS-004.

**Approach (execution path):**
1) Page (smart) lê `WorkspaceFacade.workspace()/loading()/error()`.
2) `WorkspaceSummaryComponent` (presentational) + `QuickActionsComponent` (filtrado por `can()`).
3) Estados loading/empty/error via `ui-feedback`.

**Non-goals:** settings (FE-WRKS-012).

**Layer(s):** frontend / libs/wrks/feature-workspace
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01/02/03

**Architecture alignment:** standalone + OnPush; `type:feature` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/feature-workspace/src/lib/workspace-dashboard.page.ts` (MISSING)
- 🔲 `libs/wrks/feature-workspace/src/lib/workspace-summary.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-workspace/src/lib/quick-actions.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-workspace/src/lib/feature-workspace.routes.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-workspace` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build` PASS
- Atalhos respeitam `AccessDecisionService.can()`

**Dependencies:** FE-WRKS-004 · FE-WRKS-016 (guard)
**API / Contract impact:** `GET /empresas/{id}`.
**Risks / Notes:** dashboard é a 1ª impressão — cuidar de CLS (skeleton).
