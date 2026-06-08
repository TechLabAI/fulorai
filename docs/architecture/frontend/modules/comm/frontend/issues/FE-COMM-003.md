## [FE-COMM-003] Module descriptor + registro no Shell

**Status:** REDUCED -- pos-validacao 2026-06-05
**Maturidade:** 25 -- Inicial
**Done/Total:** 1/4 itens
**GitHub:** [#TBD]

**Outcome:**
`COMM_MODULE_DESCRIPTOR` (derivado de `comm.contract.ts`) exportado por `@journeyos/comm` e registrado
no Shell (`apps/journey-os-web/.../config/module-descriptors.ts`), com `build`+`lint` do Shell verdes
— mesmo padrão do WRKS.

**Context / Problem statement:**
- O Shell precisa montar navegação e carregar o COMM lazy sem importar código interno. Fonte: SPEC-06. Depende: FE-COMM-001, FE-COMM-002.

**Approach:**
1) Garantir `comm.descriptor.ts` (gerado) com `loadChildren`, metadata, flags, permissionMap.
2) Adicionar `COMM_MODULE_DESCRIPTOR` ao array em `module-descriptors.ts`.
3) Rodar `build`+`lint journey-os-web`.

**Non-goals:** integração runtime (INT-FE-COMM-005); guards (FE-COMM-016).

**Layer(s):** frontend / `libs/comm/shell-entry` + `apps/journey-os-web`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md`
**Architecture alignment:** ADR-004; tag `scope:comm`.

**Implementation checklist (by file):**
- ✅ [DONE] `libs/comm/shell-entry/src/lib/comm.descriptor.ts`
- 🔲 [MISSING] `apps/journey-os-web/src/app/config/module-descriptors.ts` (+ `COMM_MODULE_DESCRIPTOR`)

**Tests**
- 🔲 [MISSING] `nx build journey-os-web` PASS · 🔲 [MISSING] `nx lint journey-os-web` PASS

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:comm · priority:P1

**Acceptance criteria:**
- Shell lista "Comunicação" no menu; deep links derivados de permissão
- `build`+`lint journey-os-web` verdes

**Dependencies:** FE-COMM-001, FE-COMM-002
**API / Contract impact:** nenhum direto.
**Risks / Notes:** manter descriptor ↔ contract sincronizados (o generator cuida; revisar no implement).
