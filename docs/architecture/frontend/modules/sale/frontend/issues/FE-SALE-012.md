## [FE-SALE-012] feature-offer (catálogo versionado + form nova versão + desativar)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/10 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`feature-offer` com `OfferListPageComponent` (+ `OfferFilterBarComponent`, `OfferRowComponent`,
`CreateOfferDialogComponent`) e `OfferDetailPageComponent` (+ `OfferVersionListComponent`,
`OfferFormComponent`, `DeactivateOfferButtonComponent`). Catálogo paginado/filtrado; **editar salva como
nova versão** (a versão exibida nunca é mutada); `OfferVersionListComponent` lista versões anteriores
read-only. Criar/editar/desativar gated por `sale.oferta.criar/editar/desativar`; `preco-invalido` inline.

**Context / Problem statement:**
- Governança do catálogo versionado (produto+preço+moeda+vigência).
- Fonte: SPEC-02 (feature-offer) + SPEC-03 (offer). Consome `OfferListFacade`/`OfferDetailFacade`.
- Depende de FE-SALE-006, FE-SALE-009, FE-SALE-016. Bloqueia: FE-SALE-023.

**Approach (execution path):**
1) `OfferListPageComponent` lê ofertas/filtro/podeCriar; `OfferRowComponent` → abrir.
2) `OfferDetailPageComponent` lê oferta/versoes/editavel/erros.
3) `OfferFormComponent` salvar → nova versão (refetch); `preco-invalido` inline no campo preço.
4) `DeactivateOfferButtonComponent` gated por `sale.oferta.desativar`.

**Non-goals:** data-access (FE-SALE-006); empty/error states genéricos (FE-SALE-020).

**Layer(s):** frontend / `libs/sale/feature-offer`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02` (feature-offer) · `SPEC-03` (offer) · `SPEC-07` (preco-invalido)

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-offer/src/lib/offer-list.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-offer/src/lib/offer-filter-bar.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-offer/src/lib/offer-row.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-offer/src/lib/create-offer-dialog.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-offer/src/lib/offer-detail.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-offer/src/lib/offer-version-list.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-offer/src/lib/offer-form.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-offer/src/lib/deactivate-offer-button.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-feature-offer` PASS — _MISSING_ · 🔲 `nx lint sale-feature-offer` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-offer` PASS
- Editar cria nova versão (anteriores imutáveis na lista); `preco-invalido` inline e não cria versão (EARS SPEC-07)
- Criar/editar/desativar gated por permissão

**Dependencies:** FE-SALE-006, FE-SALE-009, FE-SALE-016
**Data impact:** Nenhum.
**API / Contract impact:** `/api/v1/ofertas` (list/get/create/PUT/desativar).
**Testing / Evidence required:** e2e `offer-versioning`; screenshots (lista, detalhe versões, erro preço).
**Risks / Notes:** versão exibida nunca é mutada — `OfferVersionListComponent` é read-only.
