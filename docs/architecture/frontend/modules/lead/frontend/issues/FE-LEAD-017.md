## [FE-LEAD-017] access: guards de rota + data-scope (empresaGuard/accessGuard)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Guards do módulo em `libs/lead/access`: aplicação de `authGuard`+`empresaGuard`+`accessGuard(<perm>)`
por rota (SPEC-01) e `leadDataScopeGuard` (SDR restrito ao seu `data_scope`). Cobre **G9**
(empresa-guard-block) e o gap de RBAC de rota.

**Context / Problem statement:**
- A UI não decide RBAC — delega à Access Layer. Fonte: SPEC-01. Bloqueia: deep-link/entitlement e2e.

**Approach (execution path):**
1) Compor os guards canônicos por rota (consumindo `AccessDecisionService`).
2) `leadDataScopeGuard`: restringe a fila/detalhe ao escopo do SDR.
3) Sem contexto de empresa → bloqueio via `empresaGuard` (G9).

**Non-goals:** lógica de permissão em si (Access Layer); UI de "acesso negado" (Shell).

**Layer(s):** frontend / `libs/lead/access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md`

**Architecture alignment:** `@journeyos/shared/access-decision`; tag `scope:lead` `type:domain`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/access/src/lib/lead-data-scope.guard.ts` — _MISSING_
- 🔲 `libs/lead/access/src/lib/index.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-access` PASS · 🔲 `nx lint lead-access` PASS — _MISSING_

**Milestone:** Wave P5 / Access guards
**Labels:** type:feature · layer:frontend · scope:lead · priority:P5

**Acceptance criteria:**
- `npx nx test/lint/build lead-access` PASS
- `IF` sem empresa ativa, rotas LEAD bloqueadas (SPEC-01 EARS, G9)

**Dependencies:** FE-LEAD-002, INT-FE-LEAD-003
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** manter os guards alinhados ao `data_scope` retornado por AccessDecision.
