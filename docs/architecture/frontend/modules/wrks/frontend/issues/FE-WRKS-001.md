## [FE-WRKS-001] Module contract + permission-map + feature-flags

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** REDUCED — pos-validacao 2026-06-05
**Maturidade:** 45 — Parcial
**Done/Total:** 1/5 itens

**Outcome:**
`wrks.contract.ts`, `wrks.permission-map.ts` e `wrks.feature-flags.ts` materializados e consistentes com SPEC-05, exportando `MODULE_KEY`, `MODULE_MENU_METADATA`, `MODULE_PERMISSION_MAP`, `MODULE_FEATURE_FLAGS`.

**Context / Problem statement:**
- O Shell descobre a module via o contrato; permissões devem casar com o catálogo BE (`wrks.<recurso>.<acao>`).
- Fonte: SPEC-05. Bloqueia: FE-WRKS-002, FE-WRKS-003, INT-FE-WRKS-005.

**Approach (execution path):**
1) Preencher `wrks.contract.ts` com menu metadata + deep links (users, rbac, settings) com `permission`.
2) Mapear `MODULE_PERMISSION_MAP` papel→permissão conforme SPEC-05 (alinhado a `shared/rbac/papeis.md`).
3) Declarar flags `wrks.rbac-viewer`, `wrks.org-structure` (defaultState: enabled).

**Non-goals:**
- Lógica de guard (FE-WRKS-016); registro no Shell em runtime (INT-FE-WRKS-005).

**Layer(s):** frontend / apps/wrks <module>-module
**Bounded context:** wrks

**Service execution spec(s):**
- `frontend-spec/SPEC-05-module-contract.md`

**Architecture alignment:** module-pattern; Standalone/OnPush/Signals; tag `scope:wrks` `type:app`.

**Implementation checklist (by file):**
- 🟡 `apps/wrks/src/app/wrks-module/wrks.contract.ts` (PARTIAL) — real em `libs/wrks/shell-entry/src/lib/wrks.contract.ts`: `MODULE_KEY`/`MODULE_MENU_METADATA` presentes, mas `route:'/wrks'` (SPEC-05 pede `/wrks/workspace`) e `deepLinks: []` vazio (SPEC-05 pede 3 deep links com permission).
- 🟡 `apps/wrks/src/app/wrks-module/wrks.permission-map.ts` (PARTIAL) — real em `libs/wrks/shell-entry/src/lib/wrks.permission-map.ts`: exporta `WRKS_PERMISSION_MAP` (issue pede `MODULE_PERMISSION_MAP`); chaves `wrks.*` corretas mas todos os arrays papel→permissão estão vazios `[]` (SPEC-05 exige INFOPRODUTOR/HEAD_GROWTH).
- ✅ `apps/wrks/src/app/wrks-module/wrks.feature-flags.ts` — real em `libs/wrks/shell-entry/src/lib/wrks.feature-flags.ts`: `wrks.rbac-viewer` + `wrks.org-structure` ambos `enabled`, alinhado ao SPEC-05 (nome do export `WRKS_FEATURE_FLAGS`).

**Tests**
- 🔲 `nx test wrks` PASS (MISSING — nenhum `.spec.ts` em `libs/wrks/shell-entry`) · 🔲 `nx lint wrks` PASS (MISSING)

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P1

**Acceptance criteria:**
- `npx nx test wrks` / `lint wrks` / `build wrks` PASS
- Permissões idênticas às do `api-contract.md` BE (sem inventar códigos)

**Dependencies:** — (fecha junto com scaffold)
**API / Contract impact:** consome `wrks.*` permissions; nenhum endpoint direto.
**Risks / Notes:** manter sincronia com bundle papel→permissão do BE (single source of truth).
