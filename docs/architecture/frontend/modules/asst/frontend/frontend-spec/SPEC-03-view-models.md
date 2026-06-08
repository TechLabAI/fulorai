# SPEC-03 — View Models — ASST · Frontend

> VMs como contratos de UI (signal shapes) + eventos UI por tela. Refina `03-domain-framing-frontend.md` §2.
> Tipos base abaixo; DTOs do BE mapeados em SPEC-04.

```typescript
// ── Tipos base (espelham o BE; não redefinir o domínio) ───────────────────────
type TipoAsset    = 'LANDING_PAGE' | 'EMAIL' | 'CRIATIVO' | 'ROTEIRO' | 'DOCUMENTO' | 'SCRIPT_SDR';
type EstadoAsset  = 'RASCUNHO' | 'EM_REVISAO' | 'APROVADO' | 'PUBLICADO' | 'REJEITADO' | 'ARQUIVADO';
type OrigemVersao = 'MANUAL' | 'ASSET_STUDIO';
type EstadoVersao = 'RASCUNHO' | 'PUBLICADA';
type StudioState  = 'idle' | 'composing' | 'draft-pronto' | 'degradado';

interface AssetResumoVM { id: string; tipoAsset: TipoAsset; titulo: string; estado: EstadoAsset;
                          tags: string[]; versaoVigenteNumero: number | null; atualizadoEm: string }
interface AssetFiltroVM { tipo?: TipoAsset; estado?: EstadoAsset; tag?: string; q?: string;
                          page: number; size: number }
interface PaginacaoVM   { page: number; size: number; total: number }
interface BinarioRefVM  { url: string; mime: string }
interface VersaoResumoVM{ id: string; numero: number; estado: EstadoVersao; origem: OrigemVersao;
                          criadoEm: string; vigente: boolean }
interface VersaoDetailVM{ id: string; numero: number; conteudo: unknown; binarios: BinarioRefVM[];
                          origem: OrigemVersao; briefComposicao?: string }
interface AssetDetailVM { id: string; tipoAsset: TipoAsset; titulo: string; descricao: string;
                          estado: EstadoAsset; tags: string[]; donoId: string;
                          versaoVigenteId: string | null; versoes: VersaoResumoVM[] }
interface ApprovalItemVM{ assetId: string; titulo: string; tipoAsset: TipoAsset; versaoNumero: number;
                          submetidoEm: string; submetidoPor: string }
interface AprovacaoVM   { revisor: string; decisao: 'APROVADO' | 'REJEITADO'; comentario: string;
                          decididoEm: string }

// ── Forms ─────────────────────────────────────────────────────────────────────
interface NovoAssetForm        { tipoAsset: TipoAsset; titulo: string; descricao: string; tags: string[] }
interface AssetMetadataForm    { titulo: string; descricao: string; tags: string[] }
interface NovaVersaoForm       { conteudo: unknown; binarios: BinarioRefVM[] }
interface StudioComposeForm    { brief: string; contexto: Record<string, unknown>; baseVersaoNumero?: number }
interface ApprovalDecisionForm { decisao: 'APROVADO' | 'REJEITADO'; comentario: string }
```

## VMs por tela (signal shapes)

```typescript
// Catálogo — feature-asset-library
type AssetLibraryVM = {
  catalogo:  Signal<AssetResumoVM[]>;
  paginacao: Signal<PaginacaoVM>;
  filtro:    Signal<AssetFiltroVM>;
  loading:   Signal<boolean>;
  error:     Signal<AppError | null>;
  // eventos UI:
  onFilterChange: (f: AssetFiltroVM) => void;
  onOpen:         (id: string) => void;          // navega para /asst/assets/:id
  onCreate:       (form: NovoAssetForm) => void; // POST / (asst.asset.criar)
};

// Detalhe — feature-asset-detail
type AssetDetailViewVM = {
  asset:             Signal<AssetDetailVM | null>;
  versaoSelecionada: Signal<VersaoDetailVM | null>;
  acoesDisponiveis:  Signal<AssetAcao[]>;        // computed do estado (UINV-5)
  loading:           Signal<boolean>;
  error:             Signal<AppError | null>;
  // eventos UI:
  onSelectVersion: (numero: number) => void;
  onSaveMetadata:  (form: AssetMetadataForm) => void; // PATCH /{id} (asst.asset.editar)
  onCreateVersion: (form: NovaVersaoForm) => void;     // POST /{id}/versoes (asst.asset.editar)
  onSubmit:        () => void;                         // POST /{id}/submit (asst.asset.submeter)
  onPublish:       () => void;                         // POST /{id}/publish (asst.asset.publicar)
  onArchive:       () => void;                         // POST /{id}/arquivar (asst.asset.arquivar)
  onOpenStudio:    () => void;                         // navega para /studio
};
type AssetAcao = 'editar' | 'nova-versao' | 'submeter' | 'aprovar' | 'publicar' | 'arquivar' | 'studio';

// Asset Studio — feature-asset-studio
type AssetStudioVM = {
  studioState:    Signal<StudioState>;
  draftProduzido: Signal<VersaoDetailVM | null>;
  error:          Signal<AppError | null>;
  // eventos UI:
  onCompose:        (form: StudioComposeForm) => void; // POST /{id}/studio/compose (asst.studio.compor)
  onComposeManually:() => void;                         // fallback: abre NewVersionDialog
  onOpenInDetail:   () => void;
};

// Aprovações — feature-approval-workflow
type ApprovalQueueVM = {
  fila:       Signal<ApprovalItemVM[]>;
  itemAberto: Signal<{ item: ApprovalItemVM; versao: VersaoDetailVM } | null>;
  publicando: Signal<boolean>;
  loading:    Signal<boolean>;
  error:      Signal<AppError | null>;
  // eventos UI:
  onOpen:    (assetId: string) => void;
  onDecide:  (form: ApprovalDecisionForm) => void; // POST /{id}/approve (asst.asset.aprovar)
  onPublish: (assetId: string) => void;            // POST /{id}/publish (asst.asset.publicar)
};
```

## Notas
- `acoesDisponiveis` é `computed()` a partir de `asset().estado` + permissões
  (`AccessDecisionService.can()`), garantindo UINV-5 (sem transições inválidas na UI).
- `conteudo: unknown` no MVP (texto/estruturado simples); tipagem por `tipoAsset` é refinamento
  pós-MVP (R-5).
- `AppError` vem de `@journeyos/shared/error-model` (SPEC-07).

## Critérios de aceite (EARS)

> Notação EARS (D-057 / `be-validate-ears.py`). Backfill do gate A2.5. Derivados dos signal shapes +
> `acoesDisponiveis` (UINV-5) e do estado do Studio (StudioState).

- **A-03.1** `THE SYSTEM SHALL compute the available asset actions from the asset state combined with the user permissions.`
- **A-03.2** `WHEN a Studio composition succeeds, THE SYSTEM SHALL expose the produced draft version through the draftProduzido signal.`
- **A-03.3** `WHILE the Studio state is degradado, THE SYSTEM SHALL offer a manual composition path instead of a produced draft.`

## Referências
- `03-domain-framing-frontend.md` §2 · SPEC-02 · SPEC-04 · SPEC-07
