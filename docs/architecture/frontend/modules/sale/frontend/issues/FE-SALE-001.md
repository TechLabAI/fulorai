## [FE-SALE-001] Module contract + permission-map + feature-flags

**Status (validação):** REDUCED — pós-validação 2026-06-05
**Maturidade:** 35 — Inicial
**Done/Total:** 1/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`sale.contract.ts`, `sale.permission-map.ts` e `sale.feature-flags.ts` materializados em
`libs/sale/shell-entry`, consistentes com SPEC-05: `MODULE_KEY = 'sale'`, `MODULE_MENU_METADATA` (label
"Vendas", route `/sale/pipeline`, icon `monetization_on`, 5 deep links — Pipeline/Ofertas/Compras/
Atribuição/Receita, este último com `flag: 'sale.revenue-dashboard'`), `SALE_PERMISSION_MAP` (15 perms
`sale.*`), `SALE_FEATURE_FLAGS` (`sale.revenue-dashboard` enabled, `sale.attribution-multitouch` disabled).

**Context / Problem statement:**
- O Shell descobre o módulo via o contrato; as 15 permissões devem casar com o catálogo BE (`sale.<recurso>.<acao>`).
- `sale.compra.registrar` **NÃO** entra no mapa do FE (ingestão server-to-server).
- Fonte: SPEC-05. Bloqueia: FE-SALE-002, FE-SALE-003, INT-FE-SALE-003.

**Approach (execution path):**
1) Preencher `sale.contract.ts` com menu metadata + 5 deep links (Receita com `flag`).
2) Mapear `SALE_PERMISSION_MAP` (15 perms `sale.*`) exatamente como SPEC-05.
3) Declarar flags `sale.revenue-dashboard` (enabled) e `sale.attribution-multitouch` (disabled — reserva pós-MVP, gap G4).

**Non-goals:** lógica de guard (FE-SALE-018); registro no Shell em runtime (FE-SALE-003 / INT-FE-SALE-003).

**Layer(s):** frontend / `libs/sale/shell-entry`
**Bounded context:** sale

**Service execution spec(s):** `frontend-spec/SPEC-05-module-contract.md`

**Architecture alignment:** module-pattern; Standalone/OnPush/Signals; tag `scope:sale` `type:domain`.

**Implementation checklist (by file):**
- 🟡 `libs/sale/shell-entry/src/lib/sale.contract.ts` — _PARTIAL: route `/sale` (spec espera `/sale/pipeline`); deepLinks vazio (spec espera 5); tipos são stubs locais_
- 🟡 `libs/sale/shell-entry/src/lib/sale.permission-map.ts` — _PARTIAL: 15 chaves `sale.*` presentes mas todos os arrays de papel vazios ([])_
- ✅ `libs/sale/shell-entry/src/lib/sale.feature-flags.ts` — _DONE: `sale.revenue-dashboard` enabled + `sale.attribution-multitouch` disabled_

**Tests**
- 🔲 `nx test sale-shell-entry` PASS — _MISSING_ · 🔲 `nx lint sale-shell-entry` PASS — _MISSING_

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:sale · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build sale-shell-entry` PASS
- 15 permissões idênticas às do `sale-service/contracts/api-contract.md` (sem inventar códigos; `registrar` ausente no FE)

**Dependencies:** — (fecha junto com scaffold)
**Data impact:** Nenhum.
**API / Contract impact:** consome `sale.*` permissions; nenhum endpoint direto.
**Testing / Evidence required:** snapshot do contrato; teste de chaves do permission-map.
**Risks / Notes:** manter sincronia papel→permissão com o bundle do BE (single source of truth). `sale.compra.registrar` deliberadamente fora do mapa.
