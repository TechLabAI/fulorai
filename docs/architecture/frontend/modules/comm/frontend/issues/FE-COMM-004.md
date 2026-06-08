## [FE-COMM-004] TemplateApiService + TemplateCatalogFacade

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 12 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`TemplateApiService` (HTTP via access-http-base) + `TemplateCatalogFacade` (signals) cobrindo
`list/get/create/update/activate/archive` em `/api/v1/templates`, com signals `catalogoTemplates`,
`templateSelecionado`, `filtro`, `loading`, `error` e `computed` `acoesDisponiveis`/`variaveisInvalidas`.

**Context / Problem statement:**
- Base de dados das telas de template. Fonte: SPEC-04, SPEC-03. Depende: INT-FE-COMM-001. Bloqueia: FE-COMM-009, 010.

**Approach:**
1) `TemplateApiService` com os 6 métodos + paginação/filtros (`canal/tipo/estado/q/page/size`).
2) `TemplateCatalogFacade` convertendo Observable→signal; `computed` para ações por estado/permissão.
3) Validação síncrona de placeholders (`variaveisInvalidas`) e `assuntoObrigatorio` (EMAIL).

**Non-goals:** Studio (FE-COMM-005); UI das pages (FE-COMM-009/010); error mapping global (FE-COMM-008).

**Layer(s):** frontend / `libs/comm/data-access`
**Bounded context:** comm
**Service execution spec(s):** `frontend-spec/SPEC-04-data-access.md`, `SPEC-03-view-models.md`
**Architecture alignment:** signals-first (ADR-002); facade não usa BehaviorSubject; tag `scope:comm` `type:data-access`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/comm/data-access/src/lib/template-api.service.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/template-catalog.facade.ts`
- 🔲 [MISSING] `libs/comm/data-access/src/lib/dtos/template.dto.ts`

**Tests**
- 🔲 [MISSING] `nx test comm-data-access` PASS (mock HTTP) · 🔲 [MISSING] `nx lint comm-data-access` PASS

**Milestone:** Wave P2 / Data access
**Labels:** type:feature · layer:frontend · scope:comm · priority:P2

**Acceptance criteria:**
- Facade expõe signals readonly; `nx test/lint comm-data-access` PASS
- Cobre estados `RASCUNHO/ATIVO/ARQUIVADO` e transições

**Dependencies:** INT-FE-COMM-001
**API / Contract impact:** `/api/v1/templates` (list/get/create/update/ativar/arquivar).
**Risks / Notes:** placeholders validados no FE espelhando `comm.template.variavel-nao-declarada`.
