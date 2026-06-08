## [FE-LEAD-010] feature-lead-list: filtros + query-params + fila por segmento

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`LeadFilterBarComponent` (segmento/dimensão/estado/busca) sincronizado com query-params
(`?segmento=&dimensao=&estado=&q=&page=&size=`); navegação a partir de um segmento abre a fila filtrada.

**Context / Problem statement:**
- Permite priorização por segmento/dimensão e deep-link de filtro. Fonte: SPEC-01, SPEC-03.
- Depende da página base (FE-LEAD-009) e do `SegmentFacade` (lista de segmentos).

**Approach (execution path):**
1) `LeadFilterBarComponent` emite `filtroChange`; a page reflete em query-params e refetch.
2) Ler query-params na entrada da rota (deep-link de filtro).
3) Integração com `/lead/segments` → `?segmento=:id`.

**Non-goals:** CRUD de segmentos (FE-LEAD-014).

**Layer(s):** frontend / `libs/lead/feature-lead-list`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md` · `SPEC-03-view-models.md`

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:lead` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-lead-list/src/lib/lead-filter-bar.component.ts` — _MISSING_
- 🔲 `libs/lead/feature-lead-list/src/lib/lead-list.page.ts` (wiring query-params) — _MISSING_

**Tests**
- 🔲 `nx test lead-feature-lead-list` PASS — _MISSING_ · 🔲 `nx lint lead-feature-lead-list` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-feature-lead-list` PASS
- Filtrar por segmento lista apenas leads do segmento; filtros refletidos na URL

**Dependencies:** FE-LEAD-009, FE-LEAD-007
**API / Contract impact:** `GET /leads?segmento=...`.
**Risks / Notes:** manter os query-params como fonte para reload/deep-link.
