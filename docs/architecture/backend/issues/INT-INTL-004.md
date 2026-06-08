# INT-INTL-004 -- Integração ASST (asset como fonte de conhecimento)

## Contexto
Assets publicados alimentam a Base de Conhecimento.

## Spec de referência
- SPEC-03, `contracts/hub-integration.md §2`

## Escopo
`AssetQueryClient` (`@FeignClient(name="asst-service")`) para buscar conteúdo publicado; consumo de
`asset.versao.publicada` → ingestão idempotente (`fonte=ASSET`, `assetId:versao`). WireMock nos testes.

## Resultado esperado
Nós de conhecimento criados/atualizados a partir de assets.

## Critérios de aceite
- [ ] `asset.versao.publicada` cria/atualiza nó `ASSET`
- [ ] Conteúdo ausente → buscado via `AssetQueryClient`
- [ ] Reentrega não duplica

## Dependências
- INTL-011

## Estimativa
M

## Prioridade
P4
