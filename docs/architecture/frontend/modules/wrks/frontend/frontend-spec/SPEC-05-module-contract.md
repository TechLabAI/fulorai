# SPEC-05 — Module Contract — WRKS

> Conteúdo de `apps/wrks/src/app/wrks-module/wrks.contract.ts`. Permissões alinhadas ao catálogo
> BE (`wrks.<recurso>.<acao>`). A visibilidade efetiva é sempre decidida pela Access Layer; o
> `MODULE_PERMISSION_MAP` apenas declara qual permissão cada capacidade exige.

```typescript
export const MODULE_KEY = 'wrks';

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: 'Workspace',
  route: '/wrks/workspace',
  icon: 'business',
  deepLinks: [
    { label: 'Usuários',      route: '/wrks/users',             permission: 'wrks.usuario.read' },
    { label: 'Papéis',        route: '/wrks/rbac',              permission: 'wrks.papel.read' },
    { label: 'Configurações', route: '/wrks/workspace/settings', permission: 'wrks.empresa.editar' },
  ],
};

export const MODULE_PERMISSION_MAP: ModulePermissionMap = {
  'wrks.empresa.read':    ['INFOPRODUTOR', 'HEAD_GROWTH'],
  'wrks.empresa.editar':  ['INFOPRODUTOR'],
  'wrks.usuario.read':    ['INFOPRODUTOR', 'HEAD_GROWTH'],
  'wrks.usuario.criar':   ['INFOPRODUTOR'],
  'wrks.usuario.editar':  ['INFOPRODUTOR'],
  'wrks.usuario.associar':['INFOPRODUTOR'],
  'wrks.papel.read':      ['INFOPRODUTOR', 'HEAD_GROWTH'],
};

export const MODULE_FEATURE_FLAGS: ModuleFeatureFlags = {
  'wrks.rbac-viewer':   { defaultState: 'enabled' },
  'wrks.org-structure': { defaultState: 'enabled' },
};
```

## Justificativa das permissões

| Permissão | Por quê |
|---|---|
| `wrks.empresa.read` | Ver o dashboard do workspace (admin + head). |
| `wrks.empresa.editar` | Editar parâmetros/org structure — só o CEO (`INFOPRODUTOR`) no MVP. |
| `wrks.usuario.read` | Listar usuários da empresa (admin + head). |
| `wrks.usuario.criar` / `editar` / `associar` | Convidar / editar / atribuir papel — admin. |
| `wrks.papel.read` | RBAC viewer (read-only) — admin + head. |

> O bundle real papel→permissão é **fonte de verdade do BE** (`shared/rbac/papeis.md`); este mapa é
> a declaração do módulo e deve ser consistente com o bundle BE. `SDR` não recebe nenhuma permissão
> `wrks.*` de administração no MVP (só login + troca de empresa).

## Justificativa das flags

| Flag | Por quê |
|---|---|
| `wrks.rbac-viewer` | Permite esconder a tela de papéis se um cliente não quiser expô-la. `enabled` por padrão. |
| `wrks.org-structure` | Business units/teams podem não ser usados por operações pequenas. `enabled` por padrão. |

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL declare each WRKS capability's required permission in MODULE_PERMISSION_MAP and delegate effective visibility to the Access Layer.`
- `WHERE the user lacks wrks.usuario.read, THE SYSTEM SHALL omit the "Usuários" deep link from the WRKS menu.`
- `WHERE the user lacks wrks.papel.read, THE SYSTEM SHALL omit the "Papéis" deep link from the WRKS menu.`
- `WHERE the feature flag wrks.rbac-viewer is disabled, THE SYSTEM SHALL hide the RBAC viewer menu entry and route.`
- `THE SYSTEM SHALL grant the SDR role no administrative wrks.* permission beyond login and empresa switching.`
