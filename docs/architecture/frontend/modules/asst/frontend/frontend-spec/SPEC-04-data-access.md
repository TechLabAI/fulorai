# SPEC-04 — Data Access — ASST · Frontend

> Services (`*ApiService`) + facades (signals) + endpoints consumidos do `asst-service`.
> Fonte BE: `docs/architecture/backend/services/asst-service/contracts/api-contract.md`.
> Todo HTTP passa por `@journeyos/shared/access-http-base` (interceptor injeta JWT + `X-Empresa-Id`).

## Tabela mestre

| Resource | Endpoint | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Asset | `GET/POST /api/v1/assets`, `GET/PATCH /{id}`, `POST /{id}/arquivar` | `AssetApiService` | `AssetCatalogFacade` | list, get, create, update, archive | catálogo: revalida ao voltar |
| Versão | `GET/POST /api/v1/assets/{id}/versoes`, `GET /{id}/versoes/{numero}`, `GET /{id}/published` | `VersaoApiService` | `AssetDetailFacade` | list, get, create, getPublished | versão por id: sim (imutável) |
| Studio | `POST /api/v1/assets/{id}/studio/compose` | `StudioApiService` | `AssetStudioFacade` | compose | no |
| Workflow | `POST /{id}/submit`, `POST /{id}/approve`, `POST /{id}/publish` | `WorkflowApiService` | `ApprovalFacade` | submit, approve, publish, listQueue | no |

## Detalhe por resource

### Asset — `AssetApiService` → `AssetCatalogFacade`
- `list(filtro: AssetFiltroVM): Observable<Page<AssetResumo>>` → `GET /?tipo=&estado=&tag=&q=&page=&size=`
  - `200 Page<AssetResumo>`. `q` resolve via Elastic no BE (fallback PG); o FE só passa a query.
- `get(id): Observable<AssetResponse>` → `GET /{id}` (`404 asst.asset.nao-encontrado`).
- `create(form: NovoAssetForm): Observable<AssetResponse>` → `POST /` (`201`; `422` titulo/tipo).
- `update(id, form: AssetMetadataForm): Observable<AssetResponse>` → `PATCH /{id}`.
- `archive(id): Observable<void>` → `POST /{id}/arquivar`.
- **Facade signals:** `catalogo`, `paginacao`, `filtro`, `loading`, `error`. Escopado por empresa;
  invalidado na troca (ADR-005).

### Versão — `VersaoApiService` → `AssetDetailFacade`
- `list(assetId): Observable<VersaoAssetResponse[]>` → `GET /{id}/versoes`.
- `get(assetId, numero): Observable<VersaoAssetResponse>` → `GET /{id}/versoes/{numero}`.
- `create(assetId, form: NovaVersaoForm): Observable<VersaoAssetResponse>` → `POST /{id}/versoes`
  (`201`, `origem=MANUAL`; `409 asst.versao.imutavel` se tentar mutar existente — a UI já previne, UINV-4).
- `getPublished(assetId): Observable<VersaoAssetResponse>` → `GET /{id}/published`
  (`404 asst.asset.sem-versao-publicada`).
- **Facade signals:** `asset`, `versoes`, `versaoSelecionada`, `acoesDisponiveis` (computed), `loading`, `error`.
- **Cache:** conteúdo de uma versão por id é cacheável (imutável); só `versaoVigenteId` muda ao publicar.

### Studio — `StudioApiService` → `AssetStudioFacade`
- `compose(assetId, form: StudioComposeForm, idempotencyKey?): Observable<VersaoAssetResponse>`
  → `POST /{id}/studio/compose` (`201`, `origem=ASSET_STUDIO`, estado `RASCUNHO`).
  - `503 asst.studio.ia-indisponivel` → **degradação graciosa** (não cria versão; `studioState='degradado'`).
  - `Idempotency-Key` evita dupla composição em replay.
