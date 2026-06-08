# SPEC-01 — Route Map — SALE · Frontend

> Todas as rotas que o SALE expõe, seus guards, títulos e breadcrumbs. Todas são **pós-contexto**
> (exigem sessão + empresa ativa). Fonte: `04-frontend-architecture-direction.md` §5 + `_brief.md` (item 4).

## Tabela mestre

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/sale` | _redirect → `/sale/pipeline`_ | `shell-entry` | `authGuard`, `empresaGuard` | — | — |
| `/sale/pipeline` | `SalePipelinePageComponent` | `feature-pipeline` | `authGuard`, `empresaGuard`, `accessGuard('sale.oportunidade.read')` | "Pipeline" | `Pipeline` |
| `/sale/opportunities/:id` | `OpportunityDetailPageComponent` | `feature-opportunity` | `authGuard`, `empresaGuard`, `accessGuard('sale.oportunidade.read')` | "Oportunidade" | `Pipeline > {titulo}` |
| `/sale/offers` | `OfferListPageComponent` | `feature-offer` | `authGuard`, `empresaGuard`, `accessGuard('sale.oferta.read')` | "Ofertas" | `Ofertas` |
| `/sale/offers/:id` | `OfferDetailPageComponent` | `feature-offer` | `authGuard`, `empresaGuard`, `accessGuard('sale.oferta.read')` | "Oferta" | `Ofertas > {nome}` |
| `/sale/purchases` | `PurchaseListPageComponent` | `feature-purchase` | `authGuard`, `empresaGuard`, `accessGuard('sale.compra.read')` | "Compras" | `Compras` |
| `/sale/purchases/:id` | `PurchaseDetailPageComponent` | `feature-purchase` | `authGuard`, `empresaGuard`, `accessGuard('sale.compra.read')` | "Compra" | `Compras > {idExterno}` |
| `/sale/attribution` | `AttributionPageComponent` | `feature-attribution` | `authGuard`, `empresaGuard`, `accessGuard('sale.atribuicao.read')` | "Atribuição" | `Atribuição` |
| `/sale/dashboard` | `RevenueDashboardPageComponent` | `feature-revenue-dashboard` | `authGuard`, `empresaGuard`, `accessGuard('sale.ltv.read')` | "Receita" | `Receita` |

## Detalhe por rota

### `/sale` (raiz)
- **Ownership:** `shell-entry` (`sale.routes.ts`). Redireciona para `/sale/pipeline` (`pathMatch: 'full'`).
- Guards: `authGuard`, `empresaGuard` (não há acesso pré-contexto no SALE).

### `/sale/pipeline`
- **Ownership:** `feature-pipeline`. **Kanban** de oportunidades: colunas = estágios, cards = deals.
  Drag-and-drop move estágio (CDK DragDrop) com **optimistic update + rollback** (ADR-005).
- `data`: `{ title: 'Pipeline', breadcrumbs: ['Pipeline'], permissionRequired: 'sale.oportunidade.read' }`.
- Query params de filtro: `?responsavel=&estado=&q=` (refletem `PipelineFiltroVm`).
- Ação **criar oportunidade** gated por `sale.oportunidade.criar` (botão escondido sem permissão).
- Mover card (drag) gated por `sale.oportunidade.mover`; sem a permissão o board é read-only.

### `/sale/opportunities/:id`
- **Ownership:** `feature-opportunity`. Detalhe do deal: lead, valor, responsável, probabilidade,
  **histórico de estágio**; ações **ganhar** / **perder** (motivo obrigatório).
- `data`: `{ title: 'Oportunidade', breadcrumbs: ['Pipeline', ':titulo'], permissionRequired: 'sale.oportunidade.read' }`.
- `ganhar`/`perder` gated por `sale.oportunidade.fechar`. **Perder** exige `motivo` (`422 motivo-obrigatorio`).
- `:id` inexistente → `404 sale.oportunidade.nao-encontrada` → estado "oportunidade não encontrada".
- Oportunidade `GANHA`/`PERDIDA` → ações de fechamento desabilitadas (terminal, ADR-005).

### `/sale/offers` (+ `/sale/offers/:id`)
- **Ownership:** `feature-offer`. Catálogo **versionado** (produto+preço+moeda+vigência).
- `data` (lista): `{ title: 'Ofertas', breadcrumbs: ['Ofertas'], permissionRequired: 'sale.oferta.read' }`.
- `data` (detalhe): `{ title: 'Oferta', breadcrumbs: ['Ofertas', ':nome'], permissionRequired: 'sale.oferta.read' }`.
- Criar gated por `sale.oferta.criar`; editar (gera **nova versão**) por `sale.oferta.editar`; desativar por `sale.oferta.desativar`.
- Versões anteriores são **imutáveis** (editar nunca muta a versão exibida — cria a próxima).

### `/sale/purchases` (+ `/sale/purchases/:id`)
- **Ownership:** `feature-purchase`. Lista/busca de compras confirmadas + detalhe (itens + **breakdown de atribuição**).
- `data` (lista): `{ title: 'Compras', breadcrumbs: ['Compras'], permissionRequired: 'sale.compra.read' }`.
- `data` (detalhe): `{ title: 'Compra', breadcrumbs: ['Compras', ':idExterno'], permissionRequired: 'sale.compra.read' }`.
- **Sem criação no FE** — a ingestão (`POST /compras`) é server-to-server/idempotente (checkout/gateway).
- Ações **estornar** (`sale.compra.estornar`) / **cancelar** (`sale.compra.cancelar`), com confirmação destrutiva.
- `:id` inexistente → `404 sale.compra.nao-encontrada` → estado vazio.

### `/sale/attribution`
- **Ownership:** `feature-attribution`. Modelos de atribuição versionados: listar versões, **criar** (inativa),
  **ativar** (re-atribui as compras afetadas); ver o **breakdown** de uma compra.
- `data`: `{ title: 'Atribuição', breadcrumbs: ['Atribuição'], permissionRequired: 'sale.atribuicao.read' }`.
- Criar gated por `sale.atribuicao.criar`; ativar por `sale.atribuicao.ativar`.
- Pode ser ampliada (modelos multi-touch) pela flag `sale.attribution-multitouch` (default `disabled`; default last-touch).

### `/sale/dashboard`
- **Ownership:** `feature-revenue-dashboard`. Funil de receita por **origem/período** + **LTV** dos top contatos (read-only, Elastic-backed).
- `data`: `{ title: 'Receita', breadcrumbs: ['Receita'], permissionRequired: 'sale.ltv.read' }`.
- Pode ser desabilitada pela feature flag `sale.revenue-dashboard` (default `enabled`).

## Critérios de aceite (EARS)

- `WHEN the user navigates to /sale, THE SYSTEM SHALL redirect to /sale/pipeline.`
- `IF the user has no active empresa context, THEN THE SYSTEM SHALL block every /sale route via empresaGuard and redirect to the empresa selection.`
- `IF the user lacks the permission required by a SALE route, THEN THE SYSTEM SHALL deny activation via accessGuard and SHALL hide the corresponding menu deep link.`
- `WHEN the user opens /sale/opportunities/:id for a non-existent opportunity, THE SYSTEM SHALL render the "oportunidade não encontrada" state instead of an empty detail.`
- `WHEN the user opens /sale/purchases/:id for a non-existent purchase, THE SYSTEM SHALL render the "compra não encontrada" empty state.`
- `WHILE the feature flag sale.revenue-dashboard is disabled, THE SYSTEM SHALL omit the /sale/dashboard route and its menu entry.`
- `THE SYSTEM SHALL expose every SALE route as lazy-loaded via the @journeyos/sale shell-entry.`

## Notas

- Guards vivem em `libs/sale/access/` e consomem `AccessDecisionService` (Access Layer) — a UI **não**
  decide RBAC.
- Em troca de empresa, o `NavigationService` re-deriva o menu; pipeline/listas são invalidados.
- Deep links "Pipeline", "Ofertas", "Compras", "Atribuição", "Receita" só aparecem com a permissão respectiva.
- A rota de detalhe da oportunidade é alcançada por deep-link (card do Kanban ou de outra UI que conheça o `id`).

## Referências
- `04-frontend-architecture-direction.md` §5 · `02-architecture-blueprint.md` §3 · `adr/ADR-005-kanban-pipeline-rendering.md`
- BE: `sale-service/contracts/api-contract.md` (perms por endpoint)
