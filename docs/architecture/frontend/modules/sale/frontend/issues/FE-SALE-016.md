## [FE-SALE-016] libs/sale/ui local (chips, Money, board Kanban, empty state)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/9 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/sale/ui` com os presentational compartilhados do módulo: `OpportunityStateChipComponent`
(NOVA/EM_ANDAMENTO/GANHA/PERDIDA/DESCARTADA), `PurchaseStatusChipComponent`
(CONFIRMADA/ESTORNADA/CANCELADA), `MoneyComponent` (NUMERIC(15,2) + moeda ISO-4217),
`AttributionTypeBadgeComponent` (ORIGEM_LEAD/JORNADA/CAMPANHA/DIRETO), `EmptyStateComponent` (reusa
`@journeyos/shared/ui-feedback`), e o **board Kanban** reutilizável (`kanban-board`, `kanban-column`,
`opportunity-card`). Todos com rótulo textual (não cor-only). Resolve G2/G3 com fallback id quando
titulo/responsavelNome ausentes.

**Context / Problem statement:**
- Componentes locais consumidos por várias features (pipeline, opportunity, purchase, attribution, dashboard).
- Fonte: SPEC-02 (Componentes locais). Bloqueia: FE-SALE-010..015, FE-SALE-021.

**Approach (execution path):**
1) Chips de estado/status com rótulo textual + token de cor acessível.
2) `MoneyComponent` formata valor+moeda; `AttributionTypeBadgeComponent` por tipo de touchpoint.
3) Board Kanban estrutural (`kanban-board`/`kanban-column`/`opportunity-card`) consumido pelo feature-pipeline.
4) `EmptyStateComponent` reusa ui-feedback; fallback id para titulo/responsavel (G2/G3).

**Non-goals:** lógica de DnD/optimistic (FE-SALE-010); promoção a shared (candidato — 06-risks).

**Layer(s):** frontend / `libs/sale/ui`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02-component-hierarchy.md` (Componentes locais compartilhados) · `SPEC-03` (enums/Money)

**Architecture alignment:** Standalone + OnPush + `input()`/`output()`; `@journeyos/shared/ui-tokens`; tag `scope:sale` `type:ui`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/ui/src/lib/opportunity-state-chip.component.ts` — _MISSING_
- 🔲 `libs/sale/ui/src/lib/purchase-status-chip.component.ts` — _MISSING_
- 🔲 `libs/sale/ui/src/lib/money.component.ts` — _MISSING_
- 🔲 `libs/sale/ui/src/lib/attribution-type-badge.component.ts` — _MISSING_
- 🔲 `libs/sale/ui/src/lib/empty-state.component.ts` — _MISSING_
- 🔲 `libs/sale/ui/src/lib/kanban/{kanban-board,kanban-column,opportunity-card}.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-ui` PASS — _MISSING_ · 🔲 `nx lint sale-ui` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:ui · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-ui` PASS
- Chips/badges com rótulo textual (não cor-only); `MoneyComponent` formata moeda; fallback id (G2/G3)

**Dependencies:** — (base de P3, pode iniciar com FE-SALE-001)
**Data impact:** Nenhum.
**API / Contract impact:** nenhum.
**Testing / Evidence required:** snapshots dos chips/badges; teste do `MoneyComponent`.
**Risks / Notes:** kanban-board é novo no monorepo — candidato a promoção shared se JRNY/outros precisarem (06-risks gap).
