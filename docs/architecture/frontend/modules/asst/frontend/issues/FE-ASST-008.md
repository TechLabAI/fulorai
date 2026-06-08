## [FE-ASST-008] DTO mappers + error mapping (ProblemDetail → AppError)

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 15 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
Mappers DTO BE → VM FE (SPEC-03) e tradução `ProblemDetail`→`AppError` com a tabela de códigos
`asst.*` de SPEC-07, exposta às facades para `error()`/`studioState`.

**Context / Problem statement:**
- Centraliza o contrato de erro do módulo. Fonte: SPEC-07, SPEC-03. Depende de FE-ASST-004..007.
- Bloqueia: FE-ASST-018 (UX de erro), INT-FE-ASST-006.

**Approach (execution path):**
1) Mappers puros `AssetResponse→AssetDetailVM`, `AssetResumo→AssetResumoVM`, `VersaoAssetResponse→Versao*VM`, `Aprovacao→AprovacaoVM`.
2) `toAsstError(problem)` mapeando `code` → `AppError {code,title,detail,field?}` (422/404/409/503/403/401).
3) Casos especiais: `503 ia-indisponivel` → degradação; `404 sem-versao-publicada` → estado normal.

**Non-goals:** renderização (FE-ASST-018); wiring do error-model shared (INT-FE-ASST-006).

**Layer(s):** frontend / `libs/asst/data-access`
**Bounded context:** asst

**Service execution spec(s):** `frontend-spec/SPEC-07-error-handling.md` · `SPEC-03-view-models.md`

**Architecture alignment:** usa `@journeyos/shared/error-model`; mappers puros testáveis.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/data-access/src/lib/mappers/asset.mapper.ts`
- 🔲 [MISSING] `libs/asst/data-access/src/lib/mappers/versao.mapper.ts`
- 🔲 [MISSING] `libs/asst/data-access/src/lib/asst-error.mapper.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-data-access` PASS (cada `code` da tabela) · 🔲 [MISSING] `nx lint asst-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:asst · priority:P2

**Acceptance criteria:**
- Todos os `code` de SPEC-07 §tabela cobertos por teste
- Mappers puros (sem dependência de Angular runtime)

**Dependencies:** FE-ASST-004, FE-ASST-005, FE-ASST-006, FE-ASST-007
**API / Contract impact:** consome `ProblemDetail` (RFC 7807) do `asst-service`.
**Risks / Notes:** quando `@journeyos/shared/contracts` (OpenAPI) existir, DTOs migram para lá.
