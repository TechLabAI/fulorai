## [FE-SALE-007] Compra data-access (service + list/detail facades; NO create)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/6 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`CompraApiService` com `list/get/estornar/cancelar` (**sem `create`**) e facades `PurchaseListFacade` /
`PurchaseDetailFacade` expondo signals readonly (compras, filtro; compra com `baseLegal`/comprador,
itens, atribuicao, podeAjustar, naoEncontrada). `getBreakdown` (atribuição de uma compra) é exposto ao
detalhe. `podeAjustar = status CONFIRMADA && (perm estornar||cancelar)`.

**Context / Problem statement:**
- Compra é **read + estornar/cancelar** no FE; ingestão (`POST /compras`) é server-to-server (não existe no FE).
- Fonte: SPEC-04 (Compra) + SPEC-03 (purchase). Depende de INT-FE-SALE-001. Bloqueia: FE-SALE-013.

**Approach (execution path):**
1) `CompraApiService`: `GET ?contato=&status=&periodo=&page=&size=`, `GET /{id}`, `POST /{id}/estornar`, `POST /{id}/cancelar`. **Sem método `create`.**
2) `PurchaseListFacade`: `compras`/`filtro`.
3) `PurchaseDetailFacade`: `compra`/`itens`/`atribuicao`/`podeAjustar`; `naoEncontrada` em `404`.
4) Mapear BE → `PurchaseRowVm`/`PurchaseItemVm`/`AttributionLineVm` (Σ valorAtribuido = valorTotal).

**Non-goals:** UI/confirmação destrutiva (FE-SALE-013); criação de compra (fora de escopo — NUNCA no FE).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-04-data-access.md` (Compra) · `SPEC-03-view-models.md` (purchase)

**Architecture alignment:** facade pattern; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/compra-api.service.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/purchase-list.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/purchase-detail.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/mappers/compra.mapper.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:sale · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- Service **não expõe** operação create-compra (EARS SPEC-04 #4); `naoEncontrada` em 404

**Dependencies:** INT-FE-SALE-001
**Data impact:** carrega PII do comprador (`contatoRef`/baseLegal) só na view de detalhe (LGPD).
**API / Contract impact:** `/api/v1/compras` (list/get/estornar/cancelar) + `/compras/{id}/atribuicao`.
**Testing / Evidence required:** teste garantindo ausência de `create`; teste de `podeAjustar`.
**Risks / Notes:** R5 — não criar afford de "registrar compra"; estornar/cancelar recalculam receita/LTV no BE.
