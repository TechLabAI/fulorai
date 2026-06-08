## [FE-LEAD-015] feature-survey: lista + editor + diálogo de respostas

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`SurveyListPageComponent` + `SurveyEditorPageComponent` (survey + perguntas) +
`SurveyAnswerDialogComponent` (capturar respostas para um lead, reusado no detalhe). Respostas
atualizam o perfil e disparam recálculo.

**Context / Problem statement:**
- Surveys enriquecem o perfil. Fonte: SPEC-02, SPEC-03, SPEC-07. Consome `SurveyFacade` (FE-LEAD-005).

**Approach (execution path):**
1) `SurveyListPageComponent` (lista) + `SurveyEditorPageComponent` (perguntas tipadas).
2) `SurveyAnswerDialogComponent`: captura respostas; `422 pergunta-invalida` → erro de campo.
3) Após responder, refletir recálculo do score no detalhe.

**Non-goals:** lógica de scoring (BE); UI do detalhe (FE-LEAD-011, que abre o diálogo).

**Layer(s):** frontend / `libs/lead/feature-survey`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-02..03 + SPEC-07`

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:lead` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-survey/src/lib/survey-list.page.ts` — _MISSING_
- 🔲 `libs/lead/feature-survey/src/lib/survey-editor.page.ts` — _MISSING_
- 🔲 `libs/lead/feature-survey/src/lib/survey-answer.dialog.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-feature-survey` PASS — _MISSING_ · 🔲 `nx lint lead-feature-survey` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-feature-survey` PASS
- Responder atualiza perfil (`origem=SURVEY`) e dispara recálculo; pergunta inválida vira erro de campo

**Dependencies:** FE-LEAD-005, FE-LEAD-008
**API / Contract impact:** `GET/POST/PUT /surveys`, `POST /leads/{leadId}/surveys/{surveyId}/respostas`.
**Risks / Notes:** tipos de pergunta (TEXTO/ESCOLHA/NUMERO/BOOLEANO) mapeiam a atributos.
