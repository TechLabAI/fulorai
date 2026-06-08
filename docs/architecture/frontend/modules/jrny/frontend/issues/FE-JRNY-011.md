## [FE-JRNY-011] feature-stage-editor (editor de estágio + asset picker)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`feature-stage-editor` com `StageEditorPageComponent` (smart) + `StageFormComponent`,
`AssetRefPickerComponent`. Edita um estágio (tipo/nome/asset/terminal/config) em RASCUNHO; validações
inline espelham o BE (`tipo-invalido`, `ordem-duplicada`).

**Context / Problem statement:**
- Detalhe de um estágio; referencia asset publicado de ASST (gap G2 — label).
- Fonte: SPEC-02, SPEC-03 (StageEditorVM). Consome `JourneyBuilderFacade`/`StageApiService`.

**Approach (execution path):**
1) `StageEditorPageComponent` lê `stage/editavel/saving/erros`.
2) `StageFormComponent` com seletor de `tipoEstagio` (enum), nome, terminal, config.
3) `AssetRefPickerComponent` resolve `assetRefId → label` (ASST quando disponível; senão id).

**Non-goals:** lista de estágios (FE-JRNY-010); reorder (FE-JRNY-016).

**Layer(s):** frontend / `libs/jrny/feature-stage-editor`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `contracts/backend-api-cross-link.md` (G2)

**Architecture alignment:** Standalone + OnPush + Signals; tag `type:feature` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/feature-stage-editor/src/lib/stage-editor.page.ts` (MISSING)
- 🔲 `libs/jrny/feature-stage-editor/src/lib/stage-form.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-stage-editor/src/lib/asset-ref-picker.component.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-feature-stage-editor` PASS (MISSING) · 🔲 `nx lint ...` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-feature-stage-editor` PASS
- Editar gated por `jrny.estagio.editar` + estado RASCUNHO; erros inline

**Dependencies:** FE-JRNY-005
**API / Contract impact:** `/api/v1/journeys/{id}/estagios` (create/update).
**Risks / Notes:** label de asset (gap G2) — degradar para id se ASST não resolver.
