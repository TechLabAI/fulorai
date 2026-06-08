## [INT-FE-INTL-003] Integração — access-decision (accessGuard + menu RBAC)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 15 — Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
INTL consome `@journeyos/shared/access-decision`: `accessGuard(<perm>)` nas rotas e `NavigationService` filtrando os deep-links por permissão (item Analítica some sem `intl.analytics.read`; ações de escrita somem sem `intl.knowledge.write`).

**Context / Problem statement:**
- UI ausente por decisão de acesso. Fonte: SPEC-01 + SPEC-06 + access-layer-contracts.
- Bloqueia: FE-INTL-015 (guards), e2e entitlement-denied.

**Approach (execution path):**
1) `accessGuard` delega a `AccessDecisionService.can(perm)`.
2) `canWrite()`/visibilidade de menu via `computed` sobre AccessDecision.

**Non-goals:** definição de papéis (é do WRKS/BE).

**Layer(s):** frontend / libs/intl/access + navigation
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-01` · `SPEC-06` · `access-layer-contracts.md`

**Architecture alignment:** consome `@journeyos/shared/access-decision`; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 wiring em `libs/intl/access` + `libs/intl/navigation` — MISSING: só placeholders, sem accessGuard/menu RBAC

**Tests**
- 🔲 `nx test intl-access intl-navigation` PASS — MISSING: sem teste de visibilidade RBAC · 🔲 `nx lint` PASS — MISSING: não executado nesta baseline

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:intl · priority:P4

**Acceptance criteria:**
- `npx nx test/lint intl-access intl-navigation` PASS
- Teste: sem `intl.analytics.read`, item Analítica não aparece.

**Dependencies:** INT-FE-INTL-004
**API / Contract impact:** nenhum (decisão local via AccessDecision).
**Risks / Notes:** —
