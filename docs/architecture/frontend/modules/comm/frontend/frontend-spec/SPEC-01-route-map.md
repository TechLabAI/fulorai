# SPEC-01 — Route Map — COMM · Frontend

> Rotas expostas pelo módulo COMM, guards, títulos e breadcrumbs. Todas pós-contexto (empresa ativa).
> Entry lazy: Shell → `@journeyos/comm` (`libs/comm/shell-entry`, `COMM_ROUTES`) via `loadChildren`.

## Tabela mestre de rotas

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/comm` | (redirect → `/comm/templates`) | `shell-entry` | authGuard, empresaGuard | — | — |
| `/comm/templates` | `TemplateCatalogPageComponent` | `feature-template-catalog` | authGuard, empresaGuard, accessGuard(`comm.template.ler`) | "Templates" | Comunicação ▸ Templates |
| `/comm/templates/:id` | `TemplateEditorPageComponent` | `feature-template-catalog` | authGuard, empresaGuard, accessGuard(`comm.template.ler`) | "Editar template" | Comunicação ▸ Templates ▸ {nome} |
| `/comm/templates/:id/studio` | `TemplateStudioPageComponent` | `feature-template-studio` | authGuard, empresaGuard, accessGuard(`comm.studio.compor`) | "Template Studio" | Comunicação ▸ Templates ▸ {nome} ▸ Studio |
| `/comm/routing-rules` | `RoutingRulesPageComponent` | `feature-routing-rules` | authGuard, empresaGuard, accessGuard(`comm.roteamento.ler`) | "Roteamento" | Comunicação ▸ Roteamento |
| `/comm/messages` | `MessagesListPageComponent` | `feature-messages` | authGuard, empresaGuard, accessGuard(`comm.mensagem.ler`) | "Mensagens" | Comunicação ▸ Mensagens |
| `/comm/messages/:id` | `MessageDetailPageComponent` | `feature-messages` | authGuard, empresaGuard, accessGuard(`comm.mensagem.ler`) | "Mensagem" | Comunicação ▸ Mensagens ▸ {id curto} |
| `/comm/channels` | `ChannelConfigPageComponent` | `feature-channel-config` | authGuard, empresaGuard, accessGuard(`comm.canal.ler`) | "Canais" | Comunicação ▸ Canais |

> **Ações (não são rotas):** criar/editar template, ativar/arquivar, criar/editar regra, **disparar
> mensagem** (`DispatchDialogComponent`), criar/editar canal — abertas como dialog/drawer dentro das
> páginas, gated pela permissão de escrita correspondente (`comm.template.criar|editar|publicar|arquivar`,
> `comm.roteamento.criar|editar`, `comm.mensagem.enviar`, `comm.canal.configurar`).

## Guards (ordem de avaliação)

1. `authGuard` — sessão válida (Access Layer); sem sessão → redireciona ao login do Shell.
2. `empresaGuard` — empresa ativa selecionada; sem empresa → seleção de empresa (WRKS).
3. `accessGuard(perm)` — `AccessDecisionService.can(perm)`; negado → rota "sem permissão".

## Critérios de aceite (EARS)

- **C-01.1 (Ubiquitous):** `THE SYSTEM SHALL expor as rotas COMM apenas através do entry lazy @journeyos/comm carregado pelo Shell via loadChildren`
- **C-01.2 (Event-driven):** `WHEN o usuário navega para /comm, THE SYSTEM SHALL redirecionar para /comm/templates`
- **C-01.3 (Unwanted):** `IF a sessão não está autenticada ao acessar qualquer rota /comm, THEN THE SYSTEM SHALL bloquear via authGuard e redirecionar ao login sem renderizar a feature`
- **C-01.4 (Unwanted):** `IF não há empresa ativa ao acessar /comm, THEN THE SYSTEM SHALL bloquear via empresaGuard e levar à seleção de empresa`
- **C-01.5 (Unwanted):** `IF o usuário não possui a permissão comm exigida pela rota, THEN THE SYSTEM SHALL bloquear via accessGuard e exibir o estado sem-permissão`
- **C-01.6 (Event-driven):** `WHEN uma rota COMM é ativada, THE SYSTEM SHALL publicar o breadcrumb correspondente em libs/comm/navigation`
- **C-01.7 (State-driven):** `WHILE o deep link de menu não tiver permissão correspondente, THE SYSTEM SHALL omiti-lo da navegação via NavigationService`

## Referências

- `04-frontend-architecture-direction.md` §5 (routing) · `02-architecture-blueprint.md` §4
- SPEC-05 (module contract) · SPEC-06 (shell integration)
- BE: `comm-service/contracts/api-contract.md`
