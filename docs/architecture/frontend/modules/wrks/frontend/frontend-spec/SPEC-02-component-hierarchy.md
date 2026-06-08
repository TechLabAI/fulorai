# SPEC-02 — Component Hierarchy — WRKS

> Árvore de componentes por feature lib. Smart = consome facades (signals); Presentational =
> recebe `input()` e emite `output()`. Todos `standalone` + `OnPush`. Pages terminam em `PageComponent`.

## feature-login

```
LoginPageComponent (smart, route /login)
├── reads: authSession.status()                       (@journeyos/shared/auth-session)
└── LoginCardComponent (presentational)               # botão "Entrar com Journey OS" → output login()

OidcCallbackPageComponent (smart, route /auth/callback)
├── reads: authSession.status(), authSession.error()
└── AuthProgressComponent (presentational)            # estado redirecting/exchanging/error
```

## feature-empresa-select

```
EmpresaSelectPageComponent (smart, route /empresa-select)
├── reads: empresaListFacade.empresas(), .loading(), .error()
├── EmpresaListComponent (presentational)             # grid de empresas
│   └── EmpresaCardComponent (presentational)         # nome + papel; output select(empresaId)
└── EmptyStateComponent (@journeyos/shared/ui-feedback) # N=0 "sem acesso"
```

## feature-workspace

```
WorkspaceDashboardPageComponent (smart, route /wrks/workspace)
├── reads: workspaceFacade.workspace(), .loading(), .error()
├── WorkspaceSummaryComponent (presentational)        # nome, slug, contagens
└── QuickActionsComponent (presentational)            # atalhos visíveis conforme can(<perm>)

WorkspaceSettingsPageComponent (smart, route /wrks/workspace/settings)
├── reads: workspaceFacade.workspace(), orgFacade.businessUnits(), .saving()
├── WorkspaceFormComponent (presentational)           # form parâmetros; output save(form)
└── OrgStructureTreeComponent (presentational)         # business units / teams
    └── BusinessUnitNodeComponent (presentational)
        └── TeamNodeComponent (presentational)
```

## feature-users

```
UsersListPageComponent (smart, route /wrks/users)
├── reads: usersFacade.users(), .loading(), .error(), .filter()
├── UsersToolbarComponent (presentational)            # busca + [Convidar] (visível se can('wrks.usuario.criar'))
├── UsersTableComponent (presentational)              # output rowClick(id), toggle(id)
│   └── UserRowComponent (presentational)
└── InviteUserDrawerComponent (smart, abre em [Convidar])
    └── InviteUserFormComponent (presentational)       # email + papel + data_scope; output submit(form)

UserDetailPageComponent (smart, route /wrks/users/:id)
├── reads: userDetailFacade.user(), .loading(), .error()
└── UserRoleEditorComponent (presentational)           # papel + data_scope (papel ≤ papel do caller)
```

## feature-rbac-viewer

```
RbacViewerPageComponent (smart, route /wrks/rbac)
├── reads: rbacFacade.roles(), .loading(), .error()
├── RoleListComponent (presentational)                 # INFOPRODUTOR / HEAD_GROWTH / SDR
└── RolePermissionsComponent (presentational)          # bundle de permissões do papel selecionado (read-only)
```

## Regras

- Smart components declaram explicitamente os signals que leem (acima em `reads:`).
- Presentational nunca injetam facade nem `HttpClient`; só `input()`/`output()`.
- Estados empty/loading/error sempre via `@journeyos/shared/ui-feedback`.
- Nenhuma feature importa outra feature da mesma scope — composição é feita pela page.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL implement every WRKS component as standalone with OnPush change detection.`
- `THE SYSTEM SHALL restrict presentational components to input()/output() and keep facade and HttpClient injection out of them.`
- `THE SYSTEM SHALL render loading, empty and error states through @journeyos/shared/ui-feedback.`
- `WHEN the empresa-select list resolves to zero empresas, THE SYSTEM SHALL render the "sem acesso" empty state.`
- `WHERE the user holds wrks.usuario.criar, THE SYSTEM SHALL show the "Convidar" action in the users toolbar.`
- `THE SYSTEM SHALL compose features only through the page component and keep cross-feature imports within the same scope absent.`
