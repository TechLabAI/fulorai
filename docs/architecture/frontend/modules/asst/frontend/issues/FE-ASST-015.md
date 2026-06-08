## [FE-ASST-015] feature-approval-workflow: decidir (aprovar/rejeitar) + publicar

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 16 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`ApprovalDecisionDialogComponent` (smart) + `ApprovalDecisionFormComponent` que aprova/rejeita
(comentário obrigatório na rejeição — UINV-6) e permite publicar (`asst.asset.publicar`), via
`ApprovalFacade`, reusando `VersionContentViewComponent`.

**Context / Problem statement:**
- Fecha a state machine (APROVADO→PUBLICADO / REJEITADO). Fonte: SPEC-02, SPEC-03 (ApprovalDecisionForm), SPEC-07. Depende de FE-ASST-014, FE-ASST-012.
- Bloqueia: FE-ASST-020.

**Approach (execution path):**
1) Abrir item → ver versão submetida (`VersionContentViewComponent`) + `ApprovalDecisionForm`.
2) `decide(form)` → `POST /{id}/approve`; rejeição exige `comentario` (UINV-6); aprovar → `APROVADO`.
3) Publicar (`asst.asset.publicar`) → `POST /{id}/publish` → `PUBLICADO`, atualiza versão vigente; `publicando` signal.

**Non-goals:** lista da fila (FE-ASST-014); ações no detalhe (FE-ASST-011).

**Layer(s):** frontend / `libs/asst/feature-approval-workflow`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `SPEC-07` (409)

**Architecture alignment:** sem otimismo; ações gated por permissão.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/feature-approval-workflow/src/lib/approval-decision.dialog.ts`
- 🔲 [MISSING] `libs/asst/feature-approval-workflow/src/lib/approval-decision-form.component.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-feature-approval-workflow` PASS (aprovar/rejeitar/publicar/409) · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:asst · priority:P3

**Acceptance criteria:**
- Rejeição sem comentário é bloqueada (UINV-6); publish só disponível em `APROVADO` (UINV-5)
- Publicar atualiza `versaoVigenteId` na UI

**Dependencies:** FE-ASST-014, FE-ASST-012
**API / Contract impact:** `POST /{id}/approve`, `POST /{id}/publish`.
**Risks / Notes:** `409 transicao-invalida` recarrega e re-deriva ações.
