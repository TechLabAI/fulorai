## [FE-INTL-019] e2e Playwright — 7 specs + a11y dos badges

**Status:** REDUCED — pós-validação 2026-06-05
**Maturidade:** 28 — Inicial
**Done/Total:** 0/9 itens
**GitHub:** [#TBD]

**Outcome:**
Implementação dos 7 specs Playwright em `apps/intl-e2e` (a partir dos `.feature`): copilot-grounded, copilot-degraded, knowledge-curation, analytics-read, entitlement-denied, empresa-switch-isolation, deep-link; + a11y (badge nunca por cor isolada).

**Context / Problem statement:**
- Valida os fluxos de ponta a ponta. Fonte: SPEC-08 + e2e/*.feature.
- Última onda; depende de todas as anteriores.

**Approach (execution path):**
1) Implementar cada `.spec.ts` (remover `test.fixme`).
2) Asserts de fundamentação (chips presentes/ausentes por status).
3) Isolamento na troca de empresa; deep-link resolvendo guards.

**Non-goals:** novos fluxos além do SPEC-08.

**Layer(s):** frontend / apps/intl-e2e
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-08-e2e-scenarios.md`

**Architecture alignment:** Playwright; `type:e2e` `scope:intl`.

**Implementation checklist (by file):**
- 🟡 `apps/intl-e2e/src/copilot-grounded-answer.spec.ts` — PARTIAL: stub test.fixme compila, cenário ausente
- 🟡 `apps/intl-e2e/src/copilot-degraded-answer.spec.ts` — PARTIAL: stub test.fixme compila, cenário ausente
- 🟡 `apps/intl-e2e/src/knowledge-curation.spec.ts` — PARTIAL: stub test.fixme compila, cenário ausente
- 🟡 `apps/intl-e2e/src/analytics-read.spec.ts` — PARTIAL: stub test.fixme compila, cenário ausente
- 🟡 `apps/intl-e2e/src/entitlement-denied.spec.ts` — PARTIAL: stub test.fixme compila, cenário ausente
- 🟡 `apps/intl-e2e/src/empresa-switch-isolation.spec.ts` — PARTIAL: stub test.fixme compila, cenário ausente
- 🟡 `apps/intl-e2e/src/deep-link.spec.ts` — PARTIAL: stub test.fixme compila, cenário ausente

**Tests**
- 🔲 `nx e2e intl-e2e` PASS — MISSING: fluxos reais não implementados (fixme) · 🔲 `nx lint intl-e2e` PASS — MISSING: não executado neste baseline

**Milestone:** Wave P9 / e2e + hardening
**Labels:** type:e2e · layer:frontend · scope:intl · priority:P9

**Acceptance criteria:**
- `npx nx e2e intl-e2e` PASS (7 specs)
- a11y: status distinguível sem depender de cor.

**Dependencies:** FE-INTL-009..017, FE-INTL-020
**API / Contract impact:** depende dos endpoints estáveis (mock/fixtures no e2e).
**Risks / Notes:** R2/R4 cobertos por copilot-degraded + empresa-switch-isolation.
