## [FE-COMM-016] Access guards do módulo

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
Guards de COMM em `libs/comm/access`: composição `authGuard` + `empresaGuard` + `accessGuard(perm)`
por rota (SPEC-01); rota "sem permissão" quando negado.

**Context / Problem statement:**
- Defesa em profundidade no FE. Fonte: SPEC-01. Depende: FE-COMM-002, INT-FE-COMM-002, INT-FE-COMM-003.

**Approach:**
1) Wrapper `accessGuard(perm)` usando `AccessDecisionService.can`.
2) Aplicar combinação por rota; estado "sem permissão" para negado.

**Non-goals:** RBAC backend (WRKS); gating de botões (nas features).

**Layer(s):** frontend / `libs/comm/access`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-01-route-map.md`
**Architecture alignment:** tag `scope:comm` `type:domain`; access→shared/{access-decision,auth-session}.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/access/src/lib/comm-access.guards.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-access` PASS · 🔲 [MISSING] `nx lint comm-access` PASS

**Milestone:** Wave P5 / Access guards
**Labels:** type:feature · layer:frontend · scope:comm · priority:P5

**Acceptance criteria:**
- Rota sem permissão bloqueada (C-01.5); `nx test/lint` PASS

**Dependencies:** FE-COMM-002, INT-FE-COMM-002, INT-FE-COMM-003
**API / Contract impact:** nenhum direto.
**Risks / Notes:** ordem authGuard→empresaGuard→accessGuard.
