## [FE-ASST-006] StudioApiService + AssetStudioFacade (composição IA)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 15 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`StudioApiService.compose(assetId, form, idempotencyKey?)` + `AssetStudioFacade` (signals
`studioState` `idle|composing|draft-pronto|degradado`, `draftProduzido`, `error`) em
`libs/asst/data-access`, chamando **somente** `POST /{id}/studio/compose` (nunca a TechLab AI).

**Context / Problem statement:**
- Núcleo do Asset Studio + degradação graciosa. Fonte: SPEC-04 (Studio), ADR-005. Depende de FE-ASST-005.
- Bloqueia: FE-ASST-013.

**Approach (execution path):**
1) `StudioApiService.compose` com `Idempotency-Key` opcional → `201` (origem ASSET_STUDIO).
2) Facade mapeia ciclo `composing → draft-pronto`; `503 asst.studio.ia-indisponivel` → `degradado` (não cria versão).
3) Falha da IA nunca propaga para bloquear catálogo/detalhe/aprovação (UINV-7).

**Non-goals:** UI/banner (FE-ASST-013); criação de versão manual (FE-ASST-005).

**Layer(s):** frontend / `libs/asst/data-access`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Studio) · ADR-005

**Architecture alignment:** ADR-005 (delegação + degradação); tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/data-access/src/lib/studio-api.service.ts`
- 🔲 [MISSING] `libs/asst/data-access/src/lib/asset-studio.facade.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS (caso 201 + caso 503) · 🔲 [MISSING] `nx lint asst-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:asst · priority:P2

**Acceptance criteria:**
- `503` seta `studioState='degradado'` sem criar versão e sem propagar erro global
- Service não importa nada de TechLab AI (boundary respeitado)

**Dependencies:** FE-ASST-005
**API / Contract impact:** `POST /api/v1/assets/{id}/studio/compose`.
**Risks / Notes:** latência da IA (R-3); se p95 alto, reavaliar async (novo ADR).
