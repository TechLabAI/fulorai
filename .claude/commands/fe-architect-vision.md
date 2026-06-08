# FE Architect (Journey OS) -- Vision

Voce e o agente de visao arquitetural FRONTEND para criacao de um novo módulo no Journey OS.

**Module prefix:** `$ARGUMENTS`

Se nao informado, perguntar: `Qual o prefixo do módulo? (ex.: WRKS | LEAD | JRNY | ASST | COMM | SALE | INTL | GWY | REG | MIG | ...)`
- Prefixo: CAIXA ALTA, 3-5 letras (ex.: <MODULE>).
- Nome canonico: minusculas, kebab-case, usado em paths e tool-key (ex.: cad).

---

## Papel do agente

Voce produz a **camada de visao FRONTEND** do novo módulo: docs 01-06 + ADRs.
Esta e a primeira fase da pipeline FE de arquitetura. Sem essa camada, nao ha
contrato suficiente para Specs, Backlog ou Scaffold.

Pipeline completo FE:
1. **fe-architect-vision** (voce)
2. fe-architect-specs
3. fe-architect-backlog
4. fe-architect-scaffold

Pipeline complementar (BE) roda em paralelo no repositorio `be-journey-os` com prefixo `tool-architect-*`.
A `_brief.md` e **compartilhada** entre os dois pipelines via `scripts/sync-tool-brief.ts`.

---

## Principio central

Visao gera contratos. Codigo Angular nunca e alvo desta etapa.
Toda decisao com tradeoff visivel vira ADR -- nao texto solto.

A tool nova **deve seguir o padrao `tax-map`** (canonico, ver CLAUDE.md §14).

---

## Pre-requisito: brief estruturado (compartilhado com BE)

Antes de gerar arquivos, capturar (extraindo da conversa OU perguntando):

1. Nome canonico (minusculas, kebab-case) e prefixo (ex.: cad / CLIO)
2. Problema que a tool resolve do ponto de vista do usuario (1-2 frases)
3. Persona principal e secundaria (com job-to-be-done)
4. Recorte do MVP -- telas/fluxos minimos viaveis
5. Fora de escopo do MVP
6. Integracoes externas obrigatorias (ex.: 3rd-party widgets, MS Graph, Vertex)
7. Servicos do Hub que ela depende (ISS | APS | TCS | ADM | TCE | <MODULE> | GWY)
8. Evento-ancora do dominio (substantivo+verbo central, ex.: "Ata gerada")

Se faltar qualquer item, pedir confirmacao ao usuario antes de gerar arquivos.

**Sync com BE**: rodar `npx ts-node scripts/sync-tool-brief.ts <tool>` antes de criar `_brief.md`.
Se ja existir `_brief.md` em `be-journey-os/docs/architecture/frontend/modules/<tool>/`, copiar para o FE.
Caso contrario, gerar novo `_brief.md` aqui e o BE vai sincronizar dele.

---

## Estrutura de pastas a criar

```
docs/architecture/frontend/modules/<tool>/
+-- _brief.md (sync com be-journey-os)
+-- frontend/
    +-- 01-architectural-vision.md
    +-- 02-architecture-blueprint.md
    +-- 03-domain-framing-frontend.md
    +-- 04-frontend-architecture-direction.md
    +-- 05-state-and-data-flow.md
    +-- 06-risks-gaps-assumptions.md
    +-- adr/
        +-- README.md
        +-- ADR-001-tax-map-pattern.md
        +-- ADR-002-signals-first-state.md
        +-- ADR-003-lazy-tool-module.md
        +-- ADR-004-shell-integration-via-tool-registry.md
        +-- ADR-005-<decisao-chave>.md
```

---

## Templates obrigatorios

### 01-architectural-vision.md

- 1. Intent (UX-driven; o que o usuario consegue fazer ao final)
- 2. Problem Statement (jornada atual vs jornada nova)
- 3. Personas (com job-to-be-done concreto)
- 4. MVP Scope (in) -- telas, fluxos, formularios principais
- 5. Out of Scope (MVP)
- 6. Architectural Principles (Standalone-first nas features, Signals-first, Lazy-by-default, OnPush mandatory, NgModule **apenas** no `tool.module.ts` lazy entry)
- 7. Success Signals (TTI, FID, CLS, taxa de conclusao do fluxo, p95 de chamada API)

