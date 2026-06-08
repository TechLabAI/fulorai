## [FE-JRNY-016] Reordenação de estágios (sortable a11y + rollback otimista)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Reordenação de estágios no builder operável por **drag-and-drop e teclado** (setas ↑/↓), com nome
acessível por estágio (a11y, ADR-005). Update **otimista** da ordem com **rollback** se o `PATCH`
falhar (gap G-d / G4), refletindo o estado real.

**Context / Problem statement:**
- A reordenação é a interação central do editor estruturado; precisa ser acessível e resiliente.
- Fonte: SPEC-02 (StageList sortable), SPEC-04/05 (otimista+rollback), ADR-005. Cobre gaps G-d/G4.

**Approach (execution path):**
1) `StageListComponent` sortable (drag-handle + teclado); `aria` nos itens.
2) Aplicar nova `ordem` de forma otimista; chamar `reorder` (StageApiService).
3) Em falha → rollback da ordem em tela + toast de erro (SPEC-07).

**Non-goals:** endpoint batch (gap G4 — sequência de PATCH no MVP).

**Layer(s):** frontend / `libs/jrny/feature-journey-builder`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-02` · `SPEC-04` · `SPEC-07` · `adr/ADR-005`

**Architecture alignment:** Standalone + OnPush + Signals; a11y; tag `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/feature-journey-builder/src/lib/stage-list.component.ts` (sortable + a11y) (MISSING)
- 🔲 `libs/jrny/feature-journey-builder/src/lib/reorder.handler.ts` (otimista + rollback) (MISSING)

**Tests**
- 🔲 `nx test jrny-feature-journey-builder` PASS (MISSING) · 🔲 `nx lint ...` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-feature-journey-builder` PASS
- Reordenar por teclado e ponteiro (EARS #11); falha → rollback + toast (gap G-d)

**Dependencies:** FE-JRNY-010, FE-JRNY-005
**API / Contract impact:** `PATCH /api/v1/journeys/{id}/estagios/{estagioId}` (ordem).
**Risks / Notes:** jank com muitos estágios — virtualizar só se necessário (06-risks R7).
