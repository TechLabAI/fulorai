# 04 — Frontend Architecture Direction — ASST

> Direção técnica do módulo: stack, organização de libs (module-pattern + tags Nx), dependências
> `@journeyos/*`, routing, estado e contrato do módulo.

## 1. Stack

- **Angular 18+** (standalone, control flow novo, Signals), **Nx 19+** workspace (`@journeyos`).
- **TypeScript strict**.
- **RxJS 7.8** (interop pontual — HTTP/streams) **+ Signals** (estado de UI). Sem NgRx.
- **Jest** (unit) · **Playwright** (e2e em `apps/asst-e2e`).
- **SCSS** isolado em `libs/asst/styles` consumindo `@journeyos/shared/ui-tokens`.

## 2. App Boundary

`apps/asst/` é o host fino lazy do módulo; o entry real é a library `libs/asst/shell-entry`
(importPath `@journeyos/asst`, ADR-006), carregada pelo Shell via `loadChildren`. Todas as features
e componentes são `standalone` + `OnPush`.

## 3. Library Organization (tags Nx — padrão module-pattern)

| Lib | `type:*` | `scope:*` | Papel |
|---|---|---|---|
| `apps/asst` | `type:app` | `scope:asst` | host fino lazy |
| `libs/asst/shell-entry` | `type:domain` | `scope:asst` | entry como library (`@journeyos/asst`): contract, routes, bootstrap, permission-map, flags, nav |
| `libs/asst/feature-asset-library` | `type:feature` | `scope:asst` | catálogo + busca + filtros + criação |
| `libs/asst/feature-asset-detail` | `type:feature` | `scope:asst` | detalhe + histórico de versões + nova versão manual |
| `libs/asst/feature-asset-studio` | `type:feature` | `scope:asst` | composição assistida por IA |
| `libs/asst/feature-approval-workflow` | `type:feature` | `scope:asst` | fila + submit/aprovar/rejeitar/publicar |
| `libs/asst/data-access` | `type:data-access` | `scope:asst` | `AssetApiService`, `StudioApiService` + facades de signal |
| `libs/asst/access` | `type:domain` | `scope:asst` | guards específicos do módulo |
| `libs/asst/integration` | `type:domain` | `scope:asst` | `AsstShellIntegrationService` |
| `libs/asst/navigation` | `type:domain` | `scope:asst` | breadcrumb/menu state |
| `libs/asst/ui` | `type:ui` | `scope:asst` | asset-card, version-timeline, state-chip, origem-badge (opcional) |
| `libs/asst/styles` | `type:ui` | `scope:asst` | SCSS isolado |

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>`.

## 4. Shared Library Dependencies (`@journeyos/*` consumidas)

| Lib | Obrigatória? | Uso no ASST |
|---|---|---|
| `@journeyos/shared/access-http-base` | ✅ | HttpClient + interceptors (`X-Empresa-Id`, Correlation, ErrorNormalize). |
| `@journeyos/shared/auth-session` | ✅ | Sessão, claims, bearer token. |
| `@journeyos/shared/empresa-context` | ✅ | Empresa ativa (ASST consome; escopa todo dado). |
| `@journeyos/shared/access-decision` | ✅ | `AccessDecisionService.can('asst.*')`, `NavigationService`. |
| `@journeyos/shared/ui-tokens` · `ui-components` · `ui-feedback` | ✅ | Design tokens, primitivos, estados empty/loading/error. |
| `@journeyos/shared/error-model` | ✅ | `ProblemDetail → AppError` (`409`, `503`, `422`). |
| `@journeyos/shared/observability` | ◻ recomendado | Timing de composição, taxa de aprovação, latência do catálogo. |
| Patterns (`smart-table`, `approval-widget`, `timeline`) | ◻ se disponíveis | Catálogo, fila de aprovação, histórico de versões. Caso não existam como shared, ficam em `libs/asst/ui` e podem ser promovidos depois (asset-driven-ui). |

ASST **não** consome `@journeyos/shared/contracts` de outro módulo de domínio, nem widgets 3rd-party
no MVP.

## 5. Routing Strategy

- Shell → `@journeyos/asst` (shell-entry) via `loadChildren`.
- Sub-rotas via `loadComponent` (cada feature é standalone).
- Todas as rotas ASST são **pós-contexto** (exigem empresa ativa):
  `canActivate: [authGuard, empresaGuard, accessGuard(<perm>)]`.

```
/asst/library                → feature-asset-library      [authGuard, empresaGuard, accessGuard('asst.asset.ler')]
/asst/assets/:id             → feature-asset-detail        [authGuard, empresaGuard, accessGuard('asst.asset.ler')]
/asst/assets/:id/studio      → feature-asset-studio        [authGuard, empresaGuard, accessGuard('asst.studio.compor')]
/asst/approvals              → feature-approval-workflow   [authGuard, empresaGuard, accessGuard('asst.asset.aprovar')]
```

> Criação de asset e nova versão são ações dentro de `feature-asset-library`/`feature-asset-detail`
> (gated por `asst.asset.criar`/`asst.asset.editar`), não rotas próprias. Submeter/publicar são
> ações no detalhe/aprovação gated por `asst.asset.submeter`/`asst.asset.publicar`.

## 6. State Strategy

- **Signals locais** nas facades de `data-access`: `signal<T>` privado + `.asReadonly()` público
  (`catalogo`, `assetSelecionado`, `versoes`, `filaAprovacao`, `studioState`, `loading`, `error`).
- **Sem NgRx / BehaviorSubject manual** (ADR-002).
- Estado transversal (sessão/empresa/RBAC) **não** vive no ASST — vive na Access Layer
  (`@journeyos/shared/access-*`); o ASST apenas consome.
- `computed()` para derivações: ações disponíveis por estado do asset; versão vigente destacada;
  contagem da fila de aprovação; visibilidade de botões por permissão.

## 7. Module Contract Strategy (`asst.contract.ts`)

```ts
// ModuleMenuMetadata
{
  key: 'asst',
  label: 'Assets',
  route: '/asst/library',
  icon: 'folder_special',
  deepLinks: [
    { key: 'approvals', label: 'Aprovações', route: '/asst/approvals', perm: 'asst.asset.aprovar' },
  ],
}
```

- `ModulePermissionMap` — `asst.permission-map.ts`: mapeia rota/ação → permissão canônica
  (`asst.asset.ler|criar|editar|submeter|aprovar|publicar|arquivar`, `asst.studio.compor`).
- `ModuleFeatureFlags` — `asst.feature-flags.ts`: ex.: `asst.asset-studio` (`defaultState: on` —
  permite desligar o Studio sem afetar CRUD/aprovação, alinhado à degradação graciosa),
  `asst.approval-workflow` (`defaultState: on`). Cada flag com `defaultState` explícito.

---

## Referências

- `02-architecture-blueprint.md` (fronteiras internas)
- `05-state-and-data-flow.md` (data flow detalhado)
- BE: `docs/architecture/backend/services/asst-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- ADR-001 (module-pattern), ADR-002 (signals), ADR-003 (lazy module), ADR-004 (shell integration), ADR-005 (Asset Studio)
