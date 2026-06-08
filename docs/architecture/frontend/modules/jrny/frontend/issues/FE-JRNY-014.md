## [FE-JRNY-014] feature-journey-analytics (funil + saúde do roteamento)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`feature-journey-analytics` com `JourneyAnalyticsPageComponent` (smart) + `FunnelChartComponent`,
`RoutingHealthCardComponent`. Funil por estágio + % de decisões com assist IA (read-only). Atrás da
flag `jrny.journey-analytics`; **degrada para estado vazio** se o endpoint não existir (gap G1).

**Context / Problem statement:**
- Visão de funil/saúde; endpoint de analytics ainda **proposto** (gap G1) — feature resiliente.
- Fonte: SPEC-03 (JourneyAnalyticsVM), SPEC-04 (gap G1), SPEC-05 (flag).

**Approach (execution path):**
1) `JourneyAnalyticsPageComponent` lê `funil/taxaAssistIa/totalDecisoes/loading/error`.
2) `FunnelChart` em SVG/CSS leve (sem lib pesada — ADR-005); valores numéricos visíveis.
3) Se endpoint ausente/404 → estado vazio amigável (não erro).

**Non-goals:** definição do endpoint BE (gap G1 — fora do FE).

**Layer(s):** frontend / `libs/jrny/feature-journey-analytics`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-03` · `SPEC-04` (G1) · `SPEC-05` (flag)

**Architecture alignment:** Standalone + OnPush + Signals; tag `type:feature` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/feature-journey-analytics/src/lib/journey-analytics.page.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-analytics/src/lib/funnel-chart.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-analytics/src/lib/routing-health-card.component.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-feature-journey-analytics` PASS (MISSING) · 🔲 `nx lint ...` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-feature-journey-analytics` PASS
- Flag off → rota/menu omitidos (EARS #7/#25); endpoint ausente → vazio (gap G1)

**Dependencies:** FE-JRNY-002, FE-JRNY-007
**API / Contract impact:** `/api/v1/journeys/analytics` (**proposto** — confirmar com BE).
**Risks / Notes:** G1 — não bloquear; degradar para vazio até o BE expor o contrato.
