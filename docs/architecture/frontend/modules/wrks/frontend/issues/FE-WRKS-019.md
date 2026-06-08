## [FE-WRKS-019] Observability (bootstrap timing, troca de empresa, convites)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 18 — Inicial
**Done/Total:** 0/3 itens

**Outcome:**
Eventos de telemetria via `@journeyos/shared/observability`: timing de login/bootstrap, troca de empresa e ações de admin (convite, alteração de papel).

**Context / Problem statement:**
- Success signals exigem medir TTI/troca. Fonte: 01-vision §7, 02-blueprint §5. Recomendado pelo brief.

**Approach (execution path):**
1) Instrumentar `wrks.bootstrap.ts` (timing de boot/login).
2) Emitir evento na troca de empresa e em convites/alteração de papel.
3) Sem PII além do necessário (LGPD).

**Non-goals:** dashboards (INTL).

**Layer(s):** frontend / libs/wrks/* + integração observability
**Bounded context:** wrks

**Service execution spec(s):** `01-architectural-vision.md` §7

**Architecture alignment:** observability como serviço cross-cutting.

**Implementation checklist (by file):**
- 🔲 eventos em `wrks.bootstrap.ts` (MISSING — `libs/wrks/shell-entry/.../wrks.bootstrap.ts` é stub auto-gerado, lifecycle vazio com TODOs; sem timing/telemetria)
- 🔲 eventos em `UsersFacade`/`EmpresaContext` wiring (MISSING — facades não implementadas)

**Tests**
- 🔲 `nx test` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P8 / Observability
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P8

**Acceptance criteria:**
- Eventos emitidos sem PII sensível; `npx nx test/lint` PASS

**Dependencies:** INT-FE-WRKS-005
**API / Contract impact:** nenhum.
**Risks / Notes:** LGPD — minimizar dados no payload.
