## [FE-ASST-020] e2e Playwright + hardening (perf + a11y)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 28 -- Inicial
**Done/Total:** 0/8 itens
**GitHub:** [#TBD]

**Outcome:**
Os 6 specs Playwright de `apps/asst-e2e` implementados a partir dos `.feature` (golden path,
degradação do Studio, aprovação, isolamento multi-empresa, RBAC, deep link), + budget de performance
e checagem básica de a11y.

**Context / Problem statement:**
- Fecha o MVP com validação de fluxo real. Fonte: SPEC-08, `e2e/*.feature`. Depende de FE-ASST-009..018.
- Bloqueia: — (último da cadeia).

**Approach (execution path):**
1) Implementar cada `*.spec.ts` (remover `test.fixme`) cobrindo os cenários Gherkin.
2) Cobrir explicitamente UINV-4 (imutabilidade), UINV-7 (degradação), UINV-8 (isolamento), UINV-2 (RBAC).
3) Budget de bundle/TTI do catálogo; a11y (foco, labels, contraste via tokens).

**Non-goals:** novos fluxos; mudanças de contrato.

**Layer(s):** frontend / `apps/asst-e2e`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-08-e2e-scenarios.md` · `e2e/*.feature`

**Architecture alignment:** Playwright; `scope:asst type:e2e`.

**Implementation checklist (by file):**
- ◐ [PARTIAL] `apps/asst-e2e/src/asset-lifecycle.spec.ts`
- ◐ [PARTIAL] `apps/asst-e2e/src/asset-studio-degradation.spec.ts`
- ◐ [PARTIAL] `apps/asst-e2e/src/approval-workflow.spec.ts`
- ◐ [PARTIAL] `apps/asst-e2e/src/empresa-isolation.spec.ts`
- ◐ [PARTIAL] `apps/asst-e2e/src/entitlement-denied.spec.ts`
- ◐ [PARTIAL] `apps/asst-e2e/src/deep-link.spec.ts`

**Tests**
- 🔲 [MISSING] `nx e2e asst-e2e` PASS · 🔲 [MISSING] `nx lint asst-e2e` PASS

**Milestone:** Wave P9 / e2e + hardening
**Labels:** type:feature · layer:frontend · scope:asst · priority:P9

**Acceptance criteria:**
- 6 specs verdes; UINV-2/4/7/8 cobertas; budget de perf respeitado

**Dependencies:** FE-ASST-009..018
**API / Contract impact:** consome toda a superfície `/api/v1/assets/**` (mock/stub no e2e).
**Risks / Notes:** isolamento multi-empresa é o teste crítico de LGPD (R-2).
