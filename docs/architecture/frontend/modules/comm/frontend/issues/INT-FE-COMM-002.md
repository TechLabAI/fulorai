## [INT-FE-COMM-002] Wiring auth-session + empresa-context (authGuard/empresaGuard)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/4 itens
**GitHub:** [#TBD]

**Outcome:**
COMM usa `authGuard` (de `@journeyos/shared/auth-session`) e `empresaGuard` (de
`@journeyos/shared/empresa-context`) nas rotas; troca de empresa dispara invalidação + parada de polling.

**Context / Problem statement:**
- Rotas pós-contexto + isolamento multi-empresa. Fonte: SPEC-01, SPEC-06 (C-04.7/C-06.3). Bloqueia: FE-COMM-016.

**Approach:**
1) Aplicar authGuard/empresaGuard nas rotas COMM.
2) Assinar troca de empresa → `onDeactivate()` (limpa signals + stopPolling).

**Non-goals:** accessGuard de permissão (INT-FE-COMM-003).

**Layer(s):** frontend / `libs/comm/access` + `libs/comm/integration`
**Bounded context:** comm
**Service execution spec(s):** `SPEC-01`, `SPEC-06`
**Architecture alignment:** access→shared/{auth-session,empresa-context}; tag `scope:comm` `type:domain`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring guards nas rotas (`comm.routes.ts`)
- ◐ [PARTIAL] assinatura de empresa-context no `comm.bootstrap.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-access` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:comm · priority:P4

**Acceptance criteria:**
- Sem sessão/empresa → bloqueio; troca de empresa invalida estado + para polling; `nx test/lint` PASS

**Dependencies:** FE-COMM-002
**API / Contract impact:** nenhum direto.
**Risks / Notes:** cobre C-04.7, C-06.3.
