# INTL-011 -- KnowledgeIngestService + ingestão de asset

## Contexto
Curadoria e indexação de nós, incluindo ingestão a partir de assets publicados.

## Spec de referência
- SPEC-03, SPEC-05, `contracts/hub-integration.md §2`

## Escopo
`KnowledgeIngestService`: criar/editar/arquivar nó; indexar (embedding via `KnowledgePort` →
projeção `knowledge-nodes`); ingestão por `asset.versao.publicada` (fonte `ASSET`, idempotente por
`assetId:versao`), buscando conteúdo via `AssetQueryClient` quando ausente.

## Resultado esperado
Nós curados e indexados; asset reentregue atualiza (não duplica).

## Critérios de aceite
- [ ] Indexar nó → embedding + projeção `knowledge-nodes` + status `INDEXADO`
- [ ] Falha de embedding → nó fica `RASCUNHO` + `503`
- [ ] Editar nó indexado → versão+1 + reprojeção
- [ ] Asset reentregue → 1 nó por `assetId:versao`

## Dependências
- INTL-007, INTL-009, INTL-010 (precedem)

## Estimativa
L

## Prioridade
P4
