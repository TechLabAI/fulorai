## [INT-FE-SALE-001] Integração HTTP base (access-http-base) + auth/JWT

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/sale/data-access` configurado com `@journeyos/shared/access-http-base` (`provideHttpBase`): toda
chamada `/api/v1/oportunidades/**`, `/ofertas`, `/compras`, `/atribuicao`, `/ltv` leva **JWT** +
`X-Empresa-Id` + `X-Correlation-Id` automaticamente, com base URL do gateway. Sessão/JWT via
`@journeyos/shared/auth-session`.

**Context / Problem statement:**
- Pré-condição de todo data-access do módulo (P2 depende disto).
- Fonte: SPEC-04 (HTTP) + access-layer-contracts + _brief (auth-session obrigatório). Bloqueia: FE-SALE-005..009.

**Approach (execution path):**
1) Prover `HttpBase` no escopo do módulo; configurar base path do gateway.
2) Validar headers automáticos (JWT/X-Empresa-Id/X-Correlation-Id) num teste de service.

**Non-goals:** mapeamento de erro (FE-SALE-009); invalidação por empresa (INT-FE-SALE-002).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-04-data-access.md` · `standards/access-layer-contracts.md`

**Architecture alignment:** Access Layer; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/sale-http.providers.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:sale · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- JWT + X-Empresa-Id + X-Correlation-Id anexados automaticamente (EARS SPEC-04 #1)

**Dependencies:** — (base de P2; corre antes das facades)
**Data impact:** Nenhum.
**API / Contract impact:** gateway `/api/v1/**`.
**Testing / Evidence required:** teste de header em chamada SALE.
**Risks / Notes:** não reimplementar interceptors — reusar o shared.
