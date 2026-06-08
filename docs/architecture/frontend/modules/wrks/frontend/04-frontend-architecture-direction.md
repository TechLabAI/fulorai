# 04 — Frontend Architecture Direction — WRKS

> Direção técnica do módulo: stack, organização de libs (module-pattern + tags Nx), dependências
> `@journeyos/*`, routing, estado e contrato do módulo.

## 1. Stack

- **Angular 18+** (standalone, control flow novo, Signals), **Nx 19+** workspace (`@journeyos`).
- **TypeScript strict**.
- **RxJS 7.8** (interop pontual — HTTP/streams) **+ Signals** (estado de UI). Sem NgRx.
- **Jest** (unit) · **Playwright** (e2e em `apps/wrks-e2e`).
- **SCSS** isolado em `libs/wrks/styles` consumindo `@journeyos/shared/ui-tokens`.

## 2. App Boundary

`apps/wrks/` é o entry lazy do módulo. `wrks.module.ts` é o **único** `NgModule`; é carregado
pelo Shell via `loadChildren`. Todas as features e componentes abaixo são `standalone` + `OnPush`.

## 3. Library Organization (tags Nx — padrão module-pattern)

| Lib | `type:*` | `scope:*` | Papel |
|---|---|---|---|
| `apps/wrks` | `type:app` | `scope:wrks` | entry lazy |
| `libs/wrks/feature-login` | `type:feature` | `scope:wrks` | login + OIDC callback |
| `libs/wrks/feature-empresa-select` | `type:feature` | `scope:wrks` | seleção de empresa |
| `libs/wrks/feature-workspace` | `type:feature` | `scope:wrks` | dashboard + settings + org structure |
| `libs/wrks/feature-users` | `type:feature` | `scope:wrks` | gestão de usuários/papéis |
| `libs/wrks/feature-rbac-viewer` | `type:feature` | `scope:wrks` | papéis × permissões (leitura) |
| `libs/wrks/data-access` | `type:data-access` | `scope:wrks` | `*ApiService` + facades de signal |
| `libs/wrks/access` | `type:domain` | `scope:wrks` | guards específicos do módulo |
| `libs/wrks/integration` | `type:domain` | `scope:wrks` | `WrksShellIntegrationService` |
| `libs/wrks/navigation` | `type:domain` | `scope:wrks` | breadcrumb/menu state |
| `libs/wrks/ui` | `type:ui` | `scope:wrks` | componentes locais (opcional) |
| `libs/wrks/styles` | `type:ui` | `scope:wrks` | SCSS isolado |

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>`.

## 4. Shared Library Dependencies (`@journeyos/*` consumidas)

| Lib | Obrigatória? | Uso no WRKS |
|---|---|---|
| `@journeyos/shared/access-http-base` | ✅ | HttpClient + interceptors (`X-Empresa-Id`, Correlation, ErrorNormalize). `forRoot({})` no Shell. |
| `@journeyos/shared/auth-session` | ✅ | Sessão, claims, login/logout OIDC, refresh. |
| `@journeyos/shared/empresa-context` | ✅ | Empresa ativa (WRKS alimenta a lista e consome o sinal). |
| `@journeyos/shared/access-decision` | ✅ | `AccessDecisionService.can()`, `NavigationService`. |
| `@journeyos/shared/ui-tokens` · `ui-components` · `ui-feedback` | ✅ | Design tokens, primitivos, estados empty/loading/error. |
| `@journeyos/shared/error-model` | ✅ | `ProblemDetail → AppError`. |
| `@journeyos/shared/observability` | ◻ recomendado | Timing de bootstrap, troca de empresa, convites. |

WRKS **não** consome `@journeyos/shared/contracts` de outro módulo, nem patterns 3rd-party no MVP.

## 5. Routing Strategy

- Shell → `wrks.module.ts` via `loadChildren`.
- Sub-rotas via `loadComponent` (cada feature é standalone).
- **Rotas pré-contexto** (`/login`, `/auth/callback`, `/empresa-select`): `canActivate: [authGuard]`
  apenas (não exigem empresa ativa).
- **Rotas pós-contexto** (`/workspace`, `/users`, `/rbac`): `canActivate: [authGuard, empresaGuard,
  accessGuard(<perm>)]`.

```
/login                 → feature-login            [—]
/auth/callback         → feature-login (callback) [authGuard]
/empresa-select        → feature-empresa-select   [authGuard]
/wrks/workspace        → feature-workspace        [authGuard, empresaGuard, accessGuard('wrks.workspace.ver')]
/wrks/users            → feature-users            [authGuard, empresaGuard, accessGuard('wrks.user.ver')]
/wrks/rbac             → feature-rbac-viewer      [authGuard, empresaGuard, accessGuard('wrks.rbac.ver')]
```

## 6. State Strategy

- **Signals locais** nas facades de `data-access`: `signal<T>` privado + `.asReadonly()` público.
- **Sem NgRx / BehaviorSubject manual** (ADR-002).
- Estado global de sessão/empresa/RBAC **não** vive no WRKS — vive na Access Layer
  (`@journeyos/shared/access-*`); o WRKS apenas o consome/alimenta.
- `computed()` para derivações (ex.: lista de empresas filtrada por busca; visibilidade de ações).

## 7. Module Contract Strategy (`wrks.contract.ts`)

```ts
// ModuleMenuMetadata
{
  key: 'wrks',
  label: 'Workspace',
  route: '/wrks/workspace',
  icon: 'business',
  deepLinks: [
    { key: 'users', label: 'Usuários', route: '/wrks/users', perm: 'wrks.user.ver' },
    { key: 'rbac',  label: 'Papéis',   route: '/wrks/rbac',  perm: 'wrks.rbac.ver' },
  ],
}
```

- `ModulePermissionMap` — `wrks.permission-map.ts`: mapeia rota/ação → permissão canônica
  (`wrks.workspace.ver`, `wrks.user.convidar`, `wrks.user.papel.alterar`, `wrks.rbac.ver`, …).
- `ModuleFeatureFlags` — `wrks.feature-flags.ts`: ex.: `wrks.rbac-viewer` (`defaultState: on`),
  `wrks.org-structure` (`defaultState: on`). Cada flag com `defaultState` explícito.

---

## Referências

- `02-architecture-blueprint.md` (fronteiras internas)
- `05-state-and-data-flow.md` (data flow detalhado)
- `docs/architecture/frontend/standards/nx-boundaries.md`
- ADR-001 (module-pattern), ADR-002 (signals), ADR-003 (lazy module), ADR-004 (shell integration)
