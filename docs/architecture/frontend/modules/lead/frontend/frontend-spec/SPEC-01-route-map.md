# SPEC-01 — Route Map — LEAD · Frontend

> Todas as rotas que o LEAD expõe, seus guards, títulos e breadcrumbs. Todas são **pós-contexto**
> (exigem sessão + empresa ativa). Fonte: `04-frontend-architecture-direction.md` §5.

## Tabela mestre

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/lead` | _redirect → `/lead/leads`_ | `shell-entry` | `authGuard`, `empresaGuard` | — | — |
| `/lead/leads` | `LeadListPageComponent` | `feature-lead-list` | `authGuard`, `empresaGuard`, `accessGuard('lead.lead.read')` | "Leads" | `Leads` |
| `/lead/leads/:id` | `LeadDetailPageComponent` | `feature-lead-detail` | `authGuard`, `empresaGuard`, `accessGuard('lead.lead.read')` | "Detalhe do lead" | `Leads > {nome\|id}` |
| `/lead/maturity` | `MaturityDashboardPageComponent` | `feature-maturity-score` | `authGuard`, `empresaGuard`, `accessGuard('lead.lead.read')` | "Maturity Score" | `Leads > Maturity Score` |
| `/lead/segments` | `SegmentListPageComponent` | `feature-segmentation` | `authGuard`, `empresaGuard`, `accessGuard('lead.segment.read')` | "Segmentos" | `Leads > Segmentos` |
| `/lead/surveys` | `SurveyListPageComponent` | `feature-survey` | `authGuard`, `empresaGuard`, `accessGuard('lead.survey.read')` | "Surveys" | `Leads > Surveys` |
| `/lead/surveys/:id` | `SurveyEditorPageComponent` | `feature-survey` | `authGuard`, `empresaGuard`, `accessGuard('lead.survey.read')` | "Editar survey" | `Leads > Surveys > {título}` |
| `/lead/qualification` | `QualificationRulesPageComponent` | `feature-qualification-rules` | `authGuard`, `empresaGuard`, `accessGuard('lead.qualification.read')` | "Regras" | `Leads > Regras` |

## Detalhe por rota

### `/lead` (raiz)
- **Ownership:** `shell-entry` (`lead.routes.ts`). Redireciona para `/lead/leads` (`pathMatch: 'full'`).
- Guards: `authGuard`, `empresaGuard` (não há acesso pré-contexto no LEAD).

### `/lead/leads`
- **Ownership:** `feature-lead-list`. Lista priorizada por Maturity Score (Elastic-backed).
- `data`: `{ title: 'Leads', breadcrumbs: ['Leads'], permissionRequired: 'lead.lead.read' }`.
- Query params de filtro: `?segmento=&dimensao=&estado=&q=&page=&size=` (refletem `LeadFiltroVM`).

### `/lead/leads/:id`
- **Ownership:** `feature-lead-detail`. Perfil + breakdown 6D + ações.
- `data`: `{ title: 'Detalhe do lead', breadcrumbs: ['Leads', ':nome'], permissionRequired: 'lead.lead.read' }`.
- Ações na página (não são rotas): **editar perfil** (`lead.lead.editar`), **requalificar**
  (`lead.qualification.executar`), **anonimizar** (`lead.lead.anonimizar`), **expurgar**
  (`lead.lead.expurgar`), **responder survey** (`lead.survey.responder`). Ações derivam do **estado**
  do lead + permissão.
- `:id` inexistente → `404 lead.lead.nao-encontrado` → estado "lead não encontrado".

### `/lead/maturity`
- **Ownership:** `feature-maturity-score`. Dashboard de distribuição/saúde da base + radar reusável.
- `data`: `{ title: 'Maturity Score', breadcrumbs: ['Leads', 'Maturity Score'], permissionRequired: 'lead.lead.read' }`.
- Pode ser desabilitada pela feature flag `lead.maturity-score`.

### `/lead/segments`
- **Ownership:** `feature-segmentation`. CRUD de segmentos; abrir item → fila do segmento
  (`/lead/leads?segmento=:id`).
- `data`: `{ title: 'Segmentos', breadcrumbs: ['Leads', 'Segmentos'], permissionRequired: 'lead.segment.read' }`.

### `/lead/surveys` e `/lead/surveys/:id`
- **Ownership:** `feature-survey`. Lista/edição de surveys + perguntas.
- `data`: `{ permissionRequired: 'lead.survey.read' }`. Editar/criar gated por `lead.survey.editar`/`criar`.

### `/lead/qualification`
- **Ownership:** `feature-qualification-rules`. Lista de versões; criar versão; **ativar**; requalificar afetados.
- `data`: `{ title: 'Regras', breadcrumbs: ['Leads', 'Regras'], permissionRequired: 'lead.qualification.read' }`.
- Pode ser desabilitada pela feature flag `lead.qualification-rules`.

## Critérios de aceite (EARS)

- `WHEN the user navigates to /lead, THE SYSTEM SHALL redirect to /lead/leads.`
- `IF the user has no active empresa context, THEN THE SYSTEM SHALL block every /lead route via empresaGuard and redirect to the empresa selection.`
- `IF the user lacks the permission required by a LEAD route, THEN THE SYSTEM SHALL deny activation via accessGuard and SHALL hide the corresponding menu deep link.`
- `WHEN the user opens /lead/leads/:id for a non-existent lead, THE SYSTEM SHALL render the "lead não encontrado" state instead of an empty detail.`
- `WHILE the feature flag lead.maturity-score is disabled, THE SYSTEM SHALL omit the /lead/maturity route and its menu entry.`
- `THE SYSTEM SHALL expose every LEAD route as lazy-loaded via the @journeyos/lead shell-entry.`

## Notas

- Guards vivem em `libs/lead/access/` e consomem `AccessDecisionService` (Access Layer) — a UI **não**
  decide RBAC.
- Em troca de empresa, o `NavigationService` re-deriva o menu; a fila é invalidada.
- Deep links "Maturity Score", "Segmentos", "Surveys", "Regras" só aparecem com a permissão respectiva.

## Referências
- `04-frontend-architecture-direction.md` §5 · `02-architecture-blueprint.md` §3
- BE: `lead-service/contracts/api-contract.md` (perms por endpoint)
