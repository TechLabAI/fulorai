## [INT-FE-JRNY-004] Integração auth-session (bearer token)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/2 itens

**Outcome:**
`@journeyos/shared/auth-session` integrado: sessão/JWT disponível para o módulo; expiração/401
(`jrny.auth.token-invalido`) leva ao fluxo de login da Access Layer (sem tratamento local).

**Context / Problem statement:**
- Toda rota é autenticada; o token vem da sessão compartilhada.
- Fonte: SPEC-01 (auth), SPEC-07 (401). 

**Approach (execution path):**
1) Consumir `AuthSessionService` (token/estado de sessão).
2) 401 → delegar à Access Layer (redirect login).

**Non-goals:** UI de login (Shell/WRKS).

**Layer(s):** frontend / `libs/jrny/data-access` + `libs/jrny/access`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-01` · `SPEC-07`

**Architecture alignment:** Access Layer; tag conforme lib.

**Implementation checklist (by file):**
- 🚧 wiring de `AuthSessionService` no provider do módulo (BLOCKED: depende de INT-FE-JRNY-001 nao implementado; sem provider/import de auth-session em libs/jrny)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:jrny · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build` libs afetadas PASS
- 401 delega ao login da Access Layer (sem tratar localmente)

**Dependencies:** INT-FE-JRNY-001
**API / Contract impact:** JWT (WRKS JWKS).
**Risks / Notes:** não persistir token fora do auth-session storage.
