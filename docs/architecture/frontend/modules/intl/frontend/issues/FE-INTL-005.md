## [FE-INTL-005] CopilotFacade — conversa corrente, otimismo, cancelamento

**Status:** ⚪ INTACT — pós-validação 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`CopilotFacade` (signals) com `conversas()`, `messages()`, `status()`, `podeEnviar()` (computed); `enviarPergunta` insere otimisticamente bolha do usuário + bolha `PENDENTE`, dispara o POST com `AbortController`, e substitui pela resposta no `200`; `cancelarPergunta()` aborta e limpa.

**Context / Problem statement:**
- Núcleo de estado do chat. Fonte: SPEC-03 (CopilotVM) + SPEC-04 + ADR-005.
- Bloqueia: FE-INTL-009, FE-INTL-010.

**Approach (execution path):**
1) `signal<MensagemVM[]>` + `signal<status>`; `computed` `podeEnviar = !temPendente() && textoValido()`.
2) Otimismo na `enviarPergunta`; substituição no response com `status` + `citacoes`.
3) `cancelarPergunta()` via `AbortController`; `effect()` reage à troca de empresa (reset).

**Non-goals:** render (P3); observability (FE-INTL-018).

**Layer(s):** frontend / libs/intl/data-access
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-03-view-models.md` · `SPEC-04` · `ADR-005`

**Architecture alignment:** ADR-002/005; signals; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/data-access/src/lib/copilot.facade.ts` — MISSING: facade não existe
- 🔲 `libs/intl/data-access/src/lib/copilot.mappers.ts` (Resposta→MensagemVM) — MISSING: mapper não existe

**Tests**
- 🔲 `nx test intl-data-access` PASS (otimismo, cancelamento, status mapping) — MISSING: sem testes · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:intl · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS
- Teste: bolha PENDENTE não renderiza citação; cancelamento remove pendentes (INV-FE-1/2).

**Dependencies:** FE-INTL-004
**API / Contract impact:** consome `RespostaCopilotoResponse`.
**Risks / Notes:** status desconhecido → tratar como `DEGRADADA` (defensivo, R6).
