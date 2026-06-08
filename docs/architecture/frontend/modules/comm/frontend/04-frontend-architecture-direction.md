# 04 — Frontend Architecture Direction — COMM

> Direção técnica: stack, organização de libs (module-pattern + tags Nx), dependências `@journeyos/*`,
> routing, estado e contrato do módulo.

## 1. Stack

- **Angular 18+** (standalone, control flow novo, Signals), **Nx 19+** workspace (`@journeyos`).
- **TypeScript strict**.
- **RxJS 7.8** (interop pontual — HTTP, intervalos de polling) **+ Signals** (estado de UI). Sem NgRx.
- **Jest** (unit) · **Playwright** (e2e em `apps/comm-e2e`).
- **SCSS** isolado em `libs/comm/styles` consumindo `@journeyos/shared/ui-tokens`.

## 2. App Boundary

`apps/comm/` é o host fino lazy do módulo; o entry real é a library `libs/comm/shell-entry`
(importPath `@journeyos/comm`, ADR-006), carregada pelo Shell via `loadChildren`. Todas as features
e componentes são `standalone` + `OnPush`.

## 3. Library Organization (tags Nx — padrão module-pattern)

| Lib | `type:*` | `scope:*` | Papel |
|---|---|---|---|
| `apps/comm` | `type:app` | `scope:comm` | host fino lazy |
| `libs/comm/shell-entry` | `type:domain` | `scope:comm` | entry como library (`@journeyos/comm`): contract, routes, bootstrap, permission-map, flags, nav |
| `libs/comm/feature-template-catalog` | `type:feature` | `scope:comm` | catálogo/busca/filtros + CRUD + editor + estado (ativar/arquivar) |
| `libs/comm/feature-template-studio` | `type:feature` | `scope:comm` | composição assistida por IA (degradação graciosa) |
| `libs/comm/feature-routing-rules` | `type:feature` | `scope:comm` | CRUD de regras de roteamento (prioridade/condições/canais) |
| `libs/comm/feature-messages` | `type:feature` | `scope:comm` | disparo 1:1 + histórico/busca + timeline de entrega (polling) |
| `libs/comm/feature-channel-config` | `type:feature` | `scope:comm` | configuração de canais/provedores por empresa |
| `libs/comm/data-access` | `type:data-access` | `scope:comm` | `TemplateApiService`, `StudioApiService`, `MessageApiService`, `RoutingApiService`, `ChannelApiService` + facades de signal |
| `libs/comm/access` | `type:domain` | `scope:comm` | guards específicos do módulo |
| `libs/comm/integration` | `type:domain` | `scope:comm` | `CommShellIntegrationService` |
| `libs/comm/navigation` | `type:domain` | `scope:comm` | breadcrumb/menu state |
| `libs/comm/ui` | `type:ui` | `scope:comm` | template-card, state-chip, delivery-timeline, canal-badge (opcional) |
| `libs/comm/styles` | `type:ui` | `scope:comm` | SCSS isolado |

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>`
(COMM consome assets do ASST **só via API BE**, nunca `scope:asst`).

## 4. Shared Library Dependencies (`@journeyos/*` consumidas)

| Lib | Obrigatória? | Uso no COMM |
|---|---|---|
| `@journeyos/shared/access-http-base` | ✅ | HttpClient + interceptors (`X-Empresa-Id`, Correlation, ErrorNormalize). |
| `@journeyos/shared/auth-session` | ✅ | Sessão, claims, bearer token. |
| `@journeyos/shared/empresa-context` | ✅ | Empresa ativa (escopa todo dado). |
| `@journeyos/shared/access-decision` | ✅ | `AccessDecisionService.can('comm.*')`, `NavigationService`. |
| `@journeyos/shared/ui-tokens` · `ui-components` · `ui-feedback` | ✅ | Design tokens, primitivos, estados empty/loading/error. |
| `@journeyos/shared/error-model` | ✅ | `ProblemDetail → AppError` (`409`, `422`, `503`). |
| `@journeyos/shared/observability` | ◻ recomendado | Timing de composição, taxa de entrega/leitura, latência do catálogo, sessões de polling. |
| Patterns (`smart-table`, `timeline`, `wizard-form-shell`) | ◻ se disponíveis | Catálogo/histórico (smart-table), ciclo de vida da mensagem (timeline), config de canal (wizard). Caso não existam como shared, ficam em `libs/comm/ui` e podem ser promovidos depois (asset-driven-ui). |

COMM **não** consome `@journeyos/shared/contracts` de outro módulo de domínio, nem widgets
3rd-party no MVP.

## 5. Routing Strategy

- Shell → `@journeyos/comm` (shell-entry) via `loadChildren`.
- Sub-rotas via `loadComponent` (cada feature é standalone).
- Todas as rotas COMM são **pós-contexto** (exigem empresa ativa):
  `canActivate: [authGuard, empresaGuard, accessGuard(<perm>)]`.

```
/comm/templates                  → feature-template-catalog   [authGuard, empresaGuard, accessGuard('comm.template.ler')]
/comm/templates/:id              → feature-template-catalog    [authGuard, empresaGuard, accessGuard('comm.template.ler')]   # editor/detalhe
/comm/templates/:id/studio       → feature-template-studio     [authGuard, empresaGuard, accessGuard('comm.studio.compor')]
/comm/routing-rules              → feature-routing-rules       [authGuard, empresaGuard, accessGuard('comm.roteamento.ler')]
/comm/messages                   → feature-messages            [authGuard, empresaGuard, accessGuard('comm.mensagem.ler')]
/comm/messages/:id               → feature-messages            [authGuard, empresaGuard, accessGuard('comm.mensagem.ler')]   # detalhe + timeline
/comm/channels                   → feature-channel-config      [authGuard, empresaGuard, accessGuard('comm.canal.ler')]
```

> Criar/editar template, ativar/arquivar, criar regra, disparar mensagem e configurar canal são
> **ações** dentro das features (gated por `comm.template.criar|editar|publicar|arquivar`,
> `comm.roteamento.criar|editar`, `comm.mensagem.enviar`, `comm.canal.configurar`), não rotas próprias.

## 6. State Strategy

- **Signals locais** nas facades de `data-access`: `signal<T>` privado + `.asReadonly()` público
  (`catalogoTemplates`, `templateSelecionado`, `studioState`, `regras`, `mensagens`, `mensagemSelecionada`,
  `eventosEntrega`, `canais`, `loading`, `error`).
- **Sem NgRx / BehaviorSubject manual** (ADR-002).
- Estado transversal (sessão/empresa/RBAC) **não** vive no COMM — vive na Access Layer; o COMM consome.
- `computed()` para derivações: ações disponíveis por estado do template; visibilidade de botões por
  permissão; `estadoTerminal` da mensagem (controla o polling); contagem por estado de entrega.
- **Polling** (ADR-005): a facade de mensagens expõe um controle de polling (`startPolling(id)` /
  `stopPolling()`) baseado em `interval` RxJS com backoff, convertido em signal; para ao atingir
  estado terminal ou no `ngOnDestroy` da feature.

## 7. Module Contract Strategy (`comm.contract.ts`)

```ts
// ModuleMenuMetadata
{
  key: 'comm',
  label: 'Comunicação',
  route: '/comm/templates',
  icon: 'forum',
  deepLinks: [
    { key: 'messages',  label: 'Mensagens',  route: '/comm/messages',      perm: 'comm.mensagem.ler' },
    { key: 'routing',   label: 'Roteamento', route: '/comm/routing-rules', perm: 'comm.roteamento.ler' },
    { key: 'channels',  label: 'Canais',     route: '/comm/channels',      perm: 'comm.canal.ler' },
  ],
}
```

- `ModulePermissionMap` — `comm.permission-map.ts`: mapeia rota/ação → permissão canônica
  (`comm.template.ler|criar|editar|publicar|arquivar`, `comm.studio.compor`,
  `comm.mensagem.enviar|ler`, `comm.roteamento.criar|editar|ler`, `comm.canal.configurar|ler`).
- `ModuleFeatureFlags` — `comm.feature-flags.ts`: `comm.template-studio` (`defaultState: on` — permite
  desligar o Studio sem afetar CRUD/disparo, alinhado à degradação graciosa), `comm.delivery-tracking`
  (`defaultState: on` — habilita o polling de rastreio). Cada flag com `defaultState` explícito.

---

## Referências

- `02-architecture-blueprint.md` (fronteiras internas) · `05-state-and-data-flow.md` (data flow)
- BE: `docs/architecture/backend/services/comm-service/contracts/api-contract.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- ADR-001 (module-pattern), ADR-002 (signals), ADR-003 (lazy module), ADR-004 (shell integration), ADR-005 (delivery tracking/polling)
