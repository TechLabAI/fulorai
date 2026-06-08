## [FE-INTL-010] feature-copilot — CopilotConversationPageComponent (thread + input)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`CopilotConversationPageComponent` (smart) com `MessageThreadComponent` + `QuestionInputComponent` + `ThinkingIndicatorComponent`; envia pergunta (otimista), exibe estado `pensando` com Cancelar, e renderiza a resposta.

**Context / Problem statement:**
- Coração do chat. Fonte: SPEC-02 + SPEC-03 + ADR-005.
- Bloqueia: FE-INTL-011 (badges/citações), FE-INTL-019 (e2e).

**Approach (execution path):**
1) Page lê `messages()`, `status()`, `podeEnviar()`.
2) `QuestionInputComponent` emite `enviar`/`cancelar`; desabilita enquanto `PENDENTE`.
3) `ThinkingIndicatorComponent` mostra bolha pendente + Cancelar (< 200 ms para encerrar).

**Non-goals:** badge/citation chip (FE-INTL-011); observability (FE-INTL-018).

**Layer(s):** frontend / libs/intl/feature-copilot
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-02` · `SPEC-03` · `ADR-005`

**Architecture alignment:** Standalone + OnPush; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/feature-copilot/src/lib/copilot-conversation.page.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-copilot/src/lib/message-thread.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-copilot/src/lib/question-input.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-copilot/src/lib/thinking-indicator.component.ts` — MISSING: arquivo não existe

**Tests**
- 🔲 `nx test intl-feature-copilot` PASS — MISSING: sem teste INV-FE-2 · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:intl · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build intl-feature-copilot` PASS
- Teste: enviar com PENDENTE ativo é bloqueado (INV-FE-2).

**Dependencies:** FE-INTL-009
**API / Contract impact:** consome `CopilotFacade`.
**Risks / Notes:** latência variável (R1) — feedback `pensando` imediato.
