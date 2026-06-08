## [INT-FE-COMM-005] CommShellIntegrationService + lifecycle (runtime)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`CommShellIntegrationService` (`onRegister/onActivate/onDeactivate`) + `comm.bootstrap.ts`
(`commModuleInit/Destroy`) integrados ao Shell em runtime; `onDeactivate`/`destroy` encerram polling.

**Context / Problem statement:**
- Registro runtime + cleanup. Fonte: SPEC-06 (C-06.1/06.3/06.4). Depende: FE-COMM-003.

**Approach:**
1) Implementar o service de integração.
2) `init` assina empresa-context + modelo_acesso_versao; `destroy` cancela e para polling.

**Non-goals:** descriptor estático (FE-COMM-003).

**Layer(s):** frontend / `libs/comm/integration`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-06-shell-integration.md`
**Architecture alignment:** ADR-004; tag `scope:comm` `type:domain`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/integration/src/lib/comm-shell-integration.service.ts`
- ◐ [PARTIAL] `libs/comm/shell-entry/src/lib/comm.bootstrap.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-integration` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:comm · priority:P4

**Acceptance criteria:**
- Destroy encerra polling (C-06.4); troca de empresa chama onDeactivate (C-06.3); `nx test/lint` PASS

**Dependencies:** FE-COMM-003
**API / Contract impact:** nenhum direto.
**Risks / Notes:** evitar leaks de subscription/timer.
