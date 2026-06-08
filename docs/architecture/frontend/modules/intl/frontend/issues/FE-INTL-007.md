## [FE-INTL-007] AnalyticsApiService + AnalyticsFacade

**Status:** ⚪ INTACT — pós-validação 2026-06-05
**Maturidade:** 22 — Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`AnalyticsApiService` (`funil(periodo, granularidade)`, `copilotUsage()`) + `AnalyticsFacade` (signals `funil()`, `copilotUsage()`, `periodo()`, `granularidade()`, `loading()`, `error()`). Read-only.

**Context / Problem statement:**
- Base dos dashboards. Fonte: SPEC-04 (Analytics) + SPEC-03.
- Bloqueia: FE-INTL-014.

**Approach (execution path):**
1) Service com `GET /analytics/funil` + `GET /analytics/copilot`.
2) Facade: re-fetch ao mudar período/granularidade; sem cache.
3) Nenhuma operação de escrita exposta (INV-FE-6).

**Non-goals:** UI (FE-INTL-014); analytics preditivo (fora do MVP).

**Layer(s):** frontend / libs/intl/data-access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Analytics)

**Architecture alignment:** ADR-002; signals; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/data-access/src/lib/analytics-api.service.ts` — MISSING: service não existe
- 🔲 `libs/intl/data-access/src/lib/analytics.facade.ts` — MISSING: facade não existe

**Tests**
- 🔲 `nx test intl-data-access` PASS — MISSING: sem testes · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:intl · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS

**Dependencies:** FE-INTL-002 · INT-FE-INTL-004
**API / Contract impact:** `/api/v1/analytics/**` (perm `intl.analytics.read`).
**Risks / Notes:** toda agregação filtrada por `empresa` (BE garante; FE só lê).
