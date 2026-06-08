# SPEC-06 — Shell Integration — ASST · Frontend

> Como o Shell (`journey-os-web`) descobre e carrega o ASST: descriptor estático + integration service
> + bootstrap. Espelha o mecanismo consolidado no WRKS (ADR-004/ADR-006).

## 1. `ASST_MODULE_DESCRIPTOR` (gerado em `libs/asst/shell-entry`)

```typescript
export const ASST_MODULE_DESCRIPTOR = {
  key: 'asst',
  basePath: 'asst',
  loadChildren: () => import('./asst.module').then((m) => m.AsstModule),
  metadata: MODULE_MENU_METADATA,      // label 'Assets', route /asst/library, deepLink Aprovações
  flags: ASST_FEATURE_FLAGS,
  permissionMap: ASST_PERMISSION_MAP,
};
```

Exportado pelo barrel `@journeyos/asst` (`libs/asst/shell-entry/src/index.ts`).

## 2. Registro no Shell — `apps/journey-os-web/src/app/config/module-descriptors.ts`

O Shell importa o descriptor de `@journeyos/asst` e o adiciona ao registry (fallback estático),
ao lado de `WRKS_MODULE_DESCRIPTOR`:

```typescript
import { ASST_MODULE_DESCRIPTOR } from '@journeyos/asst';
// ...
export const MODULE_DESCRIPTORS = [
  WRKS_MODULE_DESCRIPTOR,
  ASST_MODULE_DESCRIPTOR,   // ← adicionado
];
```

> Esse registro é uma mutação **mínima** do Shell (uma import + uma entrada no array). O ASST não é
> precondição de bootstrap (diferente do WRKS/Access Layer), então pode ser registrado após o WRKS.
> `nx build journey-os-web` + `nx lint journey-os-web` devem permanecer verdes após o registro.

## 3. `AsstShellIntegrationService` (`libs/asst/integration`)

```typescript
@Injectable({ providedIn: 'root' })
export class AsstShellIntegrationService {
  onRegister(): void   { /* publica MODULE_MENU_METADATA no Shell (NavigationService) */ }
  onActivate(): void   { /* ao entrar no /asst: assina empresa-context + modelo_acesso_versao */ }
  onDeactivate(): void { /* ao sair: cancela assinaturas, reset de facades escopadas */ }
}
```

- Consome `@journeyos/shared/access-decision` (`NavigationService`) para derivar o menu/deep links
  conforme permissões (o deep link "Aprovações" só aparece com `asst.asset.aprovar`).
- O registro em runtime (TCE/Shell) substitui o fallback estático em produção, se aplicável.

## 4. `asst.bootstrap.ts` (init/destroy)

```typescript
export function asstModuleInit(): void {
  // registra MODULE_MENU_METADATA no Shell; assina empresa-context (invalidar catálogo na troca)
  // e modelo_acesso_versao (re-derivar ações/menu ao mudar RBAC)
}
export function asstModuleDestroy(): void {
  // cancela assinaturas; reset das facades (catálogo/detalhe/studio/fila) escopadas por empresa
}
```

- **Troca de empresa:** o bootstrap garante que `EmpresaContextService.switchTo` dispara invalidação
  do catálogo/detalhe antes de renderizar (UINV-8 / ADR-005 multi-empresa).

## Critérios de aceite (EARS)

> Notação EARS (D-057 / `be-validate-ears.py`). Backfill do gate A2.5. Derivados do descriptor/registro,
> da invalidação na troca de empresa (UINV-8 / ADR-005) e da re-derivação do menu por RBAC.

- **A-06.1** `WHEN the Shell registers the ASST module, THE SYSTEM SHALL publish the module menu metadata through the NavigationService.`
- **A-06.2** `WHEN the user switches empresa, THE SYSTEM SHALL invalidate the ASST catalog and detail before rendering the new empresa data.`
- **A-06.3** `WHEN the access model version changes, THE SYSTEM SHALL re-derive the module menu and the available asset actions.`

## Referências
- WRKS: SPEC-06 + registro `WRKS_MODULE_DESCRIPTOR` (master plan Wave 0)
- `02-architecture-blueprint.md` §5 · ADR-004 (shell integration) · ADR-006 global (entry como lib)
- `docs/architecture/frontend/standards/access-layer-contracts.md`
