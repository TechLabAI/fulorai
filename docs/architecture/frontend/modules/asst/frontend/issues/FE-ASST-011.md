## [FE-ASST-011] feature-asset-detail: page + header + ações estado-driven

**Status:** INTACT -- pos-validacao 2026-06-05
**Maturidade:** 18 -- Inicial
**Done/Total:** 0/5 itens
**GitHub:** [#TBD]

**Outcome:**
`AssetDetailPageComponent` (smart) + `AssetHeaderComponent` + `AssetActionsComponent` consumindo
`AssetDetailFacade`/`ApprovalFacade`; ações (editar/nova-versão/submeter/publicar/arquivar/studio)
derivadas de `acoesDisponiveis()` (estado + permissão).

**Context / Problem statement:**
- Hub do asset (estado, metadados, ações de workflow). Fonte: SPEC-02 (feature-asset-detail), SPEC-01. Depende de FE-ASST-005, FE-ASST-007.
- Bloqueia: FE-ASST-012, FE-ASST-013 (abre studio), FE-ASST-020.

**Approach (execution path):**
1) `AssetDetailPageComponent` resolve `:id`; lê `asset()/acoesDisponiveis()/loading()/error()`.
2) `AssetHeaderComponent` (título/estado/edição/arquivar) + `AssetActionsComponent` (botões derivados — UINV-5).
3) Editar metadados reusa `AssetMetadataFormComponent`; submeter via `ApprovalFacade`.

**Non-goals:** timeline/conteúdo de versão (FE-ASST-012); UI do studio (FE-ASST-013).

**Layer(s):** frontend / `libs/asst/feature-asset-detail`
**Bounded context:** asst

**Service execution spec(s):** `SPEC-02` · `SPEC-01` · `SPEC-03`

**Architecture alignment:** Standalone/OnPush/Signals; ações via `computed`.

**Implementation checklist (by file):**
- 🔲 [MISSING] `libs/asst/feature-asset-detail/src/lib/asset-detail.page.ts`
- 🔲 [MISSING] `libs/asst/feature-asset-detail/src/lib/asset-header.component.ts`
- 🔲 [MISSING] `libs/asst/feature-asset-detail/src/lib/asset-actions.component.ts`

**Tests**
- 🔲 [MISSING] `nx test asst-feature-asset-detail` PASS · 🔲 [MISSING] `nx lint asst-feature-asset-detail` PASS

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:asst · priority:P3

**Acceptance criteria:**
- Botões refletem exatamente as transições válidas do estado atual (UINV-5)
- `404 nao-encontrado` → estado "asset não encontrado"

**Dependencies:** FE-ASST-005, FE-ASST-007
**API / Contract impact:** `GET/PATCH /{id}`, `POST /{id}/submit|arquivar`.
**Risks / Notes:** ações nunca decididas pela UI sozinha — sempre via AccessDecision (UINV-2).
