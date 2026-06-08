# Backend API Cross-Link — ASST · Frontend

> Liga o FE ASST ao contrato REST do `asst-service` e registra diferenças/assunções. **Fonte da
> verdade:** `docs/architecture/backend/services/asst-service/contracts/api-contract.md`.
> O FE **não redefine** o contrato — apenas o consome via `@journeyos/shared/access-http-base`.

## Fonte BE

- **Contrato:** `docs/architecture/backend/services/asst-service/contracts/api-contract.md`
- **Base path:** `/api/v1/assets`
- **Auth:** Bearer JWT (RS256) emitido pelo WRKS; `empresa_id` via claim do JWT (não no path/body).
  `X-Empresa-Id` é debug/log apenas (o interceptor o injeta; o BE usa o claim).
- **Erros:** `application/problem+json` (RFC 7807), `code` `asst.*` (ver SPEC-07).
- **Idempotência:** `Idempotency-Key` em composição/publish (Asset Studio usa).

## Mapa endpoint → consumo FE

| Endpoint BE | Método | Perm | Service/Facade FE | Tela |
|---|---|---|---|---|
| `/api/v1/assets` | GET | `asst.asset.ler` | `AssetApiService.list` / `AssetCatalogFacade` | catálogo |
| `/api/v1/assets` | POST | `asst.asset.criar` | `AssetApiService.create` / `AssetCatalogFacade` | novo asset |
| `/api/v1/assets/{id}` | GET | `asst.asset.ler` | `AssetApiService.get` / `AssetDetailFacade` | detalhe |
| `/api/v1/assets/{id}` | PATCH | `asst.asset.editar` | `AssetApiService.update` / `AssetDetailFacade` | editar metadados |
| `/api/v1/assets/{id}/arquivar` | POST | `asst.asset.arquivar` | `AssetApiService.archive` | detalhe |
| `/api/v1/assets/{id}/versoes` | GET/POST | `asst.asset.ler` / `editar` | `VersaoApiService` / `AssetDetailFacade` | versões |
| `/api/v1/assets/{id}/versoes/{numero}` | GET | `asst.asset.ler` | `VersaoApiService.get` | conteúdo da versão |
| `/api/v1/assets/{id}/published` | GET | `asst.asset.ler` | `VersaoApiService.getPublished` | versão vigente |
| `/api/v1/assets/{id}/studio/compose` | POST | `asst.studio.compor` | `StudioApiService.compose` / `AssetStudioFacade` | Asset Studio |
| `/api/v1/assets/{id}/submit` | POST | `asst.asset.submeter` | `WorkflowApiService.submit` / `ApprovalFacade` | detalhe |
| `/api/v1/assets/{id}/approve` | POST | `asst.asset.aprovar` | `WorkflowApiService.approve` / `ApprovalFacade` | aprovações |
| `/api/v1/assets/{id}/publish` | POST | `asst.asset.publicar` | `WorkflowApiService.publish` / `ApprovalFacade` | aprovações/detalhe |

## Diffs / assunções FE (a validar quando o OpenAPI do BE estabilizar)

- **DTOs:** o FE espelha `AssetResponse`, `AssetResumo`, `VersaoAssetResponse`, `Aprovacao` com tipos
  locais em `libs/asst/data-access` até `@journeyos/shared/contracts` (gerado de OpenAPI) existir.
- **`conteudo` da versão:** tipado como `unknown` no FE (MVP); o BE define a estrutura por `tipoAsset`
  — refinamento pós-MVP (R-5).
- **Fila de aprovação:** o FE deriva via `GET /?estado=EM_REVISAO` (não há endpoint dedicado no
  contrato atual); confirmar se o BE exporá um endpoint `/approvals` dedicado.
- **`getPublished` 404:** `asst.asset.sem-versao-publicada` é estado normal de UI (banner), não erro.
- **Asset Studio síncrono:** o contrato é síncrono (`201`/`503`); o FE assume isso (ADR-005). Se o BE
  migrar para async/job, exigirá revisão (novo ADR + SPEC-04).
- **`X-Empresa-Id`:** injetado pelo interceptor; o FE nunca o usa para decisão (só o BE, via claim).

## Gaps
- OpenAPI do `asst-service` ainda não materializado → `data-access` tipado à mão até lá (R-1).
- `integrations/techlab-ai/openapi.json` vazio (P3) — não bloqueia o FE (FE→BE, não FE→TechLab AI).

## Referências
- BE: `asst-service/contracts/api-contract.md` · `techlab-ai-integration.md`
- SPEC-04 (data-access) · SPEC-07 (erros) · `06-risks-gaps-assumptions.md`