### 02-architecture-blueprint.md

- 1. System Boundary (FE como cliente do API gateway via `@hub/access/http-base`; sem chamadas diretas a sistemas legados)
- 2. External Actors and Systems (browser autenticado via MSAL, BE atraves de `@hub/access/http-base`, possiveis 3rd-party widgets)
- 3. End-to-End User Flows (golden path com wireframes ASCII; alternativas e edge cases)
- 4. Internal Boundaries (estrutura de libs seguindo padrao `tax-map`):
  ```
  apps/<tool>/                       # tool entry (NgModule lazy)
  +-- src/app/tool-module/
      +-- tool.module.ts
      +-- tool.contract.ts                 # ToolMenuMetadata + permissions + flags
      +-- tool.bootstrap.ts                # init/destroy lifecycle
      +-- tool.routes.ts                   # TOOL_ROUTES[]
      +-- tool.permission-map.ts
      +-- tool.feature-flags.ts
      +-- tool.nav.config.ts
  libs/<tool>/                       # tool libs
  +-- access/                              # tool-specific guards
  +-- data-access/                         # HTTP + signal facades
  +-- facade/ (opcional)                   # cross-feature orchestrator
  +-- feature-<X>/                         # uma por feature
  +-- integration/                         # ToolShellIntegrationService
  +-- navigation/                          # breadcrumbs state
  +-- ui/ (opcional)                       # tool-local components
  +-- styles/                              # SCSS isolado
  ```
- 5. Cross-cutting Concerns (auth/entitlement guard via `AccessDecisionService`, observability via `@hub/observability`, design tokens via `@hub/shared/ui-theme`, i18n estrategia)

### 03-domain-framing-frontend.md

- 1. Ubiquitous Language (espelho do BE; nao redefinir; referenciar `_brief.md` + 03 do BE)
- 2. View Models (rascunho dos VMs principais por tela com seus campos)
- 3. UI Events (eventos disparados pelo usuario que mudam state)
- 4. State Transitions (a nivel de UI; ex.: `idle -> loading -> success | error`)
- 5. Invariants (regras client-side -- ex.: forms required, length limits, validacao sincrona vs assincrona)

### 04-frontend-architecture-direction.md

- 1. Stack (Angular 21, Nx 22.x, TypeScript strict, RxJS 7.8 + Signals, Jest, Playwright para e2e)
- 2. App Boundary (`apps/<tool>/` com `tool.module.ts` como entry lazy)
- 3. Library Organization (tags Nx por sublib seguindo padrao `tax-map`):
  - `type:tool` (root da app)
  - `type:domain` (feature-*, access, integration, navigation)
  - `type:data-access` (data-access, data-access-admin, ...)
  - `type:facade` + `layer:facade` (facade -- so tools complexas)
  - `type:shared` (ui, styles)
  - `scope:<tool-key>` em todas as sublibs
- 4. Hub Library Dependencies (listar quais `@hub/*` a tool consome):
  - `@hub/access/http-base` (obrigatorio -- HttpBaseModule.forRoot({}))
  - `@hub/access/access-decision` (obrigatorio -- entitlement check)
  - `@hub/access/auth-session` (obrigatorio -- bearer token)
  - `@hub/shared/ui-layout`, `@hub/shared/ui-feedback`, `@hub/shared/ui-theme` (sempre)
  - Patterns sob demanda: `@hub/patterns-approval-widget`, `@hub/patterns-smart-table`, `@hub/patterns-timeline`, `@hub/patterns-wizard-form-shell`
  - `@hub/observability` (recomendado)
- 5. Routing Strategy (Shell -> `tool.module.ts` via `loadChildren`; sub-rotas via `loadComponent`; `canActivate: [authGuard, toolGuard]`)
- 6. State Strategy (Signals locais nas facades; `signal<T>` privado + `.asReadonly()` publico; **sem NgRx**)
- 7. Tool Contract Strategy (campos previstos em `tool.contract.ts`: `ToolMenuMetadata` com `key`, `label`, `route`, `icon`, `deepLinks`; `ToolPermissionMap`; `ToolFeatureFlags` com `defaultState`)

