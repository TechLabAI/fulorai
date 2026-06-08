# 05 — State and Data Flow — SALE · Frontend

> Topologia de estado, padrão de acesso a dados, cache, optimistic updates, erros e breadcrumbs.

## 1. State Topology

- **Local (por feature lib, via facade em `data-access`)** — signals privados + `.asReadonly()`:
  - `feature-pipeline`: `board` (colunas + cards), `filtros`, `movingCardId`, `loading`, `error`.
  - `feature-opportunity`: `oportunidadeSelecionada`, `historico`, `acoes`, `closeState`, `loading`, `error`.
  - `feature-offer`: `ofertas`, `ofertaEmEdicao`, `saving`.
  - `feature-purchase`: `compras`, `compraSelecionada`, `breakdown`, `adjusting`, `loading`, `error`.
  - `feature-attribution`: `modelos`, `modeloAtivo`, `activating`, `breakdownCompra`.
  - `feature-revenue-dashboard`: `funilReceita`, `ltv`, `periodo`, `loading`, `error`.
- **Transversal (NÃO no SALE)** — sessão, empresa ativa e RBAC vivem em `@journeyos/shared/access-*`.
  O SALE **consome** (`AuthSessionService`, `EmpresaContextService`, `AccessDecisionService`) e **reage**
  à troca de empresa (effect que invalida board/seleção/listas em tela).

## 2. Data Access Pattern

- `HttpClient` (via `access-http-base`) encapsulado em services de `data-access`
  (`OportunidadeApiService`, `OfertaApiService`, `CompraApiService`, `AtribuicaoApiService`, `LtvApiService`).
- O service chama a API e **a facade emite signals** — sem `BehaviorSubject` manual.
- Mapeamento de endpoints → facade:
  - `GET /oportunidades` (paged, filtros) → `PipelineFacade.board` (agrupado por estágio na facade).
  - `GET /oportunidades/{id}` (inclui histórico) → `OpportunityFacade.oportunidadeSelecionada` + `.historico`.
  - `PATCH /oportunidades/{id}/estagio` → mover estágio (optimistic — §4).
  - `POST /oportunidades/{id}/ganhar` · `POST /oportunidades/{id}/perder` → fechamento (motivo na perda).
  - `GET/POST /ofertas`, `GET/PUT /ofertas/{id}`, `POST /ofertas/{id}/desativar` → `OfferFacade` (PUT = nova versão).
  - `GET /compras`, `GET /compras/{id}` (itens + breakdown), `POST /compras/{id}/estornar`,
    `POST /compras/{id}/cancelar` → `PurchaseFacade`. **`POST /compras` NÃO é chamado pelo FE** (server-to-server).
  - `GET /atribuicao/modelos`, `POST /atribuicao/modelos`, `POST /atribuicao/modelos/{versao}/activate`,
    `GET /compras/{id}/atribuicao` → `AttributionFacade`.
  - `GET /ltv` (paged, top por valor), `GET /ltv/{contatoRef}` + funil agregado (origem/período) → `RevenueFacade`.

## 3. Cache Strategy

- **Padrão = chamar a API a cada navegação** (board e detalhe sempre frescos — estágio/receita mudam no BE).
- Sem cache persistente no MVP. Exceção justificável: manter o **board** em memória durante a sessão da
  mesma empresa para voltar do detalhe sem refetch — invalidado na troca de empresa (documentar no SPEC
  se adotado).
- O **dashboard de receita** (Elastic-backed) pode usar TTL curto / refetch sob refresh, nunca stale
  silencioso.

## 4. Optimistic Updates

- **Mover estágio no Kanban é o caso optimistic canônico do SALE** (ver `ADR-005`):
  - Ao soltar o card numa coluna, a UI **move o card imediatamente** (signal do `board`) e marca
    `movingCardId`, e dispara `PATCH /oportunidades/{id}/estagio`.
  - **Sucesso** → confirma a posição e atualiza o `estagio`/histórico.
  - **Falha** (ex.: `409 sale.oportunidade.ja-fechada`, rede, `403`) → **rollback**: o card volta para a
    coluna de origem (último estado confirmado) + toast de erro. Nenhum estado inconsistente persiste.
- **Demais ações** (ganhar/perder, estornar/cancelar, ativar modelo, editar oferta): **sem optimistic**
  — o resultado é autoridade do BE (mostrar `submitting`/`adjusting`/`activating` e refetch).
  Estornar/cancelar e ativar modelo têm efeitos colaterais (recálculo de LTV, re-atribuição) que o FE
  só reflete após confirmação.

## 5. Error Handling

- `ProblemDetail` (RFC 7807) do BE → `AppError` via `@journeyos/shared/error-model` → mensagem via
  `@journeyos/shared/ui-feedback`.
- Mapeamentos-chave:
  - `409 sale.oportunidade.ja-fechada` → **rollback** do drag no Kanban + aviso "oportunidade já fechada".
  - `422 sale.oportunidade.motivo-obrigatorio` → erro de formulário no campo "motivo" da perda.
  - `404 sale.oportunidade.nao-encontrada` → estado de erro/404 no detalhe.
  - `422 sale.oferta.preco-invalido` → erro de formulário no campo "preço".
  - `422 sale.compra.base-legal-invalida` / `422 sale.compra.receita-inconsistente` → erro de dados na
    compra (a ingestão é server-to-server; o FE apenas reflete a inconsistência se exibida).
  - `404 sale.compra.nao-encontrada` → erro no detalhe da compra.
  - `404 sale.atribuicao.modelo-nao-encontrado` → erro ao ativar versão de modelo.
  - `409 sale.atribuicao.soma-invalida` → aviso de inconsistência de conservação de receita no breakdown.
  - **Re-ingestão idempotente de compra NÃO é erro** — o BE retorna `duplicada=true`; o FE nunca cria
    duplicado (e nem dispara a ingestão).
- Erros transversais `iam.*` (JWT) são tratados pela Access Layer (redirect/login), não pelo SALE.

## 6. Breadcrumbs e Navigation State

- `libs/sale/navigation` alimenta `BreadcrumbItem[]`:
  - `/sale/pipeline` → `Vendas / Pipeline`
  - `/sale/pipeline/:id` → `Vendas / Pipeline / {tituloOportunidade|id}`
  - `/sale/ofertas` → `Vendas / Ofertas`
  - `/sale/compras` → `Vendas / Compras` (`/compras/:id` → `… / {compraId|contatoRef}`)
  - `/sale/atribuicao` → `Vendas / Atribuição`
  - `/sale/receita` → `Vendas / Receita`
- O menu lateral (deep links do `sale.contract.ts`) é filtrado por permissão via `NavigationService`.

---

## Referências

- `04-frontend-architecture-direction.md` · `03-domain-framing-frontend.md`
- BE: `docs/architecture/backend/services/sale-service/contracts/api-contract.md` (códigos de erro + EARS)
- `docs/architecture/frontend/standards/access-layer-contracts.md` · `ADR-005` (Kanban + optimistic move)
