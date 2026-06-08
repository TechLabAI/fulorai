## [FE-JRNY-001] Module contract + permission-map + feature-flags

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** REDUCED — pos-validacao 2026-06-05
**Maturidade:** 45 — Parcial
**Done/Total:** 2/4 itens

**Outcome:**
`jrny.contract.ts`, `jrny.permission-map.ts` e `jrny.feature-flags.ts` materializados em
`libs/jrny/shell-entry`, consistentes com SPEC-05: `MODULE_KEY`, `MODULE_MENU_METADATA` (label
"Jornadas", route `/jrny/journeys`, deep link Analytics gated por flag), `JRNY_PERMISSION_MAP`
(11 perms `jrny.*`), `JRNY_FEATURE_FLAGS` (`jrny.journey-analytics` enabled, `jrny.journey-builder-canvas` disabled).

**Context / Problem statement:**
- O Shell descobre o módulo via o contrato; permissões devem casar com o catálogo BE (`jrny.<recurso>.<acao>`).
- Fonte: SPEC-05. Bloqueia: FE-JRNY-002, FE-JRNY-003, INT-FE-JRNY-005.

**Approach (execution path):**
1) Preencher `jrny.contract.ts` com menu metadata + deep links (Jornadas, Analytics com `flag`).
2) Mapear `JRNY_PERMISSION_MAP` (11 perms `jrny.*`) conforme SPEC-05.
3) Declarar flags `jrny.journey-analytics` (enabled) e `jrny.journey-builder-canvas` (disabled — reserva pós-MVP, ADR-005).

**Non-goals:** lógica de guard (FE-JRNY-017); registro no Shell em runtime (INT-FE-JRNY-005).

**Layer(s):** frontend / `libs/jrny/shell-entry`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-05-module-contract.md`

**Architecture alignment:** module-pattern; Standalone/OnPush/Signals; tag `scope:jrny` `type:domain`.

**Implementation checklist (by file):**
- 🟡 `libs/jrny/shell-entry/src/lib/jrny.contract.ts` (PARTIAL) <!-- MODULE_KEY+label "Jornadas" OK; mas route='/jrny' (spec pede '/jrny/journeys') e deepLinks=[] (sem deep link Analytics gated por flag) -->
- ✅ `libs/jrny/shell-entry/src/lib/jrny.permission-map.ts` <!-- 11 perms jrny.* corretas (jornada×5, estagio×3, regra×2, roteamento×1); arrays de papel vazios (convenção scaffold, espelha WRKS) -->
- ✅ `libs/jrny/shell-entry/src/lib/jrny.feature-flags.ts` <!-- journey-analytics enabled, journey-builder-canvas disabled — exato per SPEC-05 -->

**Tests**
- 🔲 `nx test jrny-shell-entry` PASS (MISSING — sem arquivos .spec.ts em shell-entry) · 🔲 `nx lint jrny-shell-entry` PASS (MISSING)

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build jrny-shell-entry` PASS
- Permissões idênticas às do `jrny-service/contracts/api-contract.md` (sem inventar códigos)

**Dependencies:** — (fecha junto com scaffold)
**API / Contract impact:** consome `jrny.*` permissions; nenhum endpoint direto.
**Risks / Notes:** manter sincronia papel→permissão com o bundle do BE (single source of truth).
