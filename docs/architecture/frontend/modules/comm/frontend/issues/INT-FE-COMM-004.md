## [INT-FE-COMM-004] Wiring NavigationService (menu/deep-links por permissão)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
Menu e deep links do COMM derivados de permissão via `NavigationService` (Access Layer); itens sem
`comm.*` correspondente não aparecem.

**Context / Problem statement:**
- Navegação RBAC-aware. Fonte: SPEC-05 (C-05.5). Depende: FE-COMM-001. Bloqueia: FE-COMM-017.

**Approach:**
1) Registrar deep links do contrato no `NavigationService`.
2) Filtrar por permissão.

**Non-goals:** breadcrumbs (FE-COMM-017).

**Layer(s):** frontend / `libs/comm/navigation` ↔ Access Layer
**Bounded context:** comm
**Service execution spec(s):** `SPEC-05` §6
**Architecture alignment:** tag `scope:comm` `type:domain`.

**Implementation checklist (by file):**
- ◐ [PARTIAL] wiring `NavigationService` em `comm.bootstrap.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-navigation` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:comm · priority:P4

**Acceptance criteria:**
- Deep links sem permissão omitidos (C-05.5); `nx test/lint` PASS

**Dependencies:** FE-COMM-001
**API / Contract impact:** nenhum direto.
**Risks / Notes:** sincronizar com `comm.contract.ts` deepLinks.
