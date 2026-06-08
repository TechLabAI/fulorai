## [INT-FE-SALE-006] Integração observability (timing board, win/loss, latência)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Liga o módulo ao `@journeyos/shared/observability`: provê o sink de telemetria consumido por
FE-SALE-022 (timing do board, latência/rollback do move otimista, taxa de win/loss, taxa de estorno,
latência das chamadas SALE), garantindo correlação via `X-Correlation-Id` e **ausência de PII**.

**Context / Problem statement:**
- Provedor/wiring da telemetria; FE-SALE-022 emite, esta issue conecta o sink shared + correlação.
- Fonte: _brief (item 7) + SPEC-07. Depende de INT-FE-SALE-001.

**Approach (execution path):**
1) Prover o cliente de observability no escopo do módulo.
2) Correlacionar eventos com `X-Correlation-Id` da chamada HTTP.
3) Garantir filtro de PII (sem `contatoRef`/comprador nos payloads).

**Non-goals:** definição dos eventos de negócio (FE-SALE-022).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-07-error-handling.md` · `_brief.md` (item 7)

**Architecture alignment:** `@journeyos/shared/observability`; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/telemetry/sale-observability.providers.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:sale · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- Sink de observability provido + correlação por `X-Correlation-Id`; payloads sem PII

**Dependencies:** INT-FE-SALE-001
**Data impact:** telemetria sem PII (LGPD).
**API / Contract impact:** nenhum.
**Testing / Evidence required:** teste do provider; assert de ausência de PII.
**Risks / Notes:** R9 — nunca emitir PII do comprador em métricas.
