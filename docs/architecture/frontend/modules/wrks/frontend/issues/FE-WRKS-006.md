## [FE-WRKS-006] PapelApiService + RbacFacade (read-only)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
`PapelApiService` + `RbacFacade` cobrindo `GET /papeis` e `GET /papeis/{codigo}/permissoes` (read-only), alimentando o RBAC viewer.

**Context / Problem statement:**
- RBAC viewer (FE-WRKS-015) lê papéis e bundles. Fonte: SPEC-04 (Papel). MVP é só leitura.

**Approach (execution path):**
1) `PapelApiService`: `list()`, `getPermissoes(codigo)`.
2) `RbacFacade`: `roles()`, `selected()`, `loading()`, `error()`, `select(codigo)`.

**Non-goals:** editar bundle (`PUT /papeis/.../permissoes` fora do MVP).

**Layer(s):** frontend / libs/wrks/data-access
**Bounded context:** wrks

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Papel)

**Architecture alignment:** ADR-002; `type:data-access` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/data-access/src/lib/papel-api.service.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/rbac.facade.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-data-access` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:wrks · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build wrks-data-access` PASS

**Dependencies:** FE-WRKS-002 · INT-FE-WRKS-004
**API / Contract impact:** `GET /papeis`, `GET /papeis/{codigo}/permissoes` (perm `wrks.papel.read`).
**Risks / Notes:** cache de sessão aceitável (papéis mudam raramente); invalidar em `modelo.acesso.alterado`.
