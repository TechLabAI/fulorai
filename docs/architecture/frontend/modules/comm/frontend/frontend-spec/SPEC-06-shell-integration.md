# SPEC-06 — Shell Integration — COMM · Frontend

> Como o Shell (`journey-os-web`) descobre e carrega o COMM. Mecanismo igual ao WRKS (ADR-004):
> descriptor estático (fallback) + `CommShellIntegrationService` (runtime).

## module-descriptors.ts (fallback no Shell)

```typescript
// apps/journey-os-web/src/app/config/module-descriptors.ts
import { COMM_MODULE_DESCRIPTOR } from '@journeyos/comm';

export const MODULE_DESCRIPTORS = [
  WRKS_MODULE_DESCRIPTOR,
  // ...
  COMM_MODULE_DESCRIPTOR,   // registrado no implement P1 (FE-COMM-003), como nos demais módulos
];
```

`COMM_MODULE_DESCRIPTOR` (derivado de `comm.contract.ts`, emitido pelo generator):

```typescript
export const COMM_MODULE_DESCRIPTOR = {
  key: 'comm',
  basePath: 'comm',
  loadChildren: () => import('./comm.module').then((m) => m.CommModule),
  metadata: MODULE_MENU_METADATA,
  flags: COMM_FEATURE_FLAGS,
  permissionMap: COMM_PERMISSION_MAP,
};
```

## CommShellIntegrationService (`libs/comm/integration`)

API pública + lifecycle:

```typescript
@Injectable({ providedIn: 'root' })
export class CommShellIntegrationService {
  onRegister(): ModuleMenuMetadata;       // devolve metadata p/ o Shell montar navegação
  onActivate(empresaId: string): void;    // empresa ativa fixada; prepara facades escopadas
  onDeactivate(): void;                   // limpa estado escopado + encerra polling em curso
}
```

## comm.bootstrap.ts (init/destroy)

- **`commModuleInit()`** — registra `MODULE_MENU_METADATA` no Shell; assina `empresa-context`
  (troca de empresa → `onDeactivate()` + reload) e `modelo_acesso_versao` (invalida cache de
  `AccessDecision`).
- **`commModuleDestroy()`** — cancela assinaturas; reseta facades escopadas; **encerra qualquer
  polling de entrega ativo** (ADR-005 — sem timers órfãos).

## Critérios de aceite (EARS)

- **C-06.1 (Ubiquitous):** `THE SYSTEM SHALL registrar o COMM no Shell via COMM_MODULE_DESCRIPTOR estático e o CommShellIntegrationService em runtime sem o Shell importar código interno do COMM`
- **C-06.2 (Event-driven):** `WHEN o Shell ativa o COMM, THE SYSTEM SHALL carregar o módulo lazy via loadChildren de @journeyos/comm`
- **C-06.3 (Event-driven):** `WHEN a empresa ativa muda, THE SYSTEM SHALL chamar onDeactivate para limpar o estado e encerrar o polling antes de reativar com a nova empresa`
- **C-06.4 (Unwanted):** `IF o módulo é destruído com polling de entrega ativo, THEN THE SYSTEM SHALL encerrar os timers no commModuleDestroy sem deixar leaks`
- **C-06.5 (Ubiquitous):** `THE SYSTEM SHALL derivar o menu e os deep links das permissões via NavigationService e não de menu ad-hoc no COMM`

## Referências

- `04-frontend-architecture-direction.md` §7 · ADR-003 (lazy entry) · ADR-004 (registry) · ADR-005 (polling cleanup)
- WRKS shell-registration (master plan Wave 0)
