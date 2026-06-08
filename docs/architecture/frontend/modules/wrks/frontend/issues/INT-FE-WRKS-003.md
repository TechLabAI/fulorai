## [INT-FE-WRKS-003] Integração access-decision + NavigationService

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Menu/breadcrumbs e visibilidade de ações derivados de `AccessDecisionService`/`NavigationService` a partir das permissões — a UI nunca decide RBAC localmente (UINV-2).

**Context / Problem statement:**
- Guards, atalhos e menu dependem disto. Fonte: access-layer-contracts, SPEC-01/05.

**Approach (execution path):**
1) Consumir `AccessDecisionService.can(<perm>)` em pages/components (via `computed`).
2) `NavigationService` deriva o menu do WRKS a partir do `wrks.contract.ts`.
3) Esconder ações sem permissão (preferir ausência a 403).

**Non-goals:** lógica de guard custom (FE-WRKS-016).

**Layer(s):** frontend / integração (libs/wrks + @journeyos/shared/access-decision)
**Bounded context:** wrks

**Service execution spec(s):** `access-layer-contracts.md`; SPEC-01/05

**Architecture alignment:** zero `if (role===...)` em features (check de aceite).

**Implementation checklist (by file):**
- 🔲 wiring de `can()` nas features (users/workspace/rbac) (MISSING)
- 🔲 derivação de menu via `NavigationService` (MISSING)

**Tests**
- 🔲 `nx test` PASS nos projetos afetados (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:wrks · priority:P4

**Acceptance criteria:**
- SDR não vê itens de admin (`entitlement-denied.feature`)
- Zero decisão RBAC inline

**Dependencies:** FE-WRKS-001, FE-WRKS-011/013/015
**API / Contract impact:** `POST /access/evaluate` (consumido pela Access Layer).
**Risks / Notes:** consistência com bundle papel→permissão do BE.
