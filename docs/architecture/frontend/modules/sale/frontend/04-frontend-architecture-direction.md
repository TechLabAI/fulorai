# 04 — Frontend Architecture Direction — SALE

> Direção técnica do módulo: stack, organização de libs (module-pattern + tags Nx), dependências
> `@journeyos/*`, routing, estado e contrato do módulo.

## 1. Stack

- **Angular 18+** (standalone, control flow novo, Signals), **Nx 19+** workspace (`@journeyos`).
- **TypeScript strict**.
- **RxJS 7.8** (interop pontual — HTTP/streams) **+ Signals** (estado de UI). Sem NgRx.
- **Angular CDK DragDrop** (`@angular/cdk/drag-drop`) para o Kanban do pipeline (ver `ADR-005`).
- **Jest** (unit) · **Playwright** (e2e em `apps/sale-e2e`).
- **SCSS** isolado em `libs/sale/styles` consumindo `@journeyos/shared/ui-tokens`.

## 2. App Boundary

`apps/sale/` é o host fino lazy do módulo; o entry real é a library `libs/sale/shell-entry`
(importPath `@journeyos/sale`, ADR-003/006), carregada pelo Shell via `loadChildren`. Todas as
features e componentes são `standalone` + `OnPush`.

## 3. Library Organization (tags Nx — padrão module-pattern)

