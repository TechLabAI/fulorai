## [FE-ASST-003] Module descriptor + registro no Shell

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 30 -- Inicial
**Done/Total:** 2/5 itens
**GitHub:** [#TBD]

**Outcome:**
`ASST_MODULE_DESCRIPTOR` exportado por `@journeyos/asst` e registrado em
`apps/journey-os-web/src/app/config/module-descriptors.ts` (ao lado do WRKS), com `build`+`lint
journey-os-web` verdes.

**Context / Problem statement:**
- O Shell precisa do descriptor (key, basePath, loadChildren, metadata, flags, permissionMap) para montar nav + lazy load.
- Fonte: SPEC-06. Depende de FE-ASST-001/002. Bloqueia: INT-FE-ASST-005.

**Approach (execution path):**
1) Garantir `asst.descriptor.ts` gerado e exportado pelo barrel `@journeyos/asst`.
2) Importar `ASST_MODULE_DESCRIPTOR` no Shell e adicioná-lo ao array `MODULE_DESCRIPTORS`.
3) Validar `nx build journey-os-web` + `nx lint journey-os-web`.

**Non-goals:** lifecycle runtime (INT-FE-ASST-005); navegação derivada (FE-ASST-017).

**Layer(s):** frontend / `libs/asst/shell-entry` + `apps/journey-os-web`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md` §1, §2

**Architecture alignment:** ADR-004 (registry) / ADR-006 (entry como lib).

**Implementation checklist (by file):**
- ✅ [DONE] `libs/asst/shell-entry/src/lib/asst.descriptor.ts` (`ASST_MODULE_DESCRIPTOR` com key/basePath/loadChildren/metadata/flags/permissionMap)
- ✅ [DONE] `libs/asst/shell-entry/src/index.ts` (barrel exporta `asst.descriptor`)
- 🔲 [MISSING] `apps/journey-os-web/src/app/config/module-descriptors.ts` (+ ASST) (Shell registra apenas `WRKS_MODULE_DESCRIPTOR`; ASST ainda nao importado/adicionado ao array)

**Tests**
- 🔲 [MISSING] `nx build journey-os-web` PASS · 🔲 [MISSING] `nx lint journey-os-web` PASS

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:asst · priority:P1

**Acceptance criteria:**
- Shell registra `ASST_MODULE_DESCRIPTOR`; build+lint do Shell verdes (paridade com WRKS)

**Dependencies:** FE-ASST-001, FE-ASST-002
**API / Contract impact:** nenhum.
**Risks / Notes:** mutação mínima do Shell (1 import + 1 entrada no array).
