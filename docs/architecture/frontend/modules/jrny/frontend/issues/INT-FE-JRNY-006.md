## [INT-FE-JRNY-006] Integração error-model + ui-feedback

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/2 itens

**Outcome:**
Pipeline de erro do módulo ligado a `@journeyos/shared/error-model` (`toAppError`) e
`@journeyos/shared/ui-feedback` (toast/banner/inline): o mapa de `error.code` `jrny.*` (FE-JRNY-008) é
renderizado de forma consistente; `assistIa=INDISPONIVEL` nunca passa pelo pipeline de erro.

**Context / Problem statement:**
- Conecta o mapeamento de erro às primitivas de feedback compartilhadas.
- Fonte: SPEC-07. Cobre EARS #34.

**Approach (execution path):**
1) Ligar `toAppError` + apresentação (inline/banner/toast) por tipo de erro.
2) Garantir degradação graciosa de IA fora do caminho de erro.

**Non-goals:** o mapa em si (FE-JRNY-008).

**Layer(s):** frontend / `libs/jrny/data-access` + `libs/jrny/feature-*`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-07-error-handling.md`

**Architecture alignment:** error-model + ui-feedback compartilhados; tag conforme lib.

**Implementation checklist (by file):**
- 🚧 wiring de `toAppError` + `ui-feedback` nas features (BLOCKED: depende de FE-JRNY-008 nao implementado; sem import de error-model/ui-feedback em libs/jrny)

**Tests**
- 🔲 `nx test` libs afetadas PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:jrny · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build` libs afetadas PASS
- `ProblemDetail → AppError` consistente (EARS #34); IA-off fora do pipeline de erro

**Dependencies:** FE-JRNY-008
**API / Contract impact:** consome `ProblemDetail`.
**Risks / Notes:** não duplicar mapeamento — fonte única em FE-JRNY-008.
