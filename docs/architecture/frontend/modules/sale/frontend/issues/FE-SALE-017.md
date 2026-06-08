## [FE-SALE-017] Flag sale.attribution-multitouch (config multi-touch — gap G4)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 12 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Comportamento da flag `sale.attribution-multitouch` (default `disabled`): **off** → tela de atribuição
mantém o default determinístico **last-touch** (criar só LAST_TOUCH, sem config de pesos/touchpoints);
**on** → expõe a configuração multi-touch (FIRST_TOUCH/LINEAR com touchpoints configuráveis) no
`CreateAttributionModelDialogComponent`. Materializa o gap G4 do cross-link.

**Context / Problem statement:**
- Reserva pós-MVP: os tipos FIRST_TOUCH/LINEAR existem no enum, mas a config multi-touch fica atrás da flag.
- Fonte: SPEC-05 (flags) + cross-link G4. Depende de FE-SALE-001 (flag), FE-SALE-014 (tela).

**Approach (execution path):**
1) Ler a flag via Access Layer/feature-flags no `feature-attribution`.
2) Off → criar restrito a LAST_TOUCH (determinístico); badge "last-touch".
3) On → habilitar seleção de tipo + config multi-touch no dialog.

**Non-goals:** atribuição probabilística/ML (fora de escopo MVP); endpoint de config (BE).

**Layer(s):** frontend / `libs/sale/feature-attribution` + `libs/sale/shell-entry`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-05-module-contract.md` (flags) · `contracts/backend-api-cross-link.md` (G4)

**Architecture alignment:** module-pattern (feature-flags); tag `scope:sale` `type:feature`.

**Implementation checklist (by file):**
- 🟡 `libs/sale/feature-attribution/src/lib/attribution.page.ts` (gating multi-touch) — _PARTIAL_
- 🟡 `libs/sale/feature-attribution/src/lib/create-attribution-model-dialog.component.ts` (config condicional) — _PARTIAL_

**Tests**
- 🔲 `nx test sale-feature-attribution` PASS — _MISSING_ · 🔲 `nx lint sale-feature-attribution` PASS — _MISSING_

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:sale · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build sale-feature-attribution` PASS
- Flag off → default last-touch; on → config multi-touch exposta (EARS SPEC-05 — WHERE multitouch enabled)

**Dependencies:** FE-SALE-001, FE-SALE-014
**Data impact:** Nenhum.
**API / Contract impact:** nenhum (MVP); config multi-touch depende de contrato BE pós-MVP.
**Testing / Evidence required:** teste do gating (off/on); screenshots dos dois modos.
**Risks / Notes:** G4 — multi-touch é reserva; não bloquear o MVP last-touch.
