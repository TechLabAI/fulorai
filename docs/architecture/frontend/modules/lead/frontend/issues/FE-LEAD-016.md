## [FE-LEAD-016] feature-qualification-rules: versões + ativação

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`QualificationRulesPageComponent` (lista de versões, versão ativa destacada) +
`RuleVersionEditorDialogComponent` (criar versão inativa). Ativar uma versão a torna ativa e desativa
a anterior; requalificar sem regra ativa fica desabilitado.

**Context / Problem statement:**
- Governança de regras versionadas. Fonte: SPEC-02, SPEC-07. Consome `QualificationFacade` (FE-LEAD-006).

**Approach (execution path):**
1) `QualificationRulesPageComponent` lê `versoes`, `versaoAtiva`; row emite ativar/ver.
2) `RuleVersionEditorDialogComponent`: criar nova versão (inativa).
3) `409 sem-regra-ativa` reflete no detalhe (botão "Requalificar" desabilitado).

**Non-goals:** editor visual de regra (fora do MVP); recálculo em si (BE).

**Layer(s):** frontend / `libs/lead/feature-qualification-rules`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-02 + SPEC-07`

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:lead` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-qualification-rules/src/lib/qualification-rules.page.ts` — _MISSING_
- 🔲 `libs/lead/feature-qualification-rules/src/lib/rule-version-editor.dialog.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-feature-qualification-rules` PASS — _MISSING_ · 🔲 `nx lint lead-feature-qualification-rules` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-feature-qualification-rules` PASS
- Ativar versão destaca a ativa e desativa a anterior (SPEC-04 EARS)

**Dependencies:** FE-LEAD-006, FE-LEAD-008
**API / Contract impact:** `GET/POST /qualification/rules`, `POST /qualification/rules/{versao}/activate`.
**Risks / Notes:** ativação é atômica no BE; a UI apenas reflete o resultado.
