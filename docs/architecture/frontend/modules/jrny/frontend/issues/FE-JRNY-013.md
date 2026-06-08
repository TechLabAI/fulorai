## [FE-JRNY-013] feature-decision-log (trilha explicável + assist badge)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 25 — Inicial
**Done/Total:** 0/6 itens

**Outcome:**
`feature-decision-log` com `DecisionLogPageComponent` (smart) + `LeadJourneyStateCardComponent`,
`DecisionTimelineComponent`, `DecisionItemComponent`. Mostra estado de jornada do lead + trilha
imutável; **cada decisão** renderiza gatilho+regra+alvo+assist+motivo (ADR-005); IA-off = badge neutro.

**Context / Problem statement:**
- Golden path B (auditoria — "por que está aqui?"); o decision log nunca é caixa-preta.
- Fonte: SPEC-02, SPEC-03 (DecisionLogVM), ADR-005. Consome `DecisionLogFacade`.

**Approach (execution path):**
1) `DecisionLogPageComponent` lê `estadoJornada/decisoes/loading/error/semInscricao`.
2) `DecisionTimeline` newest-first + "carregar mais"; inclui SEM_MUDANCA/NAO_ROTEADO.
3) `DecisionItem` sempre com gatilho+regra+alvo+assist+motivo; `AssistBadge` (FE-JRNY-015).

**Non-goals:** badge component em si (FE-JRNY-015); analytics (FE-JRNY-014).

**Layer(s):** frontend / `libs/jrny/feature-decision-log`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-02` · `SPEC-03` · `adr/ADR-005`

**Architecture alignment:** Standalone + OnPush + Signals; tag `type:feature` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/feature-decision-log/src/lib/decision-log.page.ts` (MISSING)
- 🔲 `libs/jrny/feature-decision-log/src/lib/lead-journey-state-card.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-decision-log/src/lib/decision-timeline.component.ts` (MISSING)
- 🔲 `libs/jrny/feature-decision-log/src/lib/decision-item.component.ts` (MISSING)

**Tests**
- 🔲 `nx test jrny-feature-decision-log` PASS (MISSING) · 🔲 `nx lint ...` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build jrny-feature-decision-log` PASS
- Decisão sempre explicável (EARS #12); IA-off neutro sem erro (EARS #13/#38)
- Lead sem inscrição → estado vazio (EARS #6)

**Dependencies:** FE-JRNY-007, FE-JRNY-015
**API / Contract impact:** `/api/v1/routing/leads/{leadId}/journey` + `/decisions`.
**Risks / Notes:** decisão é read-only (imutável) — sem UI de mutação.
