# SPEC-06 — Shell Integration — WRKS

> Como o WRKS se registra no Shell (`journey-os-web`). Duas camadas: descriptor estático (fallback)
> + serviço de integração em runtime (ADR-004).

## module-descriptors.ts (fallback estático no Shell)

Entrada nova adicionada pelo scaffold:

```typescript
{
  key: 'wrks',
  loadChildren: () => import('@journeyos/wrks').then(m => m.WrksModule),
  metadata: MODULE_MENU_METADATA,        // de wrks.contract.ts
  flags: MODULE_FEATURE_FLAGS,
  // WRKS é fundação: o Shell o trata como rota de boot (login/empresa-select vivem aqui).
}
```

## WrksShellIntegrationService (`libs/wrks/integration`)

API pública + lifecycle:

```typescript
@Injectable({ providedIn: 'root' })
class WrksShellIntegrationService implements ModuleShellIntegration {
  onRegister(): void   { /* registra MODULE_MENU_METADATA + permission map no registry do Shell */ }
  onActivate(): void   { /* module entrou em foco: nada pesado (WRKS é leve) */ }
  onDeactivate(): void { /* limpa breadcrumbs próprios; mantém sessão/empresa (são globais) */ }
}
```

## wrks.bootstrap.ts (init/destroy)

- **init:** registra a module (`onRegister`), assina mudanças de `EmpresaContextService` para resetar
  breadcrumbs/menu do módulo na troca de empresa, e mudanças de `modelo_acesso_versao` para re-derivar
  navegação (`NavigationService`).
- **destroy:** cancela assinaturas; chama facades `reset()` para descartar estado escopado.

## Particularidade WRKS (fundação)

- WRKS hospeda as rotas **pré-contexto** (`/login`, `/auth/callback`, `/empresa-select`) que o Shell
  usa **antes** de qualquer empresa estar ativa. O Shell deve direcionar para elas no boot quando não
  há sessão/empresa — diferente das demais módulos, que só ativam pós-contexto.
- A troca de empresa (topbar do Shell) chama `EmpresaContextService.switchTo`, que por sua vez usa o
  `auth-session` (endpoint `/sessao/trocar-empresa`). O `WrksShellIntegrationService` só reage ao
  sinal de empresa ativa; não é dono do estado global.

## Critérios de aceite (EARS)

- `WHEN the WRKS module registers, THE SYSTEM SHALL publish MODULE_MENU_METADATA and the permission map to the Shell registry.`
- `IF there is no active session or empresa at boot, THEN THE SYSTEM SHALL route the user to the WRKS pre-context routes (/login or /empresa-select).`
- `WHEN the active empresa changes, THE SYSTEM SHALL reset WRKS breadcrumbs and re-derive the navigation via NavigationService.`
- `WHEN modelo_acesso_versao changes, THE SYSTEM SHALL re-derive navigation and access decisions for WRKS.`
- `WHEN the WRKS module is deactivated, THE SYSTEM SHALL clear its own breadcrumbs and preserve the global session and empresa context.`
