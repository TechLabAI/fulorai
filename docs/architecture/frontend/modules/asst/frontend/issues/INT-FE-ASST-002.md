## [INT-FE-ASST-002] Integração auth-session (bearer token)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/3 itens
**GitHub:** [#TBD]

**Outcome:**
O ASST consome `@journeyos/shared/auth-session` para o bearer JWT (via interceptor); nenhuma feature
lê `localStorage` nem decodifica JWT.

**Context / Problem statement:**
- Toda chamada ASST exige JWT do WRKS. Fonte: SPEC-04, `_brief §7`. Depende do shared (Wave 0). Bloqueia: FE-ASST-016.

**Approach (execution path):**
1) Garantir que o token de sessão flui via interceptor (access-http-base + auth-session).
2) Guards (`authGuard`) usam o estado de sessão de `auth-session`.
3) `401 asst.auth.token-invalido` dispara refresh/login (não tratado no ASST, delegado ao shared).

**Non-goals:** lógica de OIDC (WRKS/shared).

**Layer(s):** frontend / `libs/asst/access` + `data-access`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-04` · `access-layer-contracts.md`

**Architecture alignment:** `access → shared/auth-session`.

**Implementation checklist (by file):**
- 🔲 [MISSING] wiring de sessão nos guards/services do ASST

**Tests**
- 🔲 [MISSING] `nx test asst-access` PASS · 🔲 [MISSING] `nx lint asst-access` PASS

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:asst · priority:P4

**Acceptance criteria:**
- Nenhuma leitura direta de storage/JWT (UINV-3/UINV-7 do WRKS); token via shared

**Dependencies:** shared/auth-session (Wave 0)
**API / Contract impact:** Authorization Bearer em `/api/v1/assets/**`.
**Risks / Notes:** —.
