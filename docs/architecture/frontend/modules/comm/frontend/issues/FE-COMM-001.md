## [FE-COMM-001] Module contract + permission-map + feature-flags

**Status:** REDUCED -- pos-validacao 2026-06-05
**Maturidade:** 30 -- Inicial
**Done/Total:** 1/5 itens
**GitHub:** [#TBD]

**Outcome:**
`comm.contract.ts`, `comm.permission-map.ts` e `comm.feature-flags.ts` materializados em
`libs/comm/shell-entry`, consistentes com SPEC-05: `MODULE_KEY`, `MODULE_MENU_METADATA`
(label "Comunicação", route `/comm/templates`, deep links Templates/Mensagens/Roteamento/Canais),
`COMM_PERMISSION_MAP` (13 perms `comm.*`), `COMM_FEATURE_FLAGS` (`comm.template-studio`, `comm.delivery-tracking`).

**Context / Problem statement:**
- O Shell descobre o módulo via contrato; permissões devem casar 1:1 com o catálogo BE (`comm.<recurso>.<acao>`).
- Fonte: SPEC-05. Bloqueia: FE-COMM-002, FE-COMM-003, INT-FE-COMM-005.

**Approach:**
1) Preencher `comm.contract.ts` com menu metadata + 4 deep links (cada um com `permission`).
2) Mapear `COMM_PERMISSION_MAP` (13 perms) conforme SPEC-05 (arrays papel→perm preenchidos no implement via AccessDecision).
3) Declarar flags `comm.template-studio` e `comm.delivery-tracking` (defaultState: enabled).

**Non-goals:** lógica de guard (FE-COMM-016); registro runtime no Shell (INT-FE-COMM-005); polling (FE-COMM-014).

**Layer(s):** frontend / `libs/comm/shell-entry`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-05-module-contract.md`
**Architecture alignment:** module-pattern; Standalone/OnPush/Signals; tag `scope:comm` `type:app`.

**Implementation checklist (by file):**
- ◐ [PARTIAL] `libs/comm/shell-entry/src/lib/comm.contract.ts`
- ◐ [PARTIAL] `libs/comm/shell-entry/src/lib/comm.permission-map.ts`
- ✅ [DONE] `libs/comm/shell-entry/src/lib/comm.feature-flags.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-shell-entry` PASS · 🔲 [MISSING] `nx lint comm-shell-entry` PASS

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:comm · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build comm-shell-entry` PASS
- Permissões idênticas às do `comm-service/contracts/api-contract.md` (sem inventar códigos)

**Dependencies:** — (fecha junto com scaffold)
**API / Contract impact:** consome `comm.*` permissions; nenhum endpoint direto.
**Risks / Notes:** manter sincronia papel→permissão com o bundle RBAC do WRKS (single source of truth).
