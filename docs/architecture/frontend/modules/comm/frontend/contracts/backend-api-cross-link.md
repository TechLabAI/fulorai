# Backend API Cross-Link — COMM (FE ↔ `comm-service`)

> O FE COMM consome **apenas** o `comm-service`. Fonte da verdade dos contratos:
> `docs/architecture/backend/services/comm-service/contracts/api-contract.md`.
> Este documento lista o subconjunto consumido pelo FE e eventuais diffs/gaps.

## Base

- Base path: `/api/v1`. Auth: Bearer JWT (WRKS). Tenant via claim `empresa_id` (`X-Empresa-Id` é
  debug/log; nunca sobrepõe o claim). Erros: RFC 7807 (`application/problem+json`).
- Idempotência: `Idempotency-Key` em `POST /messages` e `POST /templates/{id}/studio/compose`.

## Endpoints consumidos pelo FE

| Método · Path | Perm | Consumido por (FE) |
|---|---|---|
| `POST /templates` | `comm.template.criar` | `TemplateApiService.create` |
| `GET /templates` | `comm.template.ler` | `TemplateApiService.list` (catálogo) |
| `GET /templates/{id}` | `comm.template.ler` | `TemplateApiService.get` (editor) |
| `PATCH /templates/{id}` | `comm.template.editar` | `TemplateApiService.update` |
| `POST /templates/{id}/ativar` | `comm.template.publicar` | `TemplateApiService.activate` |
| `POST /templates/{id}/arquivar` | `comm.template.arquivar` | `TemplateApiService.archive` |
| `POST /templates/{id}/studio/compose` | `comm.studio.compor` | `StudioApiService.compose` (+ `Idempotency-Key`) |
| `POST /messages` | `comm.mensagem.enviar` | `MessageApiService.dispatch` (+ `Idempotency-Key`) |
| `GET /messages` | `comm.mensagem.ler` | `MessageApiService.list` |
| `GET /messages/{id}` | `comm.mensagem.ler` | `MessageApiService.get` (polling) |
| `GET /messages/{id}/events` | `comm.mensagem.ler` | `MessageApiService.listEvents` (timeline) |
| `POST /routing-rules` | `comm.roteamento.criar` | `RoutingApiService.create` |
| `GET /routing-rules` · `GET /routing-rules/{id}` | `comm.roteamento.ler` | `RoutingApiService.list/get` |
| `PATCH /routing-rules/{id}` | `comm.roteamento.editar` | `RoutingApiService.update` |
| `POST /channels` | `comm.canal.configurar` | `ChannelApiService.create` |
| `GET /channels` | `comm.canal.ler` | `ChannelApiService.list` |
| `PATCH /channels/{id}` | `comm.canal.configurar` | `ChannelApiService.update` |

## NÃO consumido pelo FE

- `POST /webhooks/{canal}` — **server-to-server** (callbacks de provedor); sem UI. O FE apenas vê o
  efeito (avanço do estado de entrega) via `GET /messages/{id}` (+ `/events`).

## Diffs / Gaps a confirmar com o BE

- **OpenAPI ausente**: DTOs FE escritos à mão a partir do `api-contract.md` até o BE expor OpenAPI
  consumível (`@journeyos/shared/contracts`).
- **Seleção de asset de origem** (`assetOrigemId`): o `api-contract` aceita o campo, mas a forma de
  **buscar/escolher** um asset publicado no FE não está especificada — confirmar se via endpoint do
  `comm-service` (preferido, mantém boundary) ou consulta ao `asst-service`.
- **`janelaEnvio`** (config de canal): formato/semântica da janela horária a confirmar no BE.
- **Paginação**: `GET /templates` e `GET /messages` usam `Page<...>` (`page`/`size`); confirmar tamanho
  default e campos de ordenação.

## Referências

- BE: `docs/architecture/backend/services/comm-service/contracts/api-contract.md`
- BE: `comm-service/spec/backend/SPEC-02-message-dispatch-lifecycle.md`, `SPEC-03-channel-routing.md`
- `shared/contratos/error-model.md`
