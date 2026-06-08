## [FE-INTL-012] feature-knowledge — KnowledgeListPageComponent (filtros + tabela + paginação)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 22 — Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`KnowledgeListPageComponent` (smart) com `KnowledgeFilterBarComponent`, `KnowledgeTableComponent` (+ `KnowledgeRowComponent`) e paginação; filtros `q/tag/status`; ações por linha (editar/indexar/arquivar) visíveis só com `canWrite`.

**Context / Problem statement:**
- Tela de curadoria. Fonte: SPEC-02 (feature-knowledge) + SPEC-03.
- Bloqueia: FE-INTL-013.

**Approach (execution path):**
1) Page consome `KnowledgeFacade.page()`/`filtros()`/`canWrite()`.
2) `FilterBar` emite `filterChange`; `Table` emite `editar/indexar/arquivar`.
3) Empty/loading via `ui-feedback`.

**Non-goals:** form de nó (FE-INTL-013).

**Layer(s):** frontend / libs/intl/feature-knowledge
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-02-component-hierarchy.md` (feature-knowledge)

**Architecture alignment:** Standalone + OnPush; `scope:intl`.

**Implementation checklist (by file):**
- 🟡 `libs/intl/feature-knowledge/src/lib/knowledge-list.page.ts` — PARTIAL: placeholder shell, sem facade/tabela
- 🔲 `libs/intl/feature-knowledge/src/lib/knowledge-filter-bar.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-knowledge/src/lib/knowledge-table.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-knowledge/src/lib/knowledge-row.component.ts` — MISSING: arquivo não existe

**Tests**
- 🔲 `nx test intl-feature-knowledge` PASS — MISSING: sem teste canWrite · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:intl · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build intl-feature-knowledge` PASS
- Teste: sem `canWrite`, ações de escrita ausentes (e2e knowledge-curation).

**Dependencies:** FE-INTL-006
**API / Contract impact:** consome `KnowledgeFacade`.
**Risks / Notes:** volume de nós (R5) — paginação obrigatória.
