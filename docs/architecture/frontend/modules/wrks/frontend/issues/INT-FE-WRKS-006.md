## [INT-FE-WRKS-006] Propagação de modelo_acesso_versao (RBAC stale → re-eval)

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Quando o BE sinaliza `iam.sessao.versao-desatualizada` (ou nova `modeloAcessoVersao` na AccessDecision), o FE re-avalia acesso + re-deriva navegação em < 5 s, sem invalidar tokens 1-a-1.

**Context / Problem statement:**
- Success signal: mudança de RBAC reflete em UI rapidamente. Fonte: SPEC-07, api-contract (`/access/evaluate`).

**Approach (execution path):**
1) Detectar `iam.sessao.versao-desatualizada` no error mapper (FE-WRKS-008).
2) Disparar re-avaliação via Access Layer (`AccessDecisionService`) + `NavigationService`.
3) Ações perdidas somem do menu; nenhuma tela cross-empresa aparece.

**Non-goals:** lógica de cache do BE.

**Layer(s):** frontend / integração (libs/wrks + @journeyos/shared/access-decision)
**Bounded context:** wrks

**Service execution spec(s):** SPEC-07; `api-contract.md` (§Access)

**Architecture alignment:** cache é otimização, nunca verdade (princípio vision §6.5 BE).

**Implementation checklist (by file):**
- 🚧 hook de re-eval no `wrks.bootstrap.ts` (BLOCKED: bootstrap é stub vazio; depende de INT-FE-WRKS-005 e INT-FE-WRKS-003 não implementados)
- 🚧 tratamento de `iam.sessao.versao-desatualizada` (BLOCKED: depende do error mapper FE-WRKS-008, ainda inexistente)

**Tests**
- 🔲 `nx test` PASS nos projetos afetados (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:wrks · priority:P4

**Acceptance criteria:**
- Mudança de papel reflete em UI < 5 s (sem reload)
- `npx nx test/lint` PASS

**Dependencies:** FE-WRKS-008, INT-FE-WRKS-003, INT-FE-WRKS-005
**API / Contract impact:** `modeloAcessoVersao` em `AccessDecisionResponse`.
**Risks / Notes:** evitar loop de re-eval (debounce).
