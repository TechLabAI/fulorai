## [INT-FE-LEAD-005] Integração: ModuleShellIntegrationService (registro runtime)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 12 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`LeadShellIntegrationService` (em `libs/lead/integration`) implementa `onRegister/onActivate/onDeactivate`,
registrando metadata/permissões/flags no Shell registry em runtime e inicializando/limpando o estado
de navegação. Substitui/atualiza o descriptor por key `lead` (sem duplicar).

**Context / Problem statement:**
- Complementa o registro estático (FE-LEAD-003) com o registro runtime (TCE em prod). Fonte: SPEC-06.

**Approach (execution path):**
1) Implementar o service com o lifecycle.
2) Chamar `onRegister` no `lead.bootstrap.ts`; `onActivate/onDeactivate` nas transições do módulo.
3) Replace por key `lead` (idempotente).

**Non-goals:** layout do Shell.

**Layer(s):** frontend / `libs/lead/integration`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-06-shell-integration.md`

**Architecture alignment:** ADR-004; tag `scope:lead` `type:domain`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/integration/src/lib/lead-shell-integration.service.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-integration` PASS — _MISSING_ · 🔲 `nx lint lead-integration` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:lead · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build lead-integration` PASS
- `IF` registry já tem `lead`, faz replace (SPEC-06 EARS); ativar/desativar gerencia navegação

**Dependencies:** FE-LEAD-003
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** consistência entre descriptor estático e registro runtime.
