## [INT-FE-WRKS-001] Integração auth-session (login/refresh/logout/restore)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
WRKS integrado a `@journeyos/shared/auth-session`: login OIDC, refresh (rotation), logout (blacklist) e restore, sem reimplementar fluxo de auth nem tocar storage diretamente.

**Context / Problem statement:**
- `feature-login` depende disto. Fonte: SPEC-06, `backend-api-cross-link.md`. Endpoints `/sessao/*`.

**Approach (execution path):**
1) Consumir a fachada `AuthSessionService` (login/refresh/logout/restore).
2) Estado de sessão exposto à UI via signal da Access Layer (read-only).
3) Refresh automático no interceptor; falha → redirect login.

**Non-goals:** UI de login (FE-WRKS-009).

**Layer(s):** frontend / integração (libs/wrks + @journeyos/shared/auth-session)
**Bounded context:** wrks

**Service execution spec(s):** SPEC-06; `contracts/backend-api-cross-link.md`

**Architecture alignment:** access-layer-contracts (zero storage direto).

**Implementation checklist (by file):**
- 🔲 wiring em `libs/wrks/feature-login` para `AuthSessionService` (MISSING)
- 🔲 testes de contrato da fachada (mocks) (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-login` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:wrks · priority:P4

**Acceptance criteria:**
- `npx nx test/lint` PASS · zero `localStorage` direto (check de aceite access-layer)

**Dependencies:** FE-WRKS-009
**API / Contract impact:** `/sessao/login|refresh|logout|restore`.
**Risks / Notes:** refresh é cookie httpOnly — FE não manipula o token diretamente.
