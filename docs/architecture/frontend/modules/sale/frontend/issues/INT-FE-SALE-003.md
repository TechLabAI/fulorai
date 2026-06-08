## [INT-FE-SALE-003] Integração ModuleRegistry runtime (registro via descriptor)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 13 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`SaleShellIntegrationService.onRegister()` registra `SALE_MODULE_DESCRIPTOR` (metadata + flags + 15
permissões) no `ModuleRegistry` do Shell em runtime, complementando o fallback estático (FE-SALE-003).
No boot, o menu "Vendas" e os deep links ficam disponíveis e sincronizados com a Access Layer.

**Context / Problem statement:**
- Via runtime de descoberta (ADR-004), distinta do fallback estático em `module-descriptors.ts`.
- Fonte: SPEC-06 (§2) + SPEC-05 (descriptor). Depende de FE-SALE-003, FE-SALE-004.

**Approach (execution path):**
1) `onRegister()` publica metadata/flags/permissões no `ModuleRegistry`.
2) Sincronizar com `NavigationService` (menu filtrado por `sale.*`).

**Non-goals:** breadcrumbs (FE-SALE-019); menu permission-filter (INT-FE-SALE-004).

**Layer(s):** frontend / `libs/sale/integration`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-06-shell-integration.md` (§2) · `SPEC-05-module-contract.md`

**Architecture alignment:** ADR-004 module-registry; tag `scope:sale` `type:integration`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/integration/src/lib/sale-module-registry.integration.ts` — _MISSING (descriptor scaffold existe em shell-entry, mas registro runtime + module-descriptors.ts ausentes)_

**Tests**
- 🔲 `nx test sale-integration` PASS — _MISSING_ · 🔲 `nx lint sale-integration` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:sale · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build sale-integration` PASS
- Registro runtime expõe descriptor (key/permissions/flags) no ModuleRegistry (EARS SPEC-06)

**Dependencies:** FE-SALE-003, FE-SALE-004
**Data impact:** Nenhum.
**API / Contract impact:** nenhum.
**Testing / Evidence required:** teste de registro (metadata/flags/permissões publicadas).
**Risks / Notes:** fallback estático + runtime devem ser idempotentes (sem registro duplicado).
