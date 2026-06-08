## [FE-WRKS-012] feature-workspace — settings + org structure

**Status:** 🔲 ABERTA
**GitHub:** [#TBD]

**Status:** INTACT — pos-validacao 2026-06-05
**Maturidade:** 30 — Inicial
**Done/Total:** 0/4 itens

**Outcome:**
`WorkspaceSettingsPageComponent` com form de parâmetros da empresa e árvore de org structure (business units / teams), salvando via `WorkspaceFacade`/`OrgStructureFacade`.

**Context / Problem statement:**
- Configuração do workspace (perm `wrks.empresa.editar`). Fonte: SPEC-01/02/03. Depende de FE-WRKS-004/007.

**Approach (execution path):**
1) `WorkspaceFormComponent` (presentational) emite `save(form)`.
2) `OrgStructureTreeComponent` → `BusinessUnitNodeComponent` → `TeamNodeComponent`.
3) Validações síncronas (nome não vazio); erros de campo via SPEC-07.

**Non-goals:** excluir BU/team; criar empresa.

**Layer(s):** frontend / libs/wrks/feature-workspace
**Bounded context:** wrks

**Service execution spec(s):** SPEC-01/02/03; SPEC-07

**Architecture alignment:** standalone + OnPush; `type:feature` `scope:wrks`.

**Implementation checklist (by file):**
- 🔲 `libs/wrks/feature-workspace/src/lib/workspace-settings.page.ts` (MISSING)
- 🔲 `libs/wrks/feature-workspace/src/lib/workspace-form.component.ts` (MISSING)
- 🔲 `libs/wrks/feature-workspace/src/lib/org-structure-tree.component.ts` (+ nodes) (MISSING)

**Tests**
- 🔲 `nx test wrks-feature-workspace` PASS (MISSING) · 🔲 `nx lint` PASS (MISSING)

**Milestone:** Wave P3 / Feature libs
**Labels:** type:feature · layer:frontend · scope:wrks · priority:P3

**Acceptance criteria:**
- `npx nx test/lint/build` PASS
- Flag `wrks.org-structure` desabilitada esconde a árvore

**Dependencies:** FE-WRKS-004, FE-WRKS-007
**API / Contract impact:** `PUT /empresas/{id}`, `/business-units`, `/teams`.
**Risks / Notes:** respeitar flag; sem otimismo em save.
