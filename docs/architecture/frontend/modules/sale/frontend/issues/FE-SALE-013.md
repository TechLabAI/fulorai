## [FE-SALE-013] feature-purchase (lista + detalhe + breakdown explicável + estornar/cancelar)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/10 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`feature-purchase` com `PurchaseListPageComponent` (+ `PurchaseFilterBarComponent`,
`PurchaseRowComponent`) e `PurchaseDetailPageComponent` (+ `PurchaseSummaryComponent`,
`PurchaseItemsTableComponent`, `AttributionBreakdownComponent`, `PurchaseAdjustActionsComponent`).
`AttributionBreakdownComponent` **sempre** mostra touchpoint + tipo + valor + versão do modelo (Σ =
valorTotal) — nunca o total opaco. **Sem criação** de compra. **Estornar**/**cancelar** gated por
`sale.compra.estornar/cancelar` (status CONFIRMADA) com **confirmação destrutiva** (modal). `base_legal`/
consentimento visíveis (LGPD). `404` → estado vazio.

**Context / Problem statement:**
- Superfície de receita confirmada: consulta + breakdown explicável + ajustes (recalculam LTV no BE).
- Fonte: SPEC-02 (feature-purchase) + SPEC-03 (purchase). Consome `PurchaseListFacade`/`PurchaseDetailFacade`.
- Depende de FE-SALE-007, FE-SALE-009, FE-SALE-016. Bloqueia: FE-SALE-023.

**Approach (execution path):**
1) `PurchaseListPageComponent` lê compras/filtro; `PurchaseRowComponent` → abrir.
2) `PurchaseDetailPageComponent` lê compra/itens/atribuicao/podeAjustar/naoEncontrada.
3) `AttributionBreakdownComponent` renderiza linhas (touchpoint/tipo/valor/versão) + verifica Σ = valorTotal.
4) `PurchaseAdjustActionsComponent` (estornar/cancelar) com modal de confirmação; `PurchaseSummaryComponent` mostra baseLegal/comprador.

**Non-goals:** registrar compra (NUNCA no FE); governança de modelos (FE-SALE-014).

**Layer(s):** frontend / `libs/sale/feature-purchase`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02` (feature-purchase) · `SPEC-03` (purchase) · `SPEC-07` (estornar/cancelar modal)

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-purchase/src/lib/purchase-list.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-purchase/src/lib/purchase-filter-bar.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-purchase/src/lib/purchase-row.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-purchase/src/lib/purchase-detail.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-purchase/src/lib/purchase-summary.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-purchase/src/lib/purchase-items-table.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-purchase/src/lib/attribution-breakdown.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-purchase/src/lib/purchase-adjust-actions.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-feature-purchase` PASS — _MISSING_ · 🔲 `nx lint sale-feature-purchase` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-purchase` PASS
- Breakdown sempre com touchpoint+tipo+valor+versão e Σ = valorTotal (EARS SPEC-02/SPEC-03); sem afford de create
- Estornar/cancelar com confirmação destrutiva + gated (status CONFIRMADA)

**Dependencies:** FE-SALE-007, FE-SALE-009, FE-SALE-016
**Data impact:** PII do comprador visível só no detalhe (LGPD); ajustes não apagam histórico.
**API / Contract impact:** `/api/v1/compras` (list/get/estornar/cancelar) + `/compras/{id}/atribuicao`.
**Testing / Evidence required:** e2e `purchase-attribution-breakdown`; screenshots (lista, detalhe breakdown, modal ajuste).
**Risks / Notes:** R4 (nunca total opaco), R5 (sem create), R9 (LGPD + confirmação destrutiva).
