## [FE-SALE-018] Access guards (authGuard, empresaGuard, accessGuard sale.*)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 12 — Inicial
**Done/Total:** 0/5 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/sale/access` materializa os guards consumidos por SPEC-01: `authGuard` (sessão), `empresaGuard`
(empresa ativa — bloqueia toda rota `/sale` e redireciona à seleção quando ausente), `accessGuard(perm)`
(delega ao `AccessDecisionService` para `sale.<perm>`). A UI **não** decide RBAC — só reflete a decisão
da Access Layer; deep links são escondidos quando a permissão falta.

**Context / Problem statement:**
- Toda rota SALE é pós-contexto e gated por permissão; guards são pré-condição de ativação.
- Fonte: SPEC-01 (guards por rota) + access-layer-contracts. Depende de FE-SALE-002. Bloqueia: FE-SALE-023, INT-FE-SALE-004.

**Approach (execution path):**
1) `authGuard`/`empresaGuard` reusando shared (sem reimplementar sessão).
2) `accessGuard(perm)` → `AccessDecisionService.can(perm)`; deny → bloqueio + esconde deep link.
3) Sem empresa ativa → `empresaGuard` bloqueia `/sale/**` e redireciona à seleção de empresa.

**Non-goals:** filtro de menu (INT-FE-SALE-004 / FE-SALE-019); error mapping (FE-SALE-009).

**Layer(s):** frontend / `libs/sale/access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-01-route-map.md` (guards) · `standards/access-layer-contracts.md`

**Architecture alignment:** Access Layer; tag `scope:sale` `type:feature` (access).

**Implementation checklist (by file):**
- 🔲 `libs/sale/access/src/lib/auth.guard.ts` — _MISSING_
- 🔲 `libs/sale/access/src/lib/empresa.guard.ts` — _MISSING_
- 🔲 `libs/sale/access/src/lib/access.guard.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-access` PASS — _MISSING_ · 🔲 `nx lint sale-access` PASS — _MISSING_

**Milestone:** Wave P5 / Access guards
**Labels:** type:feature · layer:frontend · scope:sale · priority:P5

**Acceptance criteria:**
- `npx nx test/lint/build sale-access` PASS
- Sem empresa → bloqueia `/sale` e redireciona (EARS SPEC-01 #2); sem permissão → nega + esconde deep link (EARS SPEC-01 #3)

**Dependencies:** FE-SALE-002
**Data impact:** Nenhum.
**API / Contract impact:** nenhum direto (consulta Access Layer).
**Testing / Evidence required:** teste de cada guard (allow/deny); e2e `entitlement-denied`/`deep-link`.
**Risks / Notes:** reusar guards shared — não duplicar lógica de sessão/empresa.
