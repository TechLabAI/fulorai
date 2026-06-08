# SPEC-06 — Shell Integration — JRNY · Frontend

> Como o Shell `journey-os-web` descobre e registra o JRNY. Duas vias: descriptor estático (fallback)
> + `JrnyShellIntegrationService` (runtime). Espelha `ADR-004`.

## 1. `module-descriptors.ts` (fallback Shell)

Entrada registrada em `apps/journey-os-web/src/app/config/module-descriptors.ts`:

```typescript
import { JRNY_MODULE_DESCRIPTOR } from '@journeyos/jrny';
// ...
export const MODULE_DESCRIPTORS: ModuleDescriptor[] = [
  WRKS_MODULE_DESCRIPTOR,
  // ...
  JRNY_MODULE_DESCRIPTOR,
];
```

`JRNY_MODULE_DESCRIPTOR` (de `libs/jrny/shell-entry/jrny.descriptor.ts`):

```typescript
export const JRNY_MODULE_DESCRIPTOR: ModuleDescriptor = {
  key: 'jrny',
  metadata: MODULE_MENU_METADATA,                 // de jrny.contract.ts
  loadChildren: () => import('@journeyos/jrny').then(m => m.JRNY_ROUTES),
  permissions: Object.keys(MODULE_PERMISSION_MAP),
  flags: MODULE_FEATURE_FLAGS,
};
```

> O **registro efetivo no Shell** (adicionar `JRNY_MODULE_DESCRIPTOR` à lista) é tarefa do
> **implement P1** (`FE-JRNY-003`), como nos módulos anteriores (WRKS/ASST/INTL/LEAD/COMM).

## 2. `JrnyShellIntegrationService` (`libs/jrny/integration`)

```typescript
@Injectable({ providedIn: 'root' })
export class JrnyShellIntegrationService {
  onRegister(): void;     // registra metadata/flags no ModuleRegistry do Shell
  onActivate(): void;     // ao entrar no módulo: publica breadcrumbs raiz, sincroniza menu
  onDeactivate(): void;   // ao sair: limpa breadcrumbs do módulo
}
```

Consome `NavigationService` + `AccessDecisionService` (filtra menu/ações por `jrny.*`) e o
`ModuleEventsService` do Shell.

## 3. `jrny.bootstrap.ts`

```typescript
export function jrnyBootstrap(): void {
  // init: subscribe ModuleEventsService (troca de empresa -> invalidar estado do módulo);
  //       registra JrnyShellIntegrationService.onRegister()
  // destroy: onDeactivate() + unsubscribe
}
```

`init` reage à **troca de empresa** (efeito da Access Layer) invalidando lista/builder; `destroy`
desfaz subscriptions.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL expose JRNY_MODULE_DESCRIPTOR from @journeyos/jrny with key 'jrny', lazy loadChildren and the menu metadata.`
- `WHEN the Shell boots, THE SYSTEM SHALL register JRNY via the descriptor (static fallback) so the menu entry appears without runtime registration.`
- `WHEN the JRNY module is activated, THE SYSTEM SHALL publish its root breadcrumb and synchronize the permission-filtered menu.`
- `WHEN the active empresa changes, THE SYSTEM SHALL invalidate JRNY module state via the bootstrap subscription.`
- `THE SYSTEM SHALL filter every JRNY menu/deep-link by permission through NavigationService + AccessDecisionService.`

## Referências
- `adr/ADR-004-shell-integration-via-module-registry.md` · `adr/ADR-003-lazy-module-entry.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md` · `SPEC-05-module-contract.md`
