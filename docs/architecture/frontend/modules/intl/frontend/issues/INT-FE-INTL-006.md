## [INT-FE-INTL-006] Integração — error-model (ProblemDetail → AppError → ui-feedback)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
INTL consome `@journeyos/shared/error-model` (`toAppError`) e `@journeyos/shared/ui-feedback` para apresentar erros segundo o SPEC-07 (banner/toast/inline/empty), com `503 embedding-unavailable` tratado como retry.

**Context / Problem statement:**
- Apresentação consistente de erro. Fonte: SPEC-07 + FE-INTL-008.
- Complementa o mapper de domínio.

**Approach (execution path):**
1) Ligar o `intl-error.mapper.ts` (FE-INTL-008) ao `toAppError` compartilhado.
2) Padronizar a apresentação (toast/banner/inline/empty) via `ui-feedback`.

**Non-goals:** lógica de classificação (FE-INTL-008).

**Layer(s):** frontend / libs/intl/data-access + feature-*
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`

**Architecture alignment:** consome `@journeyos/shared/error-model` + `ui-feedback`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 wiring `toAppError` + apresentação nas features — MISSING: sem mapper/ui-feedback ligado

**Tests**
- 🔲 `nx test intl-data-access intl-feature-*` PASS — MISSING: sem teste de apresentação de erro · 🔲 `nx lint` PASS — MISSING: não executado nesta baseline

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:intl · priority:P4

**Acceptance criteria:**
- `npx nx test/lint intl-data-access` PASS
- Teste: `403` → banner; `409`/`5xx` → toast; `503` → inline retry.

**Dependencies:** FE-INTL-008
**API / Contract impact:** consome `type` RFC 7807 do BE.
**Risks / Notes:** falha de IA do copiloto não passa por aqui (é estado, não erro).
