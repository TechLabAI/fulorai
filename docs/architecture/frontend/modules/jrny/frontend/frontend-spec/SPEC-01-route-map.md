# SPEC-01 — Route Map — JRNY · Frontend

> Todas as rotas que o JRNY expõe, seus guards, títulos e breadcrumbs. Todas são **pós-contexto**
> (exigem sessão + empresa ativa). Fonte: `04-frontend-architecture-direction.md` §5.

## Tabela mestre

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/jrny` | _redirect → `/jrny/journeys`_ | `shell-entry` | `authGuard`, `empresaGuard` | — | — |
| `/jrny/journeys` | `JourneyListPageComponent` | `feature-journey-list` | `authGuard`, `empresaGuard`, `accessGuard('jrny.jornada.ler')` | "Jornadas" | `Jornadas` |
| `/jrny/journeys/:id/builder` | `JourneyBuilderPageComponent` | `feature-journey-builder` | `authGuard`, `empresaGuard`, `accessGuard('jrny.jornada.ler')` | "Builder" | `Jornadas > {nome}` |
| `/jrny/journeys/:id/stages/:stageId` | `StageEditorPageComponent` | `feature-stage-editor` | `authGuard`, `empresaGuard`, `accessGuard('jrny.estagio.ler')` | "Estágio" | `Jornadas > {nome} > Estágio {ordem}` |
| `/jrny/journeys/:id/rules` | `RoutingRulesPageComponent` | `feature-routing-engine` | `authGuard`, `empresaGuard`, `accessGuard('jrny.roteamento.ler')` | "Regras de roteamento" | `Jornadas > {nome} > Regras` |
| `/jrny/leads/:leadId/decisions` | `DecisionLogPageComponent` | `feature-decision-log` | `authGuard`, `empresaGuard`, `accessGuard('jrny.roteamento.ler')` | "Decisões do lead" | `Leads > {leadId} > Decisões` |
| `/jrny/analytics` | `JourneyAnalyticsPageComponent` | `feature-journey-analytics` | `authGuard`, `empresaGuard`, `accessGuard('jrny.roteamento.ler')` | "Analytics de jornada" | `Jornadas > Analytics` |

## Detalhe por rota

### `/jrny` (raiz)
- **Ownership:** `shell-entry` (`jrny.routes.ts`). Redireciona para `/jrny/journeys` (`pathMatch: 'full'`).
- Guards: `authGuard`, `empresaGuard` (não há acesso pré-contexto no JRNY).

### `/jrny/journeys`
- **Ownership:** `feature-journey-list`. Lista de jornadas por estado + busca; criar rascunho (dialog).
- `data`: `{ title: 'Jornadas', breadcrumbs: ['Jornadas'], permissionRequired: 'jrny.jornada.ler' }`.
- Query params de filtro: `?estado=&q=&page=&size=` (refletem `JourneyFiltroVm`).
- Ação **criar jornada** gated por `jrny.jornada.criar` (botão escondido sem permissão).

### `/jrny/journeys/:id/builder`
- **Ownership:** `feature-journey-builder`. Editor estruturado de estágios ordenados + máquina de estados.
- `data`: `{ title: 'Builder', breadcrumbs: ['Jornadas', ':nome'], permissionRequired: 'jrny.jornada.ler' }`.
- Edição (add/reordenar estágio, publicar, arquivar, nova-versão) gated por permissão **e** por
  `estadoJornada === 'RASCUNHO'`. Jornada `PUBLICADA`/`ARQUIVADA` → builder em **read-only**; CTA
  "criar nova versão" (`jrny.jornada.editar`) substitui a edição (ADR-005).
- `:id` inexistente → `404 jrny.jornada.nao-encontrada` → estado "jornada não encontrada".

### `/jrny/journeys/:id/stages/:stageId`
- **Ownership:** `feature-stage-editor`. Edita um estágio (tipo/nome/asset/terminal/config).
- `data`: `{ title: 'Estágio', breadcrumbs: ['Jornadas', ':nome', 'Estágio :ordem'], permissionRequired: 'jrny.estagio.ler' }`.
- Salvar gated por `jrny.estagio.editar` (+ `jrny.estagio.criar` para novo) e `estado RASCUNHO`.
- `stageId = 'novo'` abre o editor em modo criação.

### `/jrny/journeys/:id/rules`
- **Ownership:** `feature-routing-engine`. Lista de regras versionadas da jornada + editor (dialog).
- `data`: `{ title: 'Regras de roteamento', breadcrumbs: ['Jornadas', ':nome', 'Regras'], permissionRequired: 'jrny.roteamento.ler' }`.
- Criar/editar regra gated por `jrny.regra.criar`/`jrny.regra.editar`.

### `/jrny/leads/:leadId/decisions`
- **Ownership:** `feature-decision-log`. Estado de jornada do lead + trilha imutável de decisões (read-only).
- `data`: `{ title: 'Decisões do lead', breadcrumbs: ['Leads', ':leadId', 'Decisões'], permissionRequired: 'jrny.roteamento.ler' }`.
- Lead sem inscrição → `404 jrny.inscricao.nao-encontrada` → estado vazio amigável (ainda lista decisões `NAO_ROTEADO` se houver).

### `/jrny/analytics`
- **Ownership:** `feature-journey-analytics`. Funil por estágio + saúde do roteamento (read-only).
- `data`: `{ title: 'Analytics de jornada', breadcrumbs: ['Jornadas', 'Analytics'], permissionRequired: 'jrny.roteamento.ler' }`.
- Pode ser desabilitada pela feature flag `jrny.journey-analytics`.

## Critérios de aceite (EARS)

- `WHEN the user navigates to /jrny, THE SYSTEM SHALL redirect to /jrny/journeys.`
- `IF the user has no active empresa context, THEN THE SYSTEM SHALL block every /jrny route via empresaGuard and redirect to the empresa selection.`
- `IF the user lacks the permission required by a JRNY route, THEN THE SYSTEM SHALL deny activation via accessGuard and SHALL hide the corresponding menu deep link.`
- `WHEN the user opens /jrny/journeys/:id/builder for a non-existent journey, THE SYSTEM SHALL render the "jornada não encontrada" state instead of an empty builder.`
- `WHILE a journey is not in RASCUNHO, THE SYSTEM SHALL render the builder read-only and SHALL offer "criar nova versão" instead of in-place editing.`
- `WHEN the user opens /jrny/leads/:leadId/decisions for a lead without enrolment, THE SYSTEM SHALL render the "sem inscrição" empty state.`
- `WHILE the feature flag jrny.journey-analytics is disabled, THE SYSTEM SHALL omit the /jrny/analytics route and its menu entry.`
- `THE SYSTEM SHALL expose every JRNY route as lazy-loaded via the @journeyos/jrny shell-entry.`

## Notas

- Guards vivem em `libs/jrny/access/` e consomem `AccessDecisionService` (Access Layer) — a UI **não**
  decide RBAC.
- Em troca de empresa, o `NavigationService` re-deriva o menu; lista/builder são invalidados.
- Deep links "Builder", "Regras", "Analytics" só aparecem com a permissão respectiva.
- A rota de decisões é alcançada por deep-link (de outra UI que conhece o `leadId`); não há listagem
  global de leads no JRNY (isso é do LEAD).

## Referências
- `04-frontend-architecture-direction.md` §5 · `02-architecture-blueprint.md` §3
- BE: `jrny-service/contracts/api-contract.md` (perms por endpoint)
