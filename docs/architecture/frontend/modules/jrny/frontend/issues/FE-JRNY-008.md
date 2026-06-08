## [FE-JRNY-008] Error mapping (ProblemDetail → AppError) + retry policy

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Mapeamento dos `error.code` `jrny.*` (RFC 7807) para `AppError` via `@journeyos/shared/error-model`,
com mensagens user-facing e estratégia de apresentação (inline/banner/toast) conforme SPEC-07. Retry
**manual** em leituras; sem auto-retry; `assistIa=INDISPONIVEL` nunca vira erro.

**Context / Problem statement:**
- Centraliza o tratamento de erro do módulo; cobre gaps de leitura-falha e degradação graciosa.
- Fonte: SPEC-07. Cobre gap G-e (read-failure retry). Bloqueia: FE-JRNY-019.

**Approach (execution path):**
1) Tabela `error.code → mensagem + apresentação` (sem-estagio, transicao-invalida, ordem-duplicada, etc.).
2) Helper `toAppError(problem)` reusando `@journeyos/shared/error-model`.
3) Política: leitura → retry manual; mutação → inline/banner; IA-off → badge neutro (não erro).

**Non-goals:** UI dos states (FE-JRNY-019); reorder rollback (FE-JRNY-016).

**Layer(s):** frontend / `libs/jrny/data-access`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`

**Architecture alignment:** error-model compartilhado; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/data-access/src/lib/jrny-error.map.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/jrny-error.map.spec.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:jrny · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- Cada `error.code` do SPEC-07 mapeado; `assistIa=INDISPONIVEL` não produz AppError

**Dependencies:** FE-JRNY-004
**API / Contract impact:** consome `ProblemDetail` (api-contract §5).
**Risks / Notes:** não tratar degradação de IA como erro (ADR-005).
