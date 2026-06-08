## [FE-WRKS-017] Navigation / breadcrumbs (libs/wrks/navigation)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** REDUCED — pos-validacao 2026-06-05
**Maturidade:** 32 — Inicial
**Done/Total:** 0/4 itens (1 PARTIAL)

**Outcome:**
`libs/wrks/navigation` fornece a config de breadcrumb/menu do módulo (`wrks.nav.config.ts`), reset na troca de empresa e breadcrumbs por rota conforme SPEC-01.

**Context / Problem statement:**
- Navegação consistente. Fonte: SPEC-01/06, 05-state-and-data-flow §6. Depende de FE-WRKS-002.

**Approach (execution path):**
1) Definir breadcrumbs por rota (mapa do SPEC-01).
2) Resetar breadcrumbs para a raiz do módulo na troca de empresa.
3) Expor config consumida por `NavigationService`.

**Non-goals:** derivação do menu global (Access Layer).

**Layer(s):** frontend / libs/wrks/navigation
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01/06; `05-state-and-data-flow.md`

**Architecture alignment:** `type:domain` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/navigation/src/lib/wrks-breadcrumbs.ts` (MISSING)
- 🟡 `apps/wrks/src/app/wrks-module/wrks.nav.config.ts` (PARTIAL — existe `libs/wrks/shell-entry/src/lib/wrks.nav.config.ts` auto-gerado só com `breadcrumbRoot: 'Workspace'`; sem breadcrumbs por rota nem reset na troca de empresa; caminho diverge do spec)

**Tests**
- 🔲 `nx test wrks-navigation` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P6 / Navigation
**Labels:** type:domain · layer:frontend · scope:wrks · priority:P6

**Acceptance criteria:**
- Breadcrumbs corretos por rota; reset na troca de empresa
- `npx nx test/lint/build wrks-navigation` PASS

**Dependencies:** FE-WRKS-002, INT-FE-WRKS-002
**API / Contract impact:** nenhum.
**Risks / Notes:** —
