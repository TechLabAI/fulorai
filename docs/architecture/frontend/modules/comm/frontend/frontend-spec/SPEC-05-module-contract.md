# SPEC-05 — Module Contract — COMM · Frontend

> Conteúdo de `libs/comm/shell-entry/src/lib/comm.contract.ts` (+ permission-map + feature-flags).
> Gerado pelo `@journeyos/internal:module` a partir do `generator-config.yml` (ADR-006).

## comm.contract.ts

```typescript
export const MODULE_KEY = 'comm' as const;

export const MODULE_MENU_METADATA: ModuleMenuMetadata = {
  key: MODULE_KEY,
  label: 'Comunicação',
  route: '/comm/templates',
  icon: 'forum',
  deepLinks: [
    { label: 'Templates',  route: '/comm/templates',      permission: 'comm.template.ler' },
    { label: 'Mensagens',  route: '/comm/messages',        permission: 'comm.mensagem.ler' },
    { label: 'Roteamento', route: '/comm/routing-rules',   permission: 'comm.roteamento.ler' },
    { label: 'Canais',     route: '/comm/channels',        permission: 'comm.canal.ler' },
  ],
};
```

## comm.permission-map.ts

Mapeia rota/ação → permissão canônica. Justificativa de cada permissão:

| Permissão | Justificativa | Usada em |
|---|---|---|
| `comm.template.ler` | Ver catálogo e editor de templates | `/comm/templates`, `/comm/templates/:id` |
| `comm.template.criar` | Criar novo template (RASCUNHO) | ação `NewTemplateDialog` |
| `comm.template.editar` | Editar corpo/metadados (bump versão) | ação no editor |
| `comm.template.publicar` | Ativar template (`RASCUNHO→ATIVO`) | ação `Ativar` |
| `comm.template.arquivar` | Arquivar template | ação `Arquivar` |
| `comm.studio.compor` | Compor copy via Template Studio (IA) | `/comm/templates/:id/studio` |
| `comm.mensagem.enviar` | Disparar mensagem 1:1 | `DispatchDialog` |
| `comm.mensagem.ler` | Ver lista/detalhe/timeline de mensagens | `/comm/messages`, `/comm/messages/:id` |
| `comm.roteamento.criar` | Criar regra de roteamento | ação `RoutingRuleDialog` |
| `comm.roteamento.editar` | Editar regra de roteamento | ação no diálogo |
| `comm.roteamento.ler` | Ver regras de roteamento | `/comm/routing-rules` |
| `comm.canal.configurar` | Criar/editar config de canal | `ChannelConfigDialog` |
| `comm.canal.ler` | Ver canais configurados | `/comm/channels` |

> As permissões espelham 1:1 as do `comm-service/contracts/api-contract.md` (`comm.<recurso>.<acao>`),
> garantindo paridade FE↔BE. O mapa de papéis→permissão é resolvido pelo WRKS (RBAC), não hardcoded no FE.

## comm.feature-flags.ts

| Flag | defaultState | Justificativa |
|---|---|---|
| `comm.template-studio` | `enabled` | Permite desligar o Template Studio (IA) sem afetar CRUD/roteamento/disparo — alinhado à degradação graciosa (princípio 4 do `01`). |
| `comm.delivery-tracking` | `enabled` | Habilita o polling de rastreio (ADR-005); off → detalhe da mensagem usa refresh manual (degradação controlada, sem afetar disparo). |

## Critérios de aceite (EARS)

- **C-05.1 (Ubiquitous):** `THE SYSTEM SHALL expor MODULE_MENU_METADATA e COMM_PERMISSION_MAP e COMM_FEATURE_FLAGS a partir do shell-entry @journeyos/comm`
- **C-05.2 (Ubiquitous):** `THE SYSTEM SHALL usar exatamente as permissões comm definidas no api-contract do comm-service garantindo paridade entre FE e BE`
- **C-05.3 (State-driven):** `WHILE a flag comm.template-studio estiver desabilitada, THE SYSTEM SHALL ocultar o acesso ao Template Studio sem afetar as demais features`
- **C-05.4 (State-driven):** `WHILE a flag comm.delivery-tracking estiver desabilitada, THE SYSTEM SHALL substituir o polling por refresh manual no detalhe da mensagem`
- **C-05.5 (Event-driven):** `WHEN o NavigationService monta o menu, THE SYSTEM SHALL incluir apenas deep links cuja permissão o usuário possui`

## Referências

- `04-frontend-architecture-direction.md` §7 · SPEC-06 (shell integration) · ADR-004
- BE: `comm-service/contracts/api-contract.md` (permissões `comm.*`)
