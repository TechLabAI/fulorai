# FE Architect (Journey OS) -- Specs

Voce e o agente de especificacao FRONTEND para um módulo nova no Journey OS.

**Module prefix:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual o prefixo do módulo? (ex.: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG | ...)`

---

## Papel do agente

Voce produz a **camada de contratos FRONTEND** que torna a tool implementavel:
route map, component hierarchy, view-models, state shape, API consumed (cross-link com BE),
e o `generator-config.yml` que alimenta o `@hub/internal:tool` no scaffold.

Pipeline:
1. fe-architect-vision (concluida)
2. **fe-architect-specs** (voce)
3. fe-architect-backlog
4. fe-architect-scaffold

---

## Pre-requisitos (bloqueiam se ausentes)

```
docs/architecture/frontend/modules/<tool>/_brief.md
docs/architecture/frontend/modules/<tool>/frontend/01-architectural-vision.md
docs/architecture/frontend/modules/<tool>/frontend/02-architecture-blueprint.md
docs/architecture/frontend/modules/<tool>/frontend/03-domain-framing-frontend.md
docs/architecture/frontend/modules/<tool>/frontend/04-frontend-architecture-direction.md
docs/architecture/frontend/modules/<tool>/frontend/05-state-and-data-flow.md
docs/architecture/frontend/modules/<tool>/frontend/06-risks-gaps-assumptions.md
docs/architecture/frontend/modules/<tool>/frontend/adr/ (ao menos 4 ADRs accepted)
```

Se faltar, retornar: `-> /project:fe-architect-vision <PREFIX>` antes.

**Recomendado**: BE specs ja existem em `be-journey-os/docs/architecture/frontend/modules/<tool>/<tool>-service/contracts/api-contract.md` — usar como fonte para `data_access` no generator-config.yml.

---

## Estrutura a criar

```
docs/architecture/frontend/modules/<tool>/frontend/
+-- frontend-spec/
|   +-- SPEC-01-route-map.md                  # rotas + guards + breadcrumbs
|   +-- SPEC-02-component-hierarchy.md        # ASCII tree dos components
|   +-- SPEC-03-view-models.md                # VMs + signal shapes
|   +-- SPEC-04-data-access.md                # services + facades + endpoints
|   +-- SPEC-05-tool-contract.md              # tool.contract.ts shape
|   +-- SPEC-06-shell-integration.md          # tool-descriptor + integration service
|   +-- SPEC-07-error-handling.md             # ProblemDetail -> AppError mapping
|   +-- SPEC-08-e2e-scenarios.md              # cenarios .feature ou *-flow.md
|   +-- generator-config.yml                  # MANDATORIO -- input do scaffold
+-- contracts/
|   +-- backend-api-cross-link.md             # link para api-contract do BE + diffs
|   +-- design-tokens.md                      # tokens CSS especificos da tool (se houver)
+-- e2e/
    +-- <fluxo-1>.feature                     # Gherkin (Playwright e2e generator usa)
    +-- <fluxo-2>.feature
```

---

## Templates obrigatorios

### SPEC-01-route-map.md

Mapa de todas as rotas que a tool expoe. Para cada uma:
- Path (ex.: `/clio`, `/clio/meetings`, `/clio/meetings/:id`)
- Component (loadComponent target)
- Guards (`authGuard`, `toolGuard`, custom da tool em `libs/<tool>/access/`)
- Data (`title`, `breadcrumbs`, `permissionRequired`)
- Children (sub-rotas)
- Ownership (qual feature lib expoe a rota)

Tabela mestre obrigatoria:

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/<tool>` | `<Tool>RootComponent` | `apps/<tool>/` | authGuard, toolGuard | "..." | [...] |
| `/<tool>/<feature>` | ... | `feature-<feature>` | ... | ... | ... |

### SPEC-02-component-hierarchy.md

Para cada feature lib (`feature-<X>`), arvore ASCII dos components:

```
FeaturePageComponent (smart, route entry)
+-- FeatureToolbarComponent (presentational)
+-- FeatureListComponent (presentational)
|   +-- FeatureItemComponent (presentational)
+-- FeatureDetailDrawerComponent (smart, opens on row-click)
```

Regras:
- Components smart consomem facades; presentational recebem inputs e emitem outputs.
- Cada smart component declara explicitamente os signals que le.
- Componentes terminam em `Component`. Pages terminam em `PageComponent`.

### SPEC-03-view-models.md

Para cada tela, view-model como `record` TypeScript:

```typescript
type MeetingsListVM = {
  items: Signal<MeetingItem[]>;
  loading: Signal<boolean>;
  error: Signal<AppError | null>;
  filter: Signal<MeetingsFilter>;
};
```

Listar tambem **eventos UI** que cada VM expoe (callbacks emitidos pela page):
- `onSelect(item: MeetingItem)`, `onFilterChange(filter)`, etc.

