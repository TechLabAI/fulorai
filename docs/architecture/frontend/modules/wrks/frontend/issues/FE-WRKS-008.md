## [FE-WRKS-008] Error mapping (ProblemDetail→AppError) + facade reset

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Mapeamento central do error catalogue do WRKS (`api-contract.md`) para `AppError` via `@journeyos/shared/error-model`, e contrato `reset()` nas facades para invalidação na troca de empresa.

**Context / Problem statement:**
- Todas as facades precisam de mensagens user-facing consistentes (SPEC-07) e de descartar estado escopado na troca de empresa (ADR-005).

**Approach (execution path):**
1) Tabela `error.code → AppError` (SPEC-07) num mapper compartilhado da `data-access`.
2) Implementar `reset()` em todas as facades; ligar ao sinal de `EmpresaContextService`.
3) Definir apresentação (inline/toast/banner/redirect) como metadado do `AppError`.

**Non-goals:** UI de feedback (FE-WRKS-018); interceptor base (INT-FE-WRKS-004).

**Layer(s):** frontend / libs/wrks/data-access
**Bounded context:** wrks

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`, SPEC-04

**Architecture alignment:** `error-model` compartilhado; sem mensagens cruas de HTTP.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/data-access/src/lib/error/wrks-error.mapper.ts` (MISSING)
- 🔲 `libs/wrks/data-access/src/lib/facade-reset.ts` (mixin/util) (MISSING)

**Tests**
- 🔲 `nx test wrks-data-access` PASS (cada error.code mapeado) (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:wrks · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build wrks-data-access` PASS
- 100% dos `error.code` do catálogo WRKS cobertos

**Dependencies:** FE-WRKS-004..007
**API / Contract impact:** consome `application/problem+json` (RFC 7807).
**Risks / Notes:** `iam.sessao.versao-desatualizada` dispara re-eval (INT-FE-WRKS-006).
