# SPEC-04 — Data Access — SALE · Frontend

> Services HTTP + facades de signal + endpoints consumidos. Toda chamada via
> `@journeyos/shared/access-http-base` (JWT + `X-Empresa-Id` automáticos). Espelha
> `sale-service/contracts/api-contract.md`.

## Tabela mestre

| Resource | Endpoint base | Service | Facade | Operations | Cache? |
|---|---|---|---|---|---|
| Oportunidade | `/api/v1/oportunidades` | `OportunidadeApiService` | `PipelineFacade` / `OpportunityDetailFacade` | list, get, create, moverEstagio, ganhar, perder | no |
| Oferta | `/api/v1/ofertas` | `OfertaApiService` | `OfferListFacade` / `OfferDetailFacade` | list, get, create, editar, desativar | no |
| Compra | `/api/v1/compras` | `CompraApiService` | `PurchaseListFacade` / `PurchaseDetailFacade` | list, get, estornar, cancelar | no |
| Atribuicao | `/api/v1/atribuicao/modelos` | `AtribuicaoApiService` | `AttributionFacade` | list, criar, ativar, getBreakdown | no |
| Ltv | `/api/v1/ltv` | `LtvApiService` | `RevenueDashboardFacade` | getByContato, list | no |

## Oportunidade — `OportunidadeApiService` / facades

| Op | Método + path | Resposta BE | Notas |
|---|---|---|---|
| list | `GET /api/v1/oportunidades?estagio=&responsavel=&estado=&page=&size=` | `Page<OportunidadeResumo>` | tenant-escopado; fonte do board |
| get | `GET /api/v1/oportunidades/{id}` | `OportunidadeResponse` (+ `historicoEstagio[]`) | `404 sale.oportunidade.nao-encontrada` |
| create | `POST /api/v1/oportunidades` | `201` (estado NOVA) | perm `sale.oportunidade.criar` |
| moverEstagio | `PATCH /api/v1/oportunidades/{id}/estagio` | `200` (+ histórico) | **otimista com rollback**; `409 ja-fechada` em deal terminal |
| ganhar | `POST /api/v1/oportunidades/{id}/ganhar` | `200` (estado GANHA) | `409 sale.oportunidade.ja-fechada` |
| perder | `POST /api/v1/oportunidades/{id}/perder` | `200` (estado PERDIDA) | `422 motivo-obrigatorio` se sem `motivo`; `409 ja-fechada` |

## Oferta — `OfertaApiService` / facades

| Op | Método + path | Notas |
|---|---|---|
| list | `GET /api/v1/ofertas?q=&ativo=&page=&size=` | catálogo paginado |
| get | `GET /api/v1/ofertas/{id}` | inclui versões |
| create | `POST /api/v1/ofertas` | perm `sale.oferta.criar` |
| editar | `PUT /api/v1/ofertas/{id}` | **cria nova versão**; mantém anteriores imutáveis; `422 preco-invalido` |
| desativar | `POST /api/v1/ofertas/{id}/desativar` | perm `sale.oferta.desativar` |

## Compra — `CompraApiService` / facades

| Op | Método + path | Resposta BE | Notas |
|---|---|---|---|
| list | `GET /api/v1/compras?contato=&status=&periodo=&page=&size=` | `Page<CompraResumo>` | filtros server-side |
| get | `GET /api/v1/compras/{id}` | `CompraResponse` (+ `itens[]` + breakdown) | `404 sale.compra.nao-encontrada` |
| estornar | `POST /api/v1/compras/{id}/estornar` | `200` (status ESTORNADA) | recalcula receita/LTV; não apaga histórico |
| cancelar | `POST /api/v1/compras/{id}/cancelar` | `200` (status CANCELADA) | recalcula receita/LTV; não apaga histórico |

> **Sem `create` no FE** — `POST /compras` (`sale.compra.registrar`) é ingestão **server-to-server**
> idempotente (`Idempotency-Key`/`(id_externo, origem)`), mediada por GWY/integração. O FE só **consulta** e ajusta.

## Atribuicao — `AtribuicaoApiService` / `AttributionFacade`

| Op | Método + path | Notas |
|---|---|---|
| list | `GET /api/v1/atribuicao/modelos` | versões; identifica a ativa |
| criar | `POST /api/v1/atribuicao/modelos` | nasce **inativa** (nova versão) |
| ativar | `POST /api/v1/atribuicao/modelos/{versao}/activate` | **re-atribui** compras afetadas; desativa anterior; `404 modelo-nao-encontrado`; `409 soma-invalida` |
| getBreakdown | `GET /api/v1/compras/{id}/atribuicao` | breakdown de uma compra (touchpoint + versão modelo) |

> Enquanto nenhum modelo está ativo, o BE usa **LAST_TOUCH** para novas compras (`WHILE` invariant) —
> a UI reflete isso no badge de modelo efetivo.

## Ltv — `LtvApiService` / `RevenueDashboardFacade`

| Op | Método + path | Resposta BE | Notas |
|---|---|---|---|
| getByContato | `GET /api/v1/ltv/{contatoRef}` | `LtvResponse` | LTV determinístico de compras CONFIRMADA |
| list | `GET /api/v1/ltv?page=&size=` | `Page<LtvResumo>` | top contatos por `valor_total` desc (default) |

> O **funil de receita por origem/período** do dashboard é apoiado em projeção Elastic
> (`revenue-events`/`campaign-events`). Endpoint exato é **proposto** — ver gap G1 (cross-link).

## Facade pattern

`HttpClient` (via `access-http-base`) em **services**; **facades** expõem `signal<T>` privado +
`.asReadonly()`. Sem `BehaviorSubject`. RxJS só na borda (`firstValueFrom`/`toSignal`). `effect()` na
troca de empresa invalida o estado em tela. O **pipeline em edição** (board + `movingCardId`) vive no
`PipelineFacade` enquanto a página está montada; o move otimista guarda o **snapshot** do último estado
confirmado para rollback (ADR-005).

## Critérios de aceite (EARS)

- `THE SYSTEM SHALL route every SALE HTTP call through @journeyos/shared/access-http-base so JWT and X-Empresa-Id are attached automatically.`
- `THE SYSTEM SHALL expose pipeline/offer/purchase/attribution/ltv state to components only as readonly signals from a facade.`
- `WHEN a stage move PATCH fails, THE SYSTEM SHALL roll back the optimistic move to the last confirmed snapshot.`
- `THE SYSTEM SHALL NOT expose any create-compra operation in the FE because purchase ingestion is server-to-server.`
- `WHEN the active empresa changes, THE SYSTEM SHALL invalidate the in-memory SALE state before loading the new empresa's data.`

## Gap conhecido

- **`RevenueDashboard` funil por origem/período**: o `api-contract.md` cobre `/ltv` (top contatos), mas
  **não** um endpoint de funil de receita por origem/período. `GET /api/v1/receita/funil` é **proposto**
  aqui — confirmar com o BE (ou derivar de projeção Elastic `revenue-events`/`campaign-events`).
  Registrado em `contracts/backend-api-cross-link.md` (G1) e em `06-risks-gaps-assumptions.md`. A feature
  `revenue-dashboard` está atrás da flag `sale.revenue-dashboard` e degrada para LTV-apenas/estado vazio
  se o endpoint de funil não existir.

## Referências
- `05-state-and-data-flow.md` · BE `contracts/{api-contract,data-model}.md`
