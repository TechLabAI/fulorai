## [FE-COMM-006] RoutingApiService + RoutingFacade

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 13 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`RoutingApiService` (`GET/POST /routing-rules`, `GET/PATCH /routing-rules/{id}`) + `RoutingFacade`
com signal `regras` (ordenadas por prioridade), `loading`, `error`. Suporta condições, canal preferido,
fallback e flag `ativa`.

**Context / Problem statement:**
- Dados das regras de roteamento. Fonte: SPEC-04, SPEC-03. Depende: INT-FE-COMM-001. Bloqueia: FE-COMM-013.

**Approach:**
1) Service com list/get/create/update.
2) Facade ordena por `prioridade` e expõe signals readonly.

**Non-goals:** UI (FE-COMM-013); resolução de canal no FE (é do BE).

**Layer(s):** frontend / `libs/comm/data-access`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md`
**Architecture alignment:** signals-first; tag `scope:comm` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/data-access/src/lib/routing-api.service.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/routing.facade.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS · 🔲 [MISSING] `nx lint comm-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:comm · priority:P2

**Acceptance criteria:**
- Regras retornadas ordenadas por prioridade; `nx test/lint` PASS

**Dependencies:** INT-FE-COMM-001
**API / Contract impact:** `/api/v1/routing-rules`.
**Risks / Notes:** `condicoes` é objeto livre — tipar de forma defensiva.
