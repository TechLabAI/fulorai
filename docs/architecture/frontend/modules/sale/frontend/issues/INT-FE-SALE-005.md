## [INT-FE-SALE-005] Integração error-model (ProblemDetail → AppError end-to-end)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Liga o `sale-error.mapper` (FE-SALE-009) ao `@journeyos/shared/error-model` em toda a borda HTTP do
módulo: todo `ProblemDetail` (RFC 7807) do `sale-service` vira `AppError` **antes** de chegar às
features, com os 9 códigos SALE (`motivo-obrigatorio`, `ja-fechada`, `preco-invalido`, `soma-invalida`,
`nao-encontrada` opp/compra, `base-legal-invalida`, `receita-inconsistente`, `modelo-nao-encontrado`) +
`iam.token-invalido`/`iam.permissao-negada` roteados à Access Layer.

**Context / Problem statement:**
- Garante que nenhuma feature lida com `ProblemDetail` cru — só `AppError` com presentation.
- Fonte: SPEC-07 + cross-link (mapa error.code). Depende de INT-FE-SALE-001, FE-SALE-009.

**Approach (execution path):**
1) Plugar o mapper na borda HTTP (interceptor/handler do data-access).
2) Rotear `401`/`403` à Access Layer (sessão/bloqueio amigável).
3) Garantir que facades expõem `AppError` (não `HttpErrorResponse`).

**Non-goals:** componentes de feedback (FE-SALE-020); catálogo de códigos (FE-SALE-009).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-07-error-handling.md` · `contracts/backend-api-cross-link.md` (mapa error.code)

**Architecture alignment:** `@journeyos/shared/error-model`; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/errors/sale-error.interceptor.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:sale · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- Todo `ProblemDetail` → `AppError` antes da feature (EARS SPEC-07 #1); 401/403 roteados à Access Layer

**Dependencies:** INT-FE-SALE-001, FE-SALE-009
**Data impact:** Nenhum.
**API / Contract impact:** consome `ProblemDetail` de toda a superfície SALE.
**Testing / Evidence required:** teste end-to-end de mapeamento (HTTP erro → AppError).
**Risks / Notes:** R6 — isolar mudanças de contrato BE aqui.
