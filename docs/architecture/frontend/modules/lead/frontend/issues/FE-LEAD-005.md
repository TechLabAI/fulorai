## [FE-LEAD-005] Survey data-access: SurveyApiService + SurveyFacade

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`SurveyApiService` (list/get/create/update/responder) + `SurveyFacade` com signals (`surveys`,
`perguntas`, `respostasEmEdicao`, `dirty`, `error`). Responder dispara recálculo do score no BE.

**Context / Problem statement:**
- Surveys enriquecem o perfil (`origem=SURVEY`) e disparam recompute. Fonte: SPEC-04.
- Bloqueia: FE-LEAD-015 (feature-survey).

**Approach (execution path):**
1) `SurveyApiService` (`/api/v1/surveys`, `POST /leads/{leadId}/surveys/{surveyId}/respostas`).
2) `SurveyFacade`: signals + operações; `responder` retorna após upsert/recompute.

**Non-goals:** UI do editor/diálogo (FE-LEAD-015).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md`

**Architecture alignment:** Signals-first; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/data-access/src/lib/survey-api.service.ts` — _MISSING_
- 🔲 `libs/lead/data-access/src/lib/survey.facade.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:lead · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build lead-data-access` PASS
- `responder` mapeia para `POST /leads/{leadId}/surveys/{surveyId}/respostas`

**Dependencies:** FE-LEAD-002, INT-FE-LEAD-001
**API / Contract impact:** `GET/POST/PUT /surveys`, `POST /leads/{leadId}/surveys/{surveyId}/respostas`.
**Risks / Notes:** validar `422 lead.survey.pergunta-invalida` no facade (mapeado em FE-LEAD-008).
