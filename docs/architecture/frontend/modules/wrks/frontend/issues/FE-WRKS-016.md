## [FE-WRKS-016] Access guards (empresaGuard + accessGuard) em libs/wrks/access

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Guards do WRKS em `libs/wrks/access`: `empresaGuard` (exige empresa ativa) e `accessGuard(<perm>)` (delega a `AccessDecisionService.can`), aplicados conforme matriz do SPEC-01.

**Context / Problem statement:**
- Rotas pós-contexto precisam de proteção. Fonte: SPEC-01, access-layer-contracts. Depende de FE-WRKS-002, INT-FE-WRKS-003.

**Approach (execution path):**
1) `empresaGuard`: redireciona a `/empresa-select` se não houver contexto.
2) `accessGuard(perm)`: nega + redireciona/oculta se `!can(perm)`.
3) `authGuard` é da Access Layer (reuso).

**Non-goals:** authGuard global (shared).

**Layer(s):** frontend / libs/wrks/access
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01; `access-layer-contracts.md`

**Architecture alignment:** guards usam saídas de `AccessDecisionService` (check de aceite).

**Implementation checklist (by file):**
- 🔲 `libs/wrks/access/src/lib/empresa.guard.ts` (MISSING)
- 🔲 `libs/wrks/access/src/lib/access.guard.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-access` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P5 / Access guards
**Labels:** type:domain · layer:frontend · scope:wrks · priority:P5

**Acceptance criteria:**
- `/wrks/users` negado para SDR; redireciona deep link sem sessão (`deep-link.feature`)
- `npx nx test/lint/build wrks-access` PASS

**Dependencies:** FE-WRKS-002, INT-FE-WRKS-003
**API / Contract impact:** consome AccessDecision.
**Risks / Notes:** distinguir rotas pré vs pós-contexto (UINV-1).