- **Facade signals:** `studioState` (`idle|composing|draft-pronto|degradado`), `draftProduzido`, `error`.
- **Boundary:** chama **somente** o BE; nunca a TechLab AI (ADR-005, UINV-7).

### Workflow — `WorkflowApiService` → `ApprovalFacade`
- `submit(assetId, versaoNumero): Observable<AssetResponse>` → `POST /{id}/submit`
  (`RASCUNHO→EM_REVISAO`; `409 asst.estado.transicao-invalida`).
- `approve(assetId, form: ApprovalDecisionForm): Observable<AssetResponse>` → `POST /{id}/approve`
  (`APROVADO`/`REJEITADO`; persiste `aprovacao`; `409` fora de `EM_REVISAO`).
- `publish(assetId): Observable<AssetResponse>` → `POST /{id}/publish`
  (`APROVADO→PUBLICADO`, atualiza `versaoVigenteId`; `409` fora de `APROVADO`).
- `listQueue(): Observable<Page<AssetResumo>>` → `GET /?estado=EM_REVISAO` (fila de aprovação).
- **Facade signals:** `fila`, `itemAberto`, `publicando`, `loading`, `error`.

## DTOs FE
- Mapeiam os responses do BE (`AssetResponse`, `AssetResumo`, `VersaoAssetResponse`, `Aprovacao`) para
  os VMs do SPEC-03. Quando `@journeyos/shared/contracts` (gerado de OpenAPI) existir, os tipos virão
  de lá; até então, tipos locais em `libs/asst/data-access` espelham o `api-contract.md`.

## Padrão (todos os services)
```
Component → Facade (signal<T> privado + .asReadonly()) → *ApiService (HttpClient via access-http-base) → GWY → asst-service
```
Sem `BehaviorSubject` manual; `Observable` convertido para signal na facade (ADR-002). Sem otimismo
em mutações (criar/submeter/aprovar/publicar/compor) — `loading` + confirmação (SPEC-07).

## Critérios de aceite (EARS)

> Notação EARS (D-057 / `be-validate-ears.py`). Backfill do gate A2.5. Derivados dos endpoints +
> facades + escopo por empresa (ADR-005) + degradação do Studio (UINV-7) + imutabilidade de versão (UINV-4).

- **A-04.1** `WHEN the catalog list request succeeds, THE SYSTEM SHALL display only the assets scoped to the active empresa.`
- **A-04.2** `WHEN the active empresa changes, THE SYSTEM SHALL invalidate the previously loaded catalog before rendering.`
- **A-04.3** `IF a user requests an asset that belongs to another empresa, THEN THE SYSTEM SHALL NOT grant access to its detail.`
- **A-04.4** `WHEN a Studio compose request returns the ia-indisponivel error, THE SYSTEM SHALL NOT create a version and SHALL set the Studio state to degradado.`
- **A-04.5** `IF a user attempts to edit a published version, THEN THE SYSTEM SHALL prevent the mutation and SHALL keep the published version immutable.`
- **A-04.6** `WHEN an asset is published, THE SYSTEM SHALL update the asset vigente version to the newly published version.`
- **A-04.7** `THE SYSTEM SHALL NOT apply optimistic updates to create, submit, approve, publish or compose operations and SHALL show a loading state until the BE confirms.`
- **A-04.8** `THE SYSTEM SHALL route every asset HTTP request through the shared access-http-base so the JWT and X-Empresa-Id headers are attached.`
- **A-04.9** `WHEN the approval queue loads, THE SYSTEM SHALL list only the assets in the EM_REVISAO state.`
- **A-04.10** `WHEN a reviewer approves a submitted asset, THE SYSTEM SHALL move that asset to the APROVADO state.`

## Referências
- BE: `asst-service/contracts/api-contract.md` · `05-state-and-data-flow.md` · SPEC-07
- `docs/architecture/frontend/standards/access-layer-contracts.md`
