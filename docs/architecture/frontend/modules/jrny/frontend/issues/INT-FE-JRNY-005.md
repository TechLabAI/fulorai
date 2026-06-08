## [INT-FE-JRNY-005] JrnyShellIntegrationService + bootstrap (runtime)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/2 itens

**Outcome:**
`JrnyShellIntegrationService` (em `libs/jrny/integration`) + `jrny.bootstrap.ts`: registro/atualização
do módulo em runtime (`onRegister`/`onActivate`/`onDeactivate`), publicação de breadcrumb raiz e
subscrição a `ModuleEventsService` (troca de empresa → invalidar estado).

**Context / Problem statement:**
- Complementa o descriptor estático (FE-JRNY-003) com registro em runtime (TCE/governança).
- Fonte: SPEC-06 §2-§3. Cobre EARS #30/#31/#32.

**Approach (execution path):**
1) Implementar lifecycle do service; `onActivate` publica breadcrumb + sincroniza menu.
2) `bootstrap` registra no boot + subscreve eventos; `destroy` limpa.

**Non-goals:** descriptor estático (FE-JRNY-003).

**Layer(s):** frontend / `libs/jrny/integration` + `libs/jrny/shell-entry`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-06-shell-integration.md` §2-§3

**Architecture alignment:** ADR-004 (runtime registry); tag `type:domain`.

**Implementation checklist (by file):**
- 🚧 `libs/jrny/integration/src/lib/jrny-shell-integration.service.ts` (BLOCKED: arquivo ausente; depende de INT-FE-JRNY-003 nao implementado; lib integration e stub Nx default)
- 🟡 `libs/jrny/shell-entry/src/lib/jrny.bootstrap.ts` (PARTIAL) (existe stub `jrnyModuleInit`/`jrnyModuleDestroy` so com comentarios; sem registro runtime/subscricao a ModuleEventsService)

**Tests**
- 🔲 `nx test jrny-integration` PASS (MISSING) · 🔲 `nx lint jrny-integration` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:jrny · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build jrny-integration` PASS
- Ativação publica breadcrumb + sincroniza menu (EARS #31); troca de empresa invalida (EARS #32)

**Dependencies:** FE-JRNY-001, INT-FE-JRNY-003
**API / Contract impact:** nenhum direto.
**Risks / Notes:** manter consistência com o descriptor estático (fonte única).
