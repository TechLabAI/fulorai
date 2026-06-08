## [FE-LEAD-019] UX polish: loading/empty/error + lead-not-found + retry policy

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
Estados de UI consistentes em todas as features (loading/empty/error via
`@journeyos/shared/ui-feedback`), estado **"lead não encontrado"** (404), banners de degradação
(anonimizado / sem-regra-ativa), e **retry manual** para list/get (sem auto-retry em mutações).
Cobre **G1** (lead-not-found), **G6** (list-error), **G7** (retry-policy).

**Context / Problem statement:**
- Fecha os gaps de error-recovery do specs-validate. Fonte: SPEC-07.

**Approach (execution path):**
1) Padronizar loading/empty/error nas pages (componentes shared).
2) `lead-not-found` no detalhe (`404 lead.lead.nao-encontrado`).
3) Banners (anonimizado/sem-regra-ativa) + botão "tentar novamente" para list/get; mutações sem auto-retry.

**Non-goals:** lógica de dados (P2); a11y do radar (FE-LEAD-020).

**Layer(s):** frontend / features + `libs/lead/styles`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md`

**Architecture alignment:** `@journeyos/shared/ui-feedback`; tag `scope:lead`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/feature-lead-detail/src/lib/lead-not-found.component.ts` — _MISSING_
- 🔲 `libs/lead/styles/src/lib/*` (estados visuais) — _MISSING_
- 🔲 wiring de retry nas pages de lista/detalhe — _MISSING_

**Tests**
- 🔲 `nx test lead-*` PASS · 🔲 `nx lint lead-*` PASS — _MISSING_

**Milestone:** Wave P7 / UX polish
**Labels:** type:feature · layer:frontend · scope:lead · priority:P7

**Acceptance criteria:**
- `npx nx test/lint/build` das features PASS
- 404 → estado "lead não encontrado" (G1); 5xx → retry manual, mutações sem auto-retry (G7)

**Dependencies:** FE-LEAD-008, FE-LEAD-011
**API / Contract impact:** consome códigos de erro do BE.
**Risks / Notes:** evitar auto-retry em `qualify`/`activate`/LGPD (duplicação).