| Lib | `type:*` | `scope:*` | Papel |
|---|---|---|---|
| `apps/sale` | `type:app` | `scope:sale` | host fino lazy |
| `libs/sale/shell-entry` | `type:app` | `scope:sale` | entry como library (`@journeyos/sale`): contract, routes, bootstrap, permission-map, flags, nav, descriptor |
| `libs/sale/feature-pipeline` | `type:feature` | `scope:sale` | Kanban de oportunidades por estágio + drag move (ADR-005) |
| `libs/sale/feature-opportunity` | `type:feature` | `scope:sale` | detalhe + histórico de estágio + ganhar/perder |
| `libs/sale/feature-offer` | `type:feature` | `scope:sale` | catálogo de ofertas versionadas (CRUD + desativar) |
| `libs/sale/feature-purchase` | `type:feature` | `scope:sale` | lista/detalhe de compras + breakdown + estornar/cancelar |
| `libs/sale/feature-attribution` | `type:feature` | `scope:sale` | versões de modelo + ativar + breakdown de uma compra |
| `libs/sale/feature-revenue-dashboard` | `type:feature` | `scope:sale` | funil de receita por origem/período + LTV (read-only) |
| `libs/sale/data-access` | `type:data-access` | `scope:sale` | `OportunidadeApiService`, `OfertaApiService`, `CompraApiService`, `AtribuicaoApiService`, `LtvApiService` + facades de signal |
| `libs/sale/access` | `type:domain` | `scope:sale` | guards específicos (ex.: `saleDataScopeGuard`) |
| `libs/sale/integration` | `type:domain` | `scope:sale` | `SaleShellIntegrationService` |
| `libs/sale/navigation` | `type:domain` | `scope:sale` | breadcrumb/menu state |
| `libs/sale/ui` | `type:ui` | `scope:sale` | kanban-board, kanban-column, opportunity-card, stage-history-timeline, attribution-breakdown, revenue-funnel-chart, ltv-table |
| `libs/sale/styles` | `type:ui` | `scope:sale` | SCSS isolado |

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>` —
SALE **não** importa `scope:lead`/`scope:intl`; as dependências soft de LEAD/INTL são lidas **só via
API BE**.

## 4. Shared Library Dependencies (`@journeyos/*` consumidas)

| Lib | Obrigatória? | Uso no SALE |
|---|---|---|
| `@journeyos/shared/access-http-base` | ✅ | HttpClient + interceptors (`X-Empresa-Id`, Correlation, ErrorNormalize). |
| `@journeyos/shared/auth-session` | ✅ | Sessão, claims, bearer token. |
| `@journeyos/shared/empresa-context` | ✅ | Empresa ativa (escopa pipeline/ofertas/compras/atribuição/LTV). |
| `@journeyos/shared/access-decision` | ✅ | `AccessDecisionService.can('sale.*')`, `NavigationService`. |
| `@journeyos/shared/ui-tokens` · `ui-components` · `ui-feedback` | ✅ | Tokens, primitivos, estados empty/loading/error. |
| `@journeyos/shared/error-model` | ✅ | `ProblemDetail → AppError` (`409`, `422`, `404`). |
| `@angular/cdk/drag-drop` | ✅ | Drag-and-drop do Kanban (mover estágio) — ver `ADR-005`. |
| `@journeyos/shared/observability` | ◻ recomendado | Latência do Kanban, tempo até ganho/perda, taxa de estorno. |
| Patterns (`smart-table`, `timeline`, chart) | ◻ se disponíveis | Compras/ofertas/LTV (smart-table); histórico (timeline); funil de receita (chart). Caso não existam como shared, ficam em `libs/sale/ui` e podem ser promovidos depois (asset-driven-ui). |

SALE **não** consome `scope:` de outro módulo de domínio, nem widgets 3rd-party no MVP. **Não há IA no
MVP** — o FE nunca chama IA nem a TechLab AI; atribuição/LTV são determinísticos.

## 5. Routing Strategy

- Shell → `@journeyos/sale` (shell-entry) via `loadChildren`.
- Sub-rotas via `loadComponent` (cada feature standalone).
- Todas as rotas SALE são **pós-contexto** (exigem empresa ativa):
  `canActivate: [authGuard, empresaGuard, accessGuard(<perm>)]`.

```
/sale/pipeline            → feature-pipeline            [authGuard, empresaGuard, accessGuard('sale.oportunidade.read')]
/sale/pipeline/:id        → feature-opportunity         [authGuard, empresaGuard, accessGuard('sale.oportunidade.read')]
/sale/ofertas             → feature-offer               [authGuard, empresaGuard, accessGuard('sale.oferta.read')]
/sale/compras             → feature-purchase            [authGuard, empresaGuard, accessGuard('sale.compra.read')]
/sale/compras/:id         → feature-purchase (detalhe)  [authGuard, empresaGuard, accessGuard('sale.compra.read')]
/sale/atribuicao          → feature-attribution         [authGuard, empresaGuard, accessGuard('sale.atribuicao.read')]
/sale/receita             → feature-revenue-dashboard   [authGuard, empresaGuard, accessGuard('sale.ltv.read')]
```

> **Mover estágio** (`sale.oportunidade.mover`), **ganhar/perder** (`sale.oportunidade.fechar`),
> **criar/editar/desativar oferta** (`sale.oferta.criar/editar/desativar`), **estornar/cancelar compra**
> (`sale.compra.estornar/cancelar`) e **criar/ativar modelo** (`sale.atribuicao.criar/ativar`) são
> **ações** dentro das features, não rotas próprias. A criação de compra (`sale.compra.registrar`) é
> **server-to-server** — não tem tela no FE no MVP.

## 6. State Strategy

- **Signals locais** nas facades de `data-access`: `signal<T>` privado + `.asReadonly()` público
  (`board`, `oportunidadeSelecionada`, `ofertas`, `compras`, `compraSelecionada`, `modelos`,
  `breakdown`, `funilReceita`, `ltv`, `loading`, `error`).
- **Sem NgRx / BehaviorSubject manual** (ADR-002).
- Estado transversal (sessão/empresa/RBAC) **não** vive no SALE — vive na Access Layer
  (`@journeyos/shared/access-*`); o SALE apenas consome e reage a troca de empresa.
- `computed()` para derivações: ações disponíveis por estado da oportunidade + permissão; soma de valor
  por coluna do Kanban; destaque da versão de modelo ativa; conservação de receita no breakdown.
- **Optimistic move** no Kanban com rollback (ver `ADR-005` e `05-state-and-data-flow.md §4`).

## 7. Module Contract Strategy (`sale.contract.ts`)

```ts
// ModuleMenuMetadata
{
  key: 'sale',
  label: 'Vendas',
  route: '/sale/pipeline',
  icon: 'monetization_on',
  deepLinks: [
    { key: 'ofertas',    label: 'Ofertas',    route: '/sale/ofertas',    perm: 'sale.oferta.read' },
    { key: 'compras',    label: 'Compras',    route: '/sale/compras',    perm: 'sale.compra.read' },
    { key: 'atribuicao', label: 'Atribuição', route: '/sale/atribuicao', perm: 'sale.atribuicao.read' },
    { key: 'receita',    label: 'Receita',    route: '/sale/receita',    perm: 'sale.ltv.read' },
  ],
}
```

- `ModulePermissionMap` — `sale.permission-map.ts`: mapeia rota/ação → permissão canônica
  (`sale.oportunidade.{criar,read,mover,fechar}`, `sale.oferta.{read,criar,editar,desativar}`,
  `sale.compra.{read,registrar,estornar,cancelar}`, `sale.atribuicao.{read,criar,ativar}`, `sale.ltv.read`).
- `ModuleFeatureFlags` — `sale.feature-flags.ts`: `sale.pipeline-kanban` (`defaultState: on` — board com
  drag-and-drop); `sale.revenue-dashboard` (`defaultState: on` — funil + LTV). Cada flag com
  `defaultState` explícito. O **breakdown de atribuição** **não** é flag — é sempre exibido
  (explicabilidade da receita).

---

## Referências

- `02-architecture-blueprint.md` (fronteiras internas) · `05-state-and-data-flow.md` (data flow)
- BE: `docs/architecture/backend/services/sale-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- ADR-001 (module-pattern), ADR-002 (signals), ADR-003 (lazy module), ADR-004 (shell integration), ADR-005 (Kanban + optimistic move)
