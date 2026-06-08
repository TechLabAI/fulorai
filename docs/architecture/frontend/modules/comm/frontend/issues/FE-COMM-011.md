## [FE-COMM-011] feature-template-studio — composição assistida + degradação

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`TemplateStudioPageComponent` com `StudioBriefFormComponent`, `StudioComposingComponent`,
`StudioDraftPreviewComponent` e `StudioDegradedBannerComponent`. Consome `TemplateStudioFacade`;
reflete `studioState` (idle/composing/draft-pronto/degradado); revisão humana antes de aceitar.

**Context / Problem statement:**
- Diferencial de produtividade; degradação graciosa. Fonte: SPEC-02, ADR-005-degradação. Depende: FE-COMM-005, FE-COMM-010.

**Approach:**
1) Form de brief/contexto → `onCompose`.
2) `composing` bloqueia o form; `draft-pronto` mostra preview para aceitar; `degradado` mostra banner + CTA manual.
3) Respeita flag `comm.template-studio` (off → Studio oculto).

**Non-goals:** chamar TechLab AI direto (proibido); ativar automaticamente.

**Layer(s):** frontend / `libs/comm/feature-template-studio`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-02`, `SPEC-07`, `ADR-005`
**Architecture alignment:** standalone/OnPush; FE→BE only; tag `scope:comm` `type:feature`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/feature-template-studio/src/lib/template-studio.page.ts`
- 🔲 [MISSING] `libs/comm/feature-template-studio/src/lib/studio-brief-form.component.ts`
- 🔲 [MISSING] `libs/comm/feature-template-studio/src/lib/studio-draft-preview.component.ts`
- 🔲 [MISSING] `libs/comm/feature-template-studio/src/lib/studio-degraded-banner.component.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-feature-template-studio` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:comm · priority:P3

**Acceptance criteria:**
- `503` → estado degradado (corpo inalterado, CTA manual); flag off oculta Studio; `nx test/lint/build` PASS

**Dependencies:** FE-COMM-005, FE-COMM-010
**API / Contract impact:** `POST /templates/{id}/studio/compose`.
**Risks / Notes:** cobre C-05.3 (flag off) e C-07.3 (degradação).
