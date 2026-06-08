## [FE-COMM-005] StudioApiService + TemplateStudioFacade (degradação graciosa)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 10 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`StudioApiService.compose()` (`POST /templates/{id}/studio/compose` + `Idempotency-Key`) +
`TemplateStudioFacade` com signal `studioState` (`idle → composing → draft-pronto | degradado`),
`draft` e `error`. `503 comm.studio.ia-indisponivel` → `degradado` sem alterar o corpo.

**Context / Problem statement:**
- Núcleo do Template Studio (ADR-005-degradação reuso do padrão ASST). Fonte: SPEC-04, SPEC-03. Depende: INT-FE-COMM-001. Bloqueia: FE-COMM-012.

**Approach:**
1) `StudioApiService.compose(req)` síncrono com `Idempotency-Key`.
2) Facade gerencia `studioState`; `200` → `draft-pronto`; `503`/timeout → `degradado`.
3) Nunca ativa template automaticamente; preserva `briefComposicao`.

**Non-goals:** UI do Studio (FE-COMM-012); chamar TechLab AI direto (proibido).

**Layer(s):** frontend / `libs/comm/data-access`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Studio), `SPEC-07-error-handling.md`
**Architecture alignment:** signals-first; FE→BE only; tag `scope:comm` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/data-access/src/lib/studio-api.service.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/template-studio.facade.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS (cobre `200` e `503`) · 🔲 [MISSING] `nx lint comm-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:comm · priority:P2

**Acceptance criteria:**
- `503` → `studioState='degradado'`, corpo inalterado; `nx test/lint` PASS
- Idempotency-Key enviado

**Dependencies:** INT-FE-COMM-001
**API / Contract impact:** `/api/v1/templates/{id}/studio/compose`.
**Risks / Notes:** latência síncrona — feedback de progresso (`composing`) obrigatório.
