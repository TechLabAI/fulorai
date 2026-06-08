## [FE-JRNY-022] e2e Playwright + hardening (perf budget + a11y)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 14 — Inicial
**Done/Total:** 0/4 itens (1 PARTIAL)

**Outcome:**
Os 7 specs Playwright (de `e2e/*.feature`) implementados e verdes em `apps/jrny-e2e`; orçamento de
bundle do JRNY respeitado (sem lib de canvas — ADR-005); auditoria a11y dos fluxos principais. Cobre os
golden paths A (autoria) e B (auditoria) + edge cases.

**Context / Problem statement:**
- Fecha o MVP com os fluxos executáveis; A5 deixou os specs descobríveis (`--list`).
- Fonte: SPEC-08 + `e2e/*.feature`.

**Approach (execution path):**
1) Implementar steps dos 7 `.feature` (authoring, publish-guards, routing-rules, decision-log,
   empresa-switch, entitlement-denied, deep-link).
2) Verificar Web Vitals/bundle budget; a11y (axe) nos fluxos.

**Non-goals:** novos cenários além do SPEC-08.

**Layer(s):** frontend / `apps/jrny-e2e`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-08-e2e-scenarios.md` · `e2e/*.feature`

**Architecture alignment:** Playwright; tag `type:e2e` `scope:jrny`.

**Implementation checklist (by file):**
- 🟡 `apps/jrny-e2e/src/specs/*.spec.ts` (7 specs) (PARTIAL) (os 7 .spec.ts existem com tags type:e2e corretas, porem todos sao `test.fixme` + TODO placeholders do gate A5 — nenhum fluxo Gherkin implementado; example.spec.ts e stub Nx default)
- 🔲 perf/a11y checks (MISSING)

**Tests**
- 🔲 `nx e2e jrny-e2e` PASS (MISSING) · 🔲 `nx lint jrny-e2e` PASS (MISSING)

**Milestone:** Wave P9 / e2e + hardening
**Labels:** type:e2e · layer:frontend · scope:jrny · priority:P9

**Acceptance criteria:**
- `npx nx e2e jrny-e2e` PASS (7 specs)
- Bundle dentro do budget; a11y sem violações críticas

**Dependencies:** FE-JRNY-009..020
**API / Contract impact:** consome toda a superfície JRNY.
**Risks / Notes:** decision-log + publish-guards são os fluxos de maior risco (R1/R3).
