## [FE-ASST-001] Module contract + permission-map + feature-flags

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 32 -- Inicial
**Done/Total:** 1/5 itens
**GitHub:** [#TBD]

**Outcome:**
`asst.contract.ts`, `asst.permission-map.ts` e `asst.feature-flags.ts` materializados em
`libs/asst/shell-entry` e consistentes com SPEC-05, exportando `MODULE_KEY`, `MODULE_MENU_METADATA`
(label "Assets", route `/asst/library`, deep link "Aprovações"), `ASST_PERMISSION_MAP`,
`ASST_FEATURE_FLAGS`.

**Context / Problem statement:**
- O Shell descobre o módulo via o contrato; permissões devem casar com o catálogo BE (`asst.<recurso>.<acao>`).
- Fonte: SPEC-05. Bloqueia: FE-ASST-002, FE-ASST-003, INT-FE-ASST-005.

**Approach (execution path):**
1) Preencher `asst.contract.ts` com menu metadata + deep link `Aprovações` (`permission: asst.asset.aprovar`).
2) Mapear `ASST_PERMISSION_MAP` (8 perms `asst.*`) conforme SPEC-05 (arrays preenchidos no implement via AccessDecision).
3) Declarar flags `asst.asset-studio`, `asst.approval-workflow` (defaultState: enabled).

**Non-goals:** lógica de guard (FE-ASST-016); registro no Shell em runtime (INT-FE-ASST-005).

**Layer(s):** frontend / `libs/asst/shell-entry`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-05-module-contract.md`

**Architecture alignment:** module-pattern; Standalone/OnPush/Signals; tag `scope:asst` `type:app`.

**Implementation checklist (by file):**
- ◐ [PARTIAL] `libs/asst/shell-entry/src/lib/asst.contract.ts` (stub: deepLinks `[]` vazio + route `/asst` em vez de `/asst/library`; falta deep link "Aprovações")
- ◐ [PARTIAL] `libs/asst/shell-entry/src/lib/asst.permission-map.ts` (8 chaves `asst.*` presentes mas todos os arrays `[]` vazios — preenchidos no implement)
- ✅ [DONE] `libs/asst/shell-entry/src/lib/asst.feature-flags.ts` (2 flags `asst.asset-studio` + `asst.approval-workflow`, defaultState enabled — estruturalmente completo)

**Tests**
- 🔲 [MISSING] `nx test asst-shell-entry` PASS · 🔲 [MISSING] `nx lint asst-shell-entry` PASS

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:asst · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build asst-shell-entry` PASS
- Permissões idênticas às do `asst-service/contracts/api-contract.md` (sem inventar códigos)

**Dependencies:** — (fecha junto com scaffold)
**API / Contract impact:** consome `asst.*` permissions; nenhum endpoint direto.
**Risks / Notes:** manter sincronia papel→permissão com o bundle do BE (single source of truth).
