## [FE-WRKS-010] feature-empresa-select (seleção de empresa)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
`feature-empresa-select` com lista das empresas ativas do usuário e `switchTo(empresaId)` (novo JWT + contexto), auto-skip quando N=1 e estado "sem acesso" quando N=0.

**Context / Problem statement:**
- 2ª etapa do golden path. Fonte: SPEC-01/02/03, `e2e/login-and-empresa-select.feature`. Depende de INT-FE-WRKS-002.

**Approach (execution path):**
1) `EmpresaSelectPageComponent` (smart) lê `empresaListFacade`/contexto.
2) `EmpresaCardComponent` emite `select(empresaId)` → `EmpresaContextService.switchTo`.
3) Tratar N=1 (auto) e N=0 (`EmptyState`).

**Non-goals:** troca em runtime pela topbar (Shell + INT-FE-WRKS-002).

**Layer(s):** frontend / libs/wrks/feature-empresa-select
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01/02/03; `e2e/login-and-empresa-select.feature`

**Architecture alignment:** standalone + OnPush; `type:feature` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/feature-empresa-select/src/lib/empresa-select.page.ts` (MISSING)
- 🔲 `libs/wrks/feature-empresa-select/src/lib/empresa-list.component.ts` + `empresa-card.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-empresa-select/src/lib/feature-empresa-select.routes.ts` (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-empresa-select` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build` PASS
- N=1 pula a tela; N=0 mostra "sem acesso"

**Dependencies:** FE-WRKS-009 · INT-FE-WRKS-002
**API / Contract impact:** `/sessao/login` (lista), `/sessao/trocar-empresa`.
**Risks / Notes:** `empresaId` só via `EmpresaContextService` (UINV-3).
