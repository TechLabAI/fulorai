## [FE-INTL-009] feature-copilot — CopilotPageComponent (lista de conversas)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 22 — Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`CopilotPageComponent` (smart) com `ConversationListComponent` + `NewConversationButtonComponent`; lista as conversas, permite abrir nova e selecionar uma (navega a `/intl/copilot/:id`).

**Context / Problem statement:**
- Entrada do chat. Fonte: SPEC-02 (feature-copilot) + SPEC-03.
- Bloqueia: FE-INTL-010.

**Approach (execution path):**
1) Page consome `CopilotFacade.conversas()`.
2) `ConversationListComponent` (presentational) emite `select`; `NewConversationButtonComponent` emite `novaConversa`.
3) Empty state via `@journeyos/shared/ui-feedback`.

**Non-goals:** thread/resposta (FE-INTL-010); UI de citação (FE-INTL-011).

**Layer(s):** frontend / libs/intl/feature-copilot
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-02-component-hierarchy.md` (feature-copilot)

**Architecture alignment:** Standalone + OnPush; `type:feature` `scope:intl`.

**Implementation checklist (by file):**
- 🟡 `libs/intl/feature-copilot/src/lib/copilot.page.ts` — PARTIAL: placeholder shell only, no facade/lista
- 🔲 `libs/intl/feature-copilot/src/lib/conversation-list.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-copilot/src/lib/new-conversation-button.component.ts` — MISSING: arquivo não existe

**Tests**
- 🔲 `nx test intl-feature-copilot` PASS — MISSING: só spec scaffold default · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:intl · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build intl-feature-copilot` PASS
- Cobertura visual: ConversationList do SPEC-02 no DOM.

**Dependencies:** FE-INTL-005
**API / Contract impact:** consome `CopilotFacade`.
**Risks / Notes:** —
