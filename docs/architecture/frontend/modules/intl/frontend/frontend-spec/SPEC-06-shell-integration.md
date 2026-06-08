# SPEC-06 — Shell Integration — INTL

> Como o módulo INTL se registra no Shell (`journey-os-web`) e participa do ciclo de vida.
> Espelha o padrão de WRKS (ADR-004 + ADR-006).

## 1. `module-descriptors.ts` (fallback estático do Shell)

O entry-lib `@journeyos/intl` exporta `INTL_MODULE_DESCRIPTOR`; o Shell o registra:

```typescript
// apps/journey-os-web/src/app/config/module-descriptors.ts
import { INTL_MODULE_DESCRIPTOR } from '@journeyos/intl';

export const MODULE_DESCRIPTORS = [
  WRKS_MODULE_DESCRIPTOR,
  INTL_MODULE_DESCRIPTOR,   // ← adicionado por INTL (P1 do implement / shell-registration)
  // ...
];
```

`INTL_MODULE_DESCRIPTOR` (gerado pelo scaffold):
```typescript
{
  key: 'intl',
  basePath: 'intl',
  loadChildren: () => import('./intl.module').then((m) => m.IntlModule),
  metadata: MODULE_MENU_METADATA,
  flags: INTL_FEATURE_FLAGS,
  permissionMap: INTL_PERMISSION_MAP,
}
```

## 2. `IntlShellIntegrationService` (`libs/intl/integration/`)

API pública + lifecycle:

| Método | Responsabilidade |
|---|---|
| `onRegister()` | registra `MODULE_MENU_METADATA` no `NavigationService` (deep-links filtrados por permissão). |
| `onActivate()` | assina `EmpresaContextService` (empresa ativa) — gatilho de reset de facades. |
| `onDeactivate()` | cancela assinaturas; reseta facades escopadas (conversa/listas/dashboards). |

## 3. `intl.bootstrap.ts`

- `intlModuleInit()` — registra o descriptor/menu no Shell; assina `empresa-context` e
  `modelo.acesso.alterado` (invalida cache de permissão); **não** dispara chamadas de dados (lazy
  por rota).
- `intlModuleDestroy()` — cancela perguntas in-flight (`AbortController`), limpa a conversa corrente
  e reseta as facades.

## 4. Navegação derivada de RBAC

`NavigationService` exibe apenas os deep-links cujo `permission` o `AccessDecisionService` permite —
um `SDR` sem `intl.knowledge.write` ainda vê Conhecimento (read), mas sem ação de criar; sem
`intl.analytics.read`, o item Analítica **não aparece**.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL export INTL_MODULE_DESCRIPTOR from the @journeyos/intl entry-lib with key intl, lazy loadChildren and the menu metadata.`
- `WHEN the Shell boots, THE SYSTEM SHALL register INTL via the descriptor so its menu entry appears without runtime registration.`
- `WHEN the INTL module activates, THE SYSTEM SHALL subscribe to EmpresaContextService as the facade reset trigger.`
- `WHEN the INTL module deactivates, THE SYSTEM SHALL cancel in-flight questions and reset the scoped facades.`
- `WHEN modelo.acesso.alterado is received, THE SYSTEM SHALL invalidate the permission cache.`

## Referências

- WRKS SPEC-06 (espelho) · ADR-004 · ADR-006 global
- `docs/architecture/frontend/standards/bootstrap-flow.md`
- `apps/journey-os-web/src/app/config/module-descriptors.ts`
