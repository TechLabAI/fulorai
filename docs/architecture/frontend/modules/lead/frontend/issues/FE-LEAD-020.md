## [FE-LEAD-020] Feature-flag gating + a11y do Maturity Score

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Comportamento de desligamento das flags: `lead.maturity-score` oculta `/lead/maturity` + deep link;
`lead.qualification-rules` oculta "Regras" + bloqueia a rota. Auditoria de acessibilidade do
Maturity Score (contraste AA, faixa com rótulo, tabela alternativa do radar). Cobre **G2**, **G3**, **G4**.

**Context / Problem statement:**
- Fecha os gaps de feature-flag e a11y do specs-validate. Fonte: SPEC-01, SPEC-05, ADR-005.

**Approach (execution path):**
1) Filtrar rotas/deep links por estado de flag (`NavigationService` + guard de rota).
2) Garantir contraste AA + rótulo textual + tabela do radar (revisar FE-LEAD-012).
3) Testes de a11y (axe) nas telas de score.

**Non-goals:** novos componentes de score (FE-LEAD-012).

**Layer(s):** frontend / `shell-entry` + `ui` + features
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-01 + SPEC-05` · `ADR-005`

**Architecture alignment:** module-pattern; tag `scope:lead`.

**Implementation checklist (by file):**
- 🔲 wiring de flag em `lead.routes.ts` / `NavigationService` — _MISSING_
- 🔲 testes a11y (axe) em `lead-ui` / `feature-maturity-score` — _MISSING_

**Tests**
- 🔲 `nx test lead-*` PASS · 🔲 `nx lint lead-*` PASS — _MISSING_

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:lead · priority:P7

**Acceptance criteria:**
- `WHILE` flag desabilitada, rota/deep link ocultos e bloqueados (SPEC-01/05 EARS, G2/G3)
- Radar com tabela alternativa + contraste AA (G4)

**Dependencies:** FE-LEAD-002, FE-LEAD-012, FE-LEAD-013
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** flags devem ter `defaultState` explícito (SPEC-05 EARS).
