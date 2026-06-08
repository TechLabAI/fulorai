# SPEC-01 — Route Map — WRKS

> Todas as rotas que a module WRKS expõe, guards, títulos e breadcrumbs.
> Guards: `authGuard` + `empresaGuard` (`libs/wrks/access` / Access Layer) + `accessGuard(<perm>)`.
> Permissões alinhadas ao contrato BE (`wrks-service/contracts/api-contract.md`).

## Tabela mestre

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/login` | `LoginPageComponent` | `feature-login` | — | "Entrar" | [] |
| `/auth/callback` | `OidcCallbackPageComponent` | `feature-login` | `authGuard` | "Autenticando…" | [] |
| `/empresa-select` | `EmpresaSelectPageComponent` | `feature-empresa-select` | `authGuard` | "Selecionar empresa" | [] |
| `/wrks` | `WrksRootComponent` (redirect → `/wrks/workspace`) | `apps/wrks` | `authGuard, empresaGuard` | "Workspace" | [Workspace] |
| `/wrks/workspace` | `WorkspaceDashboardPageComponent` | `feature-workspace` | `authGuard, empresaGuard, accessGuard('wrks.empresa.read')` | "Workspace" | [Workspace] |
| `/wrks/workspace/settings` | `WorkspaceSettingsPageComponent` | `feature-workspace` | `authGuard, empresaGuard, accessGuard('wrks.empresa.editar')` | "Configurações" | [Workspace, Configurações] |
| `/wrks/users` | `UsersListPageComponent` | `feature-users` | `authGuard, empresaGuard, accessGuard('wrks.usuario.read')` | "Usuários" | [Workspace, Usuários] |
| `/wrks/users/:id` | `UserDetailPageComponent` | `feature-users` | `authGuard, empresaGuard, accessGuard('wrks.usuario.read')` | "Usuário" | [Workspace, Usuários, :nome] |
| `/wrks/rbac` | `RbacViewerPageComponent` | `feature-rbac-viewer` | `authGuard, empresaGuard, accessGuard('wrks.papel.read')` | "Papéis & Permissões" | [Workspace, Papéis] |

## Notas de guarda

- **Rotas pré-contexto** (`/login`, `/auth/callback`, `/empresa-select`) **não** exigem `empresaGuard`
  — acontecem antes de existir `empresaId` (UINV-1 admite essa exceção explícita).
- **Rotas pós-contexto** (`/wrks/**`) exigem `authGuard` + `empresaGuard` + `accessGuard(<perm>)`.
- `accessGuard(<perm>)` delega a `AccessDecisionService.can(<perm>)` (Access Layer) — nunca decide RBAC inline.
- Lazy: Shell → `wrks.module.ts` via `loadChildren`; cada page via `loadComponent`.
- `WrksRootComponent` apenas redireciona para a primeira rota permitida do usuário (derivada de `NavigationService`).

## Deep links (expostos no `wrks.contract.ts`)

- `/wrks/users` (perm `wrks.usuario.read`)
- `/wrks/rbac` (perm `wrks.papel.read`)
- `/wrks/workspace/settings` (perm `wrks.empresa.editar`)

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose every /wrks route as lazy-loaded via the @journeyos/wrks shell-entry.`
- `THE SYSTEM SHALL allow the pre-context routes /login, /auth/callback and /empresa-select without empresaGuard.`
- `WHEN the user navigates to /wrks, THE SYSTEM SHALL redirect to the first route permitted by the user's role.`
- `IF the user is not authenticated, THEN THE SYSTEM SHALL block every /wrks route via authGuard and redirect to /login preserving the requested deep link.`
- `IF the user has no active empresa context, THEN THE SYSTEM SHALL block every /wrks route via empresaGuard and redirect to /empresa-select.`
- `IF the user lacks the permission required by a WRKS route, THEN THE SYSTEM SHALL deny activation via accessGuard and keep the user on a route permitted by their role.`
- `WHERE a WRKS deep link's permission is not granted, THE SYSTEM SHALL hide that deep link from the navigation menu.`
- `WHEN an authenticated user with active session and empresa opens /wrks/users directly, THE SYSTEM SHALL load the users page.`
