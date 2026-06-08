## [FE-COMM-008] ChannelApiService + ChannelFacade + error mapping

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 13 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`ChannelApiService` (`GET/POST /channels`, `PATCH /channels/{id}`) + `ChannelFacade` com signal
`canais` (`credencialRefMascarada`, sem segredo) + mapeamento central `ProblemDetail → AppError`
(`@journeyos/shared/error-model`) para os códigos `comm.*` do SPEC-07.

**Context / Problem statement:**
- Config de canal + base de tratamento de erro do módulo. Fonte: SPEC-04, SPEC-07. Depende: INT-FE-COMM-001, INT-FE-COMM-006. Bloqueia: FE-COMM-015.

**Approach:**
1) Service com list/create/update; nunca trafega segredo (só `credencialRef`).
2) Facade expõe `canais` readonly.
3) Helper `toAppError` mapeando os códigos `comm.*` (422/409/503) para mensagens user-facing.

**Non-goals:** UI (FE-COMM-015); UI de erro/polish (FE-COMM-018).

**Layer(s):** frontend / `libs/comm/data-access`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md`, `SPEC-07-error-handling.md`
**Architecture alignment:** signals-first; segredo nunca no FE (UINV-6); tag `scope:comm` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/data-access/src/lib/channel-api.service.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/channel.facade.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/comm-error.mapper.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS (cobre mapeamento de códigos) · 🔲 [MISSING] `nx lint comm-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:comm · priority:P2

**Acceptance criteria:**
- `credencialRef` sempre mascarada; nenhum segredo exibido; `nx test/lint` PASS
- Códigos `comm.*` mapeados conforme SPEC-07

**Dependencies:** INT-FE-COMM-001, INT-FE-COMM-006
**API / Contract impact:** `/api/v1/channels`.
**Risks / Notes:** `janelaEnvio` formato a confirmar com BE (gap do `06`/cross-link).
