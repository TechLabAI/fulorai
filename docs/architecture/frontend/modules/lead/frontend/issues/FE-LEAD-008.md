## [FE-LEAD-008] Error mapping: ProblemDetail → AppError + assist-IA não-erro

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Mapeamento dos `error.code` do LEAD para `AppError` (`@journeyos/shared/error-model`) e helpers para
apresentação (banner/toast/erro de campo) conforme SPEC-07. **`lead.ia.indisponivel` tratado como
não-erro** (badge "score determinístico").

**Context / Problem statement:**
- Centraliza a tradução de erros do BE para a UI; cobre **G6** (list-error→error signal). Fonte: SPEC-07.
- Bloqueia: P3 (features consomem o mapeamento) e P7 (UX polish).

**Approach (execution path):**
1) Mapa `error.code → {kind, apresentação}` (404/409/422/200-não-erro/5xx).
2) Helper para `assistIa`/`lead.ia.indisponivel`: nunca produz toast de erro.
3) Facades expõem `error` signal sem lançar para a árvore de componentes.

**Non-goals:** componentes visuais de erro (FE-LEAD-019); retry policy de UI (FE-LEAD-019).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`

**Architecture alignment:** `@journeyos/shared/error-model`; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/data-access/src/lib/lead-error.map.ts` — _MISSING_
- 🔲 `libs/lead/data-access/src/lib/lead-error.util.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:lead · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build lead-data-access` PASS
- `IF lead.ia.indisponivel`, nenhum erro de UI é produzido (SPEC-07 EARS)
- `IF` list falha, o erro é exposto via signal sem throw (SPEC-04 EARS)

**Dependencies:** FE-LEAD-004 (facades)
**API / Contract impact:** consome o catálogo de erros do `lead-service/api-contract.md`.
**Risks / Notes:** manter sincronia com o catálogo de `error.code` do BE.
