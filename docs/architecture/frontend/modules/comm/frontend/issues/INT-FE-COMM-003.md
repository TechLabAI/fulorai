## [INT-FE-COMM-003] Wiring access-decision (accessGuard + gating de ações)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 11 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
`accessGuard(perm)` e gating de botões/ações via `AccessDecisionService.can('comm.*')` em todas as
features; ações não permitidas nunca renderizadas.

**Context / Problem statement:**
- RBAC no FE (defesa em profundidade). Fonte: SPEC-01/05 (C-01.5, C-03.5, C-05.5). Bloqueia: FE-COMM-016.

**Approach:**
1) `accessGuard` por rota.
2) `computed` de visibilidade por permissão nas pages (disparo, ativar, configurar, criar regra).

**Non-goals:** RBAC backend.

**Layer(s):** frontend / `libs/comm/access` ↔ Access Layer
**Bounded context:** comm
**Service execution spec(s):** `SPEC-01`, `SPEC-05`
**Architecture alignment:** access→shared/access-decision; tag `scope:comm` `type:domain`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring `AccessDecisionService` nas features
- 🔲 [MISSING] `accessGuard` factory em `libs/comm/access`

**Tests**
- 🔲 [MISSING] `nx test comm-access` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:comm · priority:P4

**Acceptance criteria:**
- Ação sem permissão não aparece; rota negada bloqueada; `nx test/lint` PASS

**Dependencies:** FE-COMM-001, FE-COMM-002
**API / Contract impact:** nenhum direto.
**Risks / Notes:** invalidar cache de decisão em `modelo_acesso_versao`.
