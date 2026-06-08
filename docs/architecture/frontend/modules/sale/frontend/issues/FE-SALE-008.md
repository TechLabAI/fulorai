## [FE-SALE-008] Atribuicao + Ltv data-access (services + facades + fallback LAST_TOUCH)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/7 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`AtribuicaoApiService` (`list/criar/ativar/getBreakdown`) com `AttributionFacade` (modelos,
`modeloAtivo`, podeCriar/podeAtivar) e `LtvApiService` (`getByContato/list`) com
`RevenueDashboardFacade` (ltvTopContatos, funilReceita, periodo). `modeloAtivo === null` ⇒ a UI reflete
fallback **LAST_TOUCH**. O **funil de receita** usa o endpoint proposto `GET /api/v1/receita/funil` (gap
G1) e **degrada** para LTV-apenas/vazio se ausente.

**Context / Problem statement:**
- Atribuição (governança de modelos) + LTV/funil (dashboard). Map → `AttributionModelVm`/`LtvContactVm`/`RevenueFunnelSliceVm` de SPEC-03.
- Fonte: SPEC-04 (Atribuicao, Ltv) + SPEC-03. Depende de INT-FE-SALE-001. Bloqueia: FE-SALE-014, FE-SALE-015.

**Approach (execution path):**
1) `AtribuicaoApiService`: `GET /modelos`, `POST /modelos` (inativa), `POST /modelos/{versao}/activate`, `GET /compras/{id}/atribuicao`.
2) `AttributionFacade`: `modelos` (versao desc) + `modeloAtivo` (null → fallback LAST_TOUCH no badge).
3) `LtvApiService`: `GET /ltv/{contatoRef}`, `GET /ltv?page=&size=`.
4) `RevenueDashboardFacade`: `ltvTopContatos` + `funilReceita` (G1: tenta `GET /receita/funil`; degrada para vazio).

**Non-goals:** UI de atribuição/dashboard (FE-SALE-014/015); flag multi-touch (FE-SALE-017).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-04-data-access.md` (Atribuicao, Ltv) · `SPEC-03` · `contracts/backend-api-cross-link.md` (G1)

**Architecture alignment:** facade pattern; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/atribuicao-api.service.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/attribution.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/ltv-api.service.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/revenue-dashboard.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/mappers/{atribuicao,ltv}.mapper.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:sale · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- `modeloAtivo` null → fallback LAST_TOUCH refletido (EARS SPEC-03 — WHILE no active model); funil degrada sem `/receita/funil` (G1)

**Dependencies:** INT-FE-SALE-001
**Data impact:** Nenhum (sem cache).
**API / Contract impact:** `/api/v1/atribuicao/modelos`, `/compras/{id}/atribuicao`, `/ltv`, `/receita/funil` (proposto, G1).
**Testing / Evidence required:** teste do fallback LAST_TOUCH; teste de degradação do funil (endpoint ausente → vazio).
**Risks / Notes:** G1 — confirmar `/receita/funil` com BE ou derivar de Elastic; ativar modelo NÃO é otimista (R7 — refetch + "re-atribuição em andamento").
