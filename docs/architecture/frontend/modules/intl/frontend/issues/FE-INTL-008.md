## [FE-INTL-008] Error mapping — ProblemDetail → AppError (503 retry, status desconhecido)

**Status:** ⚪ INTACT — pós-validação 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
Mapeamento central `ProblemDetail` → `AppError` (via `@journeyos/shared/error-model`) com as regras do SPEC-07: `503 embedding-unavailable` → retry (não fatal); `404` → empty; `409` → recarregar; `403` → banner; status de resposta do copiloto desconhecido → tratado como `DEGRADADA`.

**Context / Problem statement:**
- Particularidade do INTL: falha de IA não é erro. Fonte: SPEC-07 + SPEC-04.
- Bloqueia: FE-INTL-017 (UX polish), INT-FE-INTL-006.

**Approach (execution path):**
1) Função/serviço de mapeamento reutilizado pelas 3 facades.
2) Classificar `503` como retry; nunca tratar `DEGRADADA`/`NAO_FUNDAMENTADA` como erro.
3) Defensivo: status de resposta fora do enum → `DEGRADADA`.

**Non-goals:** componentes de UI de erro (FE-INTL-017).

**Layer(s):** frontend / libs/intl/data-access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`

**Architecture alignment:** `@journeyos/shared/error-model`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/data-access/src/lib/intl-error.mapper.ts` — MISSING: mapper não existe

**Tests**
- 🔲 `nx test intl-data-access` PASS (cada code → tratamento) — MISSING: sem testes · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:intl · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS
- Teste: `503 embedding-unavailable` → `retry`, não `AppError` fatal.

**Dependencies:** FE-INTL-004, FE-INTL-006, FE-INTL-007
**API / Contract impact:** consome `type` (RFC 7807) do BE (§4 api-contract).
**Risks / Notes:** `ai-unavailable` não deve chegar ao FE (BE degrada) — logar se chegar.
