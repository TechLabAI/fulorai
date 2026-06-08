# API Contract — SALE (`/api/v1/oportunidades/**`, `/ofertas`, `/compras`, `/atribuicao`, `/ltv`)

> REST surface of `sale-service`. All error responses use `application/problem+json` (RFC 7807,
> `shared/contratos/error-model.md`). EARS invariants per endpoint.
> Guide: `docs/architecture/backend/standards/ears-notation.md`.

## Conventions

- Base path: `/api/v1`.
- Auth: Bearer JWT (RS256) issued by WRKS; validated via WRKS JWKS. No anonymous endpoints except
  `/actuator/health`. The checkout/gateway purchase ingestion (`POST /compras`) is mediated by
  GWY/integration with a **service token** — never anonymous on SALE.
- Tenant: `empresa_id` travels as a JWT claim → `EmpresaContextHolder`. `X-Empresa-Id` accepted for
  debug/log only; never overrides the claim.
- Mandatory headers: `Authorization`, `X-Correlation-Id` (propagated/generated). `POST /compras`
  also accepts `Idempotency-Key` (mirrors `id_externo`+`origem`).
- Authorization: `sale.*` permissions evaluated via WRKS `AccessDecision` (cached; invalidated by
  `journey-os.modelo.acesso.alterado`).

---

## 1. Oportunidades — `/oportunidades`  · perm `sale.oportunidade.*`

| Verb | Path | Permission | Notes |
|---|---|---|---|
| POST | `/oportunidades` | `sale.oportunidade.criar` | create deal (manual or from qualified lead) |
| GET | `/oportunidades` | `sale.oportunidade.read` | paged, filter by estagio/responsavel/estado |
| GET | `/oportunidades/{id}` | `sale.oportunidade.read` | includes stage history |
| PATCH | `/oportunidades/{id}/estagio` | `sale.oportunidade.mover` | move pipeline stage |
| POST | `/oportunidades/{id}/ganhar` | `sale.oportunidade.fechar` | mark won |
| POST | `/oportunidades/{id}/perder` | `sale.oportunidade.fechar` | mark lost (requires motivo) |

- Request (POST): `{ "leadId": "uuid", "valorEstimado": 1997.00, "moeda": "BRL", "responsavelId": "uuid", "estagio": "NOVA" }`
- Response 201: `{ "oportunidadeId": "uuid", "estagio": "NOVA", "estado": "NOVA" }`.

- `WHEN an oportunidade is created, THE SYSTEM SHALL persist it in estado NOVA and publish journey-os.oportunidade.criada.`
- `WHEN an oportunidade stage is changed, THE SYSTEM SHALL append a historico_estagio row and publish journey-os.oportunidade.estagio.alterado.`
- `WHEN an oportunidade is marked won, THE SYSTEM SHALL set estado=GANHA and publish journey-os.oportunidade.ganha.`
- `IF an oportunidade is marked lost without motivo_perda, THEN THE SYSTEM SHALL reject with 422 error.code 'sale.oportunidade.motivo-obrigatorio'.`
- `IF an oportunidade already in GANHA or PERDIDA receives another close, THEN THE SYSTEM SHALL reject with 409 error.code 'sale.oportunidade.ja-fechada'.`

## 2. Ofertas — `/ofertas`  · perm `sale.oferta.*`

| Verb | Path | Permission |
|---|---|---|
| GET/POST | `/ofertas` | `sale.oferta.read` / `sale.oferta.criar` |
| GET/PUT | `/ofertas/{id}` | `read` / `editar` (creates new version) |
| POST | `/ofertas/{id}/desativar` | `sale.oferta.desativar` |

- `WHEN an oferta is edited, THE SYSTEM SHALL create a new versao and keep prior versions immutable.`
- `IF preco is negative, THEN THE SYSTEM SHALL reject with 422 error.code 'sale.oferta.preco-invalido'.`

## 3. Compras — `/compras`  · perm `sale.compra.*`

