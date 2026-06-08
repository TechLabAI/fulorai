## [INT-FE-WRKS-004] Integração access-http-base (interceptors)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 35 — Inicial
**Done/Total:** 0/4 itens (1 PARTIAL)

**Outcome:**
Todas as chamadas do WRKS passam por `@journeyos/shared/access-http-base` com interceptors de Correlation, `X-Empresa-Id` (debug) e ErrorNormalize, e `Authorization` Bearer.

**Context / Problem statement:**
- Pré-condição de toda a data-access (FE-WRKS-004..007). Fonte: access-layer-contracts, SPEC-04.

**Approach (execution path):**
1) Configurar `HttpBaseModule.forRoot({})` no Shell (escopo global).
2) Garantir que nenhum `*ApiService` usa `HttpClient` cru.
3) Validar header `X-Empresa-Id` automático (debug/log; nunca sobrepõe claim).

**Non-goals:** mapeamento de mensagens (FE-WRKS-008).

**Layer(s):** frontend / integração (apps + libs/wrks/data-access)
**Bounded context:** wrks

**Service execution spec(s):** `access-layer-contracts.md`; SPEC-04

**Architecture alignment:** check de aceite: toda chamada passa pelo interceptor.

**Implementation checklist (by file):**
- 🟡 `HttpBaseModule.forRoot({})` no Shell (PARTIAL) — `provideHttpBase({})` chamado em `apps/journey-os-web/src/app/app.config.ts`, mas a fachada `provideHttpBase` ainda é stub Wave-0 (registra ZERO interceptors); `apps/wrks` nao chama
- 🔲 verificação de uso exclusivo via `access-http-base` nos services (MISSING)

**Tests**
- 🔲 `nx test wrks-data-access` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:wrks · priority:P4

**Acceptance criteria:**
- Zero `HttpClient` direto em componentes/services fora do wrapper
- `npx nx test/lint` PASS

**Dependencies:** FE-WRKS-004..007
**API / Contract impact:** transversal a todos os endpoints `/api/v1/iam/**`.
**Risks / Notes:** `empresa_id` é claim JWT — header só para debug.
