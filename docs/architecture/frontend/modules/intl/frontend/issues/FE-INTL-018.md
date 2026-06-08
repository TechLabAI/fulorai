## [FE-INTL-018] Observability — timing pergunta→resposta + custo + degradação

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
Eventos de telemetria via `@journeyos/shared/observability`: tempo pergunta→resposta (p95), `custoTokens`, taxa de respostas `DEGRADADA`/`NAO_FUNDAMENTADA`, e timing de indexação — espelhando os success-signals.

**Context / Problem statement:**
- Mede os success-signals do 01 (latência, degradação). Fonte: 01 §7 + 02 §5.
- Recomendado, não bloqueante de MVP.

**Approach (execution path):**
1) Instrumentar `CopilotFacade.enviarPergunta` (start/stop + status).
2) Emitir métrica de custo/degradação por resposta.
3) Timing da ação Indexar.

**Non-goals:** dashboard de observabilidade (fora do MVP FE).

**Layer(s):** frontend / libs/intl/data-access + feature-copilot
**Bounded context:** intl

**Service execution spec(s):** `frontend/01-architectural-vision.md` (§7) · `02` (§5)

**Architecture alignment:** `@journeyos/shared/observability`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/data-access/src/lib/copilot.telemetry.ts` — MISSING: sem wiring; observability stub não emite nada

**Tests**
- 🔲 `nx test intl-data-access` PASS — MISSING: sem testes de telemetria · 🔲 `nx lint` PASS — MISSING: não executado neste baseline

**Milestone:** Wave P8 / Observability
**Labels:** type:feature · layer:frontend · scope:intl · priority:P8

**Acceptance criteria:**
- `npx nx test/lint/build intl-data-access` PASS
- Evento de timing emitido por pergunta (com `status`).

**Dependencies:** FE-INTL-005
**API / Contract impact:** nenhum.
**Risks / Notes:** não logar PII de pergunta/resposta (LGPD).
