## [INT-FE-WRKS-002] Integração empresa-context (switchTo + lista)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
WRKS alimenta a lista de empresas e integra `EmpresaContextService.switchTo` (novo JWT, cancela in-flight, invalida cache escopado, re-avalia nav) — base da troca de empresa sem reload (ADR-005).

**Context / Problem statement:**
- `feature-empresa-select` + topbar do Shell dependem disto. Fonte: ADR-005, SPEC-06, access-layer-contracts.

**Approach (execution path):**
1) Publicar a lista de empresas no `EmpresaContextService` (fonte: `/sessao/login`).
2) Implementar contrato de `switchTo`: cancelamento + invalidação + re-eval.
3) Ligar facades `reset()` (FE-WRKS-008) ao sinal de troca.

**Non-goals:** UI da seleção (FE-WRKS-010).

**Layer(s):** frontend / integração (libs/wrks + @journeyos/shared/empresa-context)
**Bounded context:** wrks

**Service execution spec(s):** ADR-005; SPEC-04/06; `access-layer-contracts.md`

**Architecture alignment:** `EmpresaContextService` é única fonte do `empresaId` (UINV-3).

**Implementation checklist (by file):**
- 🔲 wiring `libs/wrks/data-access` ↔ `EmpresaContextService` (MISSING)
- 🔲 teste e2e de isolamento referenciado (`empresa-switch-isolation.feature`) (MISSING)

**Tests**
- 🔲 `nx test wrks-data-access` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:wrks · priority:P4

**Acceptance criteria:**
- Troca de empresa não vaza dados (cenário e2e)
- `npx nx test/lint` PASS

**Dependencies:** FE-WRKS-008, FE-WRKS-010
**API / Contract impact:** `/sessao/trocar-empresa`.
**Risks / Notes:** R-2 (LGPD) — cancelamento obrigatório de in-flight.
