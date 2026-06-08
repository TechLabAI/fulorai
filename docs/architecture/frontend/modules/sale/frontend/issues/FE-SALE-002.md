## [FE-SALE-002] Shell-entry routes + lazy loadChildren (sale.routes.ts)

**Status (validação):** REDUCED — pós-validação 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 1/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/sale/shell-entry/sale.routes.ts` define `SALE_ROUTES`: raiz `/sale` redireciona a
`/sale/pipeline` (`pathMatch: 'full'`); 8 rotas lazy (`loadComponent`) para pipeline, opportunities/:id,
offers, offers/:id, purchases, purchases/:id, attribution, dashboard — cada uma com `data` (title,
breadcrumbs, permissionRequired) e cadeia de guards de SPEC-01. Exportado via importPath `@journeyos/sale`.

**Context / Problem statement:**
- O Shell carrega o módulo lazy via `@journeyos/sale`; cada rota é pós-contexto (sessão + empresa).
- Fonte: SPEC-01 (tabela mestre). Depende de FE-SALE-001 (contract). Bloqueia: features P3, FE-SALE-018/019.

**Approach (execution path):**
1) Declarar `SALE_ROUTES` com redirect raiz `/sale → /sale/pipeline`.
2) Mapear cada rota a `loadComponent` da feature lib correspondente + `data` (title/breadcrumbs/permissionRequired).
3) Anexar guards `authGuard`, `empresaGuard`, `accessGuard('sale.<perm>')` por rota.
4) Rota `/sale/dashboard` condicionada à flag `sale.revenue-dashboard`.

**Non-goals:** implementar guards (FE-SALE-018); páginas (P3).

**Layer(s):** frontend / `libs/sale/shell-entry`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-01-route-map.md` (tabela mestre + detalhe por rota)

**Architecture alignment:** ADR-003 lazy entry; `loadComponent` por rota; tag `scope:sale` `type:domain`.

**Implementation checklist (by file):**
- 🟡 `libs/sale/shell-entry/src/lib/sale.routes.ts` — _PARTIAL: `SALE_ROUTES = []` (sem redirect raiz, sem loadComponent, sem data/guards)_
- ✅ `libs/sale/shell-entry/src/index.ts` (export `SALE_ROUTES`, `SALE_MODULE_DESCRIPTOR`) — _DONE: ambos exportados via barrel_

**Tests**
- 🔲 `nx test sale-shell-entry` PASS — _MISSING_ · 🔲 `nx lint sale-shell-entry` PASS — _MISSING_

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:sale · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build sale-shell-entry` PASS
- `/sale` redireciona a `/sale/pipeline` (EARS SPEC-01 #1); todas as rotas lazy via `@journeyos/sale` (EARS #7)
- `data.permissionRequired` por rota igual à SPEC-01

**Dependencies:** FE-SALE-001
**Data impact:** Nenhum.
**API / Contract impact:** nenhum direto (guards consultam Access Layer).
**Testing / Evidence required:** teste de roteamento (redirect + lazy); checagem de `data` por rota.
**Risks / Notes:** dashboard gated por flag — rota omitida quando `sale.revenue-dashboard` off (FE-SALE-015/020).
