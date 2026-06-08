## [FE-INTL-017] UX polish — loading / empty / error states

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
Estados de loading (skeleton de dashboard/tabela/thread), empty (base sem nós, sem conversas) e error (banner `403`, toast `409`/`5xx`, inline `503` retry) padronizados via `@journeyos/shared/ui-feedback` nas 3 features.

**Context / Problem statement:**
- Coerência de UX e tratamento de erro. Fonte: SPEC-07 + 06-risks.
- Depende das pages (P3) e do error mapper (FE-INTL-008).

**Approach (execution path):**
1) Aplicar skeleton/empty/error consistentes por tela.
2) Garantir que `503` aparece como inline + retry (não erro fatal).
3) Estado `pensando` do copiloto com microcopy clara.

**Non-goals:** novos componentes de domínio (já em P3).

**Layer(s):** frontend / libs/intl/feature-*
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`

**Architecture alignment:** `@journeyos/shared/ui-feedback`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/feature-copilot/...` (loading/empty/error do thread+lista) — MISSING: sem states; ui-feedback não usado
- 🔲 `libs/intl/feature-knowledge/...` (skeleton tabela + empty base) — MISSING: sem skeleton/empty
- 🔲 `libs/intl/feature-analytics/...` (skeleton dashboard) — MISSING: sem skeleton de dashboard

**Tests**
- 🔲 `nx test intl-feature-*` PASS — MISSING: sem testes de states · 🔲 `nx lint` PASS — MISSING: não executado neste baseline

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:intl · priority:P7

**Acceptance criteria:**
- `npx nx test/lint/build intl-feature-copilot intl-feature-knowledge intl-feature-analytics` PASS
- Evidência: screenshots dos states (loading/success/error/empty).

**Dependencies:** FE-INTL-009..014, FE-INTL-008
**API / Contract impact:** nenhum.
**Risks / Notes:** —
