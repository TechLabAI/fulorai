## [INT-FE-ASST-003] Integração empresa-context (escopo + invalidação na troca)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
O ASST consome `@journeyos/shared/empresa-context`: todo dado escopado por `empresaId`; troca de
empresa **invalida** catálogo/detalhe/fila e cancela in-flight antes de renderizar (UINV-8, R-2).

**Context / Problem statement:**
- Isolamento multi-empresa (LGPD). Fonte: ADR-005 multi-empresa (WRKS), `05 §3/§6`. Depende do shared (Wave 0). Bloqueia: FE-ASST-020 (isolation e2e).

**Approach (execution path):**
1) Facades assinam `EmpresaContextService`; em `switchTo`, resetam signals e cancelam requests.
2) Catálogo/detalhe re-carregam para a nova empresa; nada da empresa anterior renderiza.
3) Cobre o cenário `empresa-isolation.feature`.

**Non-goals:** UI da troca (Shell/topbar).

**Layer(s):** frontend / `libs/asst/data-access` + `integration`
**Bounded context:** asst

**Service execution spec(s):** `05-state-and-data-flow.md §3,§6` · `empresa-isolation.feature`

**Architecture alignment:** `data-access → shared/empresa-context`.

**Implementation checklist (by file):**
- 🔲 [MISSING] invalidação/cancelamento nas facades do ASST na troca de empresa

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS (reset na troca) · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:asst · priority:P4

**Acceptance criteria:**
- Nenhum asset cross-empresa renderiza após `switchTo` (R-2)

**Dependencies:** shared/empresa-context (Wave 0)
**API / Contract impact:** `empresa_id` via claim JWT (BE); `X-Empresa-Id` debug only.
**Risks / Notes:** teste de não-vazamento é crítico (LGPD).
