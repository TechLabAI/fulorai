## [FE-COMM-007] MessageApiService + MessageFacade (disparo + polling de entrega)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 13 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`MessageApiService` (`POST /messages` + `Idempotency-Key`, `GET /messages`, `GET /messages/{id}`,
`GET /messages/{id}/events`) + `MessageFacade` com signals `mensagens`, `mensagemSelecionada`,
`eventosEntrega`, `filtro`, `polling`, `computed estadoTerminal` e controle `startPolling/stopPolling`
(interval RxJS com backoff confinado à facade — ADR-005).

**Context / Problem statement:**
- Coração do disparo + rastreio. Fonte: SPEC-04, ADR-005. Depende: INT-FE-COMM-001. Bloqueia: FE-COMM-013, 014.

**Approach:**
1) Service com dispatch/list/get/listEvents; `Idempotency-Key` no dispatch (gerado por intenção).
2) Facade: `startPolling(id)` reconsulta com backoff; `estadoTerminal` (LIDA/FALHADA) encerra; `stopPolling()` no destroy/empresa-switch.
3) Sem otimismo no dispatch (só reflete após `202`); replay (`200`) não duplica.

**Non-goals:** UI (FE-COMM-013/014); webhooks (server-to-server, sem FE).

**Layer(s):** frontend / `libs/comm/data-access`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md`, `ADR-005-delivery-status-tracking.md`
**Architecture alignment:** signals-first; RxJS confinado à facade; tag `scope:comm` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/data-access/src/lib/message-api.service.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/message.facade.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/dtos/message.dto.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS (cobre backoff, parada no terminal, idempotência) · 🔲 [MISSING] `nx lint comm-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:comm · priority:P2

**Acceptance criteria:**
- Polling para em terminal e no `stopPolling()`; sem timers órfãos; `nx test/lint` PASS
- Idempotency-Key presente no dispatch; replay não cria nova mensagem

**Dependencies:** INT-FE-COMM-001
**API / Contract impact:** `/api/v1/messages` (+ `/events`).
**Risks / Notes:** cobre gaps C-04.5/C-04.5b/C-06.4 (parada do polling); curva de backoff a calibrar (A1 do `06`).
