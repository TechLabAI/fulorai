## [FE-COMM-013] feature-messages — lista + disparo 1:1 (idempotência)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`MessagesListPageComponent` (filtros lead/canal/estado/período) + `MessageListComponent`/`MessageRowComponent`
+ `DispatchDialogComponent` (template ATIVO + leadId + variaveis; envia `Idempotency-Key`; desabilita
botão durante o request). Consome `MessageFacade`.

**Context / Problem statement:**
- Disparo idempotente + histórico. Fonte: SPEC-02, SPEC-03. Depende: FE-COMM-007. Bloqueia: FE-COMM-014.

**Approach:**
1) Lista paginada com filtros + estados de entrega (chip).
2) Dialog de disparo: valida template ATIVO (UINV-3), variáveis obrigatórias, gera/reusa `Idempotency-Key` (UINV-4).
3) Sem otimismo — reflete após `202`; replay (`200`) não duplica.

**Non-goals:** detalhe/timeline (FE-COMM-014).

**Layer(s):** frontend / `libs/comm/feature-messages`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-02`, `SPEC-03`, `SPEC-07`
**Architecture alignment:** standalone/OnPush; tag `scope:comm` `type:feature`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/feature-messages/src/lib/messages-list.page.ts`
- 🔲 [MISSING] `libs/comm/feature-messages/src/lib/message-list.component.ts`
- 🔲 [MISSING] `libs/comm/feature-messages/src/lib/dispatch.dialog.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-feature-messages` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:comm · priority:P3

**Acceptance criteria:**
- Duplo clique = 1 envio; template não-ATIVO bloqueia; variável ausente sinalizada; `nx test/lint/build` PASS

**Dependencies:** FE-COMM-007
**API / Contract impact:** `POST /messages`, `GET /messages`.
**Risks / Notes:** ponto de entrada do disparo (vs. detalhe do lead em LEAD) — confirmar no implement (gap `06`).
