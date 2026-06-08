## [FE-WRKS-013] feature-users — lista + convite

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/5 itens

**Outcome:**
`UsersListPageComponent` com tabela filtrável de usuários, toolbar com [Convidar] (visível se `can('wrks.usuario.criar')`) e `InviteUserDrawerComponent` (form email + papel + data_scope).

**Context / Problem statement:**
- Administração de equipe. Fonte: SPEC-01/02/03, `e2e/user-administration.feature`. Depende de FE-WRKS-005.

**Approach (execution path):**
1) Page lê `UsersFacade`; `UsersToolbarComponent` + `UsersTableComponent`/`UserRowComponent`.
2) `InviteUserDrawerComponent` (smart) + `InviteUserFormComponent`; submit → `invite()` (sem otimismo).
3) Tratar `409 wrks.usuario.duplicado` inline no campo email.

**Non-goals:** detalhe/edição de papel (FE-WRKS-014).

**Layer(s):** frontend / libs/wrks/feature-users
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01/02/03; `e2e/user-administration.feature`

**Architecture alignment:** standalone + OnPush; `type:feature` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/feature-users/src/lib/users-list.page.ts` (MISSING)
- 🔲 `libs/wrks/feature-users/src/lib/users-toolbar.component.ts` + `users-table.component.ts` + `user-row.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-users/src/lib/invite-user-drawer.component.ts` + `invite-user-form.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-users/src/lib/feature-users.routes.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-users` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build` PASS
- [Convidar] só aparece com permissão

**Dependencies:** FE-WRKS-005, FE-WRKS-008
**API / Contract impact:** `GET/POST /usuarios`, `POST /usuarios/{id}/empresas`.
**Risks / Notes:** lista média no MVP (sem virtual scroll, A-2).
