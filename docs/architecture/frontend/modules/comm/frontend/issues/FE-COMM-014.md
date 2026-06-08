## [FE-COMM-014] feature-messages — detalhe + timeline de entrega (polling)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`MessageDetailPageComponent` + `MessageSummaryComponent` + `DeliveryTimelineComponent`, iniciando/encerrando
o polling (`startPolling/stopPolling`) conforme `estadoTerminal` e no `ngOnDestroy`. Modo refresh manual
quando `comm.delivery-tracking` está off.

**Context / Problem statement:**
- Rastreio quase-tempo-real (ADR-005). Fonte: SPEC-02, ADR-005. Depende: FE-COMM-007, FE-COMM-013.

**Approach:**
1) Page inicia polling ao abrir; timeline append-only (`eventosEntrega`).
2) Encerra ao atingir terminal (LIDA/FALHADA) e no destroy (C-06.4); para na troca de empresa.
3) Flag `comm.delivery-tracking` off → botão "atualizar" manual (C-05.4).

**Non-goals:** lista/disparo (FE-COMM-013).

**Layer(s):** frontend / `libs/comm/feature-messages` (+ `libs/comm/ui` timeline)
**Bounded context:** comm
**Service execution spec(s):** `SPEC-02`, `ADR-005`, `SPEC-05` (flag)
**Architecture alignment:** standalone/OnPush; cleanup obrigatório; tag `scope:comm` `type:feature`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/feature-messages/src/lib/message-detail.page.ts`
- 🔲 [MISSING] `libs/comm/feature-messages/src/lib/message-summary.component.ts`
- 🔲 [MISSING] `libs/comm/ui/src/lib/delivery-timeline.component.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-feature-messages` PASS (polling para no terminal/destroy) · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:comm · priority:P3

**Acceptance criteria:**
- Timeline evolui ENVIADA→ENTREGUE→LIDA; polling encerra em terminal e no destroy; flag off = refresh manual; `nx test/lint/build` PASS

**Dependencies:** FE-COMM-007, FE-COMM-013
**API / Contract impact:** `GET /messages/{id}` (+ `/events`).
**Risks / Notes:** cobre gaps C-05.4 e C-06.4; sem timers órfãos.
