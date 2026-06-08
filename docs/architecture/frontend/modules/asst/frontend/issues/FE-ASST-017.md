## [FE-ASST-017] Navigation / breadcrumbs state

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 10 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
`libs/asst/navigation` fornece os breadcrumbs do módulo (`Assets > Catálogo`, `Assets > {título}`,
`Assets > {título} > Studio`, `Assets > Aprovações`) e a config consumida pelo `NavigationService`;
reset na troca de empresa.

**Context / Problem statement:**
- Navegação derivada de permissões (deep link "Aprovações" gated). Fonte: SPEC-05/06, `05-state-and-data-flow.md §6`. Depende de FE-ASST-002, INT-FE-ASST-004.
- Bloqueia: —.

**Approach (execution path):**
1) Mapear breadcrumb por rota a partir de `asst.nav.config.ts`.
2) Em troca de empresa, breadcrumb reseta para `/asst/library` (UINV-8).
3) Deep link "Aprovações" só no menu com `asst.asset.aprovar` (via NavigationService).

**Non-goals:** montar menu ad-hoc (proibido — vem do NavigationService).

**Layer(s):** frontend / `libs/asst/navigation`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-06` · `05-state-and-data-flow.md §6`

**Architecture alignment:** tag `type:domain`; consome `@journeyos/shared/access-decision`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/navigation/src/lib/asst-breadcrumbs.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-navigation` PASS · 🔲 [MISSING] `nx lint asst-navigation` PASS

**Milestone:** Wave P6 / Navigation
**Labels:** type:feature · layer:frontend · scope:asst · priority:P6

**Acceptance criteria:**
- Breadcrumbs corretos por rota; reset na troca de empresa

**Dependencies:** FE-ASST-002, INT-FE-ASST-004
**API / Contract impact:** nenhum.
**Risks / Notes:** título do asset no breadcrumb vem do `AssetDetailFacade`.
