## [FE-ASST-012] feature-asset-detail: timeline de versões + conteúdo + nova versão

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 16 -- Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`VersionTimelineComponent` + `VersionContentViewComponent` + `NewVersionDialogComponent`
(`VersionContentFormComponent`), mostrando o histórico imutável, badge de origem e a versão vigente;
criação de versão manual (conteúdo + binários por URL).

**Context / Problem statement:**
- Versionamento (UINV-4) + proveniência (origem). Fonte: SPEC-02, SPEC-03 (Versao*VM, NovaVersaoForm). Depende de FE-ASST-005, FE-ASST-011.
- Bloqueia: FE-ASST-020.

**Approach (execution path):**
1) `VersionTimelineComponent` lista `VersaoResumoVM[]`, destaca a vigente, badge `MANUAL|ASSET_STUDIO`.
2) `VersionContentViewComponent` exibe `conteudo` + `binarios` (URL); somente leitura para versão publicada (UINV-4).
3) `NewVersionDialogComponent` cria versão (`POST /{id}/versoes`); binário = referência por URL (sem upload — R-6).

**Non-goals:** edição in-place de versão (proibida); studio (FE-ASST-013).

**Layer(s):** frontend / `libs/asst/feature-asset-detail` (+ `libs/asst/ui`)
**Bounded context:** asst

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `SPEC-04` (Versão)

**Architecture alignment:** Standalone/OnPush; componentes presentational reusáveis.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/ui/src/lib/version-timeline.component.ts`
- 🔲 [MISSING] `libs/asst/ui/src/lib/version-content-view.component.ts`
- 🔲 [MISSING] `libs/asst/ui/src/lib/version-origem-badge.component.ts`
- 🔲 [MISSING] `libs/asst/feature-asset-detail/src/lib/new-version.dialog.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-feature-asset-detail` PASS · 🔲 [MISSING] `nx lint asst-ui` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:asst · priority:P3

**Acceptance criteria:**
- Versão publicada não oferece edição de conteúdo; só "criar nova versão" (UINV-4)
- UI deixa explícito que binário é referência por URL (R-6)

**Dependencies:** FE-ASST-005, FE-ASST-011
**API / Contract impact:** `POST /{id}/versoes`, `GET /{id}/versoes/{numero}`, `GET /{id}/published`.
**Risks / Notes:** render por `tipoAsset` é pós-MVP (R-5); conteúdo texto/estruturado simples.
