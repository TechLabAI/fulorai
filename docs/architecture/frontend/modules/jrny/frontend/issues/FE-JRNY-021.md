## [FE-JRNY-021] Observability (telemetria do módulo)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Outcome:**
Eventos de telemetria via `@journeyos/shared/observability`: latência do builder, tempo até publicar,
taxa de decisões com assist IA, p95 das leituras do decision log. Sem PII; escopado por empresa.

**Context / Problem statement:**
- Métricas de produto/saúde do módulo (recomendado).
- Fonte: 04 §4 (observability), success signals (01 §7).

**Approach (execution path):**
1) Instrumentar facades (builder/decision-log) com eventos de observability.
2) Métrica de uso de assist IA (% USADO) e tempo até publicar.

**Non-goals:** dashboards (INTL); coleta server-side.

**Layer(s):** frontend / `libs/jrny/data-access` (+ observability)
**Bounded context:** jrny

**Service execution spec(s):** `04-frontend-architecture-direction.md` §4

**Architecture alignment:** observability compartilhado; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/data-access/src/lib/jrny-telemetry.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P8 / Observability
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P8

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- Eventos emitidos sem PII; escopados por empresa

**Dependencies:** FE-JRNY-004, FE-JRNY-007
**API / Contract impact:** nenhum.
**Risks / Notes:** não vazar ids sensíveis na telemetria.
