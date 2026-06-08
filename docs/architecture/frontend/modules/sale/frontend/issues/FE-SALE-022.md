## [FE-SALE-022] Observability (telemetria via @journeyos/shared/observability)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Eventos de telemetria emitidos via `@journeyos/shared/observability` (sem PII): **timing do board**
(carga/render do Kanban), **latência do move otimista** (PATCH estágio) + taxa de rollback, **taxa de
win/loss** (ganhar/perder), **taxa de estorno/cancelamento**, e latência das chamadas SALE. Métricas
alimentam diagnóstico de R1/R2 sem expor dados do comprador.

**Context / Problem statement:**
- Telemetria operacional do módulo (board, win/loss, estorno) recomendada no brief (item 7).
- Fonte: SPEC-07 (estratégia) + _brief (observability). Depende das features P3.

**Approach (execution path):**
1) Instrumentar timing do board + latência/rollback do move no `feature-pipeline`.
2) Eventos de win/loss (opportunity) e estorno/cancelamento (purchase).
3) Latência genérica das chamadas no data-access; garantir ausência de PII nos payloads.

**Non-goals:** dashboards de telemetria (fora do FE); analytics de receita IA (pós-MVP).

**Layer(s):** frontend / `libs/sale/data-access` + `libs/sale/feature-pipeline` + `libs/sale/feature-opportunity` + `libs/sale/feature-purchase`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-07-error-handling.md` · `_brief.md` (item 7, observability)

**Architecture alignment:** `@journeyos/shared/observability`; tags conforme lib.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/telemetry/sale-telemetry.ts` — _MISSING_
- 🔲 hooks de timing no `pipeline.facade.ts` (board + move) — _MISSING_
- 🔲 eventos win/loss e estorno/cancelamento nas features — _MISSING_

**Tests**
- 🔲 `nx test` libs afetadas PASS — _MISSING_ · 🔲 `nx lint` PASS — _MISSING_

**Milestone:** Wave P8 / Observability
**Labels:** type:feature · layer:frontend · scope:sale · priority:P8

**Acceptance criteria:**
- `npx nx test/lint/build` libs afetadas PASS
- Eventos de board/move/win-loss/estorno emitidos sem PID/PII

**Dependencies:** FE-SALE-010, FE-SALE-011, FE-SALE-013
**Data impact:** telemetria sem PII (LGPD).
**API / Contract impact:** nenhum.
**Testing / Evidence required:** teste de emissão de eventos; assert de ausência de PII.
**Risks / Notes:** não vazar `contatoRef`/comprador em métricas (R9/LGPD).
