## [FE-JRNY-012] feature-routing-engine (regras versionadas + ConditionBuilder)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/6 itens

**Outcome:**
`feature-routing-engine` com `RoutingRulesPageComponent` (smart) + `RuleRowComponent`,
`RuleEditorDialogComponent`, `ConditionBuilderComponent`. Lista regras por prioridade; criar/editar
(bumpa versão); `ConditionBuilder` estruturado sobre a gramática de snapshot (data-model §5).

**Context / Problem statement:**
- Governança do roteamento; condição é formulário estruturado, não query-builder visual livre.
- Fonte: SPEC-02, SPEC-03 (RoutingRulesVM), cross-link (condicao). Cobre gap G-b (condicaoResumo render).

**Approach (execution path):**
1) `RoutingRulesPageComponent` lê `rules/estagios/podeEditar`.
2) `RuleEditorDialog` (origem/destino/prioridade) + `ConditionBuilder` (combinador `E`/`OU` + predicados).
3) Renderizar `condicaoResumo` legível por regra; refletir bump de versão.

**Non-goals:** validação semântica profunda (confia no 422 condicao-invalida/estagio-invalido).

**Layer(s):** frontend / `libs/jrny/feature-routing-engine`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `SPEC-04` (RoutingRule)

**Architecture alignment:** Standalone + OnPush + Signals; tag `type:feature` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/feature-routing-engine/src/lib/routing-rules.page.ts` (MISSING)
- 🔲 `libs/jrny/feature-routing-engine/src/lib/rule-row.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-routing-engine/src/lib/rule-editor-dialog.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-routing-engine/src/lib/condition-builder.component.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-feature-routing-engine` PASS (MISSING) · 🔲 `nx lint ...` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-feature-routing-engine` PASS
- Condição inválida/destino inválido → erro inline; `condicaoResumo` legível (gap G-b)

**Dependencies:** FE-JRNY-006
**API / Contract impact:** `/api/v1/routing/rules` (list/create/update).
**Risks / Notes:** campos da `condicao` fechados à gramática (data-model §5).
