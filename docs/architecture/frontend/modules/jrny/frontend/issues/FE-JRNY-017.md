## [FE-JRNY-017] Access guards (auth/empresa/access) do módulo

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
Guards do módulo em `libs/jrny/access`: composição `authGuard` + `empresaGuard` +
`accessGuard('jrny.*')` por rota (SPEC-01). `empresaGuard` bloqueia toda rota `/jrny` sem empresa
ativa e redireciona à seleção (gap G-a). Guards consomem `AccessDecisionService` — a UI não decide RBAC.

**Context / Problem statement:**
- Toda rota JRNY é pós-contexto; sem empresa ativa não há acesso.
- Fonte: SPEC-01 (guards/EARS), SPEC-05. Cobre gap G-a (empresaGuard sem-empresa).

**Approach (execution path):**
1) `accessGuard(perm)` factory consultando `AccessDecisionService`.
2) `empresaGuard` redireciona à seleção se `EmpresaContextService` sem empresa.
3) Aplicar a composição nas rotas (FE-JRNY-002).

**Non-goals:** menu filtering (INT-FE-JRNY-003); navegação (FE-JRNY-018).

**Layer(s):** frontend / `libs/jrny/access`
**Bounded context:** jrny

**Service execution spec(s):** `SPEC-01-route-map.md` (EARS guards)

**Architecture alignment:** Access Layer (guards não decidem RBAC); tag `type:domain` `scope:jrny`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/access/src/lib/access.guard.ts` (MISSING)
- 🔲 `libs/jrny/access/src/lib/empresa.guard.ts` (ou reuso do shared) (MISSING)

**Tests**
- 🔲 `nx test jrny-access` PASS (MISSING) · 🔲 `nx lint jrny-access` PASS (MISSING)

**Milestone:** Wave P5 / Access guards
**Labels:** type:feature · layer:frontend · scope:jrny · priority:P5

**Acceptance criteria:**
- `npx nx test/lint/build jrny-access` PASS
- Sem empresa ativa → rotas `/jrny` bloqueadas (EARS, gap G-a); sem perm → negado

**Dependencies:** FE-JRNY-002, INT-FE-JRNY-003
**API / Contract impact:** consome `AccessDecision` (WRKS).
**Risks / Notes:** preferir reusar guards shared; só especializar o que for `jrny.*`.
