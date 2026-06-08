## [FE-SALE-003] SALE_MODULE_DESCRIPTOR + registro no Shell (journey-os-web)

**Status (validação):** REDUCED — pós-validação 2026-06-05
**Maturidade:** 35 — Inicial
**Done/Total:** 1/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`SALE_MODULE_DESCRIPTOR` (em `libs/sale/shell-entry/sale.descriptor.ts`) com `key: 'sale'`, `metadata`
(de `sale.contract.ts`), `loadChildren: () => import('@journeyos/sale').then(m => m.SALE_ROUTES)`,
`permissions: Object.keys(SALE_PERMISSION_MAP)`, `flags: SALE_FEATURE_FLAGS`; e o **registro efetivo**
adicionando `SALE_MODULE_DESCRIPTOR` à lista `MODULE_DESCRIPTORS` em
`apps/journey-os-web/src/app/config/module-descriptors.ts`. Menu "Vendas" aparece sem registro runtime.

**Context / Problem statement:**
- O descriptor é o fallback estático do Shell (ADR-004); o registro foi deferido para o implement P1, como nos demais módulos.
- Fonte: SPEC-06 §1. Depende de FE-SALE-001/002. Bloqueia: INT-FE-SALE-003.

**Approach (execution path):**
1) Criar `sale.descriptor.ts` exportando `SALE_MODULE_DESCRIPTOR`.
2) Importar `SALE_MODULE_DESCRIPTOR` em `module-descriptors.ts` e adicionar à lista.
3) Validar que `build journey-os-web` resolve o importPath `@journeyos/sale`.

**Non-goals:** integração runtime/breadcrumbs (FE-SALE-004 / INT-FE-SALE-003).

**Layer(s):** frontend / `libs/sale/shell-entry` + `apps/journey-os-web` (Shell)
**Bounded context:** sale

**Service execution spec(s):** `SPEC-06-shell-integration.md` (§1) · `adr/ADR-004`

**Architecture alignment:** ADR-004 module-registry; tag `scope:sale` `type:domain`.

**Implementation checklist (by file):**
- ✅ `libs/sale/shell-entry/src/lib/sale.descriptor.ts` — _DONE: `SALE_MODULE_DESCRIPTOR` com key/basePath/loadChildren/metadata/flags/permissionMap_
- 🔲 `apps/journey-os-web/src/app/config/module-descriptors.ts` (adicionar `SALE_MODULE_DESCRIPTOR`) — _MISSING: lista contém só `WRKS_MODULE_DESCRIPTOR`; SALE não registrado_

**Tests**
- 🔲 `nx test sale-shell-entry` PASS — _MISSING_ · 🔲 `nx lint sale-shell-entry` PASS — _MISSING_ · 🔲 `nx build journey-os-web` PASS — _MISSING_

**Milestone:** Wave P1 / Foundation
**Labels:** type:feature · layer:frontend · scope:sale · priority:P1

**Acceptance criteria:**
- `npx nx build journey-os-web` PASS (descriptor resolvido)
- Menu "Vendas" presente via fallback estático (EARS SPEC-06 #2); deep links filtrados por permissão

**Dependencies:** FE-SALE-001, FE-SALE-002
**Data impact:** Nenhum.
**API / Contract impact:** nenhum.
**Testing / Evidence required:** screenshot do menu "Vendas"; teste do descriptor (key/permissions/flags).
**Risks / Notes:** alterar `module-descriptors.ts` (arquivo compartilhado do Shell) — evitar conflito com outros módulos na mesma lista.
