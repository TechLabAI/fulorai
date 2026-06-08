## [FE-WRKS-005] UsuarioApiService + UsersFacade + UserDetailFacade

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/6 itens

**Outcome:**
`UsuarioApiService` + `UsersFacade` (lista/convite/toggle) + `UserDetailFacade` (detalhe/alterar papel) sobre `/api/v1/iam/usuarios`, com signals.

**Context / Problem statement:**
- Gestão de usuários (P3) depende destes. Fonte: SPEC-04 (Usuario). Bloqueia FE-WRKS-013/014.

**Approach (execution path):**
1) `UsuarioApiService`: list, get, create, update, delete, `associar` (papel + data_scope).
2) `UsersFacade`: `users()`, `filter()`, `loading()`, `error()`, `invite()`, `toggle()` (sem otimismo).
3) `UserDetailFacade`: `user()`, `changeRole()`; `assignablePapeis` derivado do caller.

**Non-goals:** UI (P3); enforcement de escalonamento (é BE; UI só restringe opções).

**Layer(s):** frontend / libs/wrks/data-access
**Bounded context:** wrks

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Usuario), SPEC-03 (VMs)

**Architecture alignment:** ADR-002; `type:data-access` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/data-access/src/lib/usuario-api.service.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/users.facade.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/user-detail.facade.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/dtos/usuario.dto.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-data-access` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:wrks · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build wrks-data-access` PASS
- Mutações sensíveis (convite/papel) sem otimismo

**Dependencies:** FE-WRKS-002 · INT-FE-WRKS-004
**API / Contract impact:** `/usuarios`, `/usuarios/{id}`, `/usuarios/{id}/empresas`.
**Risks / Notes:** mapear `409 wrks.usuario.duplicado` e `403 wrks.papel.escalonamento` (FE-WRKS-008).
