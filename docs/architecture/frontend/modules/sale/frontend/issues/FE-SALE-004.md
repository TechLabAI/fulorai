## [FE-SALE-004] SaleShellIntegrationService + bootstrap (runtime)

**Status (validação):** REDUCED — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/sale/integration/SaleShellIntegrationService` (`onRegister`/`onActivate`/`onDeactivate`) consome
`NavigationService` + `AccessDecisionService` + `ModuleEventsService` para registrar metadata/flags,
publicar breadcrumb raiz e limpar ao sair. `sale.bootstrap.ts` (`saleBootstrap()`) subscreve a troca de
empresa (invalida pipeline/listas) e chama `onRegister()` no init; desfaz subscriptions no destroy.

**Context / Problem statement:**
- Camada runtime de descoberta/breadcrumb/sincronização de menu, distinta do fallback estático (FE-SALE-003).
- Fonte: SPEC-06 §2/§3. Depende de FE-SALE-001. Liga-se a INT-FE-SALE-002 (invalidação) e INT-FE-SALE-003 (registry).

**Approach (execution path):**
1) `SaleShellIntegrationService` com os 3 hooks; filtra menu/ações por `sale.*` via Access Layer.
2) `saleBootstrap()` subscreve `ModuleEventsService` (troca de empresa → invalidar) + `onRegister()`.
3) `onDeactivate()` limpa breadcrumbs do módulo no destroy.

**Non-goals:** lógica de invalidação por facade (INT-FE-SALE-002); guards (FE-SALE-018).

**Layer(s):** frontend / `libs/sale/integration`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-06-shell-integration.md` (§2, §3)

**Architecture alignment:** ADR-004; tag `scope:sale` `type:integration`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/integration/src/lib/sale-shell-integration.service.ts` — _MISSING: lib só tem stub default Nx (`sale-integration.component.ts`); serviço ausente_
- 🔲 `libs/sale/integration/src/lib/sale.bootstrap.ts` — _MISSING: arquivo ausente (nota: `shell-entry/sale.bootstrap.ts` tem corpos vazios, não wired)_

**Tests**
- 🔲 `nx test sale-integration` PASS — _MISSING_ · 🔲 `nx lint sale-integration` PASS — _MISSING_

**Milestone:** Wave P1 / Foundation
**Labels:** type:integration · layer:frontend · scope:sale · priority:P1

**Acceptance criteria:**
- `npx nx test/lint/build sale-integration` PASS
- Ao ativar o módulo, publica breadcrumb raiz + sincroniza menu (EARS SPEC-06 #3)

**Dependencies:** FE-SALE-001
**Data impact:** Nenhum.
**API / Contract impact:** nenhum direto.
**Testing / Evidence required:** teste dos hooks (register/activate/deactivate); subscription da troca de empresa.
**Risks / Notes:** não duplicar interceptors/Access Layer — reusar shared.
