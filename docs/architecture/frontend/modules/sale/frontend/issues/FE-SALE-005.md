## [FE-SALE-005] Oportunidade data-access (service + pipeline/detail facades + snapshot)

**Status (validação):** INTACT — pós-validação 2026-06-05
**Maturidade:** 10 — Inicial
**Done/Total:** 0/6 itens

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Outcome:**
`OportunidadeApiService` (HTTP via access-http-base) com `list/get/create/moverEstagio/ganhar/perder` e
as facades `PipelineFacade` / `OpportunityDetailFacade` expondo signals readonly (colunas, oportunidades,
filtro, `movingCardId`, podeMover/podeCriar, oportunidade, historico, podeFechar, naoEncontrada).
`PipelineFacade` guarda o **snapshot** do último estado confirmado para rollback do move otimista (ADR-005).

**Context / Problem statement:**
- Recurso central (fonte do board + detalhe). Map `OportunidadeResumo`/`OportunidadeResponse` (+ histórico) → VMs de SPEC-03.
- Fonte: SPEC-04 (Oportunidade) + SPEC-03 (VMs). Depende de INT-FE-SALE-001. Bloqueia: FE-SALE-010, FE-SALE-011.

**Approach (execution path):**
1) `OportunidadeApiService`: `GET ?estagio=&responsavel=&estado=&page=&size=`, `GET /{id}`, `POST`, `PATCH /{id}/estagio`, `POST /{id}/ganhar`, `POST /{id}/perder`.
2) `PipelineFacade`: deriva `colunas` (por estágio, com `total`/`somaValor`); `moverEstagio` faz **optimistic move + snapshot** + rollback no erro.
3) `OpportunityDetailFacade`: `oportunidade`/`historico`/`podeFechar`; `naoEncontrada` em `404`.
4) Mapear respostas BE → `OpportunityCardVm`/`OpportunityDetailVm`/`StageHistoryItemVm`.

**Non-goals:** UI do Kanban (FE-SALE-010); error→message mapping detalhado (FE-SALE-009).

**Layer(s):** frontend / `libs/sale/data-access`
**Bounded context:** sale

**Service execution spec(s):** `SPEC-04-data-access.md` (Oportunidade) · `SPEC-03-view-models.md` (pipeline/opportunity)

**Architecture alignment:** facade pattern (signal privado + `.asReadonly()`); RxJS só na borda; tag `scope:sale` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 `libs/sale/data-access/src/lib/oportunidade-api.service.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/pipeline.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/opportunity-detail.facade.ts` — _MISSING_
- 🔲 `libs/sale/data-access/src/lib/mappers/oportunidade.mapper.ts` — _MISSING_

**Tests**
- 🔲 `nx test sale-data-access` PASS — _MISSING_ · 🔲 `nx lint sale-data-access` PASS — _MISSING_

**Milestone:** Wave P2 / Data access
**Labels:** type:data-access · layer:frontend · scope:sale · priority:P2

**Acceptance criteria:**
- `npx nx test/lint/build sale-data-access` PASS
- Move otimista guarda snapshot e faz rollback (EARS SPEC-04 #3); estado exposto só como signal readonly (EARS SPEC-04 #2)

**Dependencies:** INT-FE-SALE-001
**Data impact:** estado in-memory (board + snapshot) enquanto a página está montada; sem persistência client-side.
**API / Contract impact:** `/api/v1/oportunidades` (list/get/create/estagio/ganhar/perder).
**Testing / Evidence required:** teste do rollback (PATCH falho); teste de `naoEncontrada` (404).
**Risks / Notes:** gaps G2 (titulo do card) e G3 (responsavelNome) — compor de resumo; fallback id (FE-SALE-016).
