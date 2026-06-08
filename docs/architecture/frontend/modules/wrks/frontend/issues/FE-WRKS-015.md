## [FE-WRKS-015] feature-rbac-viewer (papéis × permissões, read-only)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
`RbacViewerPageComponent` listando papéis canônicos e o bundle de permissões de cada um (somente leitura), atrás da flag `wrks.rbac-viewer`.

**Context / Problem statement:**
- Transparência de acesso para admin. Fonte: SPEC-01/02/03. Depende de FE-WRKS-006.

**Approach (execution path):**
1) Page lê `RbacFacade.roles()/selected()`.
2) `RoleListComponent` + `RolePermissionsComponent` (read-only).
3) Esconder via flag quando desabilitada.

**Non-goals:** editar bundle (fora do MVP).

**Layer(s):** frontend / libs/wrks/feature-rbac-viewer
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01/02/03

**Architecture alignment:** standalone + OnPush; `type:feature` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/feature-rbac-viewer/src/lib/rbac-viewer.page.ts` (MISSING)
- 🔲 `libs/wrks/feature-rbac-viewer/src/lib/role-list.component.ts` + `role-permissions.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-rbac-viewer/src/lib/feature-rbac-viewer.routes.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-rbac-viewer` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build` PASS
- Read-only garantido (nenhuma mutação exposta)

**Dependencies:** FE-WRKS-006
**API / Contract impact:** `GET /papeis`, `GET /papeis/{codigo}/permissoes`.
**Risks / Notes:** consistente com `shared/rbac/papeis.md`.
