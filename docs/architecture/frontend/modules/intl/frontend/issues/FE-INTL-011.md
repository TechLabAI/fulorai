## [FE-INTL-011] feature-copilot/ui — ChatBubble + AnswerStatusBadge + CitationChip + CitationPanel

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
Componentes de UI da resposta: `ChatBubbleComponent`, `AnswerStatusBadgeComponent` (RESPONDIDA/NAO_FUNDAMENTADA/DEGRADADA/ERRO), `CitationChipComponent` (clicável) e `CitationPanelComponent` (drawer com trecho/metadados). **Citações só em respostas com status final fundamentado.**

**Context / Problem statement:**
- Implementa a regra de fundamentação visual (INV-FE-1). Fonte: SPEC-02 + SPEC-07 + ADR-005.
- Bloqueia: FE-INTL-019 (e2e copilot-grounded/degraded).

**Approach (execution path):**
1) `AnswerStatusBadge` deriva label/cor/ícone do `status` (nunca cor isolada — a11y).
2) `CitationChip` emite `abrir`; `CitationPanel` mostra `trecho`/`indice`/`documentoId`.
3) Garantir: `NAO_FUNDAMENTADA`/`DEGRADADA` **não** renderizam chips.

**Non-goals:** deep-link cross-módulo (R3 — painel local no MVP).

**Layer(s):** frontend / libs/intl/ui + feature-copilot
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-02` · `SPEC-07` · `contracts/design-tokens.md`

**Architecture alignment:** Standalone + OnPush; `type:ui` `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/ui/src/lib/chat-bubble.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/ui/src/lib/answer-status-badge.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/ui/src/lib/citation-chip.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-copilot/src/lib/citation-panel.component.ts` — MISSING: arquivo não existe

**Tests**
- 🔲 `nx test intl-ui` PASS (status→render; degradado sem chip) — MISSING: sem teste INV-FE-1 · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:intl · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build intl-ui intl-feature-copilot` PASS
- Teste: `DEGRADADA`/`NAO_FUNDAMENTADA` renderizam 0 chips de citação (INV-FE-1).

**Dependencies:** FE-INTL-010
**API / Contract impact:** consome `CitacaoVM`.
**Risks / Notes:** R2 (render degradado como fato) — esta issue é a guarda visual.
