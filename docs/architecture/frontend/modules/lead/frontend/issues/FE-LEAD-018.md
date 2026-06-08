## [FE-LEAD-018] navigation: breadcrumbs + menu state

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 12 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/lead/navigation` alimenta `BreadcrumbItem[]` para as rotas do SPEC-01 (Leads / {nome} / Maturity
Score / Segmentos / Surveys / Regras) e integra o menu lateral filtrado por permissão (`NavigationService`).

**Context / Problem statement:**
- Navegação consistente + breadcrumbs por rota. Fonte: SPEC-01 (§breadcrumbs), `05` §6.

**Approach (execution path):**
1) Mapear breadcrumbs por rota (incluindo `:id`/`:nome` resolvido).
2) Integrar deep links do contrato com `NavigationService` (filtro por permissão).
3) Limpar estado de navegação no `onDeactivate` (sem breadcrumb stale).

**Non-goals:** layout do Shell; lógica de permissão (Access Layer).

**Layer(s):** frontend / `libs/lead/navigation`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-01` · `05-state-and-data-flow.md` §6

**Architecture alignment:** Signals; tag `scope:lead` `type:domain`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/navigation/src/lib/lead-breadcrumbs.ts` — _PARTIAL (apenas `breadcrumbRoot:'Leads'` em shell-entry/lead.nav.config.ts; mapa por rota ausente)_
- 🔲 `libs/lead/navigation/src/lib/lead-nav.state.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-navigation` PASS · 🔲 `nx lint lead-navigation` PASS — _MISSING_

**Milestone:** Wave P6 / Navigation
**Labels:** type:feature · layer:frontend · scope:lead · priority:P6

**Acceptance criteria:**
- `npx nx test/lint/build lead-navigation` PASS
- Breadcrumbs corretos por rota; menu reflete apenas deep links permitidos

**Dependencies:** FE-LEAD-002, INT-FE-LEAD-003
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** breadcrumb de `:id` depende do nome do lead (resolver no detalhe).
