# SPEC-04 — Data Access — COMM · Frontend

> Services (`HttpClient` via `@journeyos/shared/access-http-base`) + facades (signals). Componentes
> consomem **apenas facades** (UINV-5). Endpoints espelham `comm-service/contracts/api-contract.md`.

## Tabela mestre

| Resource | Endpoint(s) | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Template | `GET/POST /api/v1/templates`, `GET/PATCH /api/v1/templates/{id}`, `POST /api/v1/templates/{id}/{ativar,arquivar}` | `TemplateApiService` | `TemplateCatalogFacade` | list, get, create, update, activate, archive | no |
| Studio | `POST /api/v1/templates/{id}/studio/compose` (+ `Idempotency-Key`) | `StudioApiService` | `TemplateStudioFacade` | compose | no |
| RoutingRule | `GET/POST /api/v1/routing-rules`, `GET/PATCH /api/v1/routing-rules/{id}` | `RoutingApiService` | `RoutingFacade` | list, get, create, update | no |
| Message | `POST /api/v1/messages` (+ `Idempotency-Key`), `GET /api/v1/messages`, `GET /api/v1/messages/{id}`, `GET /api/v1/messages/{id}/events` | `MessageApiService` | `MessageFacade` | dispatch, list, get, listEvents | events em memória durante o detalhe |
| Channel | `GET/POST /api/v1/channels`, `PATCH /api/v1/channels/{id}` | `ChannelApiService` | `ChannelFacade` | list, create, update | no |

## DTOs FE (mapeamento do BE)

- `TemplateResponse`/`TemplateResumo` → `TemplateVM`/`TemplateResumoVM` (SPEC-03).
- `MensagemResponse`/`MensagemResumo` → `MensagemVM`/`MensagemResumoVM`; `List<EventoEntregaResponse>` → `EventoEntregaVM[]`.
- `RegraRoteamentoResponse` → `RegraRoteamentoVM`.
- `ConfigCanalResponse` → `ConfigCanalVM` (com `credencialRefMascarada`; o segredo nunca trafega).
- Até o BE expor OpenAPI/`@journeyos/shared/contracts`, os DTOs são escritos à mão (gap em `06`).

## Operações com semântica especial

- **`MessageFacade.dispatch(req)`** — envia `Idempotency-Key` (gerado por intenção de disparo); resposta `202` (ou `200` em replay) cria/retorna a `MensagemVM` (sem otimismo — SPEC-03/05).
- **`MessageFacade.startPolling(id)` / `stopPolling()`** — ADR-005: `interval` RxJS com backoff reconsulta `get(id)` (+ `listEvents` quando há avanço), atualiza signals; encerra em `estadoTerminal` ou no destroy. RxJS confinado à facade.
- **`TemplateStudioFacade.compose(req)`** — envia `Idempotency-Key`; `200` → `draft-pronto`; `503` → `degradado` (corpo inalterado).
- **`TemplateCatalogFacade.activate/archive(id)`** — transições determinísticas; atualização otimista leve do chip com rollback (SPEC-07).

## Critérios de aceite (EARS)

- **C-04.1 (Ubiquitous):** `THE SYSTEM SHALL realizar toda chamada HTTP via access-http-base com JWT e X-Empresa-Id e X-Correlation-Id injetados por interceptor`
- **C-04.2 (Ubiquitous):** `THE SYSTEM SHALL impedir que componentes acessem o HttpClient diretamente permitindo apenas o acesso via facades`
- **C-04.3 (Event-driven):** `WHEN um disparo é solicitado, THE SYSTEM SHALL incluir um Idempotency-Key na requisição POST de mensagem`
- **C-04.4 (Unwanted):** `IF o mesmo Idempotency-Key é reenviado, THEN THE SYSTEM SHALL refletir a mensagem existente sem criar um novo disparo`
- **C-04.5 (State-driven):** `WHILE a mensagem aberta não está em estado terminal, THE SYSTEM SHALL reconsultar o estado por polling com backoff`
- **C-04.5b (Event-driven):** `WHEN a mensagem aberta atinge estado terminal, THE SYSTEM SHALL encerrar o polling`
- **C-04.6 (Ubiquitous):** `THE SYSTEM SHALL nunca solicitar exibir ou persistir o segredo de provedor expondo apenas a credencialRef`
- **C-04.7 (Event-driven):** `WHEN a empresa ativa muda, THE SYSTEM SHALL invalidar os signals de COMM e encerrar qualquer polling em curso antes de recarregar`

## Referências

- BE: `comm-service/contracts/api-contract.md` · `contracts/backend-api-cross-link.md`
- `05-state-and-data-flow.md` · ADR-002 (signals) · ADR-005 (polling)
