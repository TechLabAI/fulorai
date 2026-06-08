## [FE-COMM-009] feature-template-catalog — catálogo + busca + filtros

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 15 -- Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`TemplateCatalogPageComponent` + `TemplateListComponent`/`TemplateCardComponent` + filtros (canal/tipo/estado/q)
+ `NewTemplateDialogComponent` (cria RASCUNHO). Consome `TemplateCatalogFacade`.

**Context / Problem statement:**
- Tela de entrada do módulo. Fonte: SPEC-02, SPEC-03. Depende: FE-COMM-004, FE-COMM-002. Bloqueia: FE-COMM-010.

**Approach:**
1) Page lê `catalogoTemplates/loading/error/filtro`; toolbar emite `filterChange`.
2) Lista + card com `StateChipComponent`/`CanalBadgeComponent`.
3) Dialog de criação (gated por `comm.template.criar`).

**Non-goals:** editor (FE-COMM-010); Studio (FE-COMM-012).

**Layer(s):** frontend / `libs/comm/feature-template-catalog` (+ `libs/comm/ui`)
**Bounded context:** comm
**Service execution spec(s):** `SPEC-02-component-hierarchy.md`, `SPEC-03-view-models.md`
**Architecture alignment:** standalone/OnPush; smart consome facade; tag `scope:comm` `type:feature`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/feature-template-catalog/src/lib/template-catalog.page.ts`
- 🔲 [MISSING] `libs/comm/feature-template-catalog/src/lib/template-list.component.ts`
- 🔲 [MISSING] `libs/comm/feature-template-catalog/src/lib/new-template.dialog.ts`
- 🔲 [MISSING] `libs/comm/ui/src/lib/{state-chip,canal-badge,template-card}.component.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-feature-template-catalog` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:comm · priority:P3

**Acceptance criteria:**
- Filtros aplicam server-side; estados loading/empty/error; `nx test/lint/build` PASS

**Dependencies:** FE-COMM-004, FE-COMM-002
**API / Contract impact:** `GET /templates`.
**Risks / Notes:** paginação server-side (volume A3 do `06`).
