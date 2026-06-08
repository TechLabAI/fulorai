## [FE-SALE-010] feature-pipeline (Kanban CDK DragDrop + optimistic move + rollback)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/7 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`feature-pipeline` com `SalePipelinePageComponent` (smart) + `PipelineToolbarComponent`,
`PipelineBoardComponent` (cdkDropListGroup), `PipelineColumnComponent` (cdkDropList),
`CreateOpportunityDialogComponent`. Soltar um card dispara `moverEstagio(id, destino)` →
`PATCH /oportunidades/{id}/estagio` com **optimistic move + rollback** ao snapshot confirmado em falha
(`409 ja-fechada`, rede, `403`). Cards `GANHA`/`PERDIDA` têm `arrastavel = false`. Criar oportunidade
gated por `sale.oportunidade.criar`; board read-only sem `sale.oportunidade.mover`. **CDK DragDrop
importado só aqui** (orçamento de bundle, ADR-005). Este é o nó de maior valor/risco do módulo.

**Context / Problem statement:**
- Centerpiece operacional do SALE (golden path "abrir Kanban → mover estágio → ganhar").
- Fonte: SPEC-02 (feature-pipeline) + SPEC-03 (PipelineVM) + ADR-005. Consome `PipelineFacade`.
- Depende de FE-SALE-005, FE-SALE-016 (ui board/chips). Bloqueia: FE-SALE-020/021/023.

**Approach (execution path):**
1) `SalePipelinePageComponent` lê colunas/oportunidades/filtro/movingCardId/podeMover/podeCriar/loading/error.
2) `PipelineBoardComponent` (cdkDropListGroup) + `PipelineColumnComponent` (cdkDropList) com drop → `moverEstagio`.
3) `OpportunityCardComponent` (cdkDrag) com `arrastavel` derivado; `CreateOpportunityDialogComponent` gated.
4) Ligar optimistic move: marcar `movingCardId`, mover, rollback ao snapshot no erro.
5) Filtros `?responsavel=&estado=&q=` refletidos em `PipelineFiltroVm`.

**Non-goals:** virtual scroll/perf (FE-SALE-021); UX de skeleton/toast (FE-SALE-020); ui board reusável (FE-SALE-016).

**Layer(s):** frontend / `libs/sale/feature-pipeline`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02` (feature-pipeline) · `SPEC-03` (PipelineVM) · `adr/ADR-005`

**Architecture alignment:** Standalone + OnPush + Signals; CDK DragDrop local; tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-pipeline/src/lib/sale-pipeline.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-pipeline/src/lib/pipeline-toolbar.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-pipeline/src/lib/pipeline-board.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-pipeline/src/lib/pipeline-column.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-pipeline/src/lib/create-opportunity-dialog.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-feature-pipeline` PASS — _MISSING_ · 🔲 `nx lint sale-feature-pipeline` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-pipeline` PASS
- Card dropped → optimistic move + `PATCH` (EARS SPEC-02); GANHA/PERDIDA não-arrastável (EARS SPEC-02); rollback em `409 ja-fechada`
- Criar/mover gated por permissão (board read-only sem `mover`)

**Dependencies:** FE-SALE-005, FE-SALE-016
**Data impact:** estado do board (signals) enquanto montado; snapshot para rollback.
**API / Contract impact:** `PATCH /oportunidades/{id}/estagio` (+ list).
**Testing / Evidence required:** e2e `pipeline-kanban-move`; screenshots (board, moving, rollback). Cobre R1.
**Risks / Notes:** R1 (rollback obrigatório), R3 (bundle CDK local). Estágios configuráveis por tenant — confirmar origem das colunas (06-risks gap).
