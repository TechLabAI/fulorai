## [FE-WRKS-009] feature-login (login + OIDC callback)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
`feature-login` com `LoginPageComponent` e `OidcCallbackPageComponent`, integrando `@journeyos/shared/auth-session` (redirect → exchange → authenticated), com estados idle/redirecting/exchanging/error.

**Context / Problem statement:**
- Entrada do golden path. Fonte: SPEC-01/02/08. Depende de INT-FE-WRKS-001 (auth-session).

**Approach (execution path):**
1) `LoginPageComponent` (smart) + `LoginCardComponent` (output login()).
2) `OidcCallbackPageComponent` processa o `code`; nada protegido renderiza até `authenticated`.
3) Pós-login: rotear p/ `/empresa-select` (N>1) ou auto-skip (N=1) ou "sem acesso" (N=0).

**Non-goals:** seleção de empresa (FE-WRKS-010); MFA.

**Layer(s):** frontend / libs/wrks/feature-login
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01, SPEC-02, `e2e/login-and-empresa-select.feature`

**Architecture alignment:** standalone + OnPush; `type:feature` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/feature-login/src/lib/login.page.ts` + `login-card.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-login/src/lib/oidc-callback.page.ts` + `auth-progress.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-login/src/lib/feature-login.routes.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-login` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build wrks-feature-login` PASS
- Sem flash de tela protegida durante callback

**Dependencies:** FE-WRKS-002 · INT-FE-WRKS-001
**API / Contract impact:** `/sessao/login`, `/sessao/restore` (via auth-session).
**Risks / Notes:** preservar `returnUrl` no redirect.
