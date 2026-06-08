# SPEC-04 — Data Access — JRNY · Frontend

> Services HTTP + facades de signal + endpoints consumidos. Toda chamada via
> `@journeyos/shared/access-http-base` (JWT + `X-Empresa-Id` automáticos). Espelha
> `jrny-service/contracts/api-contract.md`.

## Tabela mestre

| Resource | Endpoint base | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Journey | `/api/v1/journeys` | `JourneyApiService` | `JourneyListFacade` / `JourneyBuilderFacade` | list, get, create, update, publicar, arquivar, novaVersao | no |
| Stage | `/api/v1/journeys/{id}/estagios` | `StageApiService` | `JourneyBuilderFacade` | list, create, update, reorder | no |
| RoutingRule | `/api/v1/routing/rules` | `RoutingRuleApiService` | `RoutingRulesFacade` | list, create, update | no |
| RoutingQuery | `/api/v1/routing/leads/{leadId}` | `RoutingQueryApiService` | `DecisionLogFacade` | getJourneyState, listDecisions | no |
| JourneyAnalytics | `/api/v1/journeys/analytics` *(proposto — ver gap)* | `JourneyAnalyticsApiService` | `JourneyAnalyticsFacade` | getFunnel | no |

## Journey — `JourneyApiService` / facades

| Op | Método + path | Resposta BE | Notas |
|---|---|---|---|
| list | `GET /api/v1/journeys?estado=&q=&page=&size=` | `Page<JornadaResumo>` | tenant-escopado |
| get | `GET /api/v1/journeys/{id}` | `JornadaResponse` (+ `estagios[]`) | `404 jrny.jornada.nao-encontrada` |
| create | `POST /api/v1/journeys` | `201 JornadaResponse` (RASCUNHO, v1) | `422 nome-obrigatorio` |
| update | `PATCH /api/v1/journeys/{id}` | `JornadaResponse` | `409 transicao-invalida` se ≠ RASCUNHO |
| publicar | `POST /api/v1/journeys/{id}/publicar` | `JornadaResponse` (PUBLICADA) | `422 sem-estagio` · `409 transicao-invalida` |
| arquivar | `POST /api/v1/journeys/{id}/arquivar` | `200` | logical delete |
| novaVersao | `POST /api/v1/journeys/{id}/nova-versao` | `JornadaResponse` (RASCUNHO v+1) | só em PUBLICADA |

## Stage — `StageApiService` (sob `JourneyBuilderFacade`)

| Op | Método + path | Notas |
|---|---|---|
| list | `GET /api/v1/journeys/{id}/estagios` | ordenado por `ordem` |
| create | `POST /api/v1/journeys/{id}/estagios` | `409 ordem-duplicada` · `422 tipo-invalido` · `409 transicao-invalida` |
| update | `PATCH /api/v1/journeys/{id}/estagios/{estagioId}` | nome/asset/terminal/config/ordem |
| reorder | sequência de `PATCH` de `ordem` | **otimista com rollback** (ver SPEC-05/05-state §4) |

## RoutingRule — `RoutingRuleApiService` / `RoutingRulesFacade`

| Op | Método + path | Notas |
|---|---|---|
| list | `GET /api/v1/routing/rules?jornadaId=` | ordenado por `prioridade` |
| create | `POST /api/v1/routing/rules` | `422 condicao-invalida` · `422 estagio-invalido` |
| update | `PATCH /api/v1/routing/rules/{ruleId}` | **bumpa versão**; mantém anterior referenciável |

> `condicao` segue a gramática de snapshot do BE (`data-model.md §5`): combinador `E`/`OU` +
> predicados `{ campo, op, valor }`. Campos: `scoreAgregado`, `dimensoes.<DIM>`, `estadoQualificacao`,
> `segmentoId`, `atributo.<chave>`. Operadores: `= <> > >= < <= in nin existe`.

## RoutingQuery — `RoutingQueryApiService` / `DecisionLogFacade`

| Op | Método + path | Resposta BE | Notas |
|---|---|---|---|
| getJourneyState | `GET /api/v1/routing/leads/{leadId}/journey` | `InscricaoJornadaResponse` | `404 inscricao-nao-encontrada` → `semInscricao` |
| listDecisions | `GET /api/v1/routing/leads/{leadId}/decisions?page=&size=` | `Page<DecisaoRoteamentoResponse>` | newest-first; inclui `SEM_MUDANCA`/`NAO_ROTEADO` |

## Facade pattern

`HttpClient` (via `access-http-base`) em **services**; **facades** expõem `signal<T>` privado +
`.asReadonly()`. Sem `BehaviorSubject`. RxJS só na borda (`firstValueFrom`/`toSignal`). `effect()` na
troca de empresa invalida o estado em tela. A jornada em edição vive no `JourneyBuilderFacade`
enquanto a página está montada.

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL route every JRNY HTTP call through @journeyos/shared/access-http-base so JWT and X-Empresa-Id are attached automatically.`
- `THE SYSTEM SHALL expose journey/rule/decision state to components only as readonly signals from a facade.`
- `WHEN a journey is fetched, THE SYSTEM SHALL request the API on each navigation and SHALL NOT serve a stale cached journey.`
- `WHEN the active empresa changes, THE SYSTEM SHALL invalidate the in-memory JRNY state before loading the new empresa's data.`
- `IF a routing rule edit succeeds, THEN THE SYSTEM SHALL reflect the bumped versão in the rule list.`

## Gap conhecido

- **`JourneyAnalytics`**: o `api-contract.md` atual cobre `/journeys` e `/routing`, mas **não** um
  endpoint de funil/analytics. `GET /api/v1/journeys/analytics` é **proposto** aqui — confirmar com o
  BE (ou derivar de projeção Elastic `journey-events`). Registrado em `contracts/backend-api-cross-link.md`
  e em `06-risks-gaps-assumptions.md`. A feature `journey-analytics` está atrás da flag
  `jrny.journey-analytics` e degrada para estado vazio se o endpoint não existir.

## Referências
- `05-state-and-data-flow.md` · BE `contracts/{api-contract,data-model,event-contracts}.md`
