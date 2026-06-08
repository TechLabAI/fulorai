## [FE-ASST-013] feature-asset-studio: composição IA + degradação graciosa

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 16 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`AssetStudioPageComponent` (smart) + `StudioBriefFormComponent` + `StudioComposingIndicatorComponent`
+ `StudioDegradedBannerComponent` + `StudioResultPreviewComponent`, consumindo `AssetStudioFacade`
(`studioState`), com fallback "compor manualmente".

**Context / Problem statement:**
- Diferencial do ASST + ADR-005. Fonte: SPEC-02 (feature-asset-studio), SPEC-07 (503). Depende de FE-ASST-006, FE-ASST-012.
- Bloqueia: FE-ASST-020 (e2e degradation).

**Approach (execution path):**
1) `StudioBriefFormComponent`: `brief` (não vazio), `contexto`, `baseVersaoNumero?`; emite `compose`.
2) `studioState='composing'` → indicador; `draft-pronto` → preview + "abrir no detalhe".
3) `studioState='degradado'` (503) → banner + CTA "compor manualmente" (abre NewVersionDialog); nunca bloqueia o resto (UINV-7).

**Non-goals:** chamada de IA direta (proibida); criação manual em si (FE-ASST-012).

**Layer(s):** frontend / `libs/asst/feature-asset-studio`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-02` · `SPEC-07` · ADR-005

**Architecture alignment:** ADR-005 (degradação); flag `asst.asset-studio` desliga sem afetar o resto.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/feature-asset-studio/src/lib/asset-studio.page.ts`
- 🔲 [MISSING] `libs/asst/feature-asset-studio/src/lib/studio-brief-form.component.ts`
- 🔲 [MISSING] `libs/asst/feature-asset-studio/src/lib/studio-degraded-banner.component.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-feature-asset-studio` PASS (composing/draft/degradado) · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:asst · priority:P3

**Acceptance criteria:**
- `503` mostra banner + CTA manual; nenhuma versão criada; catálogo/aprovação intactos
- Flag `asst.asset-studio=disabled` esconde a entrada do Studio sem quebrar o detalhe

**Dependencies:** FE-ASST-006, FE-ASST-012
**API / Contract impact:** `POST /{id}/studio/compose`.
**Risks / Notes:** latência da IA (R-3); `Idempotency-Key` no retry.
