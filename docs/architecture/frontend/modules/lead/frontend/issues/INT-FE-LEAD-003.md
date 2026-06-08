## [INT-FE-LEAD-003] Integração: access-decision + NavigationService

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 6 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
LEAD consome `@journeyos/shared/access-decision` (`AccessDecisionService.can('lead.*')`) e
`NavigationService` para filtrar menu/deep links e derivar a visibilidade de ações por permissão.

**Context / Problem statement:**
- A UI não decide RBAC. Fonte: SPEC-05, `access-layer-contracts.md`.
- Bloqueia: FE-LEAD-017 (guards), FE-LEAD-018 (navigation).

**Approach (execution path):**
1) Injetar `AccessDecisionService` para `computed()` de ações disponíveis.
2) `NavigationService` filtra deep links do contrato por permissão.

**Non-goals:** decisão de permissão (Access Layer/BE).

**Layer(s):** frontend / `libs/lead/access` + `navigation`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-05` · `standards/access-layer-contracts.md`

**Architecture alignment:** Access Layer; tag `scope:lead`.

**Implementation checklist (by file):**
- 🔲 wiring de `AccessDecisionService` nas features/guards — _MISSING_
- 🔲 filtro de deep links via `NavigationService` — _MISSING_

**Tests**
- 🔲 `nx test lead-access` PASS — _MISSING_ · 🔲 `nx lint lead-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:lead · priority:P4

**Acceptance criteria:**
- Deep link só visível com a permissão (SPEC-05 EARS); ações gated por `can('lead.*')`

**Dependencies:** FE-LEAD-001
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** cache de AccessDecision invalidado por evento do WRKS (transparente ao FE).
