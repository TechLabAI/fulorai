# Backend API Cross-Link — JRNY (FE ↔ jrny-service)

> Liga o FE JRNY ao contrato REST do `jrny-service`. O FE **não redefine** contratos — referencia.
> Fonte da verdade: `docs/architecture/backend/services/jrny-service/contracts/api-contract.md` +
> `data-model.md`.

## Superfície consumida

| Área | Base path | Permissões | Consumido por (FE) |
|---|---|---|---|
| Journey CRUD | `/api/v1/journeys` | `jrny.jornada.*` | `feature-journey-list`, `feature-journey-builder` |
| Stages | `/api/v1/journeys/{id}/estagios` | `jrny.estagio.*` | `feature-journey-builder`, `feature-stage-editor` |
| Routing rules | `/api/v1/routing/rules` | `jrny.regra.*` / `jrny.roteamento.ler` | `feature-routing-engine` |
| Routing queries | `/api/v1/routing/leads/{leadId}/journey` · `/decisions` | `jrny.roteamento.ler` | `feature-decision-log` |

## Enums espelhados (do `data-model.md`)

- `estadoJornada`: `RASCUNHO` · `PUBLICADA` · `ARQUIVADA`
- `tipoEstagio`: `CAPTURA` · `NUTRICAO` · `QUALIFICACAO` · `OFERTA` · `FECHAMENTO` · `POS_VENDA`
- `assistIa` (decisão): `USADO` · `IGNORADO` · `INDISPONIVEL`  ← **3 valores, não boolean**
- `resultado` (decisão): `ROTEADO` · `SEM_MUDANCA` · `NAO_ROTEADO`
- `estado` (inscrição): `ATIVA` · `CONCLUIDA` · `ENCERRADA`

> **Nota:** a vision (`_brief`/`01`) fala em "badge assistIa" de forma binária por simplicidade; o
> contrato real é **ternário**. O FE mapeia: `USADO → "IA ✓"`, `IGNORADO|INDISPONIVEL → neutro
> "roteamento determinístico"`. SPEC-03/07 já usam o enum ternário.

## `condicao` (gramática de snapshot — `data-model.md §5`)

```json
{ "operador": "E|OU",
  "predicados": [ { "campo": "scoreAgregado", "op": ">=", "valor": 70 } ] }
```

- Campos: `scoreAgregado` (0..100), `dimensoes.<DIM>` (`PERFIL|ENGAJAMENTO|INTENCAO|CAPACIDADE|URGENCIA|ADERENCIA`),
  `estadoQualificacao`, `segmentoId`, `atributo.<chave>`.
- Operadores: `= <> > >= < <= in nin existe`. Combinadores: `E` (AND), `OU` (OR).
- O `ConditionBuilderComponent` (FE) é **formulário estruturado** sobre essa gramática — não query-builder visual livre.

## Diffs / gaps (FE precisa, BE ainda não expõe)

| # | Item | Situação | Encaminhamento |
|---|---|---|---|
| G1 | **Endpoint de analytics/funil** (`feature-journey-analytics`) | `api-contract.md` cobre `/journeys` + `/routing`, **não** funil. | `GET /api/v1/journeys/analytics` **proposto** (SPEC-04). Confirmar com BE ou derivar de projeção Elastic `journey-events`. Feature atrás da flag `jrny.journey-analytics`; degrada para vazio. |
| G2 | **Label do `assetRefId`** (estágio) | `estagio.asset_ref_id` é id lógico (ASST). O nome do asset não vem no `EstagioResponse`. | FE precisa de `assetRefLabel` — confirmar se o BE resolve o label (cross-link) ou se o FE mostra só o id no MVP (`AssetRefPickerComponent` resolve via ASST quando disponível). |
| G3 | **`temRegrasSaindo`** por estágio | Derivável de `GET /routing/rules?jornadaId=` (origem = estágio). | FE computa client-side cruzando regras × estágios; sem novo endpoint. |
| G4 | **Reorder em lote** | MVP: sequência de `PATCH /estagios/{id}` de `ordem`. | Sem endpoint batch; otimista com rollback (SPEC-04/07). Reavaliar batch se houver jank. |

> Nenhum gap **bloqueia** o scaffold (A4) — G1/G2 viram entrada de backlog (A3). A UI degrada
> graciosamente (analytics vazio; label = id) até o BE fechar os contratos.

## Referências
- BE: `jrny-service/contracts/{api-contract,data-model,event-contracts}.md`
- `SPEC-04-data-access.md` (gap G1) · `06-risks-gaps-assumptions.md`
