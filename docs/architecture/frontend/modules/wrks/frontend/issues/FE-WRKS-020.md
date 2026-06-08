## [FE-WRKS-020] e2e Playwright + hardening (token/idle, a11y, perf budget)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** REDUCED — pos-validacao 2026-06-05
**Maturidade:** 35 — Inicial
**Done/Total:** 0/7 itens (5 PARTIAL)

**Outcome:**
Specs Playwright em `apps/wrks-e2e` (1 por `.feature` do SPEC-08) executando os fluxos reais, + hardening: expiração de token / sessão inativa, a11y básica e perf budget do bundle.

**Context / Problem statement:**
- Fecha o MVP com garantias. Fonte: SPEC-08, 06-risks. Depende de todas as features + integrações.

**Approach (execution path):**
1) Implementar 5 specs (login-empresa-select, user-administration, empresa-switch-isolation, entitlement-denied, deep-link).
2) Hardening: refresh em expiração, idle timeout, redirect preservando returnUrl.
3) a11y (foco/labels) + budget de bundle do WRKS.

**Non-goals:** cenários de outros módulos.

**Layer(s):** frontend / apps/wrks-e2e + hardening transversal
**Bounded context:** wrks

**Service execution spec(s):** SPEC-08; `e2e/*.feature`; 06-risks

**Architecture alignment:** specs espelham os `.feature`; budget via Nx.

**Implementation checklist (by file):**
- 🟡 `apps/wrks-e2e/src/specs/login-and-empresa-select.spec.ts` (PARTIAL — existe em `apps/wrks-e2e/src/login-and-empresa-select.spec.ts`; só `test.fixme` com TODO, sem cenário real)
- 🟡 `apps/wrks-e2e/src/specs/user-administration.spec.ts` (PARTIAL — existe em `apps/wrks-e2e/src/user-administration.spec.ts`; `test.fixme`/TODO)
- 🟡 `apps/wrks-e2e/src/specs/empresa-switch-isolation.spec.ts` (PARTIAL — existe em `apps/wrks-e2e/src/empresa-switch-isolation.spec.ts`; `test.fixme`/TODO)
- 🟡 `apps/wrks-e2e/src/specs/entitlement-denied.spec.ts` (PARTIAL — existe em `apps/wrks-e2e/src/entitlement-denied.spec.ts`; `test.fixme`/TODO)
- 🟡 `apps/wrks-e2e/src/specs/deep-link.spec.ts` (PARTIAL — existe em `apps/wrks-e2e/src/deep-link.spec.ts`; `test.fixme`/TODO; `example.spec.ts` default ainda presente; hardening token/idle/a11y/budget ausente)

**Tests**
- 🔲 `nx e2e wrks-e2e` PASS (MISSING — todos os cenários em `test.fixme`) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P9 / e2e + Hardening
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P9

**Acceptance criteria:**
- 5 specs descobríveis e PASS; isolamento cross-empresa verificado
- `npx nx e2e wrks-e2e` PASS; perf budget respeitado

**Dependencies:** FE-WRKS-009..018, INT-FE-WRKS-001..006
**API / Contract impact:** todos os `/api/v1/iam/**` do MVP.
**Risks / Notes:** gate A5 (e2e-validate) só lista/compila; execução real é aqui.
