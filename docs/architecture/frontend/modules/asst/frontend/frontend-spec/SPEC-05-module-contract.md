# SPEC-05 — Module Contract — ASST · Frontend

> Conteúdo do `libs/asst/shell-entry/src/lib/asst.contract.ts` (+ permission-map + feature-flags).
> Entry como library (`@journeyos/asst`, ADR-003/ADR-006). Gerado pelo `@journeyos/internal:module` a
> partir do `module_contract` do `generator-config.yml`.

## `asst.contract.ts`

```typescript
export const MODULE_KEY = 'asst' as const;

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: 'Assets',
  route: '/asst/library',
  icon: 'folder_special',
  deepLinks: [
    { label: 'Aprovações', route: '/asst/approvals', permission: 'asst.asset.aprovar' },
  ],
};
```

> O entry default do generator usa `route: '/asst'` (redireciona para `/asst/library`). O deep link
> "Catálogo" é a rota raiz; "Asset Studio" não é deep link de menu (é contextual ao asset). "Aprovações"
> é deep link gated por `asst.asset.aprovar`.

## `asst.permission-map.ts`

```typescript
export const ASST_PERMISSION_MAP: ModulePermissionMap = {
  'asst.asset.ler':       [],   // preenchido por papel no /fe-implement (vem do AccessDecision BE)
  'asst.asset.criar':     [],
  'asst.asset.editar':    [],
  'asst.asset.submeter':  [],
  'asst.asset.aprovar':   [],
  'asst.asset.publicar':  [],
  'asst.asset.arquivar':  [],
  'asst.studio.compor':   [],
};
```

### Justificativa das permissões

| Permissão | Ação na UI | Persona típica |
|---|---|---|
| `asst.asset.ler` | Ver catálogo, detalhe, versões, versão publicada | Todas (Marina, Rafael, Lucas com `data_scope`) |
| `asst.asset.criar` | Criar asset (`RASCUNHO`) | `HEAD_GROWTH` |
| `asst.asset.editar` | Editar metadados + criar nova versão manual | `HEAD_GROWTH` |
| `asst.asset.submeter` | Submeter para aprovação (`RASCUNHO→EM_REVISAO`) | `HEAD_GROWTH` |
| `asst.asset.aprovar` | Aprovar/rejeitar; ver fila de aprovação | `INFOPRODUTOR` |
| `asst.asset.publicar` | Publicar (`APROVADO→PUBLICADO`) | `INFOPRODUTOR` |
| `asst.asset.arquivar` | Arquivar asset (soft-delete) | `INFOPRODUTOR`/`HEAD_GROWTH` |
| `asst.studio.compor` | Usar o Asset Studio (composição IA) | `HEAD_GROWTH` |

> Os arrays de papéis ficam **vazios** no contrato gerado; o enforcement real vem do `AccessDecision`
> do WRKS/BE (a UI consome, não decide — UINV-2). O map serve de documentação + fallback de menu.

## `asst.feature-flags.ts`

```typescript
export const ASST_FEATURE_FLAGS: ModuleFeatureFlags = {
  'asst.asset-studio':      { defaultState: 'enabled' },
  'asst.approval-workflow': { defaultState: 'enabled' },
};
```

### Justificativa das flags

| Flag | Default | Por quê |
|---|---|---|
| `asst.asset-studio` | `enabled` | Permite **desligar o Asset Studio** sem afetar CRUD/versão/aprovação — alinhado à degradação graciosa (ADR-005); útil se a TechLab AI estiver consistentemente fora ou em rollout gradual. |
| `asst.approval-workflow` | `enabled` | Permite operar o catálogo/versões antes de habilitar o fluxo de aprovação completo num tenant (rollout). |

## `asst.nav.config.ts`

```typescript
export const ASST_NAV_CONFIG = { key: 'asst', breadcrumbRoot: 'Assets' };
```

## Critérios de aceite (EARS)

> Notação EARS (D-057 / `be-validate-ears.py`). Backfill do gate A2.5. Derivados do deep link gated
> (`asst.asset.aprovar`), das feature flags e do invariante UINV-2 (UI consome, não decide RBAC).

- **A-05.1** `WHERE the user holds the asst.asset.aprovar permission, THE SYSTEM SHALL show the approvals deep link in the module menu.`
- **A-05.2** `IF the user lacks the asst.asset.aprovar permission, THEN THE SYSTEM SHALL hide the approvals deep link from the module menu.`
- **A-05.3** `WHILE the asst.asset-studio flag is disabled, THE SYSTEM SHALL keep asset CRUD, versioning and approval fully operational.`
- **A-05.4** `THE SYSTEM SHALL NOT decide RBAC locally and SHALL rely on AccessDecision for permission enforcement.`

## Referências
- `04-frontend-architecture-direction.md` §7 · SPEC-01 · SPEC-06
- Generator: `libs/internal-nx-plugin/internal/src/generators/module/generator.ts` (`writeModuleEntry`)
- BE: `asst-service/contracts/api-contract.md` (permissões `asst.*`)
