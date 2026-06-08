## [FE-INTL-013] feature-knowledge — KnowledgeNodeFormPageComponent (form + tags + indexar)

**Status:** INTACT — pós-validação 2026-06-05
**Maturidade:** 20 — Inicial
**Done/Total:** 0/6 itens
**GitHub:** [#TBD]

**Outcome:**
`KnowledgeNodeFormPageComponent` (smart) com `KnowledgeNodeFormComponent` (+ `TagInputComponent`) e `IndexActionComponent`; cria/edita nó (`titulo`/`conteudo`/`tags`), e dispara Indexar com estado assíncrono (`RASCUNHO→indexando→INDEXADO`; `503`→retry).

**Context / Problem statement:**
- Edição + indexação. Fonte: SPEC-02 + SPEC-03 + SPEC-04 (indexar 202/503).
- Bloqueia: FE-INTL-019 (e2e knowledge-curation).

**Approach (execution path):**
1) Form reativo com validação (`titulo`/`conteudo` obrigatórios — INV-FE-3).
2) `IndexAction` reflete `indexState`; no `503` mostra "tentar de novo".
3) Salvar habilitado só com `intl.knowledge.write`.

**Non-goals:** editor rico/anexos (fora do MVP); lista (FE-INTL-012).

**Layer(s):** frontend / libs/intl/feature-knowledge
**Bounded context:** intl

**Service execution spec(s):** `frontend-spec/SPEC-02` · `SPEC-03` · `SPEC-04`

**Architecture alignment:** Standalone + OnPush; `scope:intl`.

**Implementation checklist (by file):**
- 🔲 `libs/intl/feature-knowledge/src/lib/knowledge-node-form.page.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-knowledge/src/lib/knowledge-node-form.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-knowledge/src/lib/tag-input.component.ts` — MISSING: arquivo não existe
- 🔲 `libs/intl/feature-knowledge/src/lib/index-action.component.ts` — MISSING: arquivo não existe

**Tests**
- 🔲 `nx test intl-feature-knowledge` PASS — MISSING: sem teste 503/retry · 🔲 `nx lint` PASS — MISSING: não executado

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:intl · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build intl-feature-knowledge` PASS
- Teste: `503` na indexação mantém `RASCUNHO` + ação retry.

**Dependencies:** FE-INTL-012
**API / Contract impact:** `/knowledge/nos` (create/update/indexar).
**Risks / Notes:** —
