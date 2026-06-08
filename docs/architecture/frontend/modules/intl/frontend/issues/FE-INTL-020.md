## [FE-INTL-020] Hardening — status desconhecido defensivo + isolamento na troca de empresa

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
Endurecimento: status de resposta fora do enum tratado como `DEGRADADA` (R6); troca de empresa cancela in-flight + limpa conversa + recarrega Knowledge/Analytics (R4); perf budget do bundle por feature.

**Context / Problem statement:**
- Fecha os riscos R4/R6 antes do e2e. Fonte: 06-risks + ADR-005 + 05 §3.
- Bloqueia: FE-INTL-019 (e2e isolation/degraded dependem deste hardening).

**Approach (execution path):**
1) `effect()` de reset no `EmpresaContextService` em todas as facades.
2) Guarda defensiva de status desconhecido na conversão Resposta→VM.
3) Verificar perf budget (lazy de gráficos/feature).

**Non-goals:** novas features.

**Layer(s):** frontend / libs/intl/data-access + feature-*
**Bounded context:** intl

**Service execution spec(s):** `frontend/06-risks-gaps-assumptions.md` · `05` (§3) · `ADR-005`

**Architecture alignment:** signals/effects; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/data-access/src/lib/empresa-reset.effect.ts` — MISSING: sem effect de reset na troca de empresa
- 🔲 `libs/intl/data-access/src/lib/copilot.mappers.ts` (guarda de status) — MISSING: sem guarda defensiva de status

**Tests**
- 🔲 `nx test intl-data-access` PASS (reset + status desconhecido) — MISSING: sem testes · 🔲 `nx lint` PASS — MISSING: não executado neste baseline

**Milestone:** Wave P9 / e2e + hardening
**Labels:** type:feature · layer:frontend · scope:intl · priority:P9

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS
- Teste: troca de empresa → 0 dado da empresa anterior (INV-FE-4).

**Dependencies:** FE-INTL-005, FE-INTL-006, FE-INTL-007
**API / Contract impact:** nenhum.
**Risks / Notes:** cobre R2 (parcialmente) + R4 + R6.