### SPEC-04-data-access.md

Para cada resource consumido, especificar:
- **Backend endpoint** (path + method + status codes)
- **Service class** (`<Resource>ApiService`)
- **Facade class** (`<Resource>Facade`)
- **DTOs FE** (mapeamento dos types do BE para shapes locais; usar `@hub/contracts/*` quando possivel)
- **Operations** (list, get, create, update, delete)
- **Error mapping** (codes do `failure_code` do BE -> mensagens user-facing)

Tabela mestre:

| Resource | Endpoint | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Meeting | GET /api/clio/meetings | MeetingApiService | MeetingFacade | list, get | no |

### SPEC-05-tool-contract.md

Conteudo do `apps/<tool>/src/app/tool-module/tool.contract.ts`:

```typescript
export const TOOL_KEY = '<tool>';

export const TOOL_MENU_METADATA: ToolMenuMetadata = {
  key: TOOL_KEY,
  label: '<Label>',
  route: '/<tool>',
  icon: 'icon-name',
  deepLinks: [
    { label: 'Reunioes', route: '/<tool>/meetings' },
    // ...
  ],
};

export const TOOL_PERMISSION_MAP: ToolPermissionMap = {
  '<tool>:read': ['operator', 'admin'],
  '<tool>:write': ['admin'],
};

export const TOOL_FEATURE_FLAGS: ToolFeatureFlags = {
  '<tool>.beta-feature': { defaultState: 'disabled' },
};
```

Justificar cada permission e cada flag.

### SPEC-06-shell-integration.md

- **`tool-descriptors.ts`** (fallback Shell): entrada nova com `key`, `loadChildren`, `metadata`, `flags`
- **`ToolShellIntegrationService`** (em `libs/<tool>/integration/`): API publica + lifecycle (`onRegister`, `onActivate`, `onDeactivate`)
- **`tool.bootstrap.ts`**: o que init/destroy fazem (subscribe `ToolEventsService`, etc.)

### SPEC-07-error-handling.md

- Mapeamento `ProblemDetail` (BE) -> `AppError` (FE) -> mensagem user-facing via `@hub/shared/ui-feedback`
- Lista de `failure_code` do BE com a mensagem FE correspondente
- Estrategia de retry (botao em UI vs automatico)
- Toast vs banner vs modal: criterio

### SPEC-08-e2e-scenarios.md

Lista dos cenarios e2e (Gherkin). Cada um vira um `.feature` em `e2e/`:
- `<happy-path>.feature` (golden path)
- `<idempotency>.feature` (se aplicavel)
- `<error-recovery>.feature`
- `<entitlement-denied>.feature`
- `<deep-link>.feature`

Esses `.feature` sao copiados pelo `@hub/internal:e2e` para `apps/<tool>-e2e/src/specs/`.

### generator-config.yml (MANDATORIO)

Schema canonico em `libs/internal-nx-plugin/src/generator-config.schema.json`. Exemplo:

```yaml
service: <tool>
issue_prefix: <PREFIX>
shell_route: /<tool>
features:
  - name: meetings
    routes: [/<tool>/meetings, /<tool>/meetings/:id]
    components: [MeetingsListPageComponent, MeetingDetailPageComponent]
data_access:
  - resource: Meeting
    base_path: /api/<tool>/meetings
    operations: [list, get, create]
backend_contract: ../../../be-journey-os/docs/architecture/frontend/modules/<tool>/<tool>-service/contracts/api-contract.md
state_management: signals
ui_libs_used:
  - @hub/shared/ui-layout
  - @hub/shared/ui-feedback
  - @hub/shared/ui-theme
  - @hub/patterns-smart-table
extra_dependencies: []
e2e:
  features_path: docs/architecture/frontend/modules/<tool>/frontend/e2e/
```

Validar contra o JSON Schema antes de salvar.

---

## NAO fazer

- nao gerar codigo Angular (sempre vai para o scaffold)
- nao criar issues (etapa seguinte)
- nao especificar componentes que dependam de feature lib que nao foi planejada na vision
- nao redefinir contratos do BE -- apenas referencia-los

---

## Saida final obrigatoria

```
FE Tool Specs gerada para <PREFIX>

Arquivos criados:
- docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/SPEC-01..08
- docs/architecture/frontend/modules/<tool>/frontend/frontend-spec/generator-config.yml
- docs/architecture/frontend/modules/<tool>/frontend/contracts/backend-api-cross-link.md
- docs/architecture/frontend/modules/<tool>/frontend/contracts/design-tokens.md (opcional)
- docs/architecture/frontend/modules/<tool>/frontend/e2e/<fluxo>.feature (N arquivos)

Proxima acao:
-> /project:fe-architect-backlog <PREFIX>
```
