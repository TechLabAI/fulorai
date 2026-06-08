## [FE-SALE-019] Navigation / breadcrumbs (estado de navegação SALE)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 14 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/sale/navigation` deriva os breadcrumbs de SPEC-01 (`Pipeline`, `Pipeline > {titulo}`, `Ofertas`,
`Ofertas > {nome}`, `Compras`, `Compras > {idExterno}`, `Atribuição`, `Receita`) a partir do `data` das
rotas + params resolvidos, e mantém o estado de navegação do módulo sincronizado com o `NavigationService`
do Shell. Deep links de detalhe (`:id`) compõem o breadcrumb com o título resolvido.

**Context / Problem statement:**
- Breadcrumbs contextuais (com params) e sincronização do menu na navegação.
- Fonte: SPEC-01 (breadcrumbs) + SPEC-06 (NavigationService). Depende de FE-SALE-002, FE-SALE-004.

**Approach (execution path):**
1) Derivar breadcrumb de `route.data.breadcrumbs` + params (`:titulo`/`:nome`/`:idExterno`).
2) Publicar via `NavigationService` (raiz no `onActivate`, detalhe ao resolver `:id`).
3) Limpar ao sair do módulo (`onDeactivate`).

**Non-goals:** registro do módulo (FE-SALE-003/004); filtro de menu por permissão (INT-FE-SALE-004).

**Layer(s):** frontend / `libs/sale/navigation`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-01-route-map.md` (breadcrumbs) · `SPEC-06-shell-integration.md`

**Architecture alignment:** Access Layer (NavigationService); tag `scope:sale` `type:feature` (navigation).

**Implementation checklist (by file):**
- 🟡 `libs/sale/navigation/src/lib/sale-breadcrumb.state.ts` — _PARTIAL_
- 🔲 `libs/sale/navigation/src/lib/sale-breadcrumb.resolver.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-navigation` PASS — _MISSING_ · 🔲 `nx lint sale-navigation` PASS — _MISSING_

**Milestone:** Wave P6 / Navigation / breadcrumbs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P6

**Acceptance criteria:**
- `npx nx test/lint/build sale-navigation` PASS
- Breadcrumbs de detalhe compõem `{titulo}/{nome}/{idExterno}` resolvidos (SPEC-01)

**Dependencies:** FE-SALE-002, FE-SALE-004
**Data impact:** Nenhum.
**API / Contract impact:** nenhum.
**Testing / Evidence required:** teste de derivação de breadcrumb (lista + detalhe).
**Risks / Notes:** títulos de detalhe dependem do resumo (G2 titulo) — fallback id.
