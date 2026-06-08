## [INT-FE-LEAD-001] Integração: HTTP base (access-http-base) para o lead-service

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 8 — Inicial
**Done/Total:** 0/3 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`libs/lead/data-access` consome `@journeyos/shared/access-http-base` (`provideHttpBase`) com base URL
do `lead-service`; interceptors injetam `Authorization`, `X-Empresa-Id`, `X-Correlation-Id` em todas
as chamadas `/api/v1/leads/**`, `/surveys`, `/qualification`, `/segments`.

**Context / Problem statement:**
- Pré-condição de todos os services do módulo. Fonte: SPEC-04, `access-layer-contracts.md`.
- Bloqueia: FE-LEAD-004..007.

**Approach (execution path):**
1) Configurar provider HTTP no módulo (base path do lead-service).
2) Verificar injeção dos headers via interceptors da Access Layer.

**Non-goals:** services específicos (FE-LEAD-004..007).

**Layer(s):** frontend / `libs/lead/data-access`
**Bounded context:** lead

**Service execution spec(s):** `frontend-spec/SPEC-04` · `standards/access-layer-contracts.md`

**Architecture alignment:** `@journeyos/shared/access-http-base`; tag `scope:lead` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/lead/data-access/src/lib/lead-http.provider.ts` — _MISSING_

**Tests**
- 🔲 `nx test lead-data-access` PASS — _MISSING_ · 🔲 `nx lint lead-data-access` PASS — _MISSING_

**Milestone:** Wave P4 / Hub integrations
**Labels:** type:integration · layer:frontend · scope:lead · priority:P4

**Acceptance criteria:**
- `npx nx test/lint/build lead-data-access` PASS
- Toda chamada LEAD trafega com auth + empresa headers (SPEC-04 EARS)

**Dependencies:** FE-LEAD-002
**API / Contract impact:** base URL do `lead-service`.
**Risks / Notes:** base URL configurável por ambiente.
