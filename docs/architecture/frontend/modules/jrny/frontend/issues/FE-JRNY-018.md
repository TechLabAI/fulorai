## [FE-JRNY-018] Navigation / breadcrumbs do módulo

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 12 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
`libs/jrny/navigation` alimenta `BreadcrumbItem[]` para as rotas do JRNY (Jornadas / {nome} / Estágio /
Regras / Decisões / Analytics) conforme SPEC-05 §6. Menu/itens filtrados por `NavigationService` +
`AccessDecisionService`; troca de empresa limpa o estado de navegação.

**Context / Problem statement:**
- Breadcrumbs contextuais (dependem de `:id`/`:leadId`/`:ordem`).
- Fonte: SPEC-05 §6 (breadcrumbs), SPEC-01 (titles).

**Approach (execution path):**
1) Mapear breadcrumbs por rota (resolver nome da jornada/estágio).
2) Filtrar deep links por permissão; limpar na troca de empresa.

**Non-goals:** guards (FE-JRNY-017); registro Shell (INT-FE-JRNY-005).

**Layer(s):** frontend / `libs/jrny/navigation`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-05-module-contract.md` §6 · `SPEC-01`

**Architecture alignment:** Access Layer (NavigationService); tag `type:domain` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/navigation/src/lib/jrny-breadcrumbs.ts` (MISSING)
- 🔲 `libs/jrny/navigation/src/lib/jrny-nav.state.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-navigation` PASS (MISSING) · 🔲 `nx lint jrny-navigation` PASS (MISSING)

**Milestone:** Wave P6 / Navigation
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P6

**Acceptance criteria:**
- `npx nx test/lint/build jrny-navigation` PASS
- Breadcrumbs corretos por rota; deep links filtrados por permissão

**Dependencies:** FE-JRNY-002, INT-FE-JRNY-003
**API / Contract impact:** nenhum direto.
**Risks / Notes:** resolver nome da jornada/estágio sem chamada extra (reusar facade).
