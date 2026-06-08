## [INT-FE-ASST-001] Integração access-http-base (HttpClient + interceptors)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
`libs/asst/data-access` consome `@journeyos/shared/access-http-base` para todo HTTP (`/api/v1/assets`),
com interceptors de `X-Empresa-Id`, Correlation e normalização de erro ativos.

**Context / Problem statement:**
- Precondição de todos os services. Fonte: SPEC-04, `04 §4`. Depende do shared (Wave 0). Bloqueia: FE-ASST-004..007.

**Approach (execution path):**
1) Configurar `provideHttpBase` no escopo do módulo (ou herdado do Shell).
2) Garantir base URL + injeção de `X-Empresa-Id`/Correlation nos services ASST.
3) Verificar normalização de erro chega como `ProblemDetail`.

**Non-goals:** mapeamento de erro de domínio (FE-ASST-008).

**Layer(s):** frontend / `libs/asst/data-access`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-04` · `04-frontend-architecture-direction.md §4`

**Architecture alignment:** `data-access → shared/access-http-base`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring de `provideHttpBase` / `HttpClient` nos `*ApiService` do ASST

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS · 🔲 [MISSING] `nx lint asst-data-access` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:asst · priority:P4

**Acceptance criteria:**
- Requests do ASST levam `X-Empresa-Id`/Correlation; erro chega normalizado

**Dependencies:** shared/access-http-base (Wave 0)
**API / Contract impact:** todos os endpoints `/api/v1/assets/**`.
**Risks / Notes:** R-1 (contrato BE a estabilizar).
