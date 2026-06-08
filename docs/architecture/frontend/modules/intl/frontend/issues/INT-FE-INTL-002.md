## [INT-FE-INTL-002] Integração — empresa-context (X-Empresa-Id + reset na troca)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
INTL consome `@journeyos/shared/empresa-context`: header `X-Empresa-Id` automático e um `effect()` de reset que, na troca de empresa, cancela perguntas in-flight, limpa a conversa corrente e recarrega Knowledge/Analytics (INV-FE-4).

**Context / Problem statement:**
- Isolamento multi-empresa (R4). Fonte: 05 §3 + ADR-005.
- Bloqueia: e2e empresa-switch-isolation (FE-INTL-019).

**Approach (execution path):**
1) Ler `empresaId` só via `EmpresaContextService`.
2) `effect()` central que reseta as 3 facades na troca.

**Non-goals:** seleção de empresa (é do WRKS).

**Layer(s):** frontend / libs/intl/data-access + integration
**Bounded context:** intl

**Service execution spec(s):** `frontend/05-state-and-data-flow.md` (§3) · `ADR-005`

**Architecture alignment:** consome `@journeyos/shared/empresa-context`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 wiring em `libs/intl/data-access` (reset effect — coordena com FE-INTL-020) — MISSING: sem EmpresaContext/effect de reset

**Tests**
- 🔲 `nx test intl-data-access` PASS — MISSING: sem teste de troca de empresa · 🔲 `nx lint` PASS — MISSING: não executado nesta baseline

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:intl · priority:P4

**Acceptance criteria:**
- `npx nx test/lint intl-data-access` PASS
- Teste: troca de empresa cancela in-flight + limpa conversa.

**Dependencies:** INT-FE-INTL-004
**API / Contract impact:** header `X-Empresa-Id`.
**Risks / Notes:** coordenar com FE-INTL-020 (hardening do reset).