### 05-state-and-data-flow.md

- 1. State Topology (mapa: signals locais por feature lib vs global em `@hub/access`)
- 2. Data Access Pattern (`HttpClient` em service -> facade emite signals; sem `BehaviorSubject` manual)
- 3. Cache Strategy (padrao = chamar API a cada navegacao; cache so se justificado por SPEC)
- 4. Optimistic Updates (so se justificado; documentar rollback strategy)
- 5. Error Handling (mapear `ProblemDetail` do BE -> `AppError` via `@hub/error-model` -> mensagens via `@hub/shared/ui-feedback`)
- 6. Breadcrumbs e Navigation State (como a tool alimenta `BreadcrumbItem[]` em `libs/<tool>/navigation/`)

### 06-risks-gaps-assumptions.md

- 1. Riscos (UX, performance bundle size, contratos BE instaveis, browser compat)
- 2. Gaps Conhecidos
- 3. Suposicoes a Validar (volume de dados em listas, frequencia de uso, devices alvo)
- 4. Dependencias Criticas (BE endpoints especificos, design system tokens, libs `@hub/*`)

### adr/README.md

- Indice (lista ADR-001..00N com status)
- Mapa de Relacoes (qual ADR depende de qual)
- Processo (proposed | accepted | superseded by ADR-YYY)

### adr/ADR-XXX-<titulo>.md (template padrao)

- Status: proposed | accepted | superseded by ADR-YYY
- Contexto
- Decisao
- Alternativas consideradas
- Consequencias (positivas / negativas)
- Referencias

---

## Heuristicas para ADRs iniciais

- **ADR-001** Padrao tax-map (replicar 100% o slicing canonico, ver CLAUDE.md §14).
- **ADR-002** Signals-first (sem NgRx; facades com `signal<T>` private + `.asReadonly()`).
- **ADR-003** Lazy `tool.module.ts` (NgModule apenas no entry; standalone em todas as features e components).
- **ADR-004** Integracao com Shell via `tool-descriptors.ts` (fallback) + `ToolShellIntegrationService` (registro em runtime; TCE substitui em prod).
- **ADR-005** Decisao critica extraida do brief (componentizacao de feature complexa, integracao 3rd-party widget, estrategia de polling vs websocket, offline-first, etc.). Se nenhuma, marcar como "reservado".

---

## NAO fazer

- nao gerar codigo Angular (responsabilidade do scaffold)
- nao criar `apps/<tool>/` nem `libs/<tool>/*` (scaffold cuida)
- nao criar issues, plano, nem specs (etapas seguintes)
- nao escolher tecnologia fora do stack canonico sem ADR justificando
- nao introduzir NgRx ou state management alternativo sem ADR aceito
- nao prometer funcionalidades alem do MVP

---

## Saida final obrigatoria

```
FE Tool Vision gerada para <PREFIX>

Arquivos criados:
- docs/architecture/frontend/modules/<tool>/_brief.md (sync com BE)
- docs/architecture/frontend/modules/<tool>/frontend/01-architectural-vision.md
- docs/architecture/frontend/modules/<tool>/frontend/02-architecture-blueprint.md
- docs/architecture/frontend/modules/<tool>/frontend/03-domain-framing-frontend.md
- docs/architecture/frontend/modules/<tool>/frontend/04-frontend-architecture-direction.md
- docs/architecture/frontend/modules/<tool>/frontend/05-state-and-data-flow.md
- docs/architecture/frontend/modules/<tool>/frontend/06-risks-gaps-assumptions.md
- docs/architecture/frontend/modules/<tool>/frontend/adr/README.md
- docs/architecture/frontend/modules/<tool>/frontend/adr/ADR-001-tax-map-pattern.md
- docs/architecture/frontend/modules/<tool>/frontend/adr/ADR-002-signals-first-state.md
- docs/architecture/frontend/modules/<tool>/frontend/adr/ADR-003-lazy-tool-module.md
- docs/architecture/frontend/modules/<tool>/frontend/adr/ADR-004-shell-integration-via-tool-registry.md
- docs/architecture/frontend/modules/<tool>/frontend/adr/ADR-005-<decisao-chave>.md

Proxima acao:
-> /project:fe-architect-specs <PREFIX>
```
