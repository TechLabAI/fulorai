## [FE-ASST-009] feature-asset-library: catálogo (page + filtro + grid)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`AssetLibraryPageComponent` (smart) + `AssetFilterBarComponent`, `AssetGridComponent`,
`AssetCardComponent`, chips de tipo/estado, consumindo `AssetCatalogFacade` e refletindo
`AssetFiltroVM` nos query params.

**Context / Problem statement:**
- Tela principal do módulo (catálogo + busca). Fonte: SPEC-02 (feature-asset-library), SPEC-03. Depende de FE-ASST-004.
- Bloqueia: FE-ASST-010, FE-ASST-018.

**Approach (execution path):**
1) `AssetLibraryPageComponent` lê `catalogo()/loading()/error()/filtro()/paginacao()`; OnPush.
2) `AssetFilterBarComponent` emite `filterChange`; sincroniza `?tipo=&estado=&tag=&q=&page=&size=`.
3) `AssetGridComponent`/`AssetCardComponent` (presentational) com `AssetTypeChip`/`AssetStateChip`; `open(id)` navega para detalhe.

**Non-goals:** criação de asset (FE-ASST-010); empty/loading polish (FE-ASST-018).

**Layer(s):** frontend / `libs/asst/feature-asset-library` (+ `libs/asst/ui`)
**Bounded context:** asst

**Service execution spec(s):** `SPEC-02-component-hierarchy.md` · `SPEC-01` · `SPEC-03`

**Architecture alignment:** Standalone/OnPush/Signals; `feature → data-access|ui|shared/*`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/feature-asset-library/src/lib/asset-library.page.ts`
- 🔲 [MISSING] `libs/asst/ui/src/lib/asset-card.component.ts`
- 🔲 [MISSING] `libs/asst/ui/src/lib/asset-type-chip.component.ts`
- 🔲 [MISSING] `libs/asst/ui/src/lib/asset-state-chip.component.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-feature-asset-library` PASS · 🔲 [MISSING] `nx lint asst-feature-asset-library` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:asst · priority:P3

**Acceptance criteria:**
- Filtro/busca alteram a lista via facade; `build` da feature PASS
- Cobertura visual: DOM replica SPEC-02 (page → filter/grid/card)

**Dependencies:** FE-ASST-004
**API / Contract impact:** `GET /api/v1/assets` (via facade).
**Risks / Notes:** virtual scroll só se A-1 não se confirmar (volume médio).
