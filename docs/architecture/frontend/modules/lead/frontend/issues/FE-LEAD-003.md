## [FE-LEAD-003] Module descriptor + registro no Shell + bootstrap

**Status (validação):** REDUCED — pós-validação 2026-06-05
**Maturidade:** 35 — Parcial
**Done/Total:** 1/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`LEAD_MODULE_DESCRIPTOR` exportado de `@journeyos/lead` e **registrado** em
`apps/journey-os-web/src/app/config/module-descriptors.ts`; `lead.bootstrap.ts` (init/destroy)
chamando `LeadShellIntegrationService.onRegister/onActivate/onDeactivate`. `build`+`lint journey-os-web`
verdes com o LEAD registrado.

**Context / Problem statement:**
- Sem o registro, o módulo não aparece no Shell. Mesmo padrão de WRKS (§4.4 resolvido por ADR-006).
- Fonte: SPEC-06. Bloqueia: navegação real do módulo no Shell.

**Approach (execution path):**
1) `lead.descriptor.ts`: `LEAD_MODULE_DESCRIPTOR` (key, loadChildren `@journeyos/lead`, metadata, permissions, flags).
2) Importar e adicionar `LEAD_MODULE_DESCRIPTOR` ao array de `module-descriptors.ts` do Shell.
3) `lead.bootstrap.ts`: registra via integration service; subscreve troca de empresa (invalidar fila).

**Non-goals:** lógica do integration service em runtime detalhada (INT-FE-LEAD-005).

**Layer(s):** frontend / `libs/lead/shell-entry` + `apps/journey-os-web`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md`

**Architecture alignment:** ADR-004/006; descriptor único como fonte; tag `scope:lead`.

**Implementation checklist (by file):**
- ✅ `libs/lead/shell-entry/src/lib/lead.descriptor.ts` — _DONE_
- 🟡 `libs/lead/shell-entry/src/lib/lead.bootstrap.ts` — _PARTIAL_
- 🔲 `apps/journey-os-web/src/app/config/module-descriptors.ts` (adicionar LEAD) — _MISSING_

**Tests**
- 🔲 `nx build journey-os-web` PASS — _MISSING_ · 🔲 `nx lint journey-os-web` PASS — _MISSING_

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:lead · priority:P1

**Acceptance criteria:**
- `npx nx build/lint journey-os-web` PASS com `LEAD_MODULE_DESCRIPTOR` registrado
- Item de menu "Leads" aparece (gated por permissão via NavigationService)

**Dependencies:** FE-LEAD-001, FE-LEAD-002
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** evitar descriptor duplicado (replace por key `lead` — EARS SPEC-06).
