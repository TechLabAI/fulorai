# 04 — Frontend Architecture Direction — LEAD

> Direção técnica do módulo: stack, organização de libs (module-pattern + tags Nx), dependências
> `@journeyos/*`, routing, estado e contrato do módulo.

## 1. Stack

- **Angular 18+** (standalone, control flow novo, Signals), **Nx 19+** workspace (`@journeyos`).
- **TypeScript strict**.
- **RxJS 7.8** (interop pontual — HTTP/streams) **+ Signals** (estado de UI). Sem NgRx.
- **Jest** (unit) · **Playwright** (e2e em `apps/lead-e2e`).
- **SCSS** isolado em `libs/lead/styles` consumindo `@journeyos/shared/ui-tokens`.

## 2. App Boundary

`apps/lead/` é o host fino lazy do módulo; o entry real é a library `libs/lead/shell-entry`
(importPath `@journeyos/lead`, ADR-003/006), carregada pelo Shell via `loadChildren`. Todas as
features e componentes são `standalone` + `OnPush`.

## 3. Library Organization (tags Nx — padrão module-pattern)

| Lib | `type:*` | `scope:*` | Papel |
|---|---|---|---|
| `apps/lead` | `type:app` | `scope:lead` | host fino lazy |
| `libs/lead/shell-entry` | `type:domain` | `scope:lead` | entry como library (`@journeyos/lead`): contract, routes, bootstrap, permission-map, flags, nav, descriptor |
| `libs/lead/feature-lead-list` | `type:feature` | `scope:lead` | fila priorizada + filtros + busca + paginação |
| `libs/lead/feature-lead-detail` | `type:feature` | `scope:lead` | perfil + breakdown 6D + ações (qualify/LGPD) |
| `libs/lead/feature-maturity-score` | `type:feature` | `scope:lead` | radar 6D + dashboard de distribuição/saúde |
| `libs/lead/feature-segmentation` | `type:feature` | `scope:lead` | CRUD de segmentos + prévia de contagem |
| `libs/lead/feature-survey` | `type:feature` | `scope:lead` | definição de survey/perguntas + captura de respostas |
| `libs/lead/feature-qualification-rules` | `type:feature` | `scope:lead` | versões de regra + ativação + recálculo |
| `libs/lead/data-access` | `type:data-access` | `scope:lead` | `LeadApiService`, `SurveyApiService`, `QualificationApiService`, `SegmentApiService` + facades de signal |
| `libs/lead/access` | `type:domain` | `scope:lead` | guards específicos (ex.: `leadDataScopeGuard`) |
| `libs/lead/integration` | `type:domain` | `scope:lead` | `LeadShellIntegrationService` |
| `libs/lead/navigation` | `type:domain` | `scope:lead` | breadcrumb/menu state |
| `libs/lead/ui` | `type:ui` | `scope:lead` | score-radar, dimension-bar, score-badge, lead-state-chip, maturity-distribution-chart |
| `libs/lead/styles` | `type:ui` | `scope:lead` | SCSS isolado |

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>`.

## 4. Shared Library Dependencies (`@journeyos/*` consumidas)

| Lib | Obrigatória? | Uso no LEAD |
|---|---|---|
| `@journeyos/shared/access-http-base` | ✅ | HttpClient + interceptors (`X-Empresa-Id`, Correlation, ErrorNormalize). |
| `@journeyos/shared/auth-session` | ✅ | Sessão, claims, bearer token. |
| `@journeyos/shared/empresa-context` | ✅ | Empresa ativa (escopa fila/segmentos/surveys). |
| `@journeyos/shared/access-decision` | ✅ | `AccessDecisionService.can('lead.*')`, `NavigationService`. |
| `@journeyos/shared/ui-tokens` · `ui-components` · `ui-feedback` | ✅ | Tokens, primitivos, estados empty/loading/error. |
| `@journeyos/shared/error-model` | ✅ | `ProblemDetail → AppError` (`409`, `422`, `404`). |
| `@journeyos/shared/observability` | ◻ recomendado | Latência da fila, tempo até qualify, % com assist IA. |
| Patterns (`smart-table`, `chart/radar`) | ◻ se disponíveis | Fila (smart-table); Maturity Score 6D (radar). Caso não existam como shared, ficam em `libs/lead/ui` e podem ser promovidos depois (asset-driven-ui). |

LEAD **não** consome `scope:` de outro módulo de domínio, nem widgets 3rd-party no MVP. O assist de IA
do score é **BE-side**; o FE nunca chama IA nem a TechLab AI.

## 5. Routing Strategy

- Shell → `@journeyos/lead` (shell-entry) via `loadChildren`.
- Sub-rotas via `loadComponent` (cada feature standalone).
- Todas as rotas LEAD são **pós-contexto** (exigem empresa ativa):
  `canActivate: [authGuard, empresaGuard, accessGuard(<perm>)]`.

```
/lead/leads               → feature-lead-list            [authGuard, empresaGuard, accessGuard('lead.lead.read')]
/lead/leads/:id           → feature-lead-detail          [authGuard, empresaGuard, accessGuard('lead.lead.read')]
/lead/maturity            → feature-maturity-score       [authGuard, empresaGuard, accessGuard('lead.lead.read')]
/lead/segments            → feature-segmentation         [authGuard, empresaGuard, accessGuard('lead.segment.read')]
/lead/surveys             → feature-survey               [authGuard, empresaGuard, accessGuard('lead.survey.read')]
/lead/qualification       → feature-qualification-rules  [authGuard, empresaGuard, accessGuard('lead.qualification.read')]
```

> Editar perfil, **requalificar**, anonimizar e expurgar são **ações** dentro de `feature-lead-detail`
> (gated por `lead.lead.editar` / `lead.qualification.executar` / `lead.lead.anonimizar` /
> `lead.lead.expurgar`), não rotas próprias. Criar/ativar regra são ações em `feature-qualification-rules`
> (`lead.qualification.criar` / `lead.qualification.ativar`). Responder survey de um lead acontece no
> detalhe ou em `feature-survey` (`lead.survey.responder`).

## 6. State Strategy

- **Signals locais** nas facades de `data-access`: `signal<T>` privado + `.asReadonly()` público
  (`fila`, `leadSelecionado`, `score`, `distribuicao`, `segmentos`, `surveys`, `regras`, `loading`, `error`).
- **Sem NgRx / BehaviorSubject manual** (ADR-002).
- Estado transversal (sessão/empresa/RBAC) **não** vive no LEAD — vive na Access Layer
  (`@journeyos/shared/access-*`); o LEAD apenas consome e reage a troca de empresa.
- `computed()` para derivações: ações disponíveis por estado do lead + permissão; faixa do score;
  destaque da versão de regra ativa; contagem por segmento; visibilidade de badge `assistIa`.

## 7. Module Contract Strategy (`lead.contract.ts`)

```ts
// ModuleMenuMetadata
{
  key: 'lead',
  label: 'Leads',
  route: '/lead/leads',
  icon: 'groups',
  deepLinks: [
    { key: 'maturity',      label: 'Maturity Score', route: '/lead/maturity',      perm: 'lead.lead.read' },
    { key: 'segments',      label: 'Segmentos',      route: '/lead/segments',      perm: 'lead.segment.read' },
    { key: 'surveys',       label: 'Surveys',        route: '/lead/surveys',       perm: 'lead.survey.read' },
    { key: 'qualification', label: 'Regras',         route: '/lead/qualification', perm: 'lead.qualification.read' },
  ],
}
```

- `ModulePermissionMap` — `lead.permission-map.ts`: mapeia rota/ação → permissão canônica
  (`lead.lead.{read,criar,editar,anonimizar,expurgar}`, `lead.survey.{read,criar,editar,responder}`,
  `lead.qualification.{read,criar,ativar,executar}`, `lead.segment.{read,criar,editar,excluir}`).
- `ModuleFeatureFlags` — `lead.feature-flags.ts`: `lead.maturity-score` (`defaultState: on` — radar 6D +
  dashboard de distribuição); `lead.qualification-rules` (`defaultState: on` — governança de regras na UI).
  Cada flag com `defaultState` explícito. O badge `assistIa` **não** é flag — é sempre exibido
  (transparência do score).

---

## Referências

- `02-architecture-blueprint.md` (fronteiras internas) · `05-state-and-data-flow.md` (data flow)
- BE: `docs/architecture/backend/services/lead-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- ADR-001 (module-pattern), ADR-002 (signals), ADR-003 (lazy module), ADR-004 (shell integration), ADR-005 (Maturity Score viz)
