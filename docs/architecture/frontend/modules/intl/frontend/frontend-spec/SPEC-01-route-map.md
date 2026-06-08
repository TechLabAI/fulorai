# SPEC-01 — Route Map — INTL

> Todas as rotas que o módulo INTL expõe, guards, títulos e breadcrumbs.
> Guards: `authGuard` + `empresaGuard` (Access Layer) + `accessGuard(<perm>)` (`libs/intl/access`).
> Permissões alinhadas ao contrato BE (`intl-service/contracts/api-contract.md`).
> **Todas** as rotas de INTL são pós-contexto (exigem empresa ativa) — não há rota pré-contexto.

## Tabela mestre

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/intl` | `IntlRootComponent` (redirect → `/intl/copilot`) | `libs/intl/shell-entry` | `authGuard, empresaGuard` | "Inteligência" | [Inteligência] |
| `/intl/copilot` | `CopilotPageComponent` | `feature-copilot` | `authGuard, empresaGuard, accessGuard('intl.copilot.use')` | "Copilot" | [Inteligência, Copilot] |
| `/intl/copilot/:conversaId` | `CopilotConversationPageComponent` | `feature-copilot` | `authGuard, empresaGuard, accessGuard('intl.copilot.read')` | "Conversa" | [Inteligência, Copilot, :titulo] |
| `/intl/knowledge` | `KnowledgeListPageComponent` | `feature-knowledge` | `authGuard, empresaGuard, accessGuard('intl.knowledge.read')` | "Conhecimento" | [Inteligência, Conhecimento] |
| `/intl/knowledge/novo` | `KnowledgeNodeFormPageComponent` | `feature-knowledge` | `authGuard, empresaGuard, accessGuard('intl.knowledge.write')` | "Novo nó" | [Inteligência, Conhecimento, Novo nó] |
| `/intl/knowledge/:id` | `KnowledgeNodeFormPageComponent` | `feature-knowledge` | `authGuard, empresaGuard, accessGuard('intl.knowledge.read')` | "Nó de conhecimento" | [Inteligência, Conhecimento, :titulo] |
| `/intl/analytics` | `AnalyticsPageComponent` | `feature-analytics` | `authGuard, empresaGuard, accessGuard('intl.analytics.read')` | "Analítica" | [Inteligência, Analítica] |

## Notas de guarda

- **Sem rotas pré-contexto:** INTL só opera com empresa ativa; toda rota exige `authGuard` +
  `empresaGuard` + `accessGuard(<perm>)`.
- `accessGuard(<perm>)` delega a `AccessDecisionService.can(<perm>)` (Access Layer) — nunca decide
  RBAC inline.
- A rota de criação (`/intl/knowledge/novo`) exige `intl.knowledge.write`; visualização/edição
  carrega com `intl.knowledge.read` e a UI habilita salvar só se `intl.knowledge.write`.
- Lazy: Shell → `@journeyos/intl` (entry-lib) via `loadChildren`; cada page via `loadComponent`.
- `IntlRootComponent` redireciona para a primeira rota permitida do usuário (derivada de
  `NavigationService`) — tipicamente `/intl/copilot`.

## Deep links (expostos no `intl.contract.ts`)

- `/intl/copilot` (perm `intl.copilot.use`)
- `/intl/knowledge` (perm `intl.knowledge.read`)
- `/intl/analytics` (perm `intl.analytics.read`)

## Critérios de aceite (EARS)

- `WHEN the user navigates to /intl, THE SYSTEM SHALL redirect to the first permitted route, typically /intl/copilot.`
- `IF the user has no active empresa context, THEN THE SYSTEM SHALL block every /intl route via empresaGuard and redirect to empresa selection.`
- `IF the user lacks the permission required by an INTL route, THEN THE SYSTEM SHALL deny activation via accessGuard and SHALL hide the corresponding menu deep link.`
- `WHILE the user has intl.knowledge.read but not intl.knowledge.write, THE SYSTEM SHALL load the knowledge node view and SHALL disable the save action.`
- `WHEN the user opens /intl/knowledge/novo, THE SYSTEM SHALL require intl.knowledge.write to activate the route.`
- `THE SYSTEM SHALL expose every INTL route as lazy-loaded via the @journeyos/intl shell-entry.`
