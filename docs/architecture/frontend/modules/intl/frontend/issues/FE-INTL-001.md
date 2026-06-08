## [FE-INTL-001] intl.contract.ts — menu metadata + deep-links reais

**Status:** REDUCED — pós-validação 2026-06-05
**Maturidade:** 50 — Parcial
**Done/Total:** 2/5 itens
**GitHub:** [#TBD]

**Outcome:**
`intl.contract.ts` com `MODULE_MENU_METADATA` real (label "Inteligência", icon `auto_awesome`, rota `/intl/copilot`) e os 3 deep-links (copilot/knowledge/analytics) com `permission`, mais `INTL_PERMISSION_MAP` (5 perms) e `INTL_FEATURE_FLAGS` (4 flags).

**Context / Problem statement:**
- O scaffold gera os stubs; esta issue preenche valores reais. Fonte: SPEC-05.
- Bloqueia: FE-INTL-002, FE-INTL-003.

**Approach (execution path):**
1) Preencher `deepLinks` com `{ label, route, permission }` dos 3 itens.
2) Preencher `INTL_PERMISSION_MAP` (chaves `intl.*`, valores `[]` derivados da Access Layer).
3) Preencher `INTL_FEATURE_FLAGS` (copilot/knowledge/analytics enabled; copilot-streaming disabled).

**Non-goals:** lógica de rota (FE-INTL-002); registro no Shell (FE-INTL-003).

**Layer(s):** frontend / libs/intl/shell-entry
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-05-module-contract.md`

**Architecture alignment:** ADR-001/003/006; `type:app` `scope:intl`.

**Implementation checklist (by file):**
- 🟡 `libs/intl/shell-entry/src/lib/intl.contract.ts` — PARTIAL: rota `/intl` (esperado `/intl/copilot`), deepLinks `[]`
- ✅ `libs/intl/shell-entry/src/lib/intl.permission-map.ts` — DONE: 5 perms com `[]` da Access Layer
- ✅ `libs/intl/shell-entry/src/lib/intl.feature-flags.ts` — DONE: 4 flags com defaultStates corretos

**Tests**
- 🔲 `nx test intl-shell-entry` PASS — MISSING: testes não rodados · 🔲 `nx lint` PASS — MISSING: lint não rodado

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:intl · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build intl-shell-entry` PASS

**Dependencies:** — (scaffold A4)
**API / Contract impact:** nenhum (metadados de menu/perm).
**Risks / Notes:** as 5 permissões devem espelhar 1:1 o `api-contract.md` do BE.
