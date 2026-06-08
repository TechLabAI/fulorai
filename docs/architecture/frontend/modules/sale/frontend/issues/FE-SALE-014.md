## [FE-SALE-014] feature-attribution (modelos versionados: listar/criar/ativar + preview)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/7 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`feature-attribution` com `AttributionPageComponent` (smart) + `AttributionModelListComponent`
(+ `AttributionModelRowComponent`), `CreateAttributionModelDialogComponent`,
`AttributionBreakdownPreviewComponent`. Lista versões (versao desc) identificando a **ativa**; criar
nasce **inativa**; **ativar** re-atribui compras afetadas (BE) e desativa a anterior. Enquanto nenhuma
ativa, o badge mostra fallback **LAST_TOUCH**. Criar/ativar gated por `sale.atribuicao.criar/ativar`;
`soma-invalida` (409) → banner e não ativa; `modelo-nao-encontrado` (404) → inline na linha. **Sem
otimismo** em ativar (R7 — refetch + "re-atribuição em andamento").

**Context / Problem statement:**
- Governança dos modelos de atribuição (ROI por origem) — persona HEAD_GROWTH.
- Fonte: SPEC-02 (feature-attribution) + SPEC-03 (AttributionVM). Consome `AttributionFacade`.
- Depende de FE-SALE-008, FE-SALE-009, FE-SALE-016. Relaciona-se a FE-SALE-017 (flag multi-touch).

**Approach (execution path):**
1) `AttributionPageComponent` lê modelos/modeloAtivo/podeCriar/podeAtivar/saving/loading/error.
2) `AttributionModelListComponent` destaca a versão ativa; `ativar` → confirma + refetch (não otimista).
3) `CreateAttributionModelDialogComponent` cria versão inativa (tipo LAST_TOUCH/FIRST_TOUCH/LINEAR).
4) Banner `soma-invalida`; inline `modelo-nao-encontrado`; badge fallback LAST_TOUCH se sem ativa.

**Non-goals:** config multi-touch (atrás da flag — FE-SALE-017); breakdown da compra (FE-SALE-013).

**Layer(s):** frontend / `libs/sale/feature-attribution`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02` (feature-attribution) · `SPEC-03` (AttributionVM) · `SPEC-07` (soma-invalida)

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-attribution/src/lib/attribution.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-attribution/src/lib/attribution-model-list.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-attribution/src/lib/attribution-model-row.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-attribution/src/lib/create-attribution-model-dialog.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-attribution/src/lib/attribution-breakdown-preview.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-feature-attribution` PASS — _MISSING_ · 🔲 `nx lint sale-feature-attribution` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-attribution` PASS
- Ativar re-atribui (refetch, não otimista); fallback LAST_TOUCH sem ativa (EARS SPEC-03); `soma-invalida` → banner e não ativa (EARS SPEC-07)

**Dependencies:** FE-SALE-008, FE-SALE-009, FE-SALE-016
**Data impact:** Nenhum.
**API / Contract impact:** `/api/v1/atribuicao/modelos` (list/criar/activate).
**Testing / Evidence required:** e2e `attribution-model-activate`; screenshots (lista, ativar, soma-invalida).
**Risks / Notes:** R7 (efeito colateral com feedback claro), G4 (multi-touch atrás de flag — FE-SALE-017).
