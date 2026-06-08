## [FE-JRNY-004] Journey data-access: JourneyApiService + facades

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]
**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/6 itens

**Outcome:**
`JourneyApiService` (`/api/v1/journeys`) + `JourneyListFacade` e `JourneyBuilderFacade` em
`libs/jrny/data-access`, expondo signals readonly. Operações: `list`, `get`, `create`, `update`,
`publicar`, `arquivar`, `novaVersao`. `computed` para `editavel`/`podePublicar`/`acoesDisponiveis`.

**Context / Problem statement:**
- Núcleo de leitura/escrita de jornadas; alimenta journey-list e journey-builder.
- Fonte: SPEC-03 (VMs), SPEC-04 (endpoints). Bloqueia: FE-JRNY-009, FE-JRNY-010.

**Approach (execution path):**
1) `JourneyApiService` com os 7 métodos sobre `/api/v1/journeys` (via access-http-base).
2) `JourneyListFacade` (lista paginada + filtro signal) e `JourneyBuilderFacade` (jornada em edição).
3) `computed`: `editavel = RASCUNHO && perm`, `podePublicar = editavel && estagios>=1`, `acoesDisponiveis`.

**Non-goals:** estágios (FE-JRNY-005); UI (P3); error mapping detalhado (FE-JRNY-008).

**Layer(s):** frontend / `libs/jrny/data-access`
**Bounded context:** jrny

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` · `SPEC-03-view-models.md`

**Architecture alignment:** Signals-first (ADR-002); `signal` privado + `.asReadonly()`; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/jrny/data-access/src/lib/journey-api.service.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/journey-list.facade.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/journey-builder.facade.ts` (MISSING)
- 🔲 `libs/jrny/data-access/src/lib/journey.models.ts` (VMs/DTOs FE) (MISSING)

**Tests**
- 🔲 `nx test jrny-data-access` PASS (MISSING) · 🔲 `nx lint jrny-data-access` PASS (MISSING)

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:jrny · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build jrny-data-access` PASS
- Estado exposto só como readonly signals; nenhum `HttpClient` fora do service

**Dependencies:** INT-FE-JRNY-001 (http-base)
**API / Contract impact:** `/api/v1/journeys` (CRUD + publicar/arquivar/nova-versao).
**Risks / Notes:** `update` só em RASCUNHO (409 transicao-invalida) — refletir em `editavel`.
