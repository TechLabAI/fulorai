## [INT-FE-ASST-004] Integração access-decision (can('asst.*') + NavigationService)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
O ASST consome `@journeyos/shared/access-decision`: visibilidade de ações e itens de menu derivada de
`AccessDecisionService.can('asst.<perm>')` e do `NavigationService` (deep link "Aprovações" gated).

**Context / Problem statement:**
- Garante UINV-2 (UI nunca decide RBAC). Fonte: SPEC-05/06, `04 §4`. Depende do shared (Wave 0). Bloqueia: FE-ASST-016, FE-ASST-017.

**Approach (execution path):**
1) `acoesDisponiveis` e botões consultam `can('asst.*')`.
2) `NavigationService` deriva menu/deep links das permissões + `modelo_acesso_versao`.
3) Re-derivar ao detectar bump de versão de acesso (R-4 análogo do WRKS).

**Non-goals:** cálculo de AccessDecision (BE/shared).

**Layer(s):** frontend / `libs/asst/access` + `integration` + `feature-*`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-05` · `SPEC-06` · `access-layer-contracts.md`

**Architecture alignment:** `access → shared/access-decision`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring de `can('asst.*')` nas features e `NavigationService` na integration

**Tests**
- 🔲 [MISSING] `nx test asst-access` PASS · 🔲 [MISSING] `nx lint` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:asst · priority:P4

**Acceptance criteria:**
- Ações/menu refletem permissões; deep link "Aprovações" some sem `asst.asset.aprovar`

**Dependencies:** shared/access-decision (Wave 0)
**API / Contract impact:** consome AccessDecision.
**Risks / Notes:** manter mapa de permissão sincronizado com SPEC-05.
