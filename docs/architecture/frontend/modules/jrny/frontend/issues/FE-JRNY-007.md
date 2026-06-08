## [FE-JRNY-007] Routing query data-access: RoutingQueryApiService + DecisionLogFacade

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`RoutingQueryApiService` (`/api/v1/routing/leads/{leadId}/journey` + `/decisions`) +
`DecisionLogFacade`. Expõe `LeadJourneyStateVm` (estágio corrente) e `DecisionItemVm[]` (newest-first,
paginado), com `semInscricao` (404 → estado vazio) e mapeamento de `assistIa` ternário.

**Context / Problem statement:**
- Alimenta o decision log explicável (golden path B) — o "por quê" de cada lead.
- Fonte: SPEC-04 (RoutingQuery), SPEC-03 (DecisionLogVM). Bloqueia: FE-JRNY-013.

**Approach (execution path):**
1) `RoutingQueryApiService.getJourneyState` + `listDecisions` (paginado).
2) `DecisionLogFacade` com signals; `semInscricao` em 404; `DecisionItemVm` inclui SEM_MUDANCA/NAO_ROTEADO.
3) Mapear `assistIa` (USADO/IGNORADO/INDISPONIVEL) para o badge (FE-JRNY-013/015).

**Non-goals:** UI da timeline (FE-JRNY-013); badge component (FE-JRNY-015).

**Layer(s):** frontend / `libs/jrny/data-access`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (RoutingQuery) · `SPEC-03`

**Architecture alignment:** Signals-first; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/data-access/src/lib/routing-query-api.service.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/decision-log.facade.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/decision.models.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:jrny · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- 404 de inscrição → `semInscricao=true` (não erro); decisões newest-first

**Dependencies:** FE-JRNY-004, INT-FE-JRNY-001
**API / Contract impact:** `/api/v1/routing/leads/{leadId}/journey` + `/decisions`.
**Risks / Notes:** `assistIa` é ternário no contrato (não boolean) — refletir no VM.
