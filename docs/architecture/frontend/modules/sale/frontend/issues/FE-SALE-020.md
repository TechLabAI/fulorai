## [FE-SALE-020] UX polish (loading/empty/error + Kanban skeleton + rollback UX + flag gating)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/6 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Estados de UI consistentes em todas as features: **loading** (skeleton do Kanban por coluna; spinners
de lista/detalhe), **empty** (sem oportunidades/ofertas/compras; "oportunidade/compra não encontrada"),
**error** com **"tentar novamente"** (retry manual em leituras), e o **UX do rollback otimista** do
Kanban (card volta à coluna de origem + toast de erro). Gating efetivo da rota/menu `/sale/dashboard`
pela flag `sale.revenue-dashboard` (off → omite rota + item de menu).

**Context / Problem statement:**
- Endurece a experiência: leitura, mutação, optimistic, flags. Consolida os estados de SPEC-07.
- Fonte: SPEC-07 (toast/banner/modal + retry) + SPEC-05 (flag). Depende de FE-SALE-009..015.

**Approach (execution path):**
1) Skeleton do board (por coluna) + loading de listas/detalhe via `@journeyos/shared/ui-feedback`.
2) Empty states (estado vazio de listas + nao-encontrada); error state com retry manual em leituras.
3) UX do rollback: toast de falha do move + retorno do card; banner `ja-fechada` no detalhe.
4) Flag `sale.revenue-dashboard` off → omite rota `/sale/dashboard` + deep link.

**Non-goals:** a11y/perf do board (FE-SALE-021); lógica de DnD (FE-SALE-010).

**Layer(s):** frontend / `libs/sale/feature-*` + `libs/sale/styles` + `libs/sale/shell-entry` (flag gating)
**Bounded context:** sale

**Service execution spec(s):** `SPEC-07-error-handling.md` (toast/banner/modal/retry) · `SPEC-05` (flag)

**Architecture alignment:** `@journeyos/shared/ui-feedback`; module-pattern (flags); tags conforme lib.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-pipeline/src/lib/pipeline-skeleton.component.ts` (loading + rollback UX) — _MISSING_
- 🔲 estados empty/error nas pages de offer/purchase/attribution/dashboard — _MISSING_
- 🔲 `libs/sale/styles/src/lib/sale-theme.scss` (estados visuais) — _MISSING_
- 🔲 `libs/sale/shell-entry/src/lib/sale.feature-flags.ts` (gating efetivo do dashboard) — _MISSING_

**Tests**
- 🔲 `nx test` libs afetadas PASS — _MISSING_ · 🔲 `nx lint` PASS — _MISSING_

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:sale · priority:P7

**Acceptance criteria:**
- `npx nx test/lint/build` libs afetadas PASS
- Leitura falha → error state + "tentar novamente" (EARS SPEC-07); rollback do move com toast (EARS SPEC-07)
- Flag `sale.revenue-dashboard` off → rota/menu omitidos (EARS SPEC-05/SPEC-01)

**Dependencies:** FE-SALE-009, FE-SALE-010, FE-SALE-011, FE-SALE-012, FE-SALE-013, FE-SALE-014, FE-SALE-015
**Data impact:** Nenhum.
**API / Contract impact:** nenhum.
**Testing / Evidence required:** screenshots dos states (loading/empty/error + rollback toast).
**Risks / Notes:** R1 (rollback claro), G1 (dashboard degrada). Skeleton do board precede o perf (FE-SALE-021).