| Verb | Path | Permission | Notes |
|---|---|---|---|
| POST | `/compras` | `sale.compra.registrar` | **idempotent** ingestion by `(id_externo, origem)` |
| GET | `/compras` | `sale.compra.read` | paged, filter by contato/status/periodo |
| GET | `/compras/{id}` | `sale.compra.read` | includes items + attribution breakdown |
| POST | `/compras/{id}/estornar` | `sale.compra.estornar` | reverse recognized revenue |
| POST | `/compras/{id}/cancelar` | `sale.compra.cancelar` | cancel a confirmed purchase |

- Request (POST): `{ "idExterno": "HOT-9981", "origem": "hotmart", "contatoRef": "rafael@acme.com", "baseLegal": "EXECUCAO_CONTRATO", "oportunidadeId": "uuid", "itens": [ { "ofertaId": "uuid", "quantidade": 1, "valorUnitario": 1997.00 } ] }`
- Response 201: `{ "compraId": "uuid", "valorTotal": 1997.00, "status": "CONFIRMADA", "duplicada": false }`.

- `WHEN a compra is registered with an (id_externo, origem) not yet present, THE SYSTEM SHALL recognize revenue, run attribution, recompute LTV, and publish journey-os.compra.confirmada.`
- `WHEN a compra is registered with an (id_externo, origem) that already exists, THE SYSTEM SHALL return the existing compra (duplicada=true) and SHALL NOT recognize revenue again.`
- `IF the sum of itens valor_total does not equal valor_total, THEN THE SYSTEM SHALL reject with 422 error.code 'sale.compra.receita-inconsistente'.`
- `IF baseLegal is absent or not in the allowed set, THEN THE SYSTEM SHALL reject with 422 error.code 'sale.compra.base-legal-invalida'.`
- `WHEN a compra is estornada or cancelada, THE SYSTEM SHALL adjust recognized revenue, recompute the contact LTV, and SHALL NOT delete the historical row.`

## 4. Atribuição — `/atribuicao`  · perm `sale.atribuicao.*`

| Verb | Path | Permission |
|---|---|---|
| GET | `/atribuicao/modelos` | `sale.atribuicao.read` |
| POST | `/atribuicao/modelos` | `sale.atribuicao.criar` (new version, inactive) |
| POST | `/atribuicao/modelos/{versao}/activate` | `sale.atribuicao.ativar` |
| GET | `/compras/{id}/atribuicao` | `sale.atribuicao.read` (breakdown) |

- `WHEN an attribution model version is activated, THE SYSTEM SHALL deactivate the previous active version atomically and SHALL re-attribute affected compras.`
- `THE SYSTEM SHALL ensure that the sum of attributed amounts of a compra equals its recognized revenue.`
- `IF activating a model version that does not exist, THEN THE SYSTEM SHALL respond 404 error.code 'sale.atribuicao.modelo-nao-encontrado'.`
- `WHILE no attribution model is active, THE SYSTEM SHALL fall back to LAST_TOUCH for new compras.`

## 5. LTV — `/ltv`  · perm `sale.ltv.*`

| Verb | Path | Permission |
|---|---|---|
| GET | `/ltv/{contatoRef}` | `sale.ltv.read` |
| GET | `/ltv` | `sale.ltv.read` (paged, top contacts by value) |

- `THE SYSTEM SHALL compute LTV as the deterministic sum of a contact's CONFIRMADA purchases.`
- `THE SYSTEM SHALL list LTV ordered by valor_total descending by default.`

---

## Error catalogue (SALE)

| error.code | HTTP | category |
|---|---|---|
| `sale.oportunidade.motivo-obrigatorio` | 422 | validation |
| `sale.oportunidade.ja-fechada` | 409 | conflict |
| `sale.oportunidade.nao-encontrada` | 404 | not_found |
| `sale.oferta.preco-invalido` | 422 | validation |
| `sale.compra.base-legal-invalida` | 422 | validation |
| `sale.compra.receita-inconsistente` | 422 | validation |
| `sale.compra.nao-encontrada` | 404 | not_found |
| `sale.atribuicao.modelo-nao-encontrado` | 404 | not_found |
| `sale.atribuicao.soma-invalida` | 409 | business_rule |

> Idempotent re-ingestion of a compra is **not** an error: it returns 200/201 with `duplicada=true`.
> Cross-cutting `iam.*` JWT codes are emitted on token validation (see WRKS `api-contract.md`).
