# SPEC-06 — Shell Integration — SALE · Frontend

> Como o Shell `journey-os-web` descobre e registra o SALE. Duas vias: descriptor estático (fallback)
> + `SaleShellIntegrationService` (runtime). Espelha `ADR-004`.

## 1. `module-descriptors.ts` (fallback Shell)

Entrada registrada em `apps/journey-os-web/src/app/config/module-descriptors.ts`:

```typescript
import { SALE_MODULE_DESCRIPTOR } from '@journeyos/sale';
// ...
export const MODULE_DESCRIPTORS: ModuleDescriptor[] = [
  WRKS_MODULE_DESCRIPTOR,
  // ...
  SALE_MODULE_DESCRIPTOR,
];
```

`SALE_MODULE_DESCRIPTOR` (de `libs/sale/shell-entry/sale.descriptor.ts`):

```typescript
export const SALE_MODULE_DESCRIPTOR: ModuleDescriptor = {
  key: 'sale',
  metadata: MODULE_MENU_METADATA,                 // de sale.contract.ts
  loadChildren: () => import('@journeyos/sale').then(m => m.SALE_ROUTES),
  permissions: Object.keys(MODULE_PERMISSION_MAP),
  flags: MODULE_FEATURE_FLAGS,
};
```

> O **registro efetivo no Shell** (adicionar `SALE_MODULE_DESCRIPTOR` à lista) é tarefa do
> **implement P1** (`FE-SALE-003`), como nos módulos anteriores (WRKS/ASST/INTL/LEAD/COMM/JRNY).

## 2. `SaleShellIntegrationService` (`libs/sale/integration`)

```typescript
@Injectable({ providedIn: 'root' })
export class SaleShellIntegrationService {
  onRegister(): void;     // registra metadata/flags no ModuleRegistry do Shell
  onActivate(): void;     // ao entrar no módulo: publica breadcrumbs raiz, sincroniza menu
  onDeactivate(): void;   // ao sair: limpa breadcrumbs do módulo
}
```

Consome `NavigationService` + `AccessDecisionService` (filtra menu/ações por `sale.*`) e o
`ModuleEventsService` do Shell.

## 3. `sale.bootstrap.ts`

```typescript
export function saleBootstrap(): void {
  // init: subscribe ModuleEventsService (troca de empresa -> invalidar pipeline/listas do módulo);
  //       registra SaleShellIntegrationService.onRegister()
  // destroy: onDeactivate() + unsubscribe
}
```

`init` reage à **troca de empresa** (efeito da Access Layer) invalidando pipeline/compras/ofertas;
`destroy` desfaz subscriptions.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose SALE_MODULE_DESCRIPTOR from @journeyos/sale with key 'sale', lazy loadChildren and the menu metadata.`
- `WHEN the Shell boots, THE SYSTEM SHALL register SALE via the descriptor (static fallback) so the menu entry appears without runtime registration.`
- `WHEN the SALE module is activated, THE SYSTEM SHALL publish its root breadcrumb and synchronize the permission-filtered menu.`
- `WHEN the active empresa changes, THE SYSTEM SHALL invalidate SALE module state via the bootstrap subscription.`
- `THE SYSTEM SHALL filter every SALE menu/deep-link by permission through NavigationService + AccessDecisionService.`

## Referências
- `adr/ADR-004-shell-integration-via-module-registry.md` · `adr/ADR-003-lazy-module-entry.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md` · `SPEC-05-module-contract.md`
