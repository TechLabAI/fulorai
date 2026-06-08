## [FE-INTL-004] CopilotApiService — open/get/perguntar (+ AbortController)

**Status:** ⚪ INTACT — pós-validação 2026-06-05
**Maturidade:** 22 — Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`CopilotApiService` com `open(titulo?)` (`POST /copilot/conversas`), `get(id)` (`GET .../{id}`), `perguntar(id, texto, topK?)` (`POST .../{id}/perguntar`) — este último aceitando um `AbortSignal` para cancelamento.

**Context / Problem statement:**
- Base do chat. Fonte: SPEC-04 (Conversa).
- Bloqueia: FE-INTL-005 (facade).

**Approach (execution path):**
1) Service com `HttpClient`; tipos locais de request/response do api-contract.
2) `perguntar` passa `AbortSignal` (cancelamento de in-flight).
3) Mapeia `RespostaCopilotoResponse` cru (facade converte para VM).

**Non-goals:** otimismo/estado (facade, FE-INTL-005); UI (P3).

**Layer(s):** frontend / libs/intl/data-access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Conversa)

**Architecture alignment:** ADR-002; `type:data-access` `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/data-access/src/lib/copilot-api.service.ts` — MISSING: arquivo não existe (só placeholder)
- 🔲 `libs/intl/data-access/src/lib/copilot.dtos.ts` — MISSING: arquivo não existe

**Tests**
- 🔲 `nx test intl-data-access` PASS — MISSING: sem testes do service · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:intl · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS

**Dependencies:** FE-INTL-002 · INT-FE-INTL-004 (http-base)
**API / Contract impact:** `/api/v1/copilot/conversas**` (perm `intl.copilot.use/read`).
**Risks / Notes:** shape de `citacoes` pode evoluir no sync TechLab AI (R6) — tolerar `score` ausente.
