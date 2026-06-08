## [FE-COMM-010] feature-template-catalog — editor + placeholders + estado

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 15 -- Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`TemplateEditorPageComponent` com `TemplateMetaFormComponent` (nome/canal/tipo/assunto/vínculo asset),
`TemplateBodyEditorComponent` (corpo + chips `{{variavel}}` + validação síncrona de placeholders) e
`TemplateStateActionsComponent` (Ativar/Arquivar gated).

**Context / Problem statement:**
- Edição e ciclo de estado do template. Fonte: SPEC-02, SPEC-03 (UINV-1/2). Depende: FE-COMM-004, FE-COMM-009.

**Approach:**
1) Form de metadados; `assunto` obrigatório quando `canal=EMAIL` (UINV-2).
2) Editor de corpo com inserção e validação de placeholders (`variaveisInvalidas` bloqueia save — UINV-1).
3) Ações Ativar (`RASCUNHO→ATIVO`) / Arquivar com atualização otimista leve do chip + rollback.

**Non-goals:** Studio (FE-COMM-012); disparo (FE-COMM-013).

**Layer(s):** frontend / `libs/comm/feature-template-catalog`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-02`, `SPEC-03`, `SPEC-07`
**Architecture alignment:** standalone/OnPush; tag `scope:comm` `type:feature`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/feature-template-catalog/src/lib/template-editor.page.ts`
- 🔲 [MISSING] `libs/comm/feature-template-catalog/src/lib/template-meta-form.component.ts`
- 🔲 [MISSING] `libs/comm/feature-template-catalog/src/lib/template-body-editor.component.ts`
- 🔲 [MISSING] `libs/comm/feature-template-catalog/src/lib/template-state-actions.component.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-feature-template-catalog` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:comm · priority:P3

**Acceptance criteria:**
- Placeholder não declarada bloqueia salvar; EMAIL exige assunto; transições gated por permissão; `nx test/lint/build` PASS

**Dependencies:** FE-COMM-004, FE-COMM-009
**API / Contract impact:** `GET/PATCH /templates/{id}`, `POST /templates/{id}/{ativar,arquivar}`.
**Risks / Notes:** seleção de asset de origem depende de gap de contrato (cross-link) — stub até confirmar.
