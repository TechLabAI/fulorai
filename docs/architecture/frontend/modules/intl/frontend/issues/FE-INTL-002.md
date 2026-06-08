## [FE-INTL-002] intl.routes.ts — rotas lazy + guards + IntlRootComponent

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`INTL_ROUTES` com as 7 rotas do SPEC-01 via `loadComponent`, cada uma com `authGuard + empresaGuard + accessGuard(<perm>)`, `title` e `data.breadcrumb`; `IntlRootComponent` redireciona `/intl` → primeira rota permitida.

**Context / Problem statement:**
- O scaffold gera `INTL_ROUTES` vazio. Fonte: SPEC-01.
- Bloqueia: FE-INTL-009..014 (pages carregadas por estas rotas).

**Approach (execution path):**
1) Declarar as 7 rotas (`/intl`, copilot, copilot/:id, knowledge, knowledge/novo, knowledge/:id, analytics).
2) Anexar guards + `title` + `breadcrumb` por rota.
3) `IntlRootComponent` usa `NavigationService` para redirecionar à primeira permitida.

**Non-goals:** implementação das pages (P3); guards custom (FE-INTL-015).

**Layer(s):** frontend / libs/intl/shell-entry
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md`

**Architecture alignment:** ADR-003; lazy `loadComponent`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/shell-entry/src/lib/intl.routes.ts` — MISSING: INTL_ROUTES array vazio (placeholder)
- 🔲 `libs/intl/shell-entry/src/lib/intl-root.component.ts` — MISSING: componente não existe

**Tests**
- 🔲 `nx test intl-shell-entry` PASS — MISSING: testes não rodados · 🔲 `nx lint` PASS — MISSING: lint não rodado

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:intl · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build intl-shell-entry` PASS
- Todas as rotas resolvem para um `loadComponent` válido (stub até P3).

**Dependencies:** FE-INTL-001
**API / Contract impact:** nenhum.
**Risks / Notes:** guards reais vêm da Access Layer (INT-FE-INTL-003); até lá, usar stubs que permitem.
