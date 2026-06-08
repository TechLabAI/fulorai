## [FE-WRKS-014] feature-users — detalhe + editor de papel (anti-escalonamento)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/3 itens

**Outcome:**
`UserDetailPageComponent` com `UserRoleEditorComponent`; opções de papel limitadas a `≤` papel do caller (UINV-4) e tratamento de `403 wrks.papel.escalonamento`.

**Context / Problem statement:**
- Alteração de papel/data_scope. Fonte: SPEC-02/03, `e2e/user-administration.feature` (cenário anti-escalonamento). Depende de FE-WRKS-005.

**Approach (execution path):**
1) Page lê `UserDetailFacade.user()/assignablePapeis()`.
2) Editor mostra só papéis permitidos; submit → `changeRole()` (sem otimismo).
3) Erro `403` → inline no editor.

**Non-goals:** exclusão de usuário (soft-delete via toggle na lista).

**Layer(s):** frontend / libs/wrks/feature-users
**Bounded context:** wrks

**Service execution spec(s):** SPEC-02/03; SPEC-07; `e2e/user-administration.feature`

**Architecture alignment:** standalone + OnPush; `type:feature` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/feature-users/src/lib/user-detail.page.ts` (MISSING)
- 🔲 `libs/wrks/feature-users/src/lib/user-role-editor.component.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-users` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build` PASS
- UI nunca oferece papel acima do caller; servidor é a decisão final

**Dependencies:** FE-WRKS-005, FE-WRKS-008
**API / Contract impact:** `PUT /usuarios/{id}`, `POST /usuarios/{id}/empresas`.
**Risks / Notes:** UINV-4 é reflexo client-side; enforcement é BE (INV-1).
