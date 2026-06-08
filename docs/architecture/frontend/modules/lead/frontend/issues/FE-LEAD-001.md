## [FE-LEAD-001] Module contract + permission-map + feature-flags

**Status (validação):** REDUCED — pós-validação 2026-06-05
**Maturidade:** 35 — Parcial
**Done/Total:** 1/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`lead.contract.ts`, `lead.permission-map.ts` e `lead.feature-flags.ts` materializados em
`libs/lead/shell-entry`, consistentes com SPEC-05: `MODULE_KEY`, `MODULE_MENU_METADATA` (label "Leads",
route `/lead/leads`, deep links Maturity Score/Segmentos/Surveys/Regras), `LEAD_PERMISSION_MAP`
(17 perms `lead.*`), `LEAD_FEATURE_FLAGS` (`lead.maturity-score`, `lead.qualification-rules`).

**Context / Problem statement:**
- O Shell descobre o módulo via o contrato; permissões devem casar com o catálogo BE (`lead.<recurso>.<acao>`).
- Fonte: SPEC-05. Bloqueia: FE-LEAD-002, FE-LEAD-003, INT-FE-LEAD-005.

**Approach (execution path):**
1) Preencher `lead.contract.ts` com menu metadata + 4 deep links (cada um com `perm`).
2) Mapear `LEAD_PERMISSION_MAP` (17 perms `lead.*`) conforme SPEC-05 (arrays preenchidos no implement via AccessDecision).
3) Declarar flags `lead.maturity-score`, `lead.qualification-rules` (defaultState: enabled).

**Non-goals:** lógica de guard (FE-LEAD-017); registro no Shell em runtime (INT-FE-LEAD-005).

**Layer(s):** frontend / `libs/lead/shell-entry`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-05-module-contract.md`

**Architecture alignment:** module-pattern; Standalone/OnPush/Signals; tag `scope:lead` `type:domain`.

**Implementation checklist (by file):**
- 🟡 `libs/lead/shell-entry/src/lib/lead.contract.ts` — _PARTIAL_
- 🟡 `libs/lead/shell-entry/src/lib/lead.permission-map.ts` — _PARTIAL_
- ✅ `libs/lead/shell-entry/src/lib/lead.feature-flags.ts` — _DONE_

**Tests**
- 🔲 `nx test lead-shell-entry` PASS — _MISSING_ · 🔲 `nx lint lead-shell-entry` PASS — _MISSING_

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:lead · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build lead-shell-entry` PASS
- Permissões idênticas às do `lead-service/contracts/api-contract.md` (sem inventar códigos)

**Dependencies:** — (fecha junto com scaffold)
**API / Contract impact:** consome `lead.*` permissions; nenhum endpoint direto.
**Risks / Notes:** manter sincronia papel→permissão com o bundle do BE (single source of truth).
