## [FE-SALE-006] Oferta data-access (service + list/detail facades + versionamento)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/6 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`OfertaApiService` com `list/get/create/editar/desativar` e facades `OfferListFacade` /
`OfferDetailFacade` expondo signals readonly (ofertas, filtro, podeCriar; oferta, versoes, editavel,
erros). `editar` (`PUT`) é tratado como **criação de nova versão** (a versão exibida nunca é mutada);
`OfferDetailFacade.versoes` lista versões anteriores imutáveis.

**Context / Problem statement:**
- Catálogo versionado. Map oferta BE → `OfferRowVm` (versao/ativo/vigência) de SPEC-03.
- Fonte: SPEC-04 (Oferta) + SPEC-03 (offer). Depende de INT-FE-SALE-001. Bloqueia: FE-SALE-012.

**Approach (execution path):**
1) `OfertaApiService`: `GET ?q=&ativo=&page=&size=`, `GET /{id}`, `POST`, `PUT /{id}`, `POST /{id}/desativar`.
2) `OfferListFacade`: `ofertas`/`filtro`/`podeCriar`.
3) `OfferDetailFacade`: `oferta`/`versoes`/`editavel`/`erros`; salvar → refetch (nova versão).
4) Mapear BE → `OfferRowVm`.

**Non-goals:** UI do catálogo/form (FE-SALE-012); mapping de `preco-invalido` para inline (FE-SALE-009).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-04-data-access.md` (Oferta) · `SPEC-03-view-models.md` (offer)

**Architecture alignment:** facade pattern; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/oferta-api.service.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/offer-list.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/offer-detail.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/mappers/oferta.mapper.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:sale · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- `editar` cria nova versão (refetch) sem mutar a exibida (EARS SPEC-04 — nova versão)

**Dependencies:** INT-FE-SALE-001
**Data impact:** Nenhum (sem cache).
**API / Contract impact:** `/api/v1/ofertas` (list/get/create/PUT/desativar).
**Testing / Evidence required:** teste de versionamento (PUT → nova versão na lista de versões).
**Risks / Notes:** estados terminais imutáveis — `versoes` é read-only.
