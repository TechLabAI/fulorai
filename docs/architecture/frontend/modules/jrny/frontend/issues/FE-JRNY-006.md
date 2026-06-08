## [FE-JRNY-006] Routing rules data-access: RoutingRuleApiService + facade

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`RoutingRuleApiService` (`/api/v1/routing/rules`) + `RoutingRulesFacade` em `libs/jrny/data-access`.
Operações: `list` (por `prioridade`), `create`, `update` (bumpa versão). `condicaoResumo` derivado da
`Condicao` (gramática de snapshot, data-model §5).

**Context / Problem statement:**
- O Routing Engine versiona regras; a UI lista/edita e mostra resumo legível da condição.
- Fonte: SPEC-04 (RoutingRule), SPEC-03 (RoutingRuleVm). Bloqueia: FE-JRNY-012.

**Approach (execution path):**
1) `RoutingRuleApiService` list/create/update sobre `/api/v1/routing/rules?jornadaId=`.
2) `RoutingRulesFacade` com signals + `computed` `condicaoResumo` (render textual de `Condicao`).
3) Refletir bump de versão na lista após `update`.

**Non-goals:** ConditionBuilder UI (FE-JRNY-012); validação visual (confia no 422).

**Layer(s):** frontend / `libs/jrny/data-access`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (RoutingRule) · `SPEC-03`

**Architecture alignment:** Signals-first; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/data-access/src/lib/routing-rule-api.service.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/routing-rules.facade.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/condicao.ts` (tipos + `condicaoResumo`) (MISSING)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:jrny · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- Edição de regra reflete `versão` incrementada na lista (cobre EARS #23)

**Dependencies:** FE-JRNY-004, INT-FE-JRNY-001
**API / Contract impact:** `/api/v1/routing/rules` (list/create/update).
**Risks / Notes:** gramática `condicao` (data-model §5) — campos/operadores fechados.
