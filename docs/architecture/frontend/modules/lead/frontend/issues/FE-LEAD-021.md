## [FE-LEAD-021] Observability: telemetria do módulo

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Instrumentação via `@journeyos/shared/observability`: latência da fila, tempo até `qualify`,
`% com assist IA`, taxa de erro por código, uso de segmentos/regras. Eventos de telemetria nas facades.

**Context / Problem statement:**
- Visibilidade operacional do módulo. Fonte: `02` §5 (cross-cutting), `06` (success signals).

**Approach (execution path):**
1) Emitir eventos nas facades (list/get/qualify/activate) com timing.
2) Métrica de `% com assist IA` no dashboard.
3) Sem PII nos eventos (LGPD).

**Non-goals:** dashboards externos; APM backend.

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `02-architecture-blueprint.md` §5

**Architecture alignment:** `@journeyos/shared/observability`; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/data-access/src/lib/lead-telemetry.ts` — _MISSING_
- 🔲 wiring nas facades — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P8 / Observability
**Labels:** type:feature · layer:frontend · scope:lead · priority:P8

**Acceptance criteria:**
- `npx nx test/lint/build lead-data-access` PASS
- Eventos emitidos sem PII; timing da fila/qualify capturado

**Dependencies:** FE-LEAD-004
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** garantir ausência de PII nos eventos (LGPD).
