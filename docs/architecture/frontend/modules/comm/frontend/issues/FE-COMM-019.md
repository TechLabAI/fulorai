## [FE-COMM-019] Observability — telemetria do módulo

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 10 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
Eventos de telemetria via `@journeyos/shared/observability`: timing de composição do Studio, taxa de
entrega/leitura, latência do catálogo, duração/contagem de sessões de polling.

**Context / Problem statement:**
- Medir os Success Signals do `01`. Fonte: `04` §5, `06`. Depende: P2/P3.

**Approach:**
1) Instrumentar facades (compose, dispatch, polling) com spans/eventos.
2) Métrica de latência do catálogo e do polling.

**Non-goals:** dashboards (INTL); APM backend.

**Layer(s):** frontend / `libs/comm/data-access` (hooks) + observability
**Bounded context:** comm
**Service execution spec(s):** `04-frontend-architecture-direction.md` §5
**Architecture alignment:** tag `scope:comm`; observability opcional-recomendado.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/data-access/src/lib/comm-telemetry.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P8 / Observability
**Labels:** type:feature · layer:frontend · scope:comm · priority:P8

**Acceptance criteria:**
- Eventos emitidos sem PII; `nx test/lint` PASS

**Dependencies:** FE-COMM-007 (polling), FE-COMM-005 (studio)
**API / Contract impact:** nenhum.
**Risks / Notes:** não logar conteúdo de mensagem (LGPD).
