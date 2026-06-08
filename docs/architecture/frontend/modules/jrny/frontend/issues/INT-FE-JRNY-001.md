## [INT-FE-JRNY-001] Integração HTTP base (access-http-base)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/2 itens

**Outcome:**
`libs/jrny/data-access` configurado com `@journeyos/shared/access-http-base` (`provideHttpBase`): toda
chamada `/api/v1/journeys/**` e `/api/v1/routing/**` leva JWT + `X-Empresa-Id` + `X-Correlation-Id`
automaticamente, com base URL do gateway.

**Context / Problem statement:**
- Pré-condição de todo data-access do módulo.
- Fonte: SPEC-04 (HTTP), access-layer-contracts. Bloqueia: FE-JRNY-004..007.

**Approach (execution path):**
1) Prover `HttpBase` no escopo do módulo; configurar base path.
2) Validar headers automáticos num teste de service.

**Non-goals:** mapeamento de erro (FE-JRNY-008).

**Layer(s):** frontend / `libs/jrny/data-access`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-04` · `standards/access-layer-contracts.md`

**Architecture alignment:** Access Layer; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/data-access/src/lib/jrny-http.providers.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:jrny · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- JWT + X-Empresa-Id anexados automaticamente (EARS #19)

**Dependencies:** — (base de P2)
**API / Contract impact:** gateway `/api/v1/**`.
**Risks / Notes:** não reimplementar interceptors — reusar o shared.
