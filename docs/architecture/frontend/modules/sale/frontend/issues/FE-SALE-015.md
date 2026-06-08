## [FE-SALE-015] feature-revenue-dashboard (funil + LTV, flag-gated, read-only)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/6 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`feature-revenue-dashboard` com `RevenueDashboardPageComponent` (smart) +
`RevenueFunnelChartComponent` (SVG/CSS leve, por origem), `RevenuePeriodFilterComponent`,
`LtvTopContactsTableComponent`. Read-only, apoiado em `RevenueDashboardFacade`. Rota/menu **gated** pela
flag `sale.revenue-dashboard` (default enabled). O **funil** depende do endpoint proposto `/receita/funil`
(gap G1) e **degrada** para LTV-apenas/estado vazio se ausente. Chart leve para não estourar bundle (R3).

**Context / Problem statement:**
- Leitura de faturamento/LTV/funil para INFOPRODUTOR/HEAD_GROWTH.
- Fonte: SPEC-02 (feature-revenue-dashboard) + SPEC-03 (RevenueDashboardVM). Consome `RevenueDashboardFacade`.
- Depende de FE-SALE-008, FE-SALE-016. Relaciona-se a FE-SALE-002 (rota flag-gated) e G1.

**Approach (execution path):**
1) `RevenueDashboardPageComponent` lê funilReceita/ltvTopContatos/periodo/loading/error.
2) `RevenueFunnelChartComponent` (SVG/CSS próprio — sem lib de chart pesada).
3) `RevenuePeriodFilterComponent` → `periodoChange`; `LtvTopContactsTableComponent` (contato/valorTotal/numCompras).
4) Degradação G1: sem `/receita/funil` → mostra só LTV / estado vazio do funil.

**Non-goals:** flag gating na rota (FE-SALE-002/020 — aqui só a feature); analytics IA (pós-MVP).

**Layer(s):** frontend / `libs/sale/feature-revenue-dashboard`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02` (feature-revenue-dashboard) · `SPEC-03` (RevenueDashboardVM) · `contracts/backend-api-cross-link.md` (G1)

**Architecture alignment:** Standalone + OnPush + Signals; chart leve; tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-revenue-dashboard/src/lib/revenue-dashboard.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-revenue-dashboard/src/lib/revenue-funnel-chart.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-revenue-dashboard/src/lib/revenue-period-filter.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-revenue-dashboard/src/lib/ltv-top-contacts-table.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-feature-revenue-dashboard` PASS — _MISSING_ · 🔲 `nx lint sale-feature-revenue-dashboard` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-revenue-dashboard` PASS
- Funil degrada para LTV-apenas/vazio sem `/receita/funil` (G1); read-only; chart leve (sem lib pesada — R3)

**Dependencies:** FE-SALE-008, FE-SALE-016
**Data impact:** Nenhum.
**API / Contract impact:** `/api/v1/ltv` + `/receita/funil` (proposto, G1).
**Testing / Evidence required:** screenshots (funil, LTV, estado degradado). Sem e2e dedicado (coberto por `deep-link` flag).
**Risks / Notes:** G1 (endpoint funil), R3 (bundle do chart). Flag off → rota/menu omitidos (FE-SALE-002/020).
