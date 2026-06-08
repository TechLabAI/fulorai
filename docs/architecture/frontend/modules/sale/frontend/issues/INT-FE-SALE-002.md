## [INT-FE-SALE-002] Integração empresa-context (isolamento + invalidação na troca)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`effect()` nas facades reage a `EmpresaContextService`: na troca de empresa, invalida pipeline/listas
(ofertas/compras/atribuição/dashboard) + seleção em tela **antes** de carregar os dados da nova empresa —
sem vazamento cross-empresa (LGPD).

**Context / Problem statement:**
- Isolamento multi-empresa é requisito; cobre a invalidação de estado do board/listas.
- Fonte: SPEC-04 (invalidação) + SPEC-06 (bootstrap) + 06-risks R8 + _brief (empresa-context obrigatório).
- Depende de INT-FE-SALE-001 + facades P2.

**Approach (execution path):**
1) Observar empresa ativa; ao mudar, resetar signals do módulo (board/listas/seleção).
2) Garantir que nenhum dado da empresa anterior permaneça visível antes do novo fetch.

**Non-goals:** guards (FE-SALE-018); bootstrap/registro (FE-SALE-004).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-04-data-access.md` (invalidação) · `SPEC-06` · `06-risks-gaps-assumptions.md` (R8)

**Architecture alignment:** Signals `effect()`; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/empresa-invalidation.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:sale · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- Troca de empresa invalida board/listas antes de recarregar (EARS SPEC-04 — invalidação)

**Dependencies:** INT-FE-SALE-001, FE-SALE-005
**Data impact:** sem vazamento cross-empresa (LGPD).
**API / Contract impact:** nenhum direto.
**Testing / Evidence required:** e2e `empresa-switch-isolation`; teste de reset de signals.
**Risks / Notes:** R8 — evitar flicker entre invalidação e recarga.
