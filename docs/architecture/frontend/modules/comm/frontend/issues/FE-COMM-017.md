## [FE-COMM-017] Navigation + breadcrumbs

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
`comm.nav.config.ts` + estado de breadcrumb em `libs/comm/navigation` cobrindo as 7 rotas (SPEC-05 §6),
deep links filtrados por permissão via `NavigationService`.

**Context / Problem statement:**
- Navegação consistente e RBAC-aware. Fonte: SPEC-01/05. Depende: FE-COMM-002, INT-FE-COMM-004.

**Approach:**
1) Mapear breadcrumbs por rota (incluindo `:id` e Studio).
2) Deep links derivados de permissão.

**Non-goals:** menu ad-hoc no COMM (proibido — derivar de perms).

**Layer(s):** frontend / `libs/comm/navigation`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-01`, `SPEC-05` §6
**Architecture alignment:** tag `scope:comm` `type:domain`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/navigation/src/lib/comm-breadcrumbs.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-navigation` PASS · 🔲 [MISSING] `nx lint comm-navigation` PASS

**Milestone:** Wave P6 / Navigation
**Labels:** type:feature · layer:frontend · scope:comm · priority:P6

**Acceptance criteria:**
- Breadcrumbs corretos por rota; deep links sem permissão omitidos (C-05.5); `nx test/lint` PASS

**Dependencies:** FE-COMM-002, INT-FE-COMM-004
**API / Contract impact:** nenhum direto.
**Risks / Notes:** breadcrumb do detalhe usa id curto.
