# INT-ASST-006 -- AssetQueryClient (contrato provedor p/ COMM/JRNY/SALE)

## Contexto
Contrato de leitura de assets publicados exposto por ASST e consumido por COMM, JRNY e SALE.

## Spec de referencia
- hub-integration.md
- SPEC-01-api-surface

## Escopo
- Expor superfície estável `GET /api/v1/assets/{id}/published` + `GET /api/v1/assets?estado=PUBLICADO`.
- DTO `AssetQueryResponse` estável (nunca entity); só versões PUBLICADO.
- Documentar o contrato Feign para consumidores (`@FeignClient(name="asst-service")`).

## Resultado esperado
Consumidores leem deterministicamente a versão vigente; rascunhos/rejeitados nunca expostos.

## Criterios de aceite
- [ ] `/published` retorna apenas a versão vigente (PUBLICADO).
- [ ] Resposta é DTO estável (não entity).
- [ ] Asset sem versão publicada → 404 `asst.asset.sem-versao-publicada`.

## Dependencias
- ASST-006 (precede)

## Estimativa
S

## Prioridade
P6
