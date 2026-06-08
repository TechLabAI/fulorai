## [FE-COMM-020] e2e Playwright + hardening (perf + a11y)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 28 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
Os 9 specs Playwright de `apps/comm-e2e` implementados a partir dos `.feature` (SPEC-08), executando os
fluxos reais; orçamento de bundle e checagem de a11y nas pages.

**Context / Problem statement:**
- Fecha o MVP com cobertura e2e. Fonte: SPEC-08. Depende: P3..P7.

**Approach:**
1) Implementar cada `.feature` (dispatch-tracking, idempotency, authoring, studio-degradation, routing, channel-security, empresa-isolation, entitlement-denied, deep-link).
2) Incluir cenários dos gaps: refresh manual (C-05.4) e parada do polling no destroy (C-06.4).
3) Perf budget (TTI/CLS) + a11y (axe) nas pages principais.

**Non-goals:** carga/stress; testes de provedor real.

**Layer(s):** frontend / `apps/comm-e2e`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-08-e2e-scenarios.md`, `e2e/*.feature`
**Architecture alignment:** tag `scope:comm` `type:e2e`.

**Implementation checklist (by file):**
- ◐ [PARTIAL] `apps/comm-e2e/src/*.spec.ts` (9 specs dos `.feature`) — arquivos existem como `test.fixme(...)` stubs com `// TODO: implementar os cenários`; nenhum cenário real implementado
- 🔲 [MISSING] cenários extras p/ C-05.4 (refresh manual) e C-06.4 (stop-polling no destroy)

**Tests**
- 🔲 [MISSING] `nx e2e comm-e2e` PASS · 🔲 [MISSING] perf budget OK · 🔲 [MISSING] axe sem violações críticas

**Milestone:** Wave P9 / e2e + hardening
**Labels:** type:feature · layer:frontend · scope:comm · priority:P9

**Acceptance criteria:**
- 9 fluxos passam; gaps C-05.4/C-06.4 cobertos; `nx e2e comm-e2e` PASS

**Dependencies:** FE-COMM-009..018
**API / Contract impact:** todos os endpoints `comm.*` (mockados no e2e).
**Risks / Notes:** polling determinístico no e2e (mock de avanço de estado).
