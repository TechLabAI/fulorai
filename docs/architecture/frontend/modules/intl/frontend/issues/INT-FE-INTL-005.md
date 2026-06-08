## [INT-FE-INTL-005] Integração — Shell lifecycle (IntlShellIntegrationService)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`IntlShellIntegrationService` (lifecycle `onRegister`/`onActivate`/`onDeactivate`) + `intl.bootstrap.ts` ligados ao Shell: registra menu, assina `empresa-context` e `modelo.acesso.alterado`, e reseta facades no deactivate.

**Context / Problem statement:**
- Liga o módulo ao ciclo de vida do Shell. Fonte: SPEC-06.
- Depende do registro estático (FE-INTL-003).

**Approach (execution path):**
1) Implementar lifecycle no service.
2) `intlModuleInit/Destroy` chamando o lifecycle; cancelar in-flight no destroy.

**Non-goals:** descriptor estático (FE-INTL-003).

**Layer(s):** frontend / libs/intl/integration + shell-entry
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md`

**Architecture alignment:** ADR-004; `type:domain` `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/integration/src/lib/intl-shell-integration.service.ts` (lifecycle) — MISSING: só placeholder component, sem service
- 🔲 `libs/intl/shell-entry/src/lib/intl.bootstrap.ts` (init/destroy reais) — MISSING: bootstrap não implementado

**Tests**
- 🔲 `nx test intl-integration` PASS — MISSING: sem teste de deactivate/reset · 🔲 `nx lint` PASS — MISSING: não executado nesta baseline

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:intl · priority:P4

**Acceptance criteria:**
- `npx nx test/lint intl-integration` PASS
- Teste: deactivate cancela assinaturas + reseta facades.

**Dependencies:** FE-INTL-003 · INT-FE-INTL-002
**API / Contract impact:** consome eventos `modelo.acesso.alterado` (via Access Layer).
**Risks / Notes:** —
