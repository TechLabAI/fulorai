## [FE-WRKS-002] Module module + routes (lazy, split pré/pós-contexto)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** REDUCED — pos-validacao 2026-06-05
**Maturidade:** 35 — Inicial
**Done/Total:** 1/4 itens

**Outcome:**
`wrks.module.ts` (único NgModule, entry lazy) e `wrks.routes.ts` com a árvore de rotas do SPEC-01, com guards corretos por rota (rotas pré-contexto sem `empresaGuard`; pós-contexto com `authGuard + empresaGuard + accessGuard(<perm>)`).

**Context / Problem statement:**
- WRKS hospeda rotas pré-contexto (`/login`, `/auth/callback`, `/empresa-select`) e pós-contexto (`/wrks/**`).
- Fonte: SPEC-01. Depende de FE-WRKS-001. Bloqueia features P3 e guards (FE-WRKS-016).

**Approach (execution path):**
1) `wrks.module.ts` como entry lazy do Shell (`loadChildren`).
2) `wrks.routes.ts` com `loadComponent` por page; `WrksRootComponent` redireciona p/ 1ª rota permitida.
3) Aplicar matriz de guards do SPEC-01 (pré vs pós-contexto).

**Non-goals:** implementação dos guards (FE-WRKS-016); páginas (P3).

**Layer(s):** frontend / apps/wrks <module>-module
**Bounded context:** wrks

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md`

**Architecture alignment:** ADR-003 (lazy module); standalone features via `loadComponent`.

**Implementation checklist (by file):**
- ✅ `apps/wrks/src/app/wrks-module/wrks.module.ts` — real em `libs/wrks/shell-entry/src/lib/wrks.module.ts`: `WrksModule` com `RouterModule.forChild(WRKS_ROUTES)` (entry lazy do Shell).
- 🔲 `apps/wrks/src/app/wrks-module/wrks.routes.ts` (MISSING) — existe em `libs/wrks/shell-entry/src/lib/wrks.routes.ts` mas é stub vazio (`WRKS_ROUTES = []`, "filled in by /fe-implement"); sem árvore de rotas do SPEC-01 e sem matriz de guards (pré vs pós-contexto).
- 🔲 `apps/wrks/src/app/wrks-module/wrks-root.component.ts` (MISSING) — arquivo inexistente; `WrksRootComponent` (redirect → 1ª rota permitida) não criado.

**Tests**
- 🔲 `nx test wrks` PASS (MISSING — sem `.spec.ts`) · 🔲 `nx lint wrks` PASS (MISSING) (rotas lazy preservadas)

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build wrks` PASS
- Cada rota com os guards exatos do SPEC-01

**Dependencies:** FE-WRKS-001
**API / Contract impact:** nenhum direto.
**Risks / Notes:** garantir que nada protegido carrega antes de `authenticated` (race do callback).
