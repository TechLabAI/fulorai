# ASST-004 -- Versionamento imutável (criar versão + numeração)

## Contexto
Criação de versões imutáveis de asset (autoria manual), com numeração incremental por asset.

## Spec de referencia
- SPEC-02-asset-lifecycle
- SPEC-04-data-model-migrations

## Escopo
- `CriarVersaoService` (application, `@Transactional`): cria `versao_asset` (origem=MANUAL, RASCUNHO).
- `AssetController` endpoints `POST /{id}/versoes`, `GET /{id}/versoes`, `GET /{id}/versoes/{numero}`.
- Numeração: próximo `numero` sequencial; unicidade `(asset_id, numero)`.
- Bloqueio de mutação de versão existente → 409 `asst.versao.imutavel`.

## Resultado esperado
Novas versões são imutáveis e numeradas; tentativa de edição é rejeitada.

## Criterios de aceite
- [ ] 1ª versão recebe `numero=1`; 2ª recebe `numero=2`.
- [ ] Edição de versão existente → 409 `asst.versao.imutavel`.
- [ ] Versão criada nasce em estado RASCUNHO.

## Dependencias
- ASST-003 (precede)

## Estimativa
M

## Prioridade
P2
