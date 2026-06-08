## [INT-FE-JRNY-002] Integração empresa-context (invalidação na troca)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/2 itens

**Outcome:**
`effect()` nas facades reage a `EmpresaContextService`: na troca de empresa, invalida lista/builder/
decisões em tela **antes** de carregar os dados da nova empresa (sem vazamento cross-empresa).

**Context / Problem statement:**
- Isolamento multi-empresa é requisito; cobre a invalidação de estado.
- Fonte: SPEC-04 (invalidação), 06-risks R5. Cobre EARS #22/#32.

**Approach (execution path):**
1) Observar empresa ativa; ao mudar, resetar signals do módulo.
2) Garantir que nenhum dado da empresa anterior permanece visível.

**Non-goals:** guards (FE-JRNY-017).

**Layer(s):** frontend / `libs/jrny/data-access`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-04` · `06-risks-gaps-assumptions.md` (R5)

**Architecture alignment:** Signals `effect()`; tag `type:data-access`.

**Implementation checklist (by file):**
- 🚧 `libs/jrny/data-access/src/lib/empresa-invalidation.ts` (BLOCKED: depende de INT-FE-JRNY-001 e FE-JRNY-004 nao implementados; arquivo ausente)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:jrny · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- Troca de empresa invalida estado antes de recarregar (EARS #22)

**Dependencies:** INT-FE-JRNY-001, FE-JRNY-004
**API / Contract impact:** nenhum direto.
**Risks / Notes:** evitar flicker entre invalidação e recarga.
