## [FE-INTL-006] KnowledgeApiService + KnowledgeFacade

**Status:** ⚪ INTACT — pós-validação 2026-06-05
**Maturidade:** 22 — Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`KnowledgeApiService` (list/get/create/update/indexar/arquivar) + `KnowledgeFacade` (signals: `page()`, `filtros()`, `no()`, `indexState()`, `canWrite()` computed). Indexar trata `202` → `INDEXADO` e `503` → `RASCUNHO` + estado `retry`.

**Context / Problem statement:**
- Base da curadoria. Fonte: SPEC-04 (NoConhecimento) + SPEC-03.
- Bloqueia: FE-INTL-012, FE-INTL-013.

**Approach (execution path):**
1) Service com os 6 endpoints (`/knowledge/nos**`).
2) Facade: paginação + filtros (`q/tag/status/page/size`); `indexState` machine (`idle→indexando→indexado|retry`).
3) `canWrite` = `computed` via `AccessDecisionService.can('intl.knowledge.write')`.

**Non-goals:** UI (FE-INTL-012/013); error toast styling (FE-INTL-008).

**Layer(s):** frontend / libs/intl/data-access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (NoConhecimento)

**Architecture alignment:** ADR-002; signals; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/data-access/src/lib/knowledge-api.service.ts` — MISSING: service não existe
- 🔲 `libs/intl/data-access/src/lib/knowledge.facade.ts` — MISSING: facade não existe
- 🔲 `libs/intl/data-access/src/lib/knowledge.dtos.ts` — MISSING: dtos não existem

**Tests**
- 🔲 `nx test intl-data-access` PASS (indexar 202/503) — MISSING: sem testes · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:intl · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS
- Teste: 503 mantém `RASCUNHO` + `retry` (não erro fatal).

**Dependencies:** FE-INTL-002 · INT-FE-INTL-004
**API / Contract impact:** `/api/v1/knowledge/nos**` (perm `intl.knowledge.read/write`).
**Risks / Notes:** `409` (indexação concorrente) → recarregar (SPEC-07).
