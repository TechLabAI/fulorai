## [FE-ASST-010] feature-asset-library: criar asset (NewAssetDialog)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`NewAssetDialogComponent` (smart) + `AssetMetadataFormComponent` (presentational) que cria um asset
(`POST /`) em `RASCUNHO` via `AssetCatalogFacade`, com validação síncrona (título/tipo) e gate
`asst.asset.criar`.

**Context / Problem statement:**
- Entrada do golden path (criar asset). Fonte: SPEC-02, SPEC-03 (NovoAssetForm), SPEC-01 (ação). Depende de FE-ASST-009.
- Bloqueia: FE-ASST-020 (e2e lifecycle).

**Approach (execution path):**
1) `AssetMetadataFormComponent`: campos `tipoAsset` (enum), `titulo` (não vazio), `descricao`, `tags`; UINV-6.
2) `NewAssetDialogComponent` chama `facade.onCreate(form)`; trata `422` inline.
3) Botão "Novo asset" visível só com `asst.asset.criar` (AccessDecision).

**Non-goals:** edição de metadados (FE-ASST-011); versão (FE-ASST-012).

**Layer(s):** frontend / `libs/asst/feature-asset-library` (+ `libs/asst/ui`)
**Bounded context:** asst

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `SPEC-07` (422)

**Architecture alignment:** Standalone/OnPush; form reativo; gate por permissão.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/feature-asset-library/src/lib/new-asset.dialog.ts`
- 🔲 [MISSING] `libs/asst/ui/src/lib/asset-metadata-form.component.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-feature-asset-library` PASS · 🔲 [MISSING] `nx lint asst-feature-asset-library` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:asst · priority:P3

**Acceptance criteria:**
- Criação resulta em asset `RASCUNHO` e atualiza o catálogo; `422` mostrado inline no campo
- Ação escondida sem `asst.asset.criar`

**Dependencies:** FE-ASST-009
**API / Contract impact:** `POST /api/v1/assets`.
**Risks / Notes:** `AssetMetadataFormComponent` reusado na edição (FE-ASST-011).
