## [FE-INTL-003] Registro no Shell (module-descriptor) + IntlShellIntegrationService

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`INTL_MODULE_DESCRIPTOR` registrado em `apps/journey-os-web/src/app/config/module-descriptors.ts`; `IntlShellIntegrationService` (onRegister/onActivate/onDeactivate) em `libs/intl/integration`. INTL aparece no menu do Shell (filtrado por RBAC) e carrega lazy.

**Context / Problem statement:**
- Espelha o registro de WRKS. Fonte: SPEC-06 + ADR-004.
- Bloqueia: e2e (FE-INTL-019); navegação do Shell.

**Approach (execution path):**
1) Importar `INTL_MODULE_DESCRIPTOR` de `@journeyos/intl` e adicioná-lo ao array do Shell.
2) Implementar `IntlShellIntegrationService` com lifecycle.
3) Verificar `nx build/lint journey-os-web` verdes com INTL registrado.

**Non-goals:** lifecycle de dados (P2); navegação/breadcrumb (FE-INTL-016).

**Layer(s):** frontend / apps/journey-os-web + libs/intl/integration
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md`

**Architecture alignment:** ADR-004/006; `type:domain` `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `apps/journey-os-web/src/app/config/module-descriptors.ts` (+ INTL) — MISSING: INTL não importado/registrado
- 🔲 `libs/intl/integration/src/lib/intl-shell-integration.service.ts` — MISSING: service não existe

**Tests**
- 🔲 `nx test intl-integration` PASS — MISSING: testes não rodados · 🔲 `nx lint` PASS — MISSING: lint não rodado · 🔲 `nx build journey-os-web` PASS — MISSING: build não rodado

**Milestone:** Wave P1 / Foundation
**Labels:** type:integration · layer:frontend · scope:intl · priority:P1

**Acceptance criteria:**
- `npx nx build journey-os-web` PASS com INTL_MODULE_DESCRIPTOR registrado
- `npx nx test/lint intl-integration` PASS

**Dependencies:** FE-INTL-001, FE-INTL-002
**API / Contract impact:** nenhum.
**Risks / Notes:** manter sincronia entre registro estático e runtime (SPEC-06).
