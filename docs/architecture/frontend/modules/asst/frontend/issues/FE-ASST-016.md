## [FE-ASST-016] Access guards (assetGuard + accessGuard nas rotas)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 10 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`libs/asst/access` provê o wiring de `accessGuard('asst.<perm>')` nas rotas + um `assetGuard`
opcional que resolve `:id` e valida escopo de empresa, consumindo `AccessDecisionService`.

**Context / Problem statement:**
- Garante UINV-1/UINV-2 nas rotas. Fonte: SPEC-01 (guards). Depende de FE-ASST-002, INT-FE-ASST-004.
- Bloqueia: FE-ASST-020 (deep-link/entitlement e2e).

**Approach (execution path):**
1) Aplicar `authGuard, empresaGuard, accessGuard('<perm>')` em cada rota conforme SPEC-01.
2) `assetGuard` (opcional): resolve `:id`, garante que pertence à empresa ativa (UINV-8).
3) Sem decisão de RBAC local — sempre via `AccessDecisionService.can()`.

**Non-goals:** lógica de Access Layer (shared); navegação (FE-ASST-017).

**Layer(s):** frontend / `libs/asst/access`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-01-route-map.md`

**Architecture alignment:** `access → shared/{access-decision,auth-session}`; tag `type:domain`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/access/src/lib/access.guard.ts` (factory `accessGuard(perm)`)
- 🔲 [MISSING] `libs/asst/access/src/lib/asset.guard.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-access` PASS · 🔲 [MISSING] `nx lint asst-access` PASS

**Milestone:** Wave P5 / Access guards
**Labels:** type:feature · layer:frontend · scope:asst · priority:P5

**Acceptance criteria:**
- Rota sem permissão é bloqueada; deep link sem sessão redireciona a login (UINV-1)

**Dependencies:** FE-ASST-002, INT-FE-ASST-004
**API / Contract impact:** consome AccessDecision (via shared).
**Risks / Notes:** evitar duplicar guards globais — só os específicos do módulo.
