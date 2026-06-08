## [FE-SALE-023] e2e Playwright (8 specs) + hardening (perf budget + a11y)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/11 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Os 8 specs Playwright (de `e2e/*.feature`) implementados e verdes em `apps/sale-e2e`:
`pipeline-kanban-move`, `opportunity-win-loss`, `offer-versioning`, `purchase-attribution-breakdown`,
`attribution-model-activate`, `empresa-switch-isolation`, `entitlement-denied`, `deep-link`. Orçamento de
bundle do SALE respeitado (CDK DragDrop só no feature-pipeline; chart de funil leve — ADR-005/R3);
auditoria a11y (incl. DnD por teclado) dos fluxos principais. Cobre o golden path "Compra confirmada".

**Context / Problem statement:**
- Fecha o MVP com os fluxos executáveis; A5 deixou os specs descobríveis (`--list`).
- Fonte: SPEC-08 + `e2e/*.feature` (8 arquivos). Depende das features P3 + guards/flags.

**Approach (execution path):**
1) Implementar steps dos 8 `.feature` (kanban-move/rollback, win-loss/motivo, offer-versioning,
   purchase-breakdown, attribution-activate, empresa-switch, entitlement-denied, deep-link/flag).
2) Verificar Web Vitals/bundle budget (CDK local; chart leve); a11y (axe) + DnD por teclado.

**Non-goals:** novos cenários além do SPEC-08.

**Layer(s):** frontend / `apps/sale-e2e`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-08-e2e-scenarios.md` · `e2e/*.feature`

**Architecture alignment:** Playwright; tag `scope:sale` `type:e2e`.

**Implementation checklist (by file):**
- 🔲 `apps/sale-e2e/src/specs/pipeline-kanban-move.spec.ts` — _MISSING_
- 🔲 `apps/sale-e2e/src/specs/opportunity-win-loss.spec.ts` — _MISSING_
- 🔲 `apps/sale-e2e/src/specs/offer-versioning.spec.ts` — _MISSING_
- 🔲 `apps/sale-e2e/src/specs/purchase-attribution-breakdown.spec.ts` — _MISSING_
- 🔲 `apps/sale-e2e/src/specs/attribution-model-activate.spec.ts` — _MISSING_
- 🔲 `apps/sale-e2e/src/specs/empresa-switch-isolation.spec.ts` — _MISSING_
- 🔲 `apps/sale-e2e/src/specs/entitlement-denied.spec.ts` — _MISSING_
- 🔲 `apps/sale-e2e/src/specs/deep-link.spec.ts` — _MISSING_
- 🔲 perf/a11y checks — _MISSING_

**Tests**
- 🔲 `nx e2e sale-e2e` PASS — _MISSING_ · 🔲 `nx lint sale-e2e` PASS — _MISSING_

**Milestone:** Wave P9 / e2e + hardening
**Labels:** type:e2e · layer:frontend · scope:sale · priority:P9

**Acceptance criteria:**
- `npx nx e2e sale-e2e` PASS (8 specs)
- Bundle dentro do budget (CDK local; chart leve); a11y sem violações críticas (incl. DnD teclado)

**Dependencies:** FE-SALE-010..020
**API / Contract impact:** consome toda a superfície SALE.
**Data impact:** Nenhum.
**Testing / Evidence required:** relatório Playwright (8 specs verdes); relatório axe; medição de bundle.
**Risks / Notes:** kanban-move/rollback e attribution-breakdown são os fluxos de maior risco (R1/R4).
