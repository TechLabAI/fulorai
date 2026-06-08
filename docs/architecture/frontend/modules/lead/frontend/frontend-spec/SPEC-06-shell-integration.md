# SPEC-06 — Shell Integration — LEAD · Frontend

> Como o LEAD se registra no Shell `journey-os-web`: descriptor estático (fallback) + integration
> service (runtime) + bootstrap. Alinhado a ADR-004/ADR-006.

## `module-descriptors.ts` (fallback Shell)

Entrada registrada em `apps/journey-os-web/src/app/config/module-descriptors.ts`:

```typescript
import { LEAD_MODULE_DESCRIPTOR } from '@journeyos/lead';
// ...
export const MODULE_DESCRIPTORS = [
  WRKS_MODULE_DESCRIPTOR,
  LEAD_MODULE_DESCRIPTOR,   // ← registrado no implement P1 (FE-LEAD-003)
  // ...
];
```

`LEAD_MODULE_DESCRIPTOR` (de `libs/lead/shell-entry/lead.descriptor.ts`):

```typescript
export const LEAD_MODULE_DESCRIPTOR: ModuleDescriptor = {
  key: 'lead',
  loadChildren: () => import('@journeyos/lead').then(m => m.LEAD_ROUTES),
  metadata: MODULE_MENU_METADATA,
  permissions: MODULE_PERMISSION_MAP,
  flags: MODULE_FEATURE_FLAGS,
};
```

## `LeadShellIntegrationService` (`libs/lead/integration/`)

API pública + lifecycle:

```typescript
@Injectable({ providedIn: 'root' })
export class LeadShellIntegrationService {
  onRegister(): void;     // registra metadata/permissões/flags no Shell registry
  onActivate(): void;     // ao entrar no módulo: inicializa navigation/breadcrumbs
  onDeactivate(): void;   // ao sair: limpa breadcrumbs/estado de navegação
}
```

## `lead.bootstrap.ts`

- **init:** registra o módulo via `LeadShellIntegrationService.onRegister()`; subscreve troca de empresa
  (`EmpresaContextService`) para invalidar a fila; opcional: `ObservabilityService` (timing).
- **destroy:** `onDeactivate()`; encerra subscriptions/effects.

## Registro efetivo

O registro real do `LEAD_MODULE_DESCRIPTOR` em `journey-os-web` é tarefa do **implement P1**
(issue `FE-LEAD-003`), como nos módulos WRKS/ASST/INTL — o scaffold gera o descriptor mas **não** muta
o Shell.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL export LEAD_MODULE_DESCRIPTOR from @journeyos/lead for static Shell registration.`
- `WHEN the LEAD module is activated, THE SYSTEM SHALL initialise its breadcrumb/navigation state via the integration service.`
- `WHEN the LEAD module is deactivated, THE SYSTEM SHALL clear its navigation state so no stale breadcrumb persists.`
- `IF the Shell registry already holds a descriptor with key lead, THEN THE SYSTEM SHALL replace it rather than register a duplicate.`

## Referências
- ADR-004 (shell integration) · ADR-003/006 (entry as library) · `SPEC-05-module-contract.md`
- `docs/architecture/frontend/standards/access-layer-contracts.md`
