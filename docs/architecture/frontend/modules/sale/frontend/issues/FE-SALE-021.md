## [FE-SALE-021] Kanban a11y (DnD keyboard) + perf (virtual scroll / paginação por coluna)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Acessibilidade e performance do board: **mover estágio por teclado** (fallback de teclado/lista para o
CDK DragDrop, com nome acessível do card e da coluna destino) e **virtual scroll / paginação por coluna**
(CDK) para pipelines com centenas de cards, mantendo TTI/INP. Cards leves; `GET /oportunidades` paginado/
filtrado server-side. Contraste AA nos chips de estado/status (rótulo textual, não cor-only).

**Context / Problem statement:**
- Mitiga R2 (perf do board) e o requisito a11y de DnD (drag-and-drop touch é nice-to-have; teclado é requisito).
- Fonte: SPEC-02 (fallback de teclado) + 06-risks R2/R3. Depende de FE-SALE-010, FE-SALE-016.

**Approach (execution path):**
1) Fallback de teclado para mover card (selecionar → escolher coluna destino) com `aria` + nome do estágio.
2) Virtual scroll por coluna (CDK) + paginação/lazy de cards; card leve.
3) Auditoria de contraste AA nos chips/badges (`libs/sale/ui`).

**Non-goals:** novos fluxos de negócio; touch DnD (nice-to-have pós-MVP).

**Layer(s):** frontend / `libs/sale/feature-pipeline` + `libs/sale/ui`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02-component-hierarchy.md` (fallback teclado/a11y) · `06-risks-gaps-assumptions.md` (R2, R3)

**Architecture alignment:** CDK virtual scroll; a11y AA; tags conforme lib.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-pipeline/src/lib/pipeline-column.component.ts` (virtual scroll + a11y move) — _MISSING_
- 🔲 `libs/sale/feature-pipeline/src/lib/pipeline-keyboard-move.directive.ts` — _MISSING_
- 🔲 auditoria AA em `libs/sale/ui` (chips/badges) — _MISSING_

**Tests**
- 🔲 `nx test sale-feature-pipeline` PASS — _MISSING_ · 🔲 `nx lint sale-feature-pipeline` PASS — _MISSING_

**Milestone:** Wave P7 / UX polish (hardening)
**Labels:** type:feature · layer:frontend · scope:sale · priority:P7

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-pipeline` PASS
- Mover estágio por teclado funcional + nome acessível; virtual scroll por coluna; chips AA (não cor-only)

**Dependencies:** FE-SALE-010, FE-SALE-016
**API / Contract impact:** `GET /oportunidades` paginado/filtrado.
**Data impact:** Nenhum.
**Testing / Evidence required:** teste a11y (axe) do board; medição de INP com muitos cards.
**Risks / Notes:** R2 (perf), R3 (bundle). Volume típico por coluna a confirmar (06-risks suposições).
