# SPEC-03 — View Models — WRKS

> VMs como tipos TypeScript (signal-based). `Signal<T>` de leitura expostos pela page a partir da
> facade. Eventos de UI = callbacks emitidos pela page. Refinam os rascunhos do doc 03.

## Tipos base

```typescript
type PapelCodigo = 'INFOPRODUTOR' | 'HEAD_GROWTH' | 'SDR';
type UserStatus  = 'ativo' | 'inativo' | 'convidado';
```

## feature-empresa-select

```typescript
type EmpresaOption = { empresaId: string; nome: string; papel: PapelCodigo; ativa: boolean };

type EmpresaSelectVM = {
  empresas: Signal<EmpresaOption[]>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos: onSelect(empresaId: string)
```

## feature-workspace

```typescript
type WorkspaceVM = {
  workspace: Signal<{
    empresaId: string; nome: string; slug: string;
    totalUsuarios: number; businessUnits: number;
    parametros: Record<string, unknown>;
    status: 'ATIVA' | 'PROVISIONANDO' | 'INATIVA';
  } | null>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};

type WorkspaceSettingsVM = {
  form: Signal<{ nome: string; parametros: Record<string, unknown> }>;
  businessUnits: Signal<BusinessUnitNode[]>;
  saving: Signal<boolean>;
  error: Signal<AppError | null>;
};
type BusinessUnitNode = { id: string; nome: string; teams: { id: string; nome: string; totalMembros: number }[] };
// eventos: onSave(form), onAddBusinessUnit(nome), onAddTeam(buId, nome)
```

## feature-users

```typescript
type UserRow = {
  usuarioId: string; nome: string; email: string;
  papel: PapelCodigo; dataScope: string; status: UserStatus;
};
type UsersFilter = { query: string; status: UserStatus | 'todos' };

type UsersListVM = {
  users: Signal<UserRow[]>;
  filter: Signal<UsersFilter>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  canInvite: Signal<boolean>;     // computed de AccessDecisionService.can('wrks.usuario.criar')
};
// eventos: onFilterChange(filter), onRowClick(id), onToggle(id), onInvite(form)

type InviteUserForm = { email: string; papel: PapelCodigo; dataScope: string };

type UserDetailVM = {
  user: Signal<UserRow | null>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  assignablePapeis: Signal<PapelCodigo[]>;  // ≤ papel do caller (UINV-4)
};
// eventos: onRoleChange(papel, dataScope)
```

## feature-rbac-viewer

```typescript
type RoleVM = { codigo: PapelCodigo; rotulo: string; permissoes: string[] };

type RbacViewerVM = {
  roles: Signal<RoleVM[]>;
  selected: Signal<PapelCodigo | null>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
};
// eventos: onSelectRole(codigo)
```

## Notas

- Todo `Signal<AppError | null>` vem de `@journeyos/shared/error-model` (mapeado do `ProblemDetail`).
- `canInvite` / `assignablePapeis` são `computed()` sobre `AccessDecisionService` — a UI nunca
  recalcula RBAC (UINV-2).
- Nenhum VM expõe `empresaId` editável: o contexto vem de `EmpresaContextService` (UINV-3).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose every view-model read as a readonly Signal derived from the feature facade.`
- `THE SYSTEM SHALL derive canInvite and assignablePapeis as computed values over AccessDecisionService and keep RBAC recomputation out of the UI.`
- `THE SYSTEM SHALL source the active empresa from EmpresaContextService and keep empresaId read-only in every view-model.`
- `WHILE the caller edits a user's role, THE SYSTEM SHALL limit the assignable papéis to roles at or below the caller's own role.`
- `THE SYSTEM SHALL map every error read to an AppError obtained from @journeyos/shared/error-model.`
