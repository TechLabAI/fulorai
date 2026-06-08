## [FE-LEAD-014] feature-segmentation: lista + editor de predicado + prévia

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`SegmentListPageComponent` (lista + ações) + `SegmentEditorDialogComponent` (criar/editar predicado)
com `PredicatePreviewComponent` (prévia de contagem). Abrir um segmento navega à fila filtrada.

**Context / Problem statement:**
- CRUD de segmentos dinâmicos. Fonte: SPEC-02, SPEC-03, SPEC-07.
- Consome `SegmentFacade` (FE-LEAD-007).

**Approach (execution path):**
1) `SegmentListPageComponent` lê `segmentos`; row emite editar/excluir/abrirFila.
2) `SegmentEditorDialogComponent`: validação de forma do predicado + `preview(predicado)`.
3) `422 predicado-invalido` → erro de campo, editor permanece aberto.

**Non-goals:** editor visual drag-and-drop (fora do MVP).

**Layer(s):** frontend / `libs/lead/feature-segmentation`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-02..03 + SPEC-07`

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:lead` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-segmentation/src/lib/segment-list.page.ts` — _MISSING_
- 🔲 `libs/lead/feature-segmentation/src/lib/segment-editor.dialog.ts` — _MISSING_
- 🔲 `libs/lead/feature-segmentation/src/lib/predicate-preview.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-feature-segmentation` PASS — _MISSING_ · 🔲 `nx lint lead-feature-segmentation` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:lead · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build lead-feature-segmentation` PASS
- Criar segmento mostra prévia de contagem; predicado inválido vira erro de campo

**Dependencies:** FE-LEAD-007, FE-LEAD-008
**API / Contract impact:** `GET/POST/PUT/DELETE /segments`, `GET /segments/{id}/leads`.
**Risks / Notes:** não inventar gramática de predicado — veredito final é do BE.
