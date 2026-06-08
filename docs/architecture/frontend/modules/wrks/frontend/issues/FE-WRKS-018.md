## [FE-WRKS-018] UX polish — loading / empty / error states

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Estados loading/empty/error padronizados em todas as features via `@journeyos/shared/ui-feedback`, com skeletons (CLS ~0) e mensagens do SPEC-07.

**Context / Problem statement:**
- Qualidade visual consistente. Fonte: SPEC-07, success signals (CLS). Depende das features P3.

**Approach (execution path):**
1) Aplicar componentes de feedback (loading/empty/error) em cada page.
2) Skeletons em tabelas/dashboard (evitar layout shift).
3) Ligar mensagens ao `AppError` (apresentação inline/toast/banner).

**Non-goals:** novos componentes shared (promover só se reusável).

**Layer(s):** frontend / libs/wrks/feature-* + styles
**Bounded context:** wrks

**Service execution spec(s):** SPEC-07; `01-architectural-vision.md` §7

**Architecture alignment:** estados via `ui-feedback` (sem UI ad-hoc).

**Implementation checklist (by file):**
- 🔲 estados em `feature-users`, `feature-workspace`, `feature-empresa-select`, `feature-rbac-viewer` (MISSING — todas as feature libs são stubs Nx default sem ui-feedback)
- 🔲 skeletons em tabela/dashboard (MISSING)

**Tests**
- 🔲 `nx test` PASS nos projetos afetados (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P7

**Acceptance criteria:**
- Cada tela cobre loading/empty/error; CLS ~0
- `npx nx test/lint/build` PASS

**Dependencies:** FE-WRKS-011..015, FE-WRKS-008
**API / Contract impact:** nenhum.
**Risks / Notes:** screenshots dos states como evidência.
