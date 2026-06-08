## [INT-FE-LEAD-002] Integração: auth-session + empresa-context

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 6 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
LEAD consome `@journeyos/shared/auth-session` (sessão/JWT/claims) e `@journeyos/shared/empresa-context`
(empresa ativa); effect de troca de empresa invalida a fila/seleção antes de buscar dados da nova empresa.

**Context / Problem statement:**
- Isolamento multi-empresa (LGPD). Fonte: SPEC-04 (EARS de invalidação), `02` §5. Cobre parte do **G9**.
- Bloqueia: FE-LEAD-004 (effect de troca de empresa).

**Approach (execution path):**
1) Injetar `AuthSessionService` / `EmpresaContextService`.
2) `effect()` na facade que limpa a fila/seleção quando a empresa ativa muda.

**Non-goals:** lógica de login (WRKS); guards (FE-LEAD-017).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-04` · `02` §5

**Architecture alignment:** Access Layer; tag `scope:lead`.

**Implementation checklist (by file):**
- 🔲 wiring em `lead-list.facade.ts` / `lead-detail.facade.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:lead · priority:P4

**Acceptance criteria:**
- `WHEN` empresa muda, a fila é invalidada antes de novo fetch (SPEC-04 EARS)

**Dependencies:** FE-LEAD-004
**API / Contract impact:** nenhum endpoint direto.
**Risks / Notes:** garantir que nenhum dado da empresa anterior renderize sob a nova.
