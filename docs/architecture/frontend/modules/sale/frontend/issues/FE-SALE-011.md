## [FE-SALE-011] feature-opportunity (detalhe + histórico + ganhar/perder)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/7 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`feature-opportunity` com `OpportunityDetailPageComponent` (smart) + `OpportunityHeaderComponent`,
`StageHistoryTimelineComponent` (+ `StageHistoryItemComponent`), `WinOpportunityButtonComponent`,
`LoseOpportunityDialogComponent`. Mostra lead/valor/responsável/probabilidade/estado + **histórico de
estágio** (newest-first). **Ganhar** e **perder** gated por `sale.oportunidade.fechar`; **perder** exige
`motivo` (validação inline; `422 motivo-obrigatorio`). Em `GANHA`/`PERDIDA` os botões ficam desabilitados
(terminal). `404` → estado "oportunidade não encontrada".

**Context / Problem statement:**
- Detalhe do deal alcançado por deep-link do card.
- Fonte: SPEC-02 (feature-opportunity) + SPEC-03 (OpportunityDetailVM). Consome `OpportunityDetailFacade`.
- Depende de FE-SALE-005, FE-SALE-009, FE-SALE-016. Bloqueia: FE-SALE-023.

**Approach (execution path):**
1) `OpportunityDetailPageComponent` lê oportunidade/historico/podeFechar/saving/naoEncontrada/error.
2) `StageHistoryTimelineComponent` renderiza de→para estágio + ator + quando.
3) `WinOpportunityButtonComponent` (ganhar) + `LoseOpportunityDialogComponent` (motivo obrigatório, inline `422`).
4) `podeFechar = estado ∉ {GANHA,PERDIDA} && perm`; botões desabilitados no terminal.

**Non-goals:** Kanban (FE-SALE-010); navegação cross-módulo ao lead (só link, sem import scope:lead).

**Layer(s):** frontend / `libs/sale/feature-opportunity`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-02` (feature-opportunity) · `SPEC-03` (OpportunityDetailVM) · `SPEC-07` (motivo-obrigatorio, ja-fechada)

**Architecture alignment:** Standalone + OnPush + Signals; tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/feature-opportunity/src/lib/opportunity-detail.page.ts` — _MISSING_
- 🔲 `libs/sale/feature-opportunity/src/lib/opportunity-header.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-opportunity/src/lib/stage-history-timeline.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-opportunity/src/lib/win-opportunity-button.component.ts` — _MISSING_
- 🔲 `libs/sale/feature-opportunity/src/lib/lose-opportunity-dialog.component.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-feature-opportunity` PASS — _MISSING_ · 🔲 `nx lint sale-feature-opportunity` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-opportunity` PASS
- Perder sem motivo → inline `422` e não fecha (EARS SPEC-07); GANHA/PERDIDA desabilita ações (EARS SPEC-03 podeFechar)
- `404` → "oportunidade não encontrada" (EARS SPEC-01)

**Dependencies:** FE-SALE-005, FE-SALE-009, FE-SALE-016
**Data impact:** Nenhum.
**API / Contract impact:** `GET/POST /oportunidades/{id}` (+ ganhar/perder).
**Testing / Evidence required:** e2e `opportunity-win-loss`; screenshots (detalhe, terminal, erro motivo).
**Risks / Notes:** histórico vem completo no `GET /{id}` (suposição 06-risks); gap G2/G3 — titulo/responsavel = id se não enriquecido.
