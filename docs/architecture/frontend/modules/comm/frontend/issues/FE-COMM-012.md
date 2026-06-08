## [FE-COMM-012] feature-routing-rules — CRUD de regras

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`RoutingRulesPageComponent` + `RoutingRuleListComponent`/`RoutingRuleRowComponent` (ordenadas por
prioridade) + `RoutingRuleDialogComponent` com `ChannelPickerComponent` (canal preferido + fallback).
Consome `RoutingFacade`.

**Context / Problem statement:**
- Editar como o canal é escolhido. Fonte: SPEC-02, SPEC-03. Depende: FE-COMM-006.

**Approach:**
1) Lista ordenada por prioridade.
2) Dialog cria/edita (condições, canalPreferido, canaisFallback, templateId, prioridade, ativa).
3) `ChannelPicker` só com canais (nunca provedores).

**Non-goals:** resolução de canal no FE (é BE); disparo (FE-COMM-013).

**Layer(s):** frontend / `libs/comm/feature-routing-rules`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-02`, `SPEC-03`
**Architecture alignment:** standalone/OnPush; tag `scope:comm` `type:feature`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/feature-routing-rules/src/lib/routing-rules.page.ts`
- 🔲 [MISSING] `libs/comm/feature-routing-rules/src/lib/routing-rule.dialog.ts`
- 🔲 [MISSING] `libs/comm/feature-routing-rules/src/lib/channel-picker.component.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-feature-routing-rules` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:comm · priority:P3

**Acceptance criteria:**
- Regras ordenadas por prioridade; criar/editar gated; `nx test/lint/build` PASS

**Dependencies:** FE-COMM-006
**API / Contract impact:** `/api/v1/routing-rules`.
**Risks / Notes:** editor de `condicoes` (objeto livre) — UI simples no MVP (chave/valor).
