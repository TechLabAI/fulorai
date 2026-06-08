# 04 — Frontend Architecture Direction — INTL

> Direção técnica do módulo: stack, organização de libs (module-pattern + tags Nx), dependências
> `@journeyos/*`, routing, estado e contrato do módulo.

## 1. Stack

- **Angular 18+** (standalone, control flow novo, Signals), **Nx 19+** workspace (`@journeyos`).
- **TypeScript strict**.
- **RxJS 7.8** (interop pontual — HTTP + `AbortController`/cancelamento de pergunta) **+ Signals**
  (estado de UI). Sem NgRx.
- **Jest** (unit) · **Playwright** (e2e em `apps/intl-e2e`).
- **SCSS** isolado em `libs/intl/styles` consumindo `@journeyos/shared/ui-tokens`.

## 2. App Boundary

`apps/intl/` é o host fino. O entry do módulo é a **library** `@journeyos/intl` em
`libs/intl/shell-entry` (ADR-003 + ADR-006 global) — carregada pelo Shell via `loadChildren`.
Todas as features e componentes são `standalone` + `OnPush`. Não há `NgModule` de domínio.

## 3. Library Organization (tags Nx — padrão module-pattern)

| Lib | `type:*` | `scope:*` | Papel |
|---|---|---|---|
| `apps/intl` | `type:app` | `scope:intl` | host fino (carrega `@journeyos/intl`) |
| `libs/intl/shell-entry` | `type:feature` | `scope:intl` | entry-lib: contract, routes, descriptor, bootstrap |
| `libs/intl/feature-copilot` | `type:feature` | `scope:intl` | chat + conversas + citações |
| `libs/intl/feature-knowledge` | `type:feature` | `scope:intl` | lista/busca + form de nó + indexar/arquivar |
| `libs/intl/feature-analytics` | `type:feature` | `scope:intl` | dashboards funil + uso do copiloto |
| `libs/intl/data-access` | `type:data-access` | `scope:intl` | `Copilot/Knowledge/AnalyticsApiService` + facades signal |
| `libs/intl/access` | `type:domain` | `scope:intl` | guards específicos do módulo |
| `libs/intl/integration` | `type:domain` | `scope:intl` | `IntlShellIntegrationService` |
| `libs/intl/navigation` | `type:domain` | `scope:intl` | breadcrumb/menu state |
| `libs/intl/ui` | `type:ui` | `scope:intl` | `chat-bubble`, `citation-chip`, `stat-card` (opcional) |
| `libs/intl/styles` | `type:ui` | `scope:intl` | SCSS isolado |

Direções permitidas (nx-boundaries): `feature → data-access | ui | access | shared/*`;
`data-access → shared/{contracts,access-http-base,empresa-context,error-model}`;
`access → shared/{access-decision,auth-session}`. **Proibido** importar `scope:<outro-módulo>`.

## 4. Shared Library Dependencies (`@journeyos/*` consumidas)

| Lib | Obrigatória? | Uso no INTL |
|---|---|---|
| `@journeyos/shared/access-http-base` | ✅ | HttpClient + interceptors (`X-Empresa-Id`, `X-Correlation-Id`, ErrorNormalize). |
| `@journeyos/shared/auth-session` | ✅ | Sessão/JWT (bearer); INTL apenas consome. |
| `@journeyos/shared/empresa-context` | ✅ | Empresa ativa (INTL **consome**; não alimenta). Troca → reset de estado. |
| `@journeyos/shared/access-decision` | ✅ | `AccessDecisionService.can('intl.*')`, `NavigationService`. |
| `@journeyos/shared/ui-tokens` · `ui-components` · `ui-feedback` | ✅ | Tokens, primitivos, estados empty/loading/error. |
| `@journeyos/shared/error-model` | ✅ | `ProblemDetail → AppError` (incl. `503 ai/embedding-unavailable`). |
| `@journeyos/shared/observability` | ◻ recomendado | Timing pergunta→resposta, custo de tokens, taxa de degradação. |

INTL **não** consome `@journeyos/shared/contracts` de outro módulo, nem patterns 3rd-party no MVP.
Depende de **WRKS** apenas via Access Layer (não importa `scope:wrks`).

## 5. Routing Strategy

- Shell → `@journeyos/intl` (entry-lib) via `loadChildren`.
- Sub-rotas via `loadComponent` (cada feature é standalone).
- **Todas** as rotas de INTL são pós-contexto (exigem empresa ativa):
  `canActivate: [authGuard, empresaGuard, accessGuard(<perm>)]`.

```
/intl/copilot                  → feature-copilot          [authGuard, empresaGuard, accessGuard('intl.copilot.use')]
/intl/copilot/:conversaId      → feature-copilot (chat)   [authGuard, empresaGuard, accessGuard('intl.copilot.read')]
/intl/knowledge                → feature-knowledge        [authGuard, empresaGuard, accessGuard('intl.knowledge.read')]
/intl/knowledge/novo           → feature-knowledge (form) [authGuard, empresaGuard, accessGuard('intl.knowledge.write')]
/intl/knowledge/:id            → feature-knowledge (form) [authGuard, empresaGuard, accessGuard('intl.knowledge.read')]
/intl/analytics                → feature-analytics        [authGuard, empresaGuard, accessGuard('intl.analytics.read')]
```

## 6. State Strategy

- **Signals locais** nas facades de `data-access`: `signal<T>` privado + `.asReadonly()` público.
- **Sem NgRx / BehaviorSubject manual** (ADR-002).
- A **conversa corrente** do Copilot é estado de facade (lista de `MensagemVM` em `signal`), com
  inserção otimista da bolha `PENDENTE`; cancelamento via `AbortController`.
- `computed()` para derivações (ex.: pode-enviar? = sem bolha `PENDENTE` && texto não-vazio;
  visibilidade de ações de Knowledge por permissão).
- Estado global (sessão/empresa/RBAC) **não** vive no INTL — vive na Access Layer; o INTL consome
  e **reage** à troca de empresa (efeito que limpa conversa + recarrega listas).

## 7. Module Contract Strategy (`intl.contract.ts`)

```ts
// ModuleMenuMetadata
{
  key: 'intl',
  label: 'Inteligência',
  route: '/intl/copilot',
  icon: 'auto_awesome',
  deepLinks: [
    { key: 'copilot',   label: 'Copilot',     route: '/intl/copilot',   perm: 'intl.copilot.use' },
    { key: 'knowledge', label: 'Conhecimento', route: '/intl/knowledge', perm: 'intl.knowledge.read' },
    { key: 'analytics', label: 'Analítica',    route: '/intl/analytics', perm: 'intl.analytics.read' },
  ],
}
```

- `ModulePermissionMap` — `intl.permission-map.ts`: rota/ação → permissão canônica
  (`intl.copilot.use`, `intl.copilot.read`, `intl.knowledge.read`, `intl.knowledge.write`,
  `intl.analytics.read`).
- `ModuleFeatureFlags` — `intl.feature-flags.ts`: `intl.copilot` (`defaultState: on`),
  `intl.knowledge` (`defaultState: on`), `intl.analytics` (`defaultState: on`),
  `intl.copilot-streaming` (`defaultState: off` — reservado para o pós-MVP, ver ADR-005).

---

## Referências

- `02-architecture-blueprint.md` (fronteiras internas) · `05-state-and-data-flow.md`
- `docs/architecture/frontend/standards/nx-boundaries.md`
- ADR-001 (module-pattern), ADR-002 (signals), ADR-003 (lazy entry-lib), ADR-004 (shell integration),
  ADR-005 (copilot answer rendering / streaming deferral)
