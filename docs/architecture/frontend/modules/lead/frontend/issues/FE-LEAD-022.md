## [FE-LEAD-022] e2e Playwright + hardening (perf budget + a11y)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Implementação real dos specs Playwright em `apps/lead-e2e` a partir dos 9 `.feature` (substituindo os
stubs `test.fixme`), **mais** os cenários dos gaps do specs-validate (lead-not-found, profile-refetch,
redirect-root, empresa-guard). Perf budget do bundle do módulo + auditoria a11y.

**Context / Problem statement:**
- Fecha a wave de qualidade. Fonte: SPEC-08 + gaps G1/G5/G8/G9. Última onda do módulo.

**Approach (execution path):**
1) Implementar os 9 specs e2e (golden path, degradação, segmentação, regras, survey, LGPD, isolamento, RBAC, deep-link).
2) Adicionar cenários dos gaps (lead-not-found, profile-edit-refetch, redirect-root, empresa-guard).
3) Validar perf budget (lazy bundle) + axe nas telas-chave.

**Non-goals:** lógica de negócio (já nas features).

**Layer(s):** frontend / `apps/lead-e2e`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-08-e2e-scenarios.md`

**Architecture alignment:** Playwright (`@nx/playwright`); tag `scope:lead` `type:app`.

**Implementation checklist (by file):**
- 🔲 `apps/lead-e2e/src/specs/*.spec.ts` (9 fluxos implementados) — _MISSING (.feature só em docs/e2e; sem código de teste em apps/lead-e2e)_
- 🔲 specs adicionais dos gaps (lead-not-found, profile-refetch, redirect-root, empresa-guard) — _MISSING_
- 🔲 perf budget + axe — _MISSING_

**Tests**
- 🔲 `nx e2e lead-e2e` PASS · 🔲 `nx lint lead-e2e` PASS — _MISSING_

**Milestone:** Wave P9 / e2e + hardening
**Labels:** type:feature · layer:frontend · scope:lead · priority:P9

**Acceptance criteria:**
- `npx nx e2e lead-e2e` PASS (9 fluxos + gaps); perf budget respeitado; 0 violação axe crítica

**Dependencies:** FE-LEAD-009..016, FE-LEAD-019, FE-LEAD-020
**API / Contract impact:** consome toda a superfície `/api/v1/leads/**` (mock/fixtures em e2e).
**Risks / Notes:** execução real fica para o ciclo `/fe-implement` P9; aqui valem stubs descobríveis.
