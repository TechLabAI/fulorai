## [FE-SALE-009] Error mapping (ProblemDetail → AppError → apresentação)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`sale-error.mapper.ts` em `libs/sale/data-access` traduz `ProblemDetail` (RFC 7807) → `AppError`
(`@journeyos/shared/error-model`) para **todos** os `error.code` SALE de SPEC-07, com a estratégia de
apresentação por código (inline / banner / toast / estado vazio): `motivo-obrigatorio` (422 inline),
`ja-fechada` (409 rollback+toast/banner), `preco-invalido` (422 inline), `soma-invalida` (409 banner),
`nao-encontrada` opp/compra (404 vazio), `base-legal-invalida`/`receita-inconsistente` (422 banner),
`modelo-nao-encontrado` (404 inline).

**Context / Problem statement:**
- Centraliza o catálogo de erros para que as features apenas escolham a superfície (inline/banner/toast).
- Fonte: SPEC-07 + cross-link (mapa error.code). Depende de INT-FE-SALE-001. Usado por todas as features P3 + INT-FE-SALE-005.

**Approach (execution path):**
1) Mapear cada `error.code` → `AppError` com `presentation` ('inline'|'banner'|'toast'|'empty') e mensagem pt-BR de SPEC-07.
2) Tratar `iam.token-invalido` (401 → Access Layer) e `iam.permissao-negada` (403 → bloqueio amigável).
3) Expor helper para leituras (retry manual) vs mutações (sem retry automático).

**Non-goals:** componentes de feedback (FE-SALE-020); guards (FE-SALE-018).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-07-error-handling.md` · `contracts/backend-api-cross-link.md` (mapa error.code)

**Architecture alignment:** `@journeyos/shared/error-model`; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/errors/sale-error.mapper.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/errors/sale-error.codes.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:sale · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- Cada `error.code` de SPEC-07 mapeado a `AppError` + presentation correta (EARS SPEC-07 #1)

**Dependencies:** INT-FE-SALE-001
**Data impact:** Nenhum.
**API / Contract impact:** consome `ProblemDetail` de toda a superfície SALE.
**Testing / Evidence required:** teste por código (9 códigos SALE + 2 iam); assert da presentation.
**Risks / Notes:** R6 — contratos BE podem mudar; isolar adaptação de erro aqui.
