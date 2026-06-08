## [FE-LEAD-013] feature-maturity-score: dashboard de distribuição + radar da base

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`MaturityDashboardPageComponent` com `MaturityDistributionChartComponent` (histograma + saúde por
dimensão), reuso do `ScoreRadarComponent` (média 6D da base) e `AssistIaShareComponent`
(`% com assist IA`). Para a persona `HEAD_GROWTH` monitorar a base.

**Context / Problem statement:**
- Visão agregada de saúde/distribuição do score. Fonte: SPEC-02, ADR-005.
- Pode ser desligada pela flag `lead.maturity-score`.

**Approach (execution path):**
1) `MaturityDashboardPageComponent` lê `MaturityFacade` (`distribuicao`, loading, error).
2) `MaturityDistributionChartComponent` (histograma + saúde por dimensão).
3) Reuso de `ScoreRadarComponent`; `AssistIaShareComponent` (transparência).

**Non-goals:** breakdown individual (FE-LEAD-012, no detalhe).

**Layer(s):** frontend / `libs/lead/feature-maturity-score`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-02` · `ADR-005`

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:lead` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-maturity-score/src/lib/maturity-dashboard.page.ts` — _MISSING_
- 🔲 `libs/lead/ui/src/lib/maturity-distribution-chart.component.ts` — _MISSING_
- 🔲 `libs/lead/ui/src/lib/assist-ia-share.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-feature-maturity-score` PASS — _MISSING_ · 🔲 `nx lint lead-feature-maturity-score` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-feature-maturity-score` PASS
- Dashboard exibe distribuição + saúde por dimensão + % assist IA

**Dependencies:** FE-LEAD-004, FE-LEAD-012
**API / Contract impact:** `GET /leads` facetado (endpoint de agregação a confirmar com BE — ver cross-link).
**Risks / Notes:** se BE não expor agregação dedicada, derivar de `GET /leads` (gap registrado em 06-risks).
