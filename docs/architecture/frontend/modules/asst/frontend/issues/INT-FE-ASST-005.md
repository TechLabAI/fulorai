## [INT-FE-ASST-005] AsstShellIntegrationService (lifecycle + bootstrap)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 13 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`AsstShellIntegrationService` (`libs/asst/integration`) com `onRegister/onActivate/onDeactivate` +
`asst.bootstrap.ts` (`asstModuleInit/Destroy`) que registra o módulo no Shell, assina empresa-context
e `modelo_acesso_versao`, e limpa na saída.

**Context / Problem statement:**
- Ciclo de vida do módulo no Shell. Fonte: SPEC-06 §3,§4. Depende de FE-ASST-003, INT-FE-ASST-003/004.
- Bloqueia: —.

**Approach (execution path):**
1) `onRegister` publica `MODULE_MENU_METADATA` (NavigationService).
2) `onActivate` assina empresa-context (invalidar catálogo) + versão de acesso (re-derivar nav).
3) `onDeactivate`/`asstModuleDestroy` cancela assinaturas + reseta facades.

**Non-goals:** descriptor estático (FE-ASST-003).

**Layer(s):** frontend / `libs/asst/integration` + `shell-entry`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-06-shell-integration.md §3,§4`

**Architecture alignment:** tag `type:domain`; consome shared/access-decision.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/integration/src/lib/asst-shell-integration.service.ts`
- ◐ [PARTIAL] `libs/asst/shell-entry/src/lib/asst.bootstrap.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-integration` PASS · 🔲 [MISSING] `nx lint asst-integration` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:asst · priority:P4

**Acceptance criteria:**
- Registro/ativação/desativação funcionam; sem leaks de assinatura na saída

**Dependencies:** FE-ASST-003, INT-FE-ASST-003, INT-FE-ASST-004
**API / Contract impact:** nenhum.
**Risks / Notes:** registro runtime (TCE/Shell) substitui o fallback estático em prod.
