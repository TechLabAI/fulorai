# Backend API Cross-Link — SALE (FE ↔ sale-service)

> Liga o FE SALE ao contrato REST do `sale-service`. O FE **não redefine** contratos — referencia.
> Fonte da verdade: `docs/architecture/backend/services/sale-service/contracts/api-contract.md` +
> `data-model.md`.

## Superfície consumida

| Área | Base path | Permissões | Consumido por (FE) |
|---|---|---|---|
| Oportunidades (pipeline) | `/api/v1/oportunidades` | `sale.oportunidade.*` (read/criar/mover/fechar) | `feature-pipeline`, `feature-opportunity` |
| Ofertas (catálogo) | `/api/v1/ofertas` | `sale.oferta.*` (read/criar/editar/desativar) | `feature-offer` |
| Compras (receita) | `/api/v1/compras` | `sale.compra.read/estornar/cancelar` | `feature-purchase` |
| Atribuição | `/api/v1/atribuicao/modelos` · `/compras/{id}/atribuicao` | `sale.atribuicao.*` (read/criar/ativar) | `feature-attribution`, `feature-purchase` |
| LTV | `/api/v1/ltv` | `sale.ltv.read` | `feature-revenue-dashboard` |

> **`POST /compras`** (`sale.compra.registrar`) **não** é consumido pelo FE — ingestão server-to-server
> idempotente (`(id_externo, origem)` / `Idempotency-Key`) mediada por GWY/integração. O FE só consulta e ajusta.

## Enums espelhados (do `data-model.md`)

- `estado` (oportunidade): `NOVA` · `EM_ANDAMENTO` · `GANHA` · `PERDIDA` · `DESCARTADA`
- `estagio` (oportunidade): **configurável** por tenant (ex.: `NOVA → CONTATO → PROPOSTA → GANHA/PERDIDA`)
- `status` (compra): `CONFIRMADA` · `ESTORNADA` · `CANCELADA`
- `base_legal` (compra): `CONSENTIMENTO` · `LEGITIMO_INTERESSE` · `EXECUCAO_CONTRATO` · `OBRIGACAO_LEGAL`
- `tipo` (modelo de atribuição): `LAST_TOUCH` · `FIRST_TOUCH` · `LINEAR`
- `tipo_touchpoint` (atribuição): `ORIGEM_LEAD` · `JORNADA` · `CAMPANHA` · `DIRETO`

## Invariantes de UI espelhadas (do api-contract / data-model)

- **Fechamento terminal:** deal `GANHA`/`PERDIDA` não reabre/move (`409 sale.oportunidade.ja-fechada`).
- **Perder exige motivo:** `422 sale.oportunidade.motivo-obrigatorio`.
- **Oferta versionada:** editar **cria nova versão**; anteriores imutáveis.
- **Idempotência de compra:** re-ingestão não é erro (`duplicada=true`) — irrelevante ao FE (sem create).
- **Conservação de receita:** Σ `atribuicao.valor_atribuido` = `compra.valor_total` (exibido no breakdown).
- **Modelo de atribuição:** no máximo 1 ativo; ativar **re-atribui**; sem ativo → fallback **LAST_TOUCH**.
- **LTV determinístico:** soma de compras `CONFIRMADA`; `ESTORNADA`/`CANCELADA` excluídas.

## Mapa de `error.code` → FE (resumo; detalhe em SPEC-07)

| error.code | HTTP | Apresentação FE |
|---|---|---|
| `sale.oportunidade.motivo-obrigatorio` | 422 | inline (motivo) |
| `sale.oportunidade.ja-fechada` | 409 | rollback Kanban + toast / banner detalhe |
| `sale.oportunidade.nao-encontrada` | 404 | estado vazio |
| `sale.oferta.preco-invalido` | 422 | inline (preço) |
| `sale.compra.base-legal-invalida` | 422 | banner detalhe (informativo) |
| `sale.compra.receita-inconsistente` | 422 | banner detalhe (informativo) |
| `sale.compra.nao-encontrada` | 404 | estado vazio |
| `sale.atribuicao.modelo-nao-encontrado` | 404 | inline (linha do modelo) |
| `sale.atribuicao.soma-invalida` | 409 | banner (atribuição) |

## Diffs / gaps (FE precisa, BE ainda não expõe)

| # | Item | Situação | Encaminhamento |
|---|---|---|---|
| G1 | **Funil de receita por origem/período** (`feature-revenue-dashboard`) | `api-contract.md` cobre `/ltv` (top contatos), **não** um funil de receita por origem/período. | `GET /api/v1/receita/funil` **proposto** (SPEC-04). Confirmar com BE ou derivar de projeção Elastic `revenue-events`/`campaign-events`. Feature atrás da flag `sale.revenue-dashboard`; degrada para LTV-apenas/vazio. |
| G2 | **Título legível do card** (`OpportunityCardVm.titulo`) | `oportunidade` referencia `lead_id`/oferta por id; o nome do lead/oferta não vem no resumo. | FE compõe `titulo` a partir do que o resumo trouxer; senão mostra id/ref no MVP. Confirmar se o BE enriquece o resumo (cross-link LEAD/oferta). |
| G3 | **Nome do responsável** (`responsavelNome`) | `responsavel_id` é id (WRKS). O `OportunidadeResponse` não traz o nome. | FE resolve via WRKS quando disponível; senão mostra id no MVP. |
| G4 | **Touchpoints multi-touch configuráveis** | MVP determinístico last-touch; modelos `FIRST_TOUCH`/`LINEAR` existem no enum mas a config multi-touch é pós-MVP. | Atrás da flag `sale.attribution-multitouch` (default `disabled`). |

> Nenhum gap **bloqueia** o scaffold (A4) — G1/G2/G3 viram entrada de backlog (A3). A UI degrada
> graciosamente (funil vazio; título/responsável = id) até o BE fechar os contratos.

## Referências
- BE: `sale-service/contracts/{api-contract,data-model}.md`
- `SPEC-04-data-access.md` (gap G1) · `SPEC-07-error-handling.md` · `06-risks-gaps-assumptions.md`
