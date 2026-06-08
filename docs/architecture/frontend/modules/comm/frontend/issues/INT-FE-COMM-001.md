## [INT-FE-COMM-001] Wiring access-http-base (HTTP + interceptors)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
COMM consome `@journeyos/shared/access-http-base` (`provideHttpBase`) com interceptors de JWT,
`X-Empresa-Id` e `X-Correlation-Id` + normalização de erro, base de todos os `*ApiService`.

**Context / Problem statement:**
- Pré-condição de toda chamada HTTP. Fonte: SPEC-04 (C-04.1). Bloqueia: FE-COMM-004..008.

**Approach:**
1) Garantir provider HTTP no bootstrap do módulo/app.
2) Validar interceptors aplicados nas chamadas COMM.

**Non-goals:** services de domínio (P2).

**Layer(s):** frontend / `libs/comm/data-access` ↔ Access Layer
**Bounded context:** comm
**Service execution spec(s):** `SPEC-04`, `access-layer-contracts.md`
**Architecture alignment:** data-access→shared/access-http-base; tag `scope:comm` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring `provideHttpBase` (app/module bootstrap)
- 🔲 [MISSING] smoke test de interceptor (header presente)

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:comm · priority:P4

**Acceptance criteria:**
- Chamadas COMM levam JWT + X-Empresa-Id + Correlation; `nx test/lint` PASS

**Dependencies:** FE-COMM-001
**API / Contract impact:** todos `/api/v1/**` do comm-service.
**Risks / Notes:** empresa vem do claim; `X-Empresa-Id` é debug/log.
