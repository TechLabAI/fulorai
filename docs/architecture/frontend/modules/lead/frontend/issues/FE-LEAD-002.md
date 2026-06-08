## [FE-LEAD-002] Module routes + lazy entry + nav.config

**Status (validação):** REDUCED — pós-validação 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 1/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`lead.routes.ts` (`MODULE_ROUTES`) com as 8 rotas do SPEC-01 (lazy `loadComponent` por feature),
guards `authGuard`+`empresaGuard`+`accessGuard(<perm>)`, redirect raiz `/lead → /lead/leads`, e
`lead.nav.config.ts`. Entry exportada de `@journeyos/lead`.

**Context / Problem statement:**
- Define a superfície de navegação do módulo carregada pelo Shell via `loadChildren`.
- Fonte: SPEC-01. Cobre o gap **G8** (redirect raiz). Bloqueia: features P3, FE-LEAD-017, FE-LEAD-018.

**Approach (execution path):**
1) `lead.routes.ts`: redirect `'' → leads` (`pathMatch: 'full'`) + uma rota lazy por feature com `data` (title/breadcrumbs/permissionRequired).
2) Aplicar guards por rota conforme SPEC-01 (permissão de cada rota).
3) `lead.nav.config.ts`: ordem dos itens + ícones; barrel `@journeyos/lead`.

**Non-goals:** implementação das pages (P3); guard customizado de data-scope (FE-LEAD-017).

**Layer(s):** frontend / `libs/lead/shell-entry`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-01-route-map.md`

**Architecture alignment:** module-pattern; lazy entry as library (ADR-003); tag `scope:lead`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/shell-entry/src/lib/lead.routes.ts` — _MISSING_
- 🟡 `libs/lead/shell-entry/src/lib/lead.nav.config.ts` — _PARTIAL_
- ✅ `libs/lead/shell-entry/src/index.ts` (barrel exporta `LEAD_ROUTES`) — _DONE_

**Tests**
- 🔲 `nx test lead-shell-entry` PASS — _MISSING_ · 🔲 `nx lint lead-shell-entry` PASS — _MISSING_

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:lead · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build lead-shell-entry` PASS
- `/lead` redireciona para `/lead/leads`; cada rota carrega a feature correta com os guards do SPEC-01

**Dependencies:** FE-LEAD-001
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** rotas devem casar com os componentes gerados pelo scaffold (nomes do generator-config).
