## [FE-COMM-002] COMM routes + lazy entry (COMM_ROUTES)

**Status:** REDUCED -- pos-validacao 2026-06-05
**Maturidade:** 28 -- Inicial
**Done/Total:** 1/5 itens
**GitHub:** [#TBD]

**Outcome:**
`comm.routes.ts` com `COMM_ROUTES[]` cobrindo as 7 rotas do SPEC-01, cada feature via `loadComponent`,
guards `[authGuard, empresaGuard, accessGuard(<perm>)]`, redirect `/comm → /comm/templates`. Entry lib
`@journeyos/comm` carregada pelo host `apps/comm` via `loadChildren`.

**Context / Problem statement:**
- Define o mapa de navegação interno do módulo. Fonte: SPEC-01. Depende: FE-COMM-001. Bloqueia: FE-COMM-009..016.

**Approach:**
1) Declarar `COMM_ROUTES` com `loadComponent` por feature page (catalog, editor, studio, routing, messages list/detail, channels).
2) Aplicar guards por rota conforme SPEC-01 (permissão de leitura da feature).
3) Redirect raiz `'' → templates`.

**Non-goals:** implementação das pages (P3); guards customizados (FE-COMM-016).

**Layer(s):** frontend / `libs/comm/shell-entry`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md`
**Architecture alignment:** lazy `loadComponent`; ADR-003; tag `scope:comm` `type:app`.

**Implementation checklist (by file):**
- ◐ [PARTIAL] `libs/comm/shell-entry/src/lib/comm.routes.ts`
- ✅ [DONE] `apps/comm/src/app/app.routes.ts` (host carrega `@journeyos/comm`)

**Tests**
- 🔲 [MISSING] `nx test comm-shell-entry` PASS · 🔲 [MISSING] `nx lint comm` PASS · 🔲 [MISSING] `nx build comm` PASS

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:comm · priority:P1

**Acceptance criteria:**
- `npx nx build comm` PASS; rotas resolvem para os componentes corretos (stubs até P3)
- Guards aplicados em todas as rotas `/comm/**`

**Dependencies:** FE-COMM-001
**API / Contract impact:** nenhum direto.
**Risks / Notes:** garantir que `:id` do editor/detalhe resolve antes de chamar a facade.
