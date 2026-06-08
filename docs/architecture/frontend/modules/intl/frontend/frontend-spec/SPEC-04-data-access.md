# SPEC-04 — Data Access — INTL

> Services HTTP + facades de signal por recurso. Endpoints espelham
> `intl-service/contracts/api-contract.md`. Interceptors de `@journeyos/shared/access-http-base`
> injetam `Authorization`, `X-Empresa-Id`, `X-Correlation-Id`.

## Tabela mestre

| Resource | Endpoint base | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Conversa | `/api/v1/copilot/conversas` | `CopilotApiService` | `CopilotFacade` | open(create), get, perguntar | conversa corrente em memória |
| NoConhecimento | `/api/v1/knowledge/nos` | `KnowledgeApiService` | `KnowledgeFacade` | list, get, create, update, indexar, arquivar | no |
| Analytics | `/api/v1/analytics` | `AnalyticsApiService` | `AnalyticsFacade` | funil, copilotUsage | no |

## CopilotApiService → CopilotFacade

| Operação | HTTP | Status | Notas |
|---|---|---|---|
| `open(titulo?)` | `POST /copilot/conversas` | 201 | retorna `ConversaResponse` |
| `perguntar(conversaId, texto, topK?)` | `POST /copilot/conversas/{id}/perguntar` | 200 | retorna `RespostaCopilotoResponse { mensagemId, texto, status, citacoes[], modelo?, custoTokens?, latenciaMs }` |
| `get(conversaId)` | `GET /copilot/conversas/{id}` | 200 / 404 | histórico `ConversaDetalheResponse` |

- **Permissões:** `intl.copilot.use` (open/perguntar), `intl.copilot.read` (get).
- **Otimismo (perguntar):** facade insere `MensagemVM(USUARIO)` + bolha `COPILOTO(PENDENTE)`; dispara
  o POST com um `AbortController`. No `200`, substitui a bolha pelo conteúdo + `status`. **Citações só
  são renderizadas no estado final** (nunca em `PENDENTE`).
- **Status semantics:** `RESPONDIDA` (≥1 citação), `NAO_FUNDAMENTADA` (sem evidência), `DEGRADADA`
  (IA off). **Nenhum** vira erro de UI — todos são `200`.
- **Cancelamento:** `abort()` remove as bolhas pendentes; texto volta ao input.

## KnowledgeApiService → KnowledgeFacade

| Operação | HTTP | Status | Notas |
|---|---|---|---|
| `list(filtros)` | `GET /knowledge/nos?q=&tag=&status=&page=&size=` | 200 | `Page<NoConhecimentoResponse>` |
| `get(id)` | `GET /knowledge/nos/{id}` | 200 / 404 | |
| `create(form)` | `POST /knowledge/nos` | 201 | `{ id, status: 'RASCUNHO', versao: 1 }` |
| `update(id, form)` | `PUT /knowledge/nos/{id}` | 200 | incrementa `versao`, dispara reindexação |
| `indexar(id)` | `POST /knowledge/nos/{id}/indexar` | 202 / 503 | 202 → `INDEXADO`; **503 → mantém RASCUNHO + retry** |
| `arquivar(id)` | `DELETE /knowledge/nos/{id}` | 200 | `status: 'ARQUIVADO'` (sem hard-delete) |

- **Permissões:** `intl.knowledge.read` (list/get), `intl.knowledge.write` (create/update/indexar/arquivar).
- **503 (`embedding-unavailable`)** é tratado como **retry**, não erro fatal (SPEC-07).

## AnalyticsApiService → AnalyticsFacade

| Operação | HTTP | Status | Notas |
|---|---|---|---|
| `funil(periodo, granularidade)` | `GET /analytics/funil?periodo=&granularidade=` | 200 | `FunilResponse { etapas[], periodo }` |
| `copilotUsage()` | `GET /analytics/copilot` | 200 | `CopilotUsageResponse { totalRespostas, custoTokens, taxaFundamentadas, taxaDegradadas }` |

- **Permissão:** `intl.analytics.read`. **Read-only** — nenhuma operação de escrita.

## DTOs FE

- Mapeamento direto dos shapes do `api-contract.md`; quando `@journeyos/shared/contracts` expor os
  tipos gerados de OpenAPI, migrar para eles. Por ora, tipos locais em `libs/intl/data-access`.
- Conversão de `RespostaCopilotoResponse` → `MensagemVM` é feita na facade (não no componente).

## Error mapping (resumo — detalhe em SPEC-07)

| BE | FE |
|---|---|
| `503 ai-unavailable` (copilot) | **não ocorre** — BE degrada para `200/DEGRADADA` |
| `503 embedding-unavailable` (indexar) | ação "tentar de novo" (retry), não erro |
| `404 not-found` | empty state + voltar à lista |
| `409 conflict` | "este nó está sendo indexado; recarregue" |
| `403 forbidden` | guard oculta rota; banner em runtime |

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL route every INTL HTTP call through the shared access-http-base so Authorization, X-Empresa-Id and X-Correlation-Id are attached.`
- `WHEN the user sends a question, THE SYSTEM SHALL optimistically insert a USUARIO message and a PENDENTE COPILOTO bubble and dispatch the request with an AbortController.`
- `WHEN a copilot response returns 200, THE SYSTEM SHALL replace the pending bubble with the content and its status.`
- `WHEN the user cancels a pending question, THE SYSTEM SHALL abort the request, remove the pending bubbles and restore the text to the input.`
- `IF the indexar action returns 503 embedding-unavailable, THEN THE SYSTEM SHALL keep the node RASCUNHO and SHALL present a retry instead of an error.`
- `WHILE a copilot answer status is DEGRADADA or NAO_FUNDAMENTADA, THE SYSTEM SHALL treat it as a 200 response state and SHALL NOT render an error.`
