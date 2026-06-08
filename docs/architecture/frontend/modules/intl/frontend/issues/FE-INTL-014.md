## [FE-INTL-014] feature-analytics — AnalyticsPageComponent (funil + uso do copiloto)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 22 — Inicial
**Done/Total:** 0/7 itens
**GitHub:** [#TBD]

**Outcome:**
`AnalyticsPageComponent` (smart) com `PeriodFilterComponent`, `FunnelChartComponent` (+ `FunnelStageComponent`) e `CopilotUsagePanelComponent` (+ `StatCardComponent`); dashboards read-only com filtro de período.

**Context / Problem statement:**
- Tela analítica. Fonte: SPEC-02 (feature-analytics) + SPEC-03.
- Bloqueia: FE-INTL-019 (e2e analytics-read).

**Approach (execution path):**
1) Page consome `AnalyticsFacade.funil()`/`copilotUsage()`/`periodo()`.
2) `PeriodFilter` emite `periodoChange`/`granularidadeChange` → re-fetch.
3) `StatCard` exibe `totalRespostas/custoTokens/taxas`. Skeleton via `ui-feedback`.

**Non-goals:** dashboard builder/preditivo (fora do MVP); qualquer escrita (INV-FE-6).

**Layer(s):** frontend / libs/intl/feature-analytics + ui
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-02-component-hierarchy.md` (feature-analytics)

**Architecture alignment:** Standalone + OnPush; `scope:intl`.

**Implementation checklist (by file):**
- 🟡 `libs/intl/feature-analytics/src/lib/analytics.page.ts` — PARTIAL: placeholder shell, sem facade/dashboards
- 🔲 `libs/intl/feature-analytics/src/lib/period-filter.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-analytics/src/lib/funnel-chart.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-analytics/src/lib/copilot-usage-panel.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/ui/src/lib/stat-card.component.ts` — MISSING: arquivo não existe

**Tests**
- 🔲 `nx test intl-feature-analytics` PASS — MISSING: sem teste read-only · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:intl · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build intl-feature-analytics` PASS
- Teste: nenhuma ação de escrita presente (read-only).

**Dependencies:** FE-INTL-007
**API / Contract impact:** `/analytics/funil`, `/analytics/copilot`.
**Risks / Notes:** bundle de gráficos (R7) — carregar sob demanda.
