# SPEC-02 — Component Hierarchy — ASST · Frontend

> Árvore de componentes por feature lib. Smart components consomem facades (signals);
> presentational recebem `input()` e emitem `output()`. Pages terminam em `PageComponent`.
> Todos `standalone` + `OnPush`.

## feature-asset-library

```
AssetLibraryPageComponent (smart, route entry)            ← lê AssetCatalogFacade
├── AssetFilterBarComponent (presentational)              → out: filterChange(AssetFiltroVM)
├── AssetGridComponent (presentational)                   ← in: assets, loading; out: open(id)
│   └── AssetCardComponent (presentational)               ← in: AssetResumoVM; out: open
│       ├── AssetTypeChipComponent (presentational)       ← in: tipoAsset
│       └── AssetStateChipComponent (presentational)      ← in: estado
├── JosEmptyStateComponent (@journeyos/shared/ui-feedback)  (catálogo vazio)
├── JosLoadingComponent (@journeyos/shared/ui-feedback)
├── JosErrorComponent (@journeyos/shared/ui-feedback)       ← in: AppError
└── NewAssetDialogComponent (smart, opens on "Novo asset") ← lê/escreve AssetCatalogFacade
    └── AssetMetadataFormComponent (presentational)        → out: submit(NovoAssetForm)
```

Signals lidos por `AssetLibraryPageComponent`: `catalogo()`, `loading()`, `error()`, `filtro()`,
`paginacao()`.

## feature-asset-detail

```
AssetDetailPageComponent (smart, route entry)             ← lê AssetDetailFacade
├── AssetHeaderComponent (presentational)                 ← in: AssetDetailVM; out: editMetadata, archive
│   ├── AssetStateChipComponent (presentational)
│   └── AssetActionsComponent (presentational)            ← in: estado, perms; out: submit, publish, openStudio
├── VersionTimelineComponent (presentational)             ← in: VersaoResumoVM[]; out: selectVersion(numero)
│   └── VersionOrigemBadgeComponent (presentational)      ← in: origem (MANUAL | ASSET_STUDIO)
├── VersionContentViewComponent (presentational)          ← in: VersaoDetailVM (conteúdo + binários por URL)
├── AssetMetadataFormComponent (presentational, reuse)    → out: save(metadata)   [edição]
└── NewVersionDialogComponent (smart)                     ← escreve AssetDetailFacade; out: created
    └── VersionContentFormComponent (presentational)      → out: submit(NovaVersaoForm) [conteúdo + URLs]
```

Signals lidos por `AssetDetailPageComponent`: `asset()`, `versoes()`, `versaoSelecionada()`,
`acoesDisponiveis()` (computed do estado), `loading()`, `error()`.

## feature-asset-studio

```
AssetStudioPageComponent (smart, route entry)             ← lê AssetStudioFacade
├── StudioBriefFormComponent (presentational)             → out: compose(StudioComposeForm)
│   └── (campos: brief, contexto, baseVersaoNumero?)
├── StudioComposingIndicatorComponent (presentational)    ← in: studioState='composing'
├── StudioDegradedBannerComponent (presentational)        ← in: studioState='degradado'; out: composeManually
└── StudioResultPreviewComponent (presentational)         ← in: VersaoDetailVM (draft); out: openInDetail
```

Signals lidos por `AssetStudioPageComponent`: `studioState()`, `draftProduzido()`, `error()`.

## feature-approval-workflow

```
ApprovalQueuePageComponent (smart, route entry)           ← lê ApprovalFacade
├── ApprovalQueueListComponent (presentational)           ← in: ApprovalItemVM[]; out: open(assetId)
│   └── ApprovalQueueItemComponent (presentational)       ← in: ApprovalItemVM
├── JosEmptyStateComponent (fila vazia)
└── ApprovalDecisionDialogComponent (smart, opens on item)← lê/escreve ApprovalFacade
    ├── VersionContentViewComponent (reuse)               ← in: versão submetida
    └── ApprovalDecisionFormComponent (presentational)    → out: decide(ApprovalDecisionForm)
                                                              (comentário obrigatório se REJEITADO)
```

Signals lidos por `ApprovalQueuePageComponent`: `fila()`, `itemAberto()`, `loading()`, `error()`,
`publicando()`.

## Componentes locais reusáveis (`libs/asst/ui`)

`AssetCardComponent`, `AssetTypeChipComponent`, `AssetStateChipComponent`, `VersionTimelineComponent`,
`VersionOrigemBadgeComponent`, `VersionContentViewComponent`, `AssetMetadataFormComponent`.
Candidatos a promoção para `@journeyos/shared/*` (smart-table/approval-widget/timeline) se reusados
por outro módulo (asset-driven-ui) — decisão fica para implement/ADR.

## Regras
- Smart components (Page + Dialogs) consomem facades; presentational são puros (in/out).
- Cada smart component declara explicitamente os signals que lê (listados acima).
- Nenhum componente chama `HttpClient` direto (UINV-2 / access-layer).

## Critérios de aceite (EARS)

> Notação EARS (D-057 / `be-validate-ears.py`). Backfill do gate A2.5. Cláusulas estruturais
> (standalone/OnPush, sem HttpClient em componente) são invariantes de arquitetura (INFO, não-e2e).

- **A-02.1** `THE SYSTEM SHALL render the asset library, detail, studio and approval views as standalone OnPush components that read state from facades.`
- **A-02.2** `IF an approval decision is a rejection, THEN THE SYSTEM SHALL require a non-empty comment before submitting the decision.`
- **A-02.3** `THE SYSTEM SHALL NOT call HttpClient from any component and SHALL route all data access through facades.`

## Referências
- SPEC-03 (view-models) · SPEC-04 (facades) · `02-architecture-blueprint.md` §4
