## [FE-LEAD-007] Segment data-access: SegmentApiService + SegmentFacade

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`SegmentApiService` (list/get/create/update/delete/listLeads) + `SegmentFacade` com signals
(`segmentos`, `predicadoEmEdicao`, `previewContagem`, `error`). `listLeads` ordena por score desc.

**Context / Problem statement:**
- Segmentação dinâmica por predicado sobre perfil+score. Fonte: SPEC-04.
- Bloqueia: FE-LEAD-014 (feature-segmentation).

**Approach (execution path):**
1) `SegmentApiService` (`/api/v1/segments`, `.../{id}/leads`).
2) `SegmentFacade`: CRUD + `preview(predicado)` → contagem; `listLeads(id)` para a fila do segmento.

**Non-goals:** UI do editor (FE-LEAD-014); validação semântica do predicado (BE — `422`).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md`

**Architecture alignment:** Signals-first; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/data-access/src/lib/segment-api.service.ts` — _MISSING_
- 🔲 `libs/lead/data-access/src/lib/segment.facade.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:lead · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build lead-data-access` PASS
- `listLeads` retorna leads ordenados por Maturity Score desc (SPEC-04)

**Dependencies:** FE-LEAD-002, INT-FE-LEAD-001
**API / Contract impact:** `GET/POST/PUT/DELETE /segments`, `GET /segments/{id}/leads`.
**Risks / Notes:** `422 predicado-invalido` mapeado a erro de campo (FE-LEAD-008).
