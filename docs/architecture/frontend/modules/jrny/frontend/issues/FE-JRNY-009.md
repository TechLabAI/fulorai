## [FE-JRNY-009] feature-journey-list (lista + filtro + criar rascunho)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/6 itens

**Outcome:**
`feature-journey-list` com `JourneyListPageComponent` (smart) + `JourneyFilterBarComponent`,
`JourneyRowComponent`, `CreateJourneyDialogComponent`. Lista jornadas por estado + busca; criar
rascunho (gated `jrny.jornada.criar`); abrir builder; nova versão de publicada.

**Context / Problem statement:**
- Porta de entrada do módulo (`/jrny/journeys`).
- Fonte: SPEC-02 (árvore), SPEC-03 (JourneyListVM). Consome `JourneyListFacade`.

**Approach (execution path):**
1) `JourneyListPageComponent` lê `journeys/loading/error/filtro/podeCriar`.
2) Filtro por estado/busca (query params); paginação.
3) Criar rascunho (dialog) e navegar ao builder; ação "nova versão" por linha.

**Non-goals:** builder (FE-JRNY-010); guards (FE-JRNY-017).

**Layer(s):** frontend / `libs/jrny/feature-journey-list`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `SPEC-01` (`/jrny/journeys`)

**Architecture alignment:** Standalone + OnPush + Signals; tag `type:feature` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/feature-journey-list/src/lib/journey-list.page.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-list/src/lib/journey-filter-bar.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-list/src/lib/journey-row.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-list/src/lib/create-journey-dialog.component.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-feature-journey-list` PASS (MISSING) · 🔲 `nx lint ...` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-feature-journey-list` PASS
- DOM reflete a árvore do SPEC-02; criar rascunho gated por permissão

**Dependencies:** FE-JRNY-002, FE-JRNY-004
**API / Contract impact:** `/api/v1/journeys` (list/create).
**Risks / Notes:** smart-table candidata a pattern shared.
