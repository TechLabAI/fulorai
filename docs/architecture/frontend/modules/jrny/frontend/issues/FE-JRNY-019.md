## [FE-JRNY-019] UX polish: loading/empty/error states + retry

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Estados de loading/empty/error consistentes em todas as features (via `@journeyos/shared/ui-feedback`):
"jornada não encontrada", "sem inscrição", lista vazia; **retry manual** em falha de leitura (gap G-e);
sem auto-retry. Banner de `transicao-invalida` com CTA "criar nova versão".

**Context / Problem statement:**
- Fecha os estados não-felizes e os gaps de erro do Specs-Validate.
- Fonte: SPEC-07, SPEC-01 (estados vazios). Cobre gap G-e (read-failure retry).

**Approach (execution path):**
1) Padronizar loading/empty/error por feature reusando ui-feedback.
2) Estados vazios: jornada-not-found, sem-inscrição, lista vazia.
3) Falha de leitura → estado de erro com "tentar novamente"; banner transicao-invalida.

**Non-goals:** flags/a11y (FE-JRNY-020); observability (FE-JRNY-021).

**Layer(s):** frontend / `libs/jrny/feature-*` + `libs/jrny/styles`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-07-error-handling.md` · `SPEC-01`

**Architecture alignment:** ui-feedback compartilhado; tag conforme lib.

**Implementation checklist (by file):**
- 🔲 estados em `feature-journey-list/-builder/-decision-log/-routing-engine` (MISSING)
- 🔲 `libs/jrny/styles/src/lib/_states.scss` (MISSING)

**Tests**
- 🔲 `nx test` das features afetadas PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P7

**Acceptance criteria:**
- `npx nx test/lint/build` das libs afetadas PASS
- Falha de leitura → retry manual (gap G-e); estados vazios cobertos (EARS #4/#6)

**Dependencies:** FE-JRNY-008, FE-JRNY-009..014
**API / Contract impact:** consome `ProblemDetail`.
**Risks / Notes:** evitar auto-retry (pode mascarar erro do BE).
