## [FE-ASST-014] feature-approval-workflow: fila de aprovação (page + lista)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`ApprovalQueuePageComponent` (smart) + `ApprovalQueueListComponent` + `ApprovalQueueItemComponent`
consumindo `ApprovalFacade.fila()` (assets `EM_REVISAO`), com empty state e gate `asst.asset.aprovar`.

**Context / Problem statement:**
- Superfície da persona Rafael. Fonte: SPEC-02 (feature-approval-workflow), SPEC-01. Depende de FE-ASST-007.
- Bloqueia: FE-ASST-015, FE-ASST-020.

**Approach (execution path):**
1) `ApprovalQueuePageComponent` lê `fila()/loading()/error()`; rota gated `accessGuard('asst.asset.aprovar')`.
2) `ApprovalQueueListComponent`/`ApprovalQueueItemComponent` (presentational); `open(assetId)`.
3) Empty state quando a fila está vazia (`@journeyos/shared/ui-feedback`).

**Non-goals:** diálogo de decisão (FE-ASST-015); publish (FE-ASST-015).

**Layer(s):** frontend / `libs/asst/feature-approval-workflow`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-02` · `SPEC-01` · `SPEC-03` (ApprovalItemVM)

**Architecture alignment:** Standalone/OnPush/Signals.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/feature-approval-workflow/src/lib/approval-queue.page.ts`
- 🔲 [MISSING] `libs/asst/feature-approval-workflow/src/lib/approval-queue-list.component.ts`
- 🔲 [MISSING] `libs/asst/feature-approval-workflow/src/lib/approval-queue-item.component.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-feature-approval-workflow` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:asst · priority:P3

**Acceptance criteria:**
- Fila lista apenas `EM_REVISAO` da empresa ativa; rota bloqueada sem `asst.asset.aprovar`

**Dependencies:** FE-ASST-007
**API / Contract impact:** `GET /?estado=EM_REVISAO`.
**Risks / Notes:** endpoint de fila dedicado pode surgir no BE (a validar).
