## [FE-INTL-016] libs/intl/navigation — breadcrumbs + menu state

**Status:** REDUCED — pós-validação 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`libs/intl/navigation` alimenta `BreadcrumbItem[]` para as rotas do INTL (Inteligência ▸ Copilot/Conhecimento/Analítica ▸ …) e expõe o estado de menu derivado de RBAC.

**Context / Problem statement:**
- Navegação consistente. Fonte: SPEC-05 (05-state-and-data-flow §6).
- Bloqueia: e2e deep-link (FE-INTL-019).

**Approach (execution path):**
1) Mapear breadcrumbs por rota (incluindo `:titulo` dinâmico de conversa/nó).
2) Integrar com `NavigationService` (deep-links filtrados por permissão).

**Non-goals:** registro do descriptor (FE-INTL-003).

**Layer(s):** frontend / libs/intl/navigation
**Bounded context:** intl

**Service execution spec(s):** `frontend/05-state-and-data-flow.md` (§6 Breadcrumbs)

**Architecture alignment:** `type:domain` `scope:intl`.

**Implementation checklist (by file):**
- 🟡 `libs/intl/navigation/src/lib/intl-breadcrumbs.ts` — PARTIAL: só breadcrumbRoot stub em nav.config, sem mapa por rota
- 🔲 `libs/intl/navigation/src/lib/intl-nav.state.ts` — MISSING: sem estado de menu derivado de RBAC

**Tests**
- 🔲 `nx test intl-navigation` PASS — MISSING: sem testes de breadcrumb · 🔲 `nx lint` PASS — MISSING: não executado neste baseline

**Milestone:** Wave P6 / Navigation
**Labels:** type:feature · layer:frontend · scope:intl · priority:P6

**Acceptance criteria:**
- `npx nx test/lint/build intl-navigation` PASS
- Teste: breadcrumb de `/intl/copilot/:id` resolve com título da conversa.

**Dependencies:** FE-INTL-002
**API / Contract impact:** nenhum.
**Risks / Notes:** —
