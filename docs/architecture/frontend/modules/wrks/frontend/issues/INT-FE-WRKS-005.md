## [INT-FE-WRKS-005] WrksShellIntegrationService + bootstrap lifecycle

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
`WrksShellIntegrationService` registra a module em runtime (onRegister/onActivate/onDeactivate) e `wrks.bootstrap.ts` faz init/destroy (assina empresa-context + modelo_acesso_versao; reset de facades no destroy).

**Context / Problem statement:**
- Camada runtime do ADR-004. Fonte: SPEC-06.

**Approach (execution path):**
1) Implementar `WrksShellIntegrationService` (registro de metadata + permission map).
2) `wrks.bootstrap.ts`: assinar troca de empresa (reset breadcrumbs) e versão de acesso.
3) destroy: cancelar assinaturas + `reset()` facades.

**Non-goals:** descriptor estático (FE-WRKS-003).

**Layer(s):** frontend / libs/wrks/integration + apps/wrks <module>-module
**Bounded context:** wrks

**Service execution spec(s):** SPEC-06

**Architecture alignment:** ADR-004 (runtime registry).

**Implementation checklist (by file):**
- 🔲 `libs/wrks/integration/src/lib/wrks-shell-integration.service.ts` (MISSING) — arquivo inexistente; `libs/wrks/integration` só tem o componente stub default do Nx
- 🔲 `apps/wrks/src/app/wrks-module/wrks.bootstrap.ts` (MISSING) — inexistente; existe apenas `libs/wrks/shell-entry/src/lib/wrks.bootstrap.ts` com corpos vazios (só comentários)

**Tests**
- 🔲 `nx test wrks-integration` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:wrks · priority:P4

**Acceptance criteria:**
- Registro runtime funciona; destroy limpa estado escopado
- `npx nx test/lint` PASS

**Dependencies:** FE-WRKS-001, FE-WRKS-003, INT-FE-WRKS-002
**API / Contract impact:** nenhum direto.
**Risks / Notes:** WRKS é fundação — não fazer trabalho pesado em onActivate.
