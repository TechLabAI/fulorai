## [INT-FE-JRNY-003] Integração AccessDecision + NavigationService (menu/ações)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/2 itens

**Outcome:**
Menu, deep links e ações do JRNY filtrados por `AccessDecisionService` + `NavigationService` (permissões
`jrny.*`): publicar/arquivar/criar regra/criar jornada só aparecem com a permissão respectiva; deep
links omitidos sem permissão.

**Context / Problem statement:**
- A UI reflete RBAC, não decide; cobre o gating de menu/ações.
- Fonte: SPEC-05, SPEC-06. Cobre EARS #3/#27/#28/#33.

**Approach (execution path):**
1) Resolver visibilidade de cada deep link/ação por permissão.
2) Esconder ação sem permissão; negar rota via guard (FE-JRNY-017).

**Non-goals:** guards (FE-JRNY-017); breadcrumbs (FE-JRNY-018).

**Layer(s):** frontend / `libs/jrny/access` + `libs/jrny/navigation`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-05` · `SPEC-06` · `access-layer-contracts.md`

**Architecture alignment:** Access Layer; tag `type:domain`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/access/src/lib/jrny-access.facade.ts` (helpers `can(perm)`) (MISSING)

**Tests**
- 🔲 `nx test jrny-access` PASS (MISSING) · 🔲 `nx lint jrny-access` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:jrny · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build jrny-access` PASS
- Ações/menus gated por `jrny.*` (EARS #27/#28); deep links filtrados

**Dependencies:** FE-JRNY-001
**API / Contract impact:** consome `AccessDecision` (WRKS).
**Risks / Notes:** single source of truth de permissões = bundle BE.
