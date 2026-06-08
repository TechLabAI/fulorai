## [FE-ASST-005] VersaoApiService + AssetDetailFacade (versões)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`VersaoApiService` (list/get/create/getPublished) + `AssetDetailFacade` (signals `asset`, `versoes`,
`versaoSelecionada`, `acoesDisponiveis` computed, `loading`, `error`) em `libs/asst/data-access`.

**Context / Problem statement:**
- Detalhe + histórico de versões + versão vigente. Fonte: SPEC-04 (Versão). Depende de FE-ASST-004 (asset get).
- Bloqueia: FE-ASST-011, FE-ASST-012.

**Approach (execution path):**
1) `VersaoApiService`: `GET /{id}/versoes`, `GET /{id}/versoes/{numero}`, `POST /{id}/versoes` (origem MANUAL), `GET /{id}/published`.
2) `AssetDetailFacade`: `acoesDisponiveis` = `computed` do `asset().estado` + permissões (UINV-5).
3) Cache de conteúdo de versão por id (imutável — UINV-4); só `versaoVigenteId` muda ao publicar.

**Non-goals:** UI (P3); workflow transitions (FE-ASST-007).

**Layer(s):** frontend / `libs/asst/data-access`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md` (Versão)

**Architecture alignment:** ADR-002 signals; `computed` para ações; tag `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/data-access/src/lib/versao-api.service.ts` (apenas o stub default `asst-data-access.component.*` existe; service nao criado)
- 🔲 [MISSING] `libs/asst/data-access/src/lib/asset-detail.facade.ts` (inexistente)
- 🔲 [MISSING] `libs/asst/data-access/src/lib/dto/versao.dto.ts` (inexistente)

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS · 🔲 [MISSING] `nx lint asst-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:asst · priority:P2

**Acceptance criteria:**
- `getPublished` 404 (`sem-versao-publicada`) tratado como estado normal, não erro
- `acoesDisponiveis` nunca inclui transição inválida para o estado atual (UINV-5)

**Dependencies:** FE-ASST-004
**API / Contract impact:** `GET/POST /{id}/versoes`, `GET /{id}/versoes/{numero}`, `GET /{id}/published`.
**Risks / Notes:** `conteudo` tipado `unknown` no MVP (R-5).
