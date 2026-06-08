## [INT-FE-COMM-006] Wiring error-model (ProblemDetail → AppError → ui-feedback)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 11 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
`ProblemDetail` do comm-service convertido em `AppError` via `@journeyos/shared/error-model` e exibido
por `@journeyos/shared/ui-feedback` (inline/banner/toast) conforme SPEC-07.

**Context / Problem statement:**
- Erro consistente em todo o módulo. Fonte: SPEC-07 (C-07.1, C-07.7). Bloqueia: FE-COMM-008.

**Approach:**
1) Integrar `toAppError` ao interceptor/facades.
2) Mapear códigos `comm.*` (422/409/503) para apresentação correta.

**Non-goals:** mapper de domínio detalhado (FE-COMM-008).

**Layer(s):** frontend / `libs/comm/data-access` ↔ Access Layer
**Bounded context:** comm
**Service execution spec(s):** `SPEC-07-error-handling.md`
**Architecture alignment:** data-access→shared/error-model; tag `scope:comm`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring `toAppError` + apresentação `ui-feedback`

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:comm · priority:P4

**Acceptance criteria:**
- Todo erro vira AppError antes de exibir (C-07.1); inline/banner/toast por critério (C-07.7); `nx test/lint` PASS

**Dependencies:** INT-FE-COMM-001
**API / Contract impact:** todos os `comm.*` error codes (SPEC-07).
**Risks / Notes:** não expor `detail` cru com PII.
