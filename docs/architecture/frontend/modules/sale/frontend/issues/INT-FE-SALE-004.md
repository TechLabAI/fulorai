## [INT-FE-SALE-004] Integração access-decision/entitlement (15 perms sale.*)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/sale/access` + features consultam `AccessDecisionService` para as **15 permissões `sale.*`**: os
guards (FE-SALE-018) e as affordances (criar oportunidade, mover, ganhar/perder, criar/editar/desativar
oferta, estornar/cancelar, criar/ativar modelo) ficam escondidas/desabilitadas sem permissão; o
`NavigationService` filtra os deep links do menu por permissão. A UI nunca decide RBAC.

**Context / Problem statement:**
- Liga as 15 perms do contrato ao gating efetivo de rota + ação + menu.
- Fonte: SPEC-05 (gating) + SPEC-01 (accessGuard) + SPEC-02 (afford gating) + access-layer-contracts.
- Depende de FE-SALE-001, FE-SALE-018.

**Approach (execution path):**
1) Expor helpers de entitlement (`can('sale.<perm>')`) consumidos por guards/features.
2) Filtrar deep links do menu por permissão via `NavigationService` + `AccessDecisionService`.
3) Esconder/desabilitar afford de mutação sem a permissão respectiva.

**Non-goals:** definição dos guards (FE-SALE-018); permission-map (FE-SALE-001).

**Layer(s):** frontend / `libs/sale/access` + `libs/sale/navigation`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-05` (gating) · `SPEC-01` (accessGuard) · `standards/access-layer-contracts.md`

**Architecture alignment:** Access Layer; tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/access/src/lib/sale-entitlement.ts` — _MISSING_
- 🔲 `libs/sale/navigation/src/lib/sale-menu-filter.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-access` PASS — _MISSING_ · 🔲 `nx lint sale-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:sale · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build sale-access` PASS
- Afford de mutação escondida/desabilitada sem perm (EARS SPEC-02/SPEC-05); deep links filtrados (EARS SPEC-05/SPEC-06)

**Dependencies:** FE-SALE-001, FE-SALE-018
**Data impact:** Nenhum.
**API / Contract impact:** consulta Access Layer (sem endpoint direto).
**Testing / Evidence required:** e2e `entitlement-denied`; teste de gating por permissão.
**Risks / Notes:** as 15 perms devem casar com o bundle BE — single source of truth.
