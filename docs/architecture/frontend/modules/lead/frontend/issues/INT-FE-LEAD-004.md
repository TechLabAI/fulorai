## [INT-FE-LEAD-004] Integração: entitlement das ações (gating de UI por permissão)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 6 — Inicial
**Done/Total:** 0/4 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
As ações sensíveis do LEAD (requalificar, editar/anonimizar/expurgar, criar/ativar regra,
criar/editar segmento, editar survey) e os deep links de governança são **escondidos/desabilitados**
sem a permissão correspondente. Espelha o RBAC do BE.

**Context / Problem statement:**
- Coerência entre o que a UI oferece e o que o BE autoriza. Fonte: SPEC-05, SPEC-01.
- Bloqueia: e2e `entitlement-denied`.

**Approach (execution path):**
1) `computed()` de visibilidade por ação (combinando estado + `can('lead.*')`).
2) Esconder deep links "Regras"/"Segmentos" sem permissão.
3) Validar com a persona SDR (somente `lead.lead.read`).

**Non-goals:** enforcement server-side (BE); guards de rota (FE-LEAD-017).

**Layer(s):** frontend / features + `shell-entry`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-05 + SPEC-01`

**Architecture alignment:** Access Layer; tag `scope:lead`.

**Implementation checklist (by file):**
- 🔲 gating de ações em `lead-actions-bar.component.ts` / features — _MISSING_
- 🔲 filtro de deep links de governança — _MISSING_

**Tests**
- 🔲 `nx test lead-*` PASS — _MISSING_ · 🔲 `nx lint lead-*` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:lead · priority:P4

**Acceptance criteria:**
- SDR sem permissão não vê "Requalificar"/"Regras"/edição de segmentos (SPEC-01/05 EARS)

**Dependencies:** INT-FE-LEAD-003, FE-LEAD-011
**API / Contract impact:** nenhum endpoint direto (gating de UI).
**Risks / Notes:** gating de UI é UX, não segurança — o BE continua autoritativo.
