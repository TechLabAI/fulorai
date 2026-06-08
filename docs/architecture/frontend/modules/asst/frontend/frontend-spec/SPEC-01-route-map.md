# SPEC-01 — Route Map — ASST · Frontend

> Todas as rotas que o ASST expõe, seus guards, títulos e breadcrumbs. Todas são **pós-contexto**
> (exigem sessão + empresa ativa). Fonte: `04-frontend-architecture-direction.md` §5.

## Tabela mestre

| Path | Component | Feature Lib | Guards | Title | Breadcrumb |
|---|---|---|---|---|---|
| `/asst` | _redirect → `/asst/library`_ | `shell-entry` | `authGuard`, `empresaGuard` | — | — |
| `/asst/library` | `AssetLibraryPageComponent` | `feature-asset-library` | `authGuard`, `empresaGuard`, `accessGuard('asst.asset.ler')` | "Assets" | `Assets > Catálogo` |
| `/asst/assets/:id` | `AssetDetailPageComponent` | `feature-asset-detail` | `authGuard`, `empresaGuard`, `accessGuard('asst.asset.ler')` | "Detalhe do asset" | `Assets > {título}` |
| `/asst/assets/:id/studio` | `AssetStudioPageComponent` | `feature-asset-studio` | `authGuard`, `empresaGuard`, `accessGuard('asst.studio.compor')` | "Asset Studio" | `Assets > {título} > Studio` |
| `/asst/approvals` | `ApprovalQueuePageComponent` | `feature-approval-workflow` | `authGuard`, `empresaGuard`, `accessGuard('asst.asset.aprovar')` | "Aprovações" | `Assets > Aprovações` |

## Detalhe por rota

### `/asst` (raiz)
- **Ownership:** `shell-entry` (`asst.routes.ts`).
- Redireciona para `/asst/library` (`pathMatch: 'full'`).
- Guards: `authGuard`, `empresaGuard` (não há acesso pré-contexto no ASST).

### `/asst/library`
- **Ownership:** `feature-asset-library`.
- `data`: `{ title: 'Assets', breadcrumbs: ['Assets', 'Catálogo'], permissionRequired: 'asst.asset.ler' }`.
- Ações na página (não são rotas): **criar asset** (`NewAssetDialogComponent`, gated `asst.asset.criar`).
- Query params de filtro: `?tipo=&estado=&tag=&q=&page=&size=` (refletem `AssetFiltroVM`).

### `/asst/assets/:id`
- **Ownership:** `feature-asset-detail`.
- `data`: `{ title: 'Detalhe do asset', breadcrumbs: ['Assets', ':titulo'], permissionRequired: 'asst.asset.ler' }`.
- Ações na página: **editar metadados** (`asst.asset.editar`), **nova versão manual**
  (`NewVersionDialogComponent`, `asst.asset.editar`), **submeter** (`asst.asset.submeter`),
  **arquivar** (`asst.asset.arquivar`), **publicar** (`asst.asset.publicar`, quando `APROVADO`).
  Ações derivam do **estado atual** do asset (UINV-5).
- `:id` inválido / inexistente → `404 asst.asset.nao-encontrado` → estado "asset não encontrado".

### `/asst/assets/:id/studio`
- **Ownership:** `feature-asset-studio`.
- `data`: `{ title: 'Asset Studio', breadcrumbs: ['Assets', ':titulo', 'Studio'], permissionRequired: 'asst.studio.compor' }`.
- Pode ser desabilitada pela feature flag `asst.asset-studio` (degradação/desligamento — ADR-005).

### `/asst/approvals`
- **Ownership:** `feature-approval-workflow`.
- `data`: `{ title: 'Aprovações', breadcrumbs: ['Assets', 'Aprovações'], permissionRequired: 'asst.asset.aprovar' }`.
- Lista assets em `EM_REVISAO`; abrir item → `ApprovalDecisionDialogComponent` (aprovar/rejeitar);
  publicar exige `asst.asset.publicar`.

## Notas

- Guards vivem em `libs/asst/access/` (`assetGuard` opcional para resolver `:id` + escopo) e
  consomem `AccessDecisionService` (Access Layer) — a UI **não** decide RBAC (UINV-2).
- Em troca de empresa, o `NavigationService` re-deriva o menu; o catálogo é invalidado (UINV-8).
- O deep link "Aprovações" só aparece no menu para quem tem `asst.asset.aprovar` (SPEC-05/06).

## Critérios de aceite (EARS)

> Notação EARS (D-057 / `be-validate-ears.py`), uma cláusula por linha entre crases. Backfill do gate
> A2.5 (`/fe-architect-specs-validate`) — derivados do conteúdo desta SPEC + dos `e2e/*.feature`, sem
> introduzir comportamento novo. Os ids `A-0X.Y` rastreiam a cobertura EARS→Gherkin no master plan.

- **A-01.1** `IF a user without an active session opens an /asst route, THEN THE SYSTEM SHALL redirect to the login route before rendering any asset view.`
- **A-01.2** `WHEN a user navigates to the /asst root, THE SYSTEM SHALL redirect to /asst/library.`
- **A-01.3** `IF a user lacks the permission required by an /asst route, THEN THE SYSTEM SHALL deny access and SHALL NOT render the protected view.`
- **A-01.4** `WHEN a user opens an asset detail route whose id does not exist, THE SYSTEM SHALL show the asset-not-found state.`
- **A-01.5** `THE SYSTEM SHALL derive the actions available on the asset detail route from the asset current state.`
- **A-01.6** `WHILE the asst.asset-studio flag is disabled, THE SYSTEM SHALL keep the asset studio route unavailable.`
- **A-01.7** `WHEN a user opens a valid asset detail deep link with an active session and the asst.asset.ler permission, THE SYSTEM SHALL render the asset detail view.`

## Referências
- `04-frontend-architecture-direction.md` §5 · `02-architecture-blueprint.md` §3
- BE: `asst-service/contracts/api-contract.md` (perms por endpoint)
