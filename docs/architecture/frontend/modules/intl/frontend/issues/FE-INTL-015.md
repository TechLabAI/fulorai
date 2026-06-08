## [FE-INTL-015] libs/intl/access — guards do módulo (intlModuleGuard + accessGuard)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 18 — Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
Guards específicos do INTL em `libs/intl/access`: `intlModuleGuard` (módulo habilitado por flag) + helper `accessGuard(<perm>)` por rota, delegando a `AccessDecisionService` (sem RBAC inline).

**Context / Problem statement:**
- Endurece o controle de acesso das 7 rotas. Fonte: SPEC-01 + access-layer-contracts.
- Bloqueia: e2e entitlement-denied (FE-INTL-019).

**Approach (execution path):**
1) `accessGuard(perm)` → `AccessDecisionService.can(perm)`.
2) `intlModuleGuard` respeita feature-flags do módulo.
3) Aplicar nas rotas (substitui stubs de FE-INTL-002).

**Non-goals:** authGuard/empresaGuard (são da Access Layer global).

**Layer(s):** frontend / libs/intl/access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md` (Notas de guarda)

**Architecture alignment:** `type:domain` `scope:intl`; consome `@journeyos/shared/access-decision`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/access/src/lib/intl-module.guard.ts` — MISSING: só placeholder component, sem guard
- 🔲 `libs/intl/access/src/lib/access.guard.ts` — MISSING: helper accessGuard inexistente

**Tests**
- 🔲 `nx test intl-access` PASS — MISSING: sem testes de guard · 🔲 `nx lint` PASS — MISSING: não executado neste baseline

**Milestone:** Wave P5 / Access guards
**Labels:** type:integration · layer:frontend · scope:intl · priority:P5

**Acceptance criteria:**
- `npx nx test/lint/build intl-access` PASS
- Teste: sem permissão → guard nega; com permissão → permite.

**Dependencies:** FE-INTL-002 · INT-FE-INTL-003
**API / Contract impact:** nenhum.
**Risks / Notes:** —
