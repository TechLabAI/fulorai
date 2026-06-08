## [INT-FE-ASST-006] Integração error-model (ProblemDetail → AppError → ui-feedback)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
O ASST consome `@journeyos/shared/error-model` (`toAppError`) e `@journeyos/shared/ui-feedback` para
renderizar os erros mapeados em SPEC-07 (inline/toast/banner/página), incluindo a degradação do Studio.

**Context / Problem statement:**
- Fecha o contrato de erro end-to-end. Fonte: SPEC-07. Depende de FE-ASST-008, FE-ASST-018. Bloqueia: —.

**Approach (execution path):**
1) Conectar `toAsstError` (FE-ASST-008) ao `error-model` shared, garantindo o shape `AppError`.
2) Renderizar via `ui-feedback` conforme o critério SPEC-07.
3) Validar o caso `503` (banner de degradação) não vaza para bloquear o módulo.

**Non-goals:** mapper de domínio em si (FE-ASST-008).

**Layer(s):** frontend / `libs/asst/feature-*` + `data-access`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-07-error-handling.md`

**Architecture alignment:** `data-access → shared/error-model`; features → `shared/ui-feedback`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring `toAppError` + render `ui-feedback` nas features

**Tests**
- 🔲 [MISSING] `nx test asst-feature-*` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:asst · priority:P4

**Acceptance criteria:**
- Cada `code` SPEC-07 renderiza na superfície correta; `503` = banner não-bloqueante

**Dependencies:** FE-ASST-008, FE-ASST-018
**API / Contract impact:** consome `ProblemDetail` do `asst-service`.
**Risks / Notes:** mensagens pt-BR (humano); chaves técnicas en-US.
