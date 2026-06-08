## [FE-ASST-007] WorkflowApiService + ApprovalFacade (submit/approve/publish)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 15 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`WorkflowApiService` (submit/approve/publish/listQueue) + `ApprovalFacade` (signals `fila`,
`itemAberto`, `publicando`, `loading`, `error`) em `libs/asst/data-access`.

**Context / Problem statement:**
- State machine de aprovação (RASCUNHO→EM_REVISAO→APROVADO→PUBLICADO/REJEITADO). Fonte: SPEC-04 (Workflow). Depende de FE-ASST-005.
- Bloqueia: FE-ASST-011 (ações no detalhe), FE-ASST-014, FE-ASST-015.

**Approach (execution path):**
1) `submit(id, versaoNumero)`, `approve(id, decisão+comentário)`, `publish(id)`, `listQueue()` (`GET /?estado=EM_REVISAO`).
2) Facade sem otimismo: `loading` + confirmação; trata `409 transicao-invalida`.
3) Após publish, refletir novo `versaoVigenteId` (refetch do asset).

**Non-goals:** UI da fila/diálogo (FE-ASST-014/015); guards (FE-ASST-016).

**Layer(s):** frontend / `libs/asst/data-access`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Workflow)

**Architecture alignment:** ADR-002 signals; sem otimismo em transição; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/data-access/src/lib/workflow-api.service.ts`
- 🔲 [MISSING] `libs/asst/data-access/src/lib/approval.facade.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS (transições + 409) · 🔲 [MISSING] `nx lint asst-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:asst · priority:P2

**Acceptance criteria:**
- `409 transicao-invalida` tratado sem quebrar a tela (recarrega asset + re-deriva ações)
- `listQueue` retorna apenas `EM_REVISAO` da empresa ativa

**Dependencies:** FE-ASST-005
**API / Contract impact:** `POST /{id}/submit|approve|publish`, `GET /?estado=EM_REVISAO`.
**Risks / Notes:** endpoint de fila dedicado pode surgir no BE (backend-api-cross-link: a validar).
