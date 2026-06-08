# ASST-006 -- Publicação + versão vigente + evento asset.versao.publicada

## Contexto
Conclusão do golden path (evento-âncora): publicar um asset aprovado promove a versão a vigente
e notifica a plataforma.

## Spec de referencia
- SPEC-02-asset-lifecycle
- SPEC-09-messaging-architecture

## Escopo
- `PublicarAssetService` (`APROVADO → PUBLICADO`): seta `versao_vigente_id`, marca versão `PUBLICADA`.
- `AssetApprovalController`: `POST /{id}/publish`; `AssetController`: `GET /{id}/published`.
- Emitir `journey-os.asset.versao.publicada` (outbox) após commit.
- Publicar nova versão preserva versões publicadas anteriores.

## Resultado esperado
Versão aprovada vira vigente, consumível por COMM/JRNY/SALE; evento-âncora emitido.

## Criterios de aceite
- [ ] publish fora de APROVADO → 409 `asst.estado.transicao-invalida`.
- [ ] `versao_vigente_id` aponta para a versão aprovada; estado=PUBLICADO.
- [ ] `asset.versao.publicada` emitido com `assetId/versaoId/numero/tipoAsset`.
- [ ] Republicação não duplica o evento (idempotente — ver ASST-013).
- [ ] Publicar v2 mantém v1 retida.

## Dependencias
- ASST-005 (precede)

## Estimativa
M

## Prioridade
P2
