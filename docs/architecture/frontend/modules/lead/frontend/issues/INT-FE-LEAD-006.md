## [INT-FE-LEAD-006] Integração: error-model (ProblemDetail → AppError)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 6 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
LEAD consome `@journeyos/shared/error-model` (`toAppError`) para normalizar `ProblemDetail` (RFC 7807)
do `lead-service` em `AppError`, alimentando a apresentação (banner/toast/erro de campo) e tratando
`lead.ia.indisponivel` como não-erro.

**Context / Problem statement:**
- Padroniza a tradução de erros do BE. Fonte: SPEC-07. Complementa FE-LEAD-008.
- Bloqueia: UX de erro (FE-LEAD-019).

**Approach (execution path):**
1) Integrar `toAppError` no pipeline de erro das facades.
2) Garantir mapeamento dos `error.code` do LEAD (404/409/422/5xx) + caso não-erro da IA.

**Non-goals:** componentes visuais (FE-LEAD-019).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`

**Architecture alignment:** `@journeyos/shared/error-model`; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 wiring de `toAppError` em `lead-error.util.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:lead · priority:P4

**Acceptance criteria:**
- `WHEN` BE retorna ProblemDetail, é mapeado para AppError (SPEC-07 EARS)
- `lead.ia.indisponivel` não vira erro de UI (SPEC-07 EARS)

**Dependencies:** FE-LEAD-008
**API / Contract impact:** consome catálogo de erros do `lead-service`.
**Risks / Notes:** manter alinhamento com o catálogo de `error.code` do BE.
