## [FE-LEAD-011] feature-lead-detail: perfil + ações (qualify/LGPD) + estados

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`LeadDetailPageComponent` (smart) com `LeadProfilePanelComponent`, `LeadActionsBarComponent` e
`ConfirmDialogComponent`. Ações (editar/requalificar/anonimizar/expurgar) derivadas de estado+permissão;
lead `ANONIMIZADO` trava edição. Refetch do score após mutação.

**Context / Problem statement:**
- Coração da leitura acionável do lead. Fonte: SPEC-02, SPEC-03, SPEC-07.
- Consome `ScoreBreakdownComponent` (FE-LEAD-012). Bloqueia: e2e LGPD/qualify.

**Approach (execution path):**
1) `LeadDetailPageComponent` lê `LeadDetailFacade` (lead, score, acoes, editState).
2) `LeadProfilePanelComponent` (editar perfil, base legal); `LeadActionsBarComponent` (ações gated).
3) Ações LGPD via `ConfirmDialogComponent` (modal antes da chamada); `ANONIMIZADO` desabilita edição.

**Non-goals:** visualização do score 6D (FE-LEAD-012); captura de survey (FE-LEAD-015).

**Layer(s):** frontend / `libs/lead/feature-lead-detail`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-02..03 + SPEC-07`

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:lead` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-lead-detail/src/lib/lead-detail.page.ts` — _MISSING_
- 🔲 `libs/lead/feature-lead-detail/src/lib/lead-profile-panel.component.ts` — _MISSING_
- 🔲 `libs/lead/feature-lead-detail/src/lib/lead-actions-bar.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-feature-lead-detail` PASS — _MISSING_ · 🔲 `nx lint lead-feature-lead-detail` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-feature-lead-detail` PASS
- `WHEN ANONIMIZADO`, editar/requalificar desabilitados (SPEC-03/07 EARS); ações LGPD exigem modal

**Dependencies:** FE-LEAD-004, FE-LEAD-008
**API / Contract impact:** `GET/PUT /leads/{id}`, `POST /leads/{id}/qualify|anonimizar`, `DELETE /leads/{id}`.
**Risks / Notes:** confirmação obrigatória em ações destrutivas (LGPD); foco de acessibilidade no modal.
