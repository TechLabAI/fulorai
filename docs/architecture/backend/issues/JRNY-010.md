# JRNY-010 -- AssetQueryClient (conteúdo publicado dos estágios) + reação a asset.versao.publicada

## Contexto
Estágios referenciam assets publicados de ASST (`asset_ref_id`). JRNY lê o conteúdo vigente via
Feign `AssetQueryClient` e reage a `asset.versao.publicada` para atualizar a referência — sem
rerotear leads.

## Spec de referencia
- SPEC-10-integrations
- hub-integration.md
- SPEC-09-messaging-architecture

## Escopo
- `AssetQueryPort` → `@FeignClient(name="asst-service")` `AssetQueryClient` (leitura de asset publicado).
- Resolução do conteúdo vigente do estágio na leitura da jornada (quando `asset_ref_id` presente).
- Consumer `AssetVersaoPublicadaConsumer`: atualiza a referência de conteúdo dos estágios cujo
  `asset_ref_id = assetId`; **não** dispara reroteamento.
- Degradação graciosa: ASST indisponível → estágio retorna referência sem conteúdo resolvido (não quebra a jornada).

## Resultado esperado
Estágios exibem o conteúdo publicado correto; nova publicação de asset atualiza a referência sem efeito colateral de roteamento.

## Criterios de aceite
- [ ] `GET /journeys/{id}` resolve conteúdo de estágio via `AssetQueryClient` quando há `asset_ref_id`.
- [ ] `asset.versao.publicada` atualiza referências sem criar decisões de roteamento.
- [ ] ASST indisponível não impede leitura da jornada (fallback).

## Dependencias
- JRNY-003 (estágios)
- INT-JRNY-002 (infra Feign/discovery)

## Estimativa
M

## Prioridade
P4
