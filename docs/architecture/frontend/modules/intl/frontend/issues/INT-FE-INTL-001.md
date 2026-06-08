## [INT-FE-INTL-001] Integração — auth-session (bearer token)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
INTL consome `@journeyos/shared/auth-session` para o bearer token em todas as chamadas (via interceptor de `access-http-base`). Nenhuma leitura de `localStorage`/JWT decodificado nas features.

**Context / Problem statement:**
- Access Layer alimentada por WRKS. Fonte: SPEC-04 + access-layer-contracts.
- Bloqueia: chamadas autenticadas (P2).

**Approach (execution path):**
1) Garantir que data-access usa o `HttpClient` provido por `provideHttpBase` (bearer automático).
2) Proibir acesso direto a token nas features (ESLint boundary).

**Non-goals:** login/OIDC (é do WRKS).

**Layer(s):** frontend / libs/intl/data-access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` · `access-layer-contracts.md`

**Architecture alignment:** consome `@journeyos/shared/auth-session`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 wiring em `libs/intl/data-access` (sem token manual) — MISSING: só placeholder, sem wiring

**Tests**
- 🔲 `nx test intl-data-access` PASS — MISSING: sem testes de integração · 🔲 `nx lint` PASS (boundary) — MISSING: não executado nesta baseline

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:intl · priority:P4

**Acceptance criteria:**
- `npx nx test/lint intl-data-access` PASS
- Nenhuma feature lê token diretamente.

**Dependencies:** INT-FE-INTL-004
**API / Contract impact:** header `Authorization` (interceptor).
**Risks / Notes:** —
