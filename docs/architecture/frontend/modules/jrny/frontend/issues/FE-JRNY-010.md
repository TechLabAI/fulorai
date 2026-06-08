## [FE-JRNY-010] feature-journey-builder (estágios ordenados + máquina de estados)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/7 itens

**Outcome:**
`feature-journey-builder` com `JourneyBuilderPageComponent` (smart) + `JourneyHeaderComponent`,
`StageListComponent`, `StageCardComponent`, `PublishBarComponent`. Editor **estruturado** de estágios
ordenados (ADR-005, sem canvas); ações publicar/arquivar/nova-versão; **read-only** quando não-RASCUNHO.

**Context / Problem statement:**
- Coração de autoria; gate de editabilidade espelha o BE (imutabilidade do publicado).
- Fonte: SPEC-02, SPEC-03 (JourneyBuilderVM), ADR-005. Consome `JourneyBuilderFacade`.

**Approach (execution path):**
1) `JourneyBuilderPageComponent` lê `journey/estagios/editavel/acoesDisponiveis/podePublicar`.
2) Header com ações (gated por estado+perm); `PublishBar` com `motivoBloqueio`.
3) `StageList` em read-only quando `!editavel`; abrir estágio → stage-editor.

**Non-goals:** sortable a11y + rollback (FE-JRNY-016); stage form (FE-JRNY-011).

**Layer(s):** frontend / `libs/jrny/feature-journey-builder`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `adr/ADR-005-canvas-builder-rendering.md`

**Architecture alignment:** Standalone + OnPush + Signals; tag `type:feature` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/feature-journey-builder/src/lib/journey-builder.page.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-builder/src/lib/journey-header.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-builder/src/lib/stage-list.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-builder/src/lib/stage-card.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-journey-builder/src/lib/publish-bar.component.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-feature-journey-builder` PASS (MISSING) · 🔲 `nx lint ...` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-feature-journey-builder` PASS
- Jornada não-RASCUNHO → builder read-only + CTA nova versão (EARS #5, #10)
- Publicar sem estágio bloqueado com mensagem (EARS #16)

**Dependencies:** FE-JRNY-004, FE-JRNY-005
**API / Contract impact:** `/api/v1/journeys` (publicar/arquivar/nova-versao) + estágios.
**Risks / Notes:** sem lib de canvas (ADR-005); `temRegrasSaindo` client-side (gap G3).
