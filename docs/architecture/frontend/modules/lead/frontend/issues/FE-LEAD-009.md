## [FE-LEAD-009] feature-lead-list: página da fila + tabela + paginação

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/6 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`LeadListPageComponent` (smart) renderizando a fila ordenada por Maturity Score desc, com
`LeadTableComponent`/`LeadRowComponent`, `ScoreBadgeComponent`, `LeadStateChipComponent` e
`LeadPaginatorComponent`. Consome `LeadListFacade`.

**Context / Problem statement:**
- Tela default do módulo (golden path do SDR). Fonte: SPEC-02, SPEC-03.
- Bloqueia: FE-LEAD-010 (filtros).

**Approach (execution path):**
1) `LeadListPageComponent` lê signals (`fila`, `loading`, `error`, `paginacao`).
2) `LeadRowComponent` (presentational) emite `select`; badges de score/estado.
3) Estados loading/empty/error via `@journeyos/shared/ui-feedback`.

**Non-goals:** filtros e query-params (FE-LEAD-010); detalhe (FE-LEAD-011).

**Layer(s):** frontend / `libs/lead/feature-lead-list` + `libs/lead/ui`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-02-component-hierarchy.md` · `SPEC-03-view-models.md`

**Architecture alignment:** Standalone + OnPush; smart/presentational; tag `scope:lead` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-lead-list/src/lib/lead-list.page.ts` — _MISSING_
- 🔲 `libs/lead/feature-lead-list/src/lib/lead-table.component.ts` — _MISSING_
- 🔲 `libs/lead/feature-lead-list/src/lib/lead-row.component.ts` — _MISSING_
- 🔲 `libs/lead/ui/src/lib/score-badge.component.ts` · `lead-state-chip.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-feature-lead-list` PASS — _MISSING_ · 🔲 `nx lint lead-feature-lead-list` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-feature-lead-list` PASS
- Fila exibida ordenada por score desc (SPEC-01 EARS); states loading/empty/error cobertos

**Dependencies:** FE-LEAD-004
**API / Contract impact:** `GET /leads`.
**Risks / Notes:** performance de listas grandes (virtual scroll — ver FE-LEAD-022/risco R2).
