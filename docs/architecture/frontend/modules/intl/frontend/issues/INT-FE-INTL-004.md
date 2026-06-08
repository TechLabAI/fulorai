## [INT-FE-INTL-004] Integração — access-http-base (HttpClient + interceptors + correlation)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
INTL consome `@journeyos/shared/access-http-base`: os `*ApiService` usam o `HttpClient` provido por `provideHttpBase`, com interceptors de `Authorization`, `X-Empresa-Id`, `X-Correlation-Id` e normalização de erro.

**Context / Problem statement:**
- Base de toda chamada HTTP do INTL. Fonte: SPEC-04 + backend-api-cross-link.
- Bloqueia: FE-INTL-004, 006, 007 e demais INT.

**Approach (execution path):**
1) Garantir que os services injetam o HttpClient correto (sem `HttpClientModule` próprio).
2) Validar propagação de `X-Correlation-Id`.

**Non-goals:** mapeamento de erro de domínio (FE-INTL-008).

**Layer(s):** frontend / libs/intl/data-access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-04` · `contracts/backend-api-cross-link.md`

**Architecture alignment:** consome `@journeyos/shared/access-http-base`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 wiring de provider/serviços em `libs/intl/data-access` — MISSING: sem provideHttpBase/ApiServices

**Tests**
- 🔲 `nx test intl-data-access` PASS — MISSING: sem teste de correlation-id · 🔲 `nx lint` PASS — MISSING: não executado nesta baseline

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:intl · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS
- Correlation id presente nas requisições.

**Dependencies:** FE-INTL-002
**API / Contract impact:** headers de transporte.
**Risks / Notes:** pré-requisito das demais INT — fazer primeiro na P4.
