## [FE-ASST-018] UX polish (loading / empty / error states)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
Estados de loading/empty/error consistentes em todas as features via `@journeyos/shared/ui-feedback`,
com o critério toast/banner/inline/página de SPEC-07 aplicado (degradação do Studio = banner).

**Context / Problem statement:**
- Consistência de UX + tratamento de erro user-facing. Fonte: SPEC-07. Depende de FE-ASST-008, FE-ASST-009..015.
- Bloqueia: FE-ASST-020.

**Approach (execution path):**
1) Catálogo/detalhe/fila: `JosLoading`/`JosEmptyState`/`JosError` por estado.
2) Aplicar critério SPEC-07: inline (422), toast (409/403), banner (503/sem-versão), página (404).
3) Banner de degradação do Studio com CTA "compor manualmente".

**Non-goals:** novas telas; lógica de dados (P2).

**Layer(s):** frontend / `libs/asst/feature-*` (+ `libs/asst/ui`)
**Bounded context:** asst

**Service execution spec(s):** `SPEC-07-error-handling.md`

**Architecture alignment:** usa `@journeyos/shared/ui-feedback`; sem cor hardcoded (design-tokens).

**Implementation checklist (by file):**
- 🔲 [MISSING] estados em `feature-asset-library`, `feature-asset-detail`, `feature-asset-studio`, `feature-approval-workflow`
- 🔲 [MISSING] `libs/asst/styles/src/lib/*` (tokens de estado/origem)

**Tests**
- 🔲 [MISSING] `nx test asst-feature-*` PASS · 🔲 [MISSING] `nx lint asst-*` PASS

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:asst · priority:P7

**Acceptance criteria:**
- Cada feature tem loading/empty/error; mapeamento SPEC-07 respeitado
- Evidência: screenshots dos states (loading/success/error/empty)

**Dependencies:** FE-ASST-008, FE-ASST-009, FE-ASST-011, FE-ASST-013, FE-ASST-014
**API / Contract impact:** nenhum (consome erros já mapeados).
**Risks / Notes:** alinhar tokens com `@journeyos/shared/ui-tokens` (design-tokens.md).
